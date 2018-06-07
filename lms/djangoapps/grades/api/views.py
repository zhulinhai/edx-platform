""" API v0 views. """
import logging

from django.contrib.auth import get_user_model
from django.http import Http404
from opaque_keys import InvalidKeyError
from opaque_keys.edx.keys import CourseKey
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.generics import GenericAPIView, ListAPIView
from rest_framework.response import Response

from courseware.access import has_access
from enrollment.views import course_requires_intervention, call_origin_requires_intervention
from lms.djangoapps.courseware import courses
from lms.djangoapps.courseware.exceptions import CourseAccessRedirect
from lms.djangoapps.grades.api.serializers import GradingPolicySerializer
from lms.djangoapps.grades.course_grade_factory import CourseGradeFactory
from openedx.core.djangoapps.site_configuration import helpers as configuration_helpers
from openedx.core.lib.api.view_utils import DeveloperErrorViewMixin, view_auth_classes
from student.roles import CourseStaffRole

log = logging.getLogger(__name__)
USER_MODEL = get_user_model()


@view_auth_classes()
class GradeViewMixin(DeveloperErrorViewMixin):
    """
    Mixin class for Grades related views.
    """
    def _get_course(self, course_key_string, user, access_action):
        """
        Returns the course for the given course_key_string after
        verifying the requested access to the course by the given user.
        """
        try:
            course_key = CourseKey.from_string(course_key_string)
        except InvalidKeyError:
            raise self.api_error(
                status_code=status.HTTP_404_NOT_FOUND,
                developer_message='The provided course key cannot be parsed.',
                error_code='invalid_course_key'
            )

        try:
            return courses.get_course_with_access(
                user,
                access_action,
                course_key,
                check_if_enrolled=True,
            )
        except Http404:
            log.info('Course with ID "%s" not found', course_key_string)
        except CourseAccessRedirect:
            log.info('User %s does not have access to course with ID "%s"', user.username, course_key_string)

        raise self.api_error(
            status_code=status.HTTP_404_NOT_FOUND,
            developer_message='The user, the course or both do not exist.',
            error_code='user_or_course_does_not_exist',
        )

    def _get_effective_user(self, request, course):
        """
        Returns the user object corresponding to the request's 'username' parameter,
        or the current request.user if no 'username' was provided.

        Verifies that the request.user has access to the requested users's grades.
        Returns a 403 error response if access is denied, or a 404 error response if the user does not exist.
        """

        # Use the request user's if none provided.
        if 'username' in request.GET:
            username = request.GET.get('username')
        else:
            username = request.user.username

        if request.user.username == username:
            # Any user may request her own grades
            return request.user

        # Only a user with staff access may request grades for a user other than herself.
        if not has_access(request.user, CourseStaffRole.ROLE, course):
            log.info(
                'User %s tried to access the grade for user %s.',
                request.user.username,
                username
            )
            raise self.api_error(
                status_code=status.HTTP_403_FORBIDDEN,
                developer_message='The user requested does not match the logged in user.',
                error_code='user_mismatch'
            )

        try:
            return USER_MODEL.objects.get(username=username)

        except USER_MODEL.DoesNotExist:
            raise self.api_error(
                status_code=status.HTTP_404_NOT_FOUND,
                developer_message='The user matching the requested username does not exist.',
                error_code='user_does_not_exist'
            )

    def perform_authentication(self, request):
        """
        Ensures that the user is authenticated (e.g. not an AnonymousUser), unless DEBUG mode is enabled.
        """
        super(GradeViewMixin, self).perform_authentication(request)
        if request.user.is_anonymous:
            raise AuthenticationFailed


class UserGradeView(GradeViewMixin, GenericAPIView):
    """
    **Use Case**

        * Get the current course grades for a user in a course.

        The currently logged-in user may request her own grades, or a user with staff access to the course may request
        any enrolled user's grades.

    **Example Request**

        GET /api/grades/v0/course_grade/{course_id}/users/?username={username}

    **GET Parameters**

        A GET request may include the following parameters.

        * course_id: (required) A string representation of a Course ID.
        * username: (optional) A string representation of a user's username.
          Defaults to the currently logged-in user's username.

    **GET Response Values**

        If the request for information about the course grade
        is successful, an HTTP 200 "OK" response is returned.

        The HTTP 200 response has the following values.

        * username: A string representation of a user's username passed in the request.

        * course_id: A string representation of a Course ID.

        * passed: Boolean representing whether the course has been
                  passed according the course's grading policy.

        * percent: A float representing the overall grade for the course

        * letter_grade: A letter grade as defined in grading_policy (e.g. 'A' 'B' 'C' for 6.002x) or None


    **Example GET Response**

        [{
            "username": "bob",
            "course_key": "edX/DemoX/Demo_Course",
            "passed": false,
            "percent": 0.03,
            "letter_grade": None,
        }]

    """
    def get(self, request, course_id):
        """
        Gets a course progress status.

        Args:
            request (Request): Django request object.
            course_id (string): URI element specifying the course location.

        Return:
            A JSON serialized representation of the requesting user's current grade status.
        """

        course = self._get_course(course_id, request.user, 'load')

        # Grades intervention:
        # if the course was not found, we attempt to find it using the org display name
        if call_origin_requires_intervention(request):
            course_key = CourseKey.from_string(course_id)

            def test_course_for_intervention(org):
                real_course_key = course_key.replace(org=org)
                real_course = self._get_course(unicode(real_course_key), request.user, 'load')

                if not isinstance(real_course, Response) and course_requires_intervention(real_course):
                    log.info('Course with ID "%s" was found using org intervention with [%s]',
                             course_id, unicode(real_course_key))
                    return real_course

            site_orgs = configuration_helpers.get_value('course_org_filter', [])
            possible_courses = filter(None, map(test_course_for_intervention, site_orgs))

            # If we also found a course with the org ID add it to the possibilities
            if not isinstance(course, Response):
                possible_courses.append(course)

            # By now, more than one course is possibly in the list, we need to pick one
            if len(possible_courses) == 1:
                course = possible_courses[0]
            elif len(possible_courses) > 1:
                # This scenario means there is a collision.
                # More than one course where this user has access was found with <ORG>+ID+RUN
                # Where <ORG> is any of the site's orgs or the original org ID
                # We will select the first match of the org against the site's preferred list
                preferred_list = configuration_helpers.get_value(
                    'PREFERRED_ORG_FOR_CERTIFICATES',
                    configuration_helpers.get_value('course_org_filter', [])
                )
                for preferred in preferred_list:
                    match = [x for x in possible_courses if x.org == preferred]
                    if match:
                        course = match[0]
                        break

                log.warn('Collision found on the intervention [%s]. Using [%s] '
                         'based on the site PREFERRED_ORG_FOR_CERTIFICATES',
                         ','.join([unicode(x.id) for x in possible_courses]), unicode(course.id))

        grade_user = self._get_effective_user(request, course)
        course_grade = CourseGradeFactory().read(grade_user, course)

        return Response([{
            'username': grade_user.username,
            'course_key': course_id,
            'passed': course_grade.passed,
            'percent': course_grade.percent,
            'letter_grade': course_grade.letter_grade,
        }])


class CourseGradingPolicy(GradeViewMixin, ListAPIView):
    """
    **Use Case**

        Get the course grading policy.

    **Example requests**:

        GET /api/grades/v0/policy/{course_id}/

    **Response Values**

        * assignment_type: The type of the assignment, as configured by course
          staff. For example, course staff might make the assignment types Homework,
          Quiz, and Exam.

        * count: The number of assignments of the type.

        * dropped: Number of assignments of the type that are dropped.

        * weight: The weight, or effect, of the assignment type on the learner's
          final grade.
    """

    allow_empty = False

    def get(self, request, course_id, **kwargs):
        course = self._get_course(course_id, request.user, 'staff')
        return Response(GradingPolicySerializer(course.raw_grader, many=True).data)
