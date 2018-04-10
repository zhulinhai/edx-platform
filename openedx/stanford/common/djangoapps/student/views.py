from django.conf import settings
from django.utils.translation import ugettext as _

from courseware.courses import get_course_about_section
from util.date_utils import get_default_time_display
from util.json_request import JsonResponse
from util.keyword_substitution import substitute_keywords_with_data

from openedx.core.djangoapps.site_configuration import helpers as configuration_helpers


def notify_enrollment_by_email(course, user, request):
    """
    Updates the user about the course enrollment by email.

    If the Course has already started, use post_enrollment_email
    If the Course has not yet started, use pre_enrollment_email
    """
    if (not (settings.FEATURES.get('AUTOMATIC_AUTH_FOR_TESTING')) and course.enable_enrollment_email):
        from_address = configuration_helpers.get_value(
            'email_from_address',
            settings.DEFAULT_FROM_EMAIL,
        )
        try:
            if course.has_started():
                subject = get_course_about_section(
                    request,
                    course,
                    'post_enrollment_email_subject',
                )
                message = get_course_about_section(
                    request,
                    course,
                    'post_enrollment_email',
                )
            else:
                subject = get_course_about_section(
                    request,
                    course,
                    'pre_enrollment_email_subject',
                )
                message = get_course_about_section(
                    request,
                    course,
                    'pre_enrollment_email',
                )
            subject = ''.join(subject.splitlines())
            context = {
                'username': user.username,
                'user_id': user.id,
                'name': user.profile.name,
                'course_title': course.display_name,
                'course_id': course.id,
                'course_start_date': get_default_time_display(course.start),
                'course_end_date': get_default_time_display(course.end),
            }
            message = substitute_keywords_with_data(message, context)
            user.email_user(subject, message, from_address)
        except Exception:
            log.error(
                "unable to send course enrollment verification email to user from '{from_address}'".format(
                    from_address=from_address,
                ),
                exc_info=True,
            )
            return JsonResponse({
                'is_success': False,
                'error': _('Could not send enrollment email to the user'),
            })
        return JsonResponse({
            'is_success': True,
            'subject': subject,
            'message': message,
        })
    else:
        return JsonResponse({
            'email_did_fire': False,
        })
