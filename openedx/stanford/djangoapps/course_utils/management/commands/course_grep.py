"""
Search component data for specific text
"""
from __future__ import unicode_literals

from django.conf import settings
from django.core.management.base import BaseCommand

from opaque_keys.edx.keys import CourseKey
from xmodule.capa_module import CapaDescriptor
from xmodule.html_module import HtmlBlock
from xmodule.modulestore.django import modulestore

_supported_component_types = [
    'capa',
    'html',
]


class Command(BaseCommand):
    """
    Search component data for specific text
    """
    help = __doc__

    def add_arguments(self, parser):
        parser.add_argument(
            '-t',
            '--type',
            action='append',
            choices=_supported_component_types,
            help=(
                'Limit search to specific component types. '
                'By default, search all component types. '
            ),
        )
        parser.add_argument(
            '-c',
            '--course',
            action='append',
            help=(
                'Limit search to a specific course. '
                'By default, search all courses. '
            ),
        )
        parser.add_argument(
            'search_terms',
            help=(
                'Specify one or more search terms, '
                'case-sensitive. '
            ),
            nargs='*',
        )

    def handle(self, *args, **options):
        """
        Execute the command
        """
        terms = options['search_terms'] or ['', ]
        component_types = options.get('type', _supported_component_types)
        course_ids = options.get('course')
        results = search(terms, component_types, course_ids)
        for course, component in results:
            output = format_output(course, component)
            print(output)


def format_output(course, component):
    base = settings.CMS_BASE
    url = "{base}/container/{location}".format(
        base=base,
        location=component.location,
    )
    data = component.data
    data = data.split('\n')
    data = ''.join(data)
    output = "{course_id}	{url}	{data}".format(
        course_id=course.id,
        url=url,
        data=data,
    )
    return output


def get_courses(course_ids=None):
    module_store = modulestore()
    courses = []
    if course_ids:
        for course_id in course_ids:
            course_key = CourseKey.from_string(course_id)
            course = module_store.get_course(course_key)
            if not course:
                raise Exception('No such course_id')
            courses.append(course)
    else:
        courses = module_store.get_courses()
    return courses


def get_components(course_id=None):
    for course in get_courses(course_id):
        for section in course.get_children():
            for subsection in section.get_children():
                for unit in subsection.get_children():
                    for component in unit.get_children():
                        yield course, component


def search(search_terms, component_types=None, course_ids=None):
    for course, component in get_components(course_ids):
        if search_data(component, search_terms, component_types):
            yield (
                course,
                component,
            )


def search_data(component, search_terms, component_types=None):
    if not hasattr(component, 'data'):
        return None
    if component_types:
        if isinstance(component, HtmlBlock):
            if 'html' not in component_types:
                return None
        if isinstance(component, CapaDescriptor):
            if 'capa' not in component_types:
                return None
    if any(term in component.data for term in search_terms):
        return True
    return False
