"""
Tests for course_info
"""

import ddt
from django.conf import settings
from nose.plugins.attrib import attr

from xmodule.html_module import CourseInfoModule
from xmodule.modulestore import ModuleStoreEnum
from xmodule.modulestore.django import modulestore
from xmodule.modulestore.xml_importer import import_course_from_xml
from milestones.tests.utils import MilestonesTestCaseMixin

from ..testutils import (
    MobileAPITestCase, MobileCourseAccessTestMixin, MobileAuthTestMixin
)


@attr(shard=3)
@ddt.ddt
class TestUpdates(MobileAPITestCase, MobileAuthTestMixin, MobileCourseAccessTestMixin, MilestonesTestCaseMixin):
    """
    Tests for /api/mobile/v0.5/course_info/{course_id}/updates
    """
    REVERSE_INFO = {'name': 'course-updates-list', 'params': ['course_id']}

    def verify_success(self, response):
        super(TestUpdates, self).verify_success(response)
        self.assertEqual(response.data, [])

    @ddt.data(True, False)
    def test_updates(self, new_format):
        """
        Tests updates endpoint with /static in the content.
        Tests both new updates format (using "items") and old format (using "data").
        """
        self.login_and_enroll()

        # create course Updates item in modulestore
        updates_usage_key = self.course.id.make_usage_key('course_info', 'updates')
        course_updates = modulestore().create_item(
            self.user.id,
            updates_usage_key.course_key,
            updates_usage_key.block_type,
            block_id=updates_usage_key.block_id
        )

        # store content in Updates item (either new or old format)
        num_updates = 3
        if new_format:
            for num in range(1, num_updates + 1):
                course_updates.items.append(
                    {
                        "id": num,
                        "date": "Date" + str(num),
                        "content": "<a href=\"/static/\">Update" + str(num) + "</a>",
                        "status": CourseInfoModule.STATUS_VISIBLE
                    }
                )
        else:
            update_data = ""
            # old format stores the updates with the newest first
            for num in range(num_updates, 0, -1):
                update_data += "<li><h2>Date" + str(num) + "</h2><a href=\"/static/\">Update" + str(num) + "</a></li>"
            course_updates.data = u"<ol>" + update_data + "</ol>"
        modulestore().update_item(course_updates, self.user.id)

        # call API
        response = self.api_response()

        # verify static URLs are replaced in the content returned by the API
        self.assertNotIn("\"/static/", response.content)

        # verify static URLs remain in the underlying content
        underlying_updates = modulestore().get_item(updates_usage_key)
        underlying_content = underlying_updates.items[0]['content'] if new_format else underlying_updates.data
        self.assertIn("\"/static/", underlying_content)

        # verify content and sort order of updates (most recent first)
        for num in range(1, num_updates + 1):
            update_data = response.data[num_updates - num]
            self.assertEquals(num, update_data['id'])
            self.assertEquals("Date" + str(num), update_data['date'])
            self.assertIn("Update" + str(num), update_data['content'])


@attr(shard=3)
@ddt.ddt
class TestHandouts(MobileAPITestCase, MobileAuthTestMixin, MobileCourseAccessTestMixin, MilestonesTestCaseMixin):
    """
    Tests for /api/mobile/v0.5/course_info/{course_id}/handouts
    """
    REVERSE_INFO = {'name': 'course-handouts-list', 'params': ['course_id']}

    @ddt.data(ModuleStoreEnum.Type.mongo, ModuleStoreEnum.Type.split)
    def test_handouts(self, default_ms):
        with self.store.default_store(default_ms):
            self.add_mobile_available_toy_course()
            response = self.api_response(expected_response_code=200)
            self.assertIn("Sample", response.data['handouts_html'])

    @ddt.data(ModuleStoreEnum.Type.mongo, ModuleStoreEnum.Type.split)
    def test_no_handouts(self, default_ms):
        with self.store.default_store(default_ms):
            self.add_mobile_available_toy_course()

            # delete handouts in course
            handouts_usage_key = self.course.id.make_usage_key('course_info', 'handouts')
            with self.store.branch_setting(ModuleStoreEnum.Branch.draft_preferred, self.course.id):
                self.store.delete_item(handouts_usage_key, self.user.id)

            response = self.api_response(expected_response_code=200)
            self.assertIsNone(response.data['handouts_html'])

    @ddt.data(ModuleStoreEnum.Type.mongo, ModuleStoreEnum.Type.split)
    def test_empty_handouts(self, default_ms):
        with self.store.default_store(default_ms):
            self.add_mobile_available_toy_course()

            # set handouts to empty tags
            handouts_usage_key = self.course.id.make_usage_key('course_info', 'handouts')
            underlying_handouts = self.store.get_item(handouts_usage_key)
            underlying_handouts.data = "<ol></ol>"
            self.store.update_item(underlying_handouts, self.user.id)
            response = self.api_response(expected_response_code=200)
            self.assertIsNone(response.data['handouts_html'])

    @ddt.data(ModuleStoreEnum.Type.mongo, ModuleStoreEnum.Type.split)
    def test_handouts_static_rewrites(self, default_ms):
        with self.store.default_store(default_ms):
            self.add_mobile_available_toy_course()

            # check that we start with relative static assets
            handouts_usage_key = self.course.id.make_usage_key('course_info', 'handouts')
            underlying_handouts = self.store.get_item(handouts_usage_key)
            self.assertIn('\'/static/', underlying_handouts.data)

            # but shouldn't finish with any
            response = self.api_response()
            self.assertNotIn('\'/static/', response.data['handouts_html'])

    @ddt.data(ModuleStoreEnum.Type.mongo, ModuleStoreEnum.Type.split)
    def test_jump_to_id_handout_href(self, default_ms):
        with self.store.default_store(default_ms):
            self.add_mobile_available_toy_course()

            # check that we start with relative static assets
            handouts_usage_key = self.course.id.make_usage_key('course_info', 'handouts')
            underlying_handouts = self.store.get_item(handouts_usage_key)
            underlying_handouts.data = "<a href=\"/jump_to_id/identifier\">Intracourse Link</a>"
            self.store.update_item(underlying_handouts, self.user.id)

            # but shouldn't finish with any
            response = self.api_response()
            self.assertIn("/courses/{}/jump_to_id/".format(self.course.id), response.data['handouts_html'])

    @ddt.data(ModuleStoreEnum.Type.mongo, ModuleStoreEnum.Type.split)
    def test_course_url_handout_href(self, default_ms):
        with self.store.default_store(default_ms):
            self.add_mobile_available_toy_course()

            # check that we start with relative static assets
            handouts_usage_key = self.course.id.make_usage_key('course_info', 'handouts')
            underlying_handouts = self.store.get_item(handouts_usage_key)
            underlying_handouts.data = "<a href=\"/course/identifier\">Linked Content</a>"
            self.store.update_item(underlying_handouts, self.user.id)

            # but shouldn't finish with any
            response = self.api_response()
            self.assertIn("/courses/{}/".format(self.course.id), response.data['handouts_html'])

    def add_mobile_available_toy_course(self):
        """ use toy course with handouts, and make it mobile_available """
        course_items = import_course_from_xml(
            self.store, self.user.id,
            settings.COMMON_TEST_DATA_ROOT, ['toy'],
            create_if_not_present=True
        )
        self.course = course_items[0]
        self.course.mobile_available = True
        self.store.update_item(self.course, self.user.id)
        self.login_and_enroll()
