import logging
import pkg_resources

from web_fragments.fragment import Fragment

from xmodule.x_module import STUDENT_VIEW
from courseware.courses import get_course_by_id, get_course_with_access
from opaque_keys.edx.keys import CourseKey
from django.contrib.auth.models import User
from courseware.module_render import get_module_for_descriptor
from courseware.model_data import FieldDataCache
from openedx.core.djangoapps.crawlers.models import CrawlersConfig
CONTENT_DEPTH = 2

LOG = logging.getLogger(__name__)


class ModifyTeams(object):
    """this class alows to modifies the team's behavior"""

    def __init__(self, request):

        course_id = "course-v1:edX+E2E-101+course"
        user = User.objects.filter( username="staff")
        self.effective_user = user[0]
        self.course_key = CourseKey.from_string(course_id)
        self.course = get_course_by_id(self.course_key, CONTENT_DEPTH)
        self.chapter_url_name = "d500be97e289446ea881b96bb77d3864"
        self.section_url_name = "ce53628e4ccc4139a6507b3695a125be"
        self.unit_url_name = "8a1f71613be44683ace5b45599487f04"
        self.rocket_url_name = "65bc5128d6834b6483cfab904fe5a01e"
        self._prefetch_and_bind_course(request)

        self.chapter = self._find_chapter()
        self.section = self._find_section()

    def get_fragment(self):
        """This method allows to get a fragment from a course's section"""
        section = self._find_unit()
        frag = section.render(STUDENT_VIEW)
        return frag

    def _find_block(self, parent, url_name, block_type, min_depth=None):
        """
        Finds the block in the parent with the specified url_name.
        If not found, calls get_current_child on the parent.
        """
        child = None
        if url_name:
            child = parent.get_child_by(lambda m: m.location.block_id == url_name)
            if not child:
                # User may be trying to access a child that isn't live yet
                child = None
            elif min_depth and not child.has_children_at_depth(min_depth - 1):
                child = None
        if not child:
            child = get_current_child(
                parent, min_depth=min_depth, requested_child=self.request.GET.get("child"))
        return child

    def _find_chapter(self):
        """
        Finds the requested chapter.
        """
        return self._find_block(self.course, self.chapter_url_name, 'chapter', CONTENT_DEPTH - 1)

    def _find_unit(self):
        """
        Finds the requested chapter.
        """
        return self._find_block(self.section, self.unit_url_name, 'sequential', CONTENT_DEPTH - 1)

    def _find_rocket(self):
        """
        Finds the requested chapter.
        """
        return self._find_block(self.unit, self.rocket_url_name, 'vertical', CONTENT_DEPTH - 1)

    def _find_section(self):
        """
        Finds the requested section.
        """
        if self.chapter:
            return self._find_block(self.chapter, self.section_url_name, 'section')


    def _prefetch_and_bind_course(self, request):
        """
        Prefetches all descendant data for the requested section and
        sets up the runtime, which binds the request user to the section.
        """
        self.field_data_cache = FieldDataCache.cache_for_descriptor_descendents(
            self.course_key,
            self.effective_user,
            self.course,
            depth=CONTENT_DEPTH,
            read_only=CrawlersConfig.is_crawler(request),
        )
        self.course = get_module_for_descriptor(
            self.effective_user,
            request,
            self.course,
            self.field_data_cache,
            self.course_key,
            course=self.course,
        )
    def resource_string(self, path):
        """Handy helper for getting resources from our kit."""
        # pylint: disable=no-self-use
        data = pkg_resources.resource_string(__name__, path)
        return data.decode("utf8")
