"""
Test LMS instructor background task queue management
"""
from ddt import data
from ddt import ddt
from mock import patch, Mock, MagicMock
from nose.plugins.attrib import attr

from lms.djangoapps.instructor_task.tests.test_api import InstructorTaskCourseSubmitTest

from openedx.stanford.lms.djangoapps.instructor_task.api import request_report


@ddt
class StanfordInstructorTaskCourseSubmitTest(InstructorTaskCourseSubmitTest):
    """
    Test API methods that involve the submission of course-based background tasks
    """

    def setUp(self):
        super(StanfordInstructorTaskCourseSubmitTest, self).setUp()

    @data(True, False)
    def test_ora2(self, include_email):
        api_call = lambda: request_report(
            self.create_task_request(self.instructor),
            self.course.id,
            'ora2_responses',
            include_email=include_email,
        )
        self._test_resubmission(api_call)

    @data('course_forums_usage', 'student_forums')
    def test_task(self, task_type):
        api_call = lambda: request_report(
            self.create_task_request(self.instructor),
            self.course.id,
            task_type,
        )
        self._test_resubmission(api_call)


del(InstructorTaskCourseSubmitTest)
