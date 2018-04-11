from mock import patch, Mock

from django.test.client import RequestFactory
from django.test.utils import override_settings

from capa.tests.response_xml_factory import OptionResponseXMLFactory
from courseware import module_render as render
from courseware.model_data import FieldDataCache
from courseware.tests.factories import InstructorFactory
from courseware.tests.factories import StaffFactory
from courseware.tests.factories import UserFactory
from xmodule.modulestore.tests.django_utils import ModuleStoreTestCase
from xmodule.modulestore.tests.factories import CourseFactory
from xmodule.modulestore.tests.factories import ItemFactory
from xmodule.x_module import STUDENT_VIEW


@override_settings(ANALYTICS_DATA_URL='dummy_url')
class TestInlineAnalytics(ModuleStoreTestCase):
    """
    Verify that Inline Analytics fragment is generated correctly
    """

    def setUp(self):
        super(TestInlineAnalytics, self).setUp()
        self.user = UserFactory.create()
        self.request = RequestFactory().get('/')
        self.request.user = self.user
        self.request.session = {}
        self.course = CourseFactory.create(
            org='A',
            number='B',
            display_name='C',
        )
        self.staff = StaffFactory(course_key=self.course.id)
        self.instructor = InstructorFactory(course_key=self.course.id)
        self.problem_xml = OptionResponseXMLFactory().build_xml(
            question_text='The correct answer is Correct',
            num_inputs=2,
            weight=2,
            options=['Correct', 'Incorrect'],
            correct_option='Correct',
        )
        self.descriptor = ItemFactory.create(
            category='problem',
            data=self.problem_xml,
            display_name='Option Response Problem',
            rerandomize='never',
        )
        self.location = self.descriptor.location
        self.field_data_cache = FieldDataCache.cache_for_descriptor_descendents(
            self.course.id,
            self.user,
            self.descriptor,
        )
        self.field_data_cache_staff = FieldDataCache.cache_for_descriptor_descendents(
            self.course.id,
            self.staff,
            self.descriptor,
        )
        self.field_data_cache_instructor = FieldDataCache.cache_for_descriptor_descendents(
            self.course.id,
            self.instructor,
            self.descriptor,
        )

    @patch('courseware.module_render.has_access', Mock(return_value=True))
    def test_inline_analytics_enabled(self):
        module = render.get_module(
            self.user,
            self.request,
            self.location,
            self.field_data_cache,
        )
        result_fragment = module.render(STUDENT_VIEW)
        self.assertIn('Staff Analytics Info', result_fragment.content)

    @override_settings(ANALYTICS_DATA_URL=None)
    def test_inline_analytics_disabled(self):
        module = render.get_module(
            self.user,
            self.request,
            self.location,
            self.field_data_cache,
        )
        result_fragment = module.render(STUDENT_VIEW)
        self.assertNotIn('Staff Analytics Info', result_fragment.content)

    def test_inline_analytics_no_access(self):
        module = render.get_module(
            self.user,
            self.request,
            self.location,
            self.field_data_cache,
        )
        result_fragment = module.render(STUDENT_VIEW)
        self.assertNotIn('Staff Analytics Info', result_fragment.content)

    def test_inline_analytics_staff_access(self):
        module = render.get_module(
            self.staff,
            self.request,
            self.location,
            self.field_data_cache_staff,
        )
        result_fragment = module.render(STUDENT_VIEW)
        self.assertIn('Staff Analytics Info', result_fragment.content)

    def test_inline_analytics_instructor_access(self):
        module = render.get_module(
            self.instructor,
            self.request,
            self.location,
            self.field_data_cache_instructor,
        )
        result_fragment = module.render(STUDENT_VIEW)
        self.assertIn('Staff Analytics Info', result_fragment.content)

    @patch('courseware.module_render.has_access', Mock(return_value=True))
    @override_settings(INLINE_ANALYTICS_SUPPORTED_TYPES={'ChoiceResponse': 'checkbox'})
    def test_unsupported_response_type(self):
        module = render.get_module(
            self.user,
            self.request,
            self.location,
            self.field_data_cache,
        )
        result_fragment = module.render(STUDENT_VIEW)
        self.assertIn('Staff Analytics Info', result_fragment.content)
        self.assertIn(
            'The analytics cannot be displayed for this type of question.',
            result_fragment.content
        )

    @patch('courseware.module_render.has_access', Mock(return_value=True))
    def test_rerandomization_set(self):
        descriptor = ItemFactory.create(
            category='problem',
            data=self.problem_xml,
            display_name='Option Response Problem2',
            rerandomize='always',
        )
        location = descriptor.location
        field_data_cache = FieldDataCache.cache_for_descriptor_descendents(
            self.course.id,
            self.user,
            descriptor
        )
        module = render.get_module(
            self.user,
            self.request,
            location,
            field_data_cache,
        )
        result_fragment = module.render(STUDENT_VIEW)
        self.assertIn('Staff Analytics Info', result_fragment.content)
        self.assertIn(
            'The analytics cannot be displayed for this question as it uses randomization.',
            result_fragment.content
        )

    def test_no_problems(self):
        descriptor = ItemFactory.create(
            category='html',
            display_name='HTML Component',
        )
        location = descriptor.location
        field_data_cache = FieldDataCache.cache_for_descriptor_descendents(
            self.course.id,
            self.user,
            descriptor
        )
        module = render.get_module(
            self.user,
            self.request,
            location,
            field_data_cache,
        )
        result_fragment = module.render(STUDENT_VIEW)
        self.assertNotIn('Staff Analytics Info', result_fragment.content)
