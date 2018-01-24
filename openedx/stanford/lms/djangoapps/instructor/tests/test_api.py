from ddt import data
from ddt import ddt
from mock import patch

from lms.djangoapps.instructor.tests.test_api import reverse
from lms.djangoapps.instructor.tests.test_api import TestInstructorAPILevelsDataDump
from lms.djangoapps.instructor_task.api_helper import AlreadyRunningError

_TASK_DATA = [
    'get_course_forums_usage',
    'get_student_forums_usage',
]


@ddt
class TestStanfordInstructorApi(TestInstructorAPILevelsDataDump):

    def setUp(self):
        super(TestStanfordInstructorApi, self).setUp()
        self.data = {
            'course_id': unicode(self.course.id),
        }

    def _get_task_and_url(self, url_name):
        task = "openedx.stanford.lms.djangoapps.instructor_task.api.{task_name}".format(
            task_name='request_report',
        )
        url = reverse(url_name, kwargs=self.data)
        return task, url

    @data(*_TASK_DATA)
    def test_task_already_running(self, url_name):
        task, url = self._get_task_and_url(url_name)
        with patch(task) as mock_task:
            mock_task.side_effect = AlreadyRunningError()
            response = self.client.post(url, {})
        expected = 'report task is already in progress'
        self.assertIn(expected, response.content)

    @data(*_TASK_DATA)
    def test_task_success(self, url_name):
        task, url = self._get_task_and_url(url_name)
        response = self.client.post(url, {})
        expected = 'report is being generated'
        self.assertIn(expected, response.content)


class TestDeleteReportDownload(TestInstructorAPILevelsDataDump):

    def setUp(self):
        super(TestDeleteReportDownload, self).setUp()
        self.data = {
            'course_id': unicode(self.course.id),
        }

    def test_delete_report_download(self):
        def noop():
            pass
        url = reverse('delete_report_download', kwargs=self.data)
        method = 'lms.djangoapps.instructor_task.models.DjangoStorageReportStore.delete_file'
        with patch(method, side_effect=noop()):
            response = self.client.post(url, {})
        self.assertEqual(response.status_code, 200)


del(TestInstructorAPILevelsDataDump)
