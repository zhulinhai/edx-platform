import json

from django.test.client import RequestFactory

from student.tests.factories import UserFactory
from xmodule.modulestore.tests.django_utils import ModuleStoreTestCase
from xmodule.modulestore.tests.factories import CourseFactory

from openedx.stanford.common.djangoapps.student.views import notify_enrollment_by_email


class EnrollmentEmailTests(ModuleStoreTestCase):
    """
    Test sending automated emails to users upon course enrollment
    """
    def setUp(self):
        super(EnrollmentEmailTests, self).setUp()
        self.user = UserFactory(
            username='tester',
            email='tester@gmail.com',
            password='test',
        )
        self.course = CourseFactory(
            org='EDX',
            display_name='test_course',
            number='100',
        )
        self.assertIsNotNone(self.course)
        self.request = RequestFactory().post('random_url')
        self.request.user = self.user

    def _send_enrollment_email(self):
        """
        Send enrollment email to the user and return the Json response data
        """
        return json.loads(notify_enrollment_by_email(self.course, self.user, self.request).content)

    def test_disabled_email_case(self):
        """
        Make sure emails don't fire when enable_enrollment_email setting is disabled
        """
        self.course.enable_enrollment_email = False
        email_result = self._send_enrollment_email()
        self.assertIn('email_did_fire', email_result)
        self.assertFalse(email_result['email_did_fire'])

    def test_custom_enrollment_email_sent(self):
        """
        Test sending of enrollment emails when enable_default_enrollment_email setting is disabled
        """
        self.course.enable_enrollment_email = True
        email_result = self._send_enrollment_email()
        self.assertNotIn('email_did_fire', email_result)
        self.assertIn('is_success', email_result)
