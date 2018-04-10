"""
Tests for the Mgmt Commands Feature on the Sysadmin page
"""
from mock import patch
import unittest

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile

from dashboard.tests.test_sysadmin import SysadminBaseTestCase

from openedx.stanford.lms.djangoapps.instructor.lti_grader import LTIGrader


always_true = lambda *args, **kwargs: True
always_false = lambda *args, **kwargs: False


@unittest.skipUnless(
    settings.FEATURES.get('ENABLE_SYSADMIN_DASHBOARD'),
    'ENABLE_SYSADMIN_DASHBOARD not set',
)
class TestLtiGrader(SysadminBaseTestCase):
    """Tests all code paths in Sysadmin Mgmt Commands"""

    def setUp(self):
        super(TestLtiGrader, self).setUp()
        self._setsuperuser_login()
        self.post_params = {
            'command': 'fake_command',
            'key1': 'value1',
            'key2': 'value2',
            'kwflags': ['kwflag1', 'kwflag2'],
            'args': ['arg1', 'arg2'],
        }
        self.data = SimpleUploadedFile(
            'file.csv',
            '\n'.join([
                'ID,Anonymized User ID,email,grade, max_grade, comments,',
                '1,abcdabcd,abcd@abcd.com,5,10,not bad',
                '2,cdefcdef,cdef@cdef.com,6,10,great',
            ])
        )
        self.grader = LTIGrader('course_id', 'url_base', 'lti_key', 'lti_secret')

    def test_lti_grader_properly_initialized(self):
        self.assertEquals('course_id', self.grader.course_id)
        self.assertEquals('url_base', self.grader.url_base)
        self.assertEquals('lti_key', self.grader.key)
        self.assertEquals('lti_secret', self.grader.secret)

    def test_get_first_anon_id(self):
        first_anon_id = self.grader._get_first_anon_id(self.data)  # pylint: disable=protected-access
        self.assertEquals(first_anon_id, 'abcdabcd')

    def test_generate_valid_grading_rows(self):
        valid_rows = self.grader._generate_valid_grading_rows(self.data)  # pylint: disable=protected-access
        self.assertEquals((1, u'abcdabcd', u'abcd@abcd.com', 5.0, 10.0, u'not bad'), valid_rows.next())
        self.assertEquals((2, u'cdefcdef', u'cdef@cdef.com', 6.0, 10.0, u'great'), valid_rows.next())

    def test_update_grades_passport_failure(self):
        with patch('openedx.stanford.lms.djangoapps.instructor.lti_grader.lti_connection') as mock_lti_connection:
            mock_lti_connection.validate_lti_passport.side_effect = always_false
            actual_output = self.grader.update_grades(self.data)['error']
            expected_output = ['LTI passport sanity check failed. Your lti_key (lti_key) or lti_secret (lti_secret) are probably incorrect.']
            self.assertEquals(expected_output, actual_output)

    def test_update_grades_success(self):
        def side_effect(_url_base, _key, _secret, grade_row):
            return (True, grade_row[0], grade_row[2])
        with patch('openedx.stanford.lms.djangoapps.instructor.lti_grader.lti_connection') as mock_lti_connection:
            mock_lti_connection.validate_lti_passport.side_effect = always_true
            mock_lti_connection.post_grade.side_effect = side_effect
            actual_output = self.grader.update_grades(self.data)['success']
            expected_output = [
                'Grade post successful: user id 1 (email: abcd@abcd.com).',
                'Grade post successful: user id 2 (email: cdef@cdef.com).',
            ]
            self.assertEquals(expected_output, actual_output)

    def test_update_grades_failure(self):
        def side_effect(_url_base, _key, _secret, grade_row):
            return (False, grade_row[0], grade_row[2])
        with patch('openedx.stanford.lms.djangoapps.instructor.lti_grader.lti_connection') as mock_lti_connection:
            mock_lti_connection.validate_lti_passport.side_effect = always_true
            mock_lti_connection.post_grade.side_effect = side_effect
            actual_output = self.grader.update_grades(self.data)['error']
            expected_output = [
                'Grade post failed: user id 1 (email: abcd@abcd.com).',
                'Grade post failed: user id 2 (email: cdef@cdef.com).',
            ]
            self.assertEquals(expected_output, actual_output)
