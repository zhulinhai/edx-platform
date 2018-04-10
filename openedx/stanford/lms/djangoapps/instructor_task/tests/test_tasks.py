from functools import partial

from ddt import data
from ddt import ddt
from ddt import unpack
from django.utils.translation import ugettext_noop
from mock import patch

from lms.djangoapps.instructor_task.tests.test_tasks import TestInstructorTasks

from openedx.stanford.lms.djangoapps.instructor_task.tasks import get_course_forums_usage_task
from openedx.stanford.lms.djangoapps.instructor_task.tasks import get_student_forums_usage_task
from openedx.stanford.lms.djangoapps.instructor_task.tasks_helper import push_course_forums_data_to_s3
from openedx.stanford.lms.djangoapps.instructor_task.tasks_helper import push_student_forums_data_to_s3


@ddt
class TestForumsUsageInstructorTasks(TestInstructorTasks):
    """
    Test instructor task that fetches ora2 response data
    """

    @data(get_course_forums_usage_task, get_student_forums_usage_task)
    def test_course_forums_missing_current_task(self, task):
        self._test_missing_current_task(task)

    @data(get_course_forums_usage_task, get_student_forums_usage_task)
    def test_course_forums_with_failure(self, task):
        self._test_run_with_failure(task, 'We expected this to fail')

    @data(get_course_forums_usage_task, get_student_forums_usage_task)
    def test_course_forums_with_long_error_msg(self, task):
        self._test_run_with_long_error_msg(task)

    @data(get_course_forums_usage_task, get_student_forums_usage_task)
    def test_course_forums_with_short_error_msg(self, task):
        self._test_run_with_short_error_msg(task)

    @data(
        (get_course_forums_usage_task, push_course_forums_data_to_s3),
        (get_student_forums_usage_task, push_student_forums_data_to_s3),
    )
    @unpack
    def test_course_forums_runs_task(self, task, push_data_to_s3):
        task_entry = self._create_input_entry()
        task_xmodule_args = self._get_xmodule_instance_args()
        with patch('openedx.stanford.lms.djangoapps.instructor_task.tasks.run_main_task') as mock_main_task:
            task(task_entry.id, task_xmodule_args)
            action_name = ugettext_noop('generated')
            task_fn = partial(push_data_to_s3, task_xmodule_args)
            mock_main_task.assert_called_once_with_args(task_entry.id, task_fn, action_name)
