from django.conf import settings
from django.shortcuts import get_object_or_404

from openedx.core.djangoapps.content.course_overviews.models import CourseOverview
from openedx.core.djangoapps.site_configuration import helpers as configuration_helpers
from edxmako.shortcuts import render_to_response
from courseware.access import has_access
from courseware.courses import sort_by_announcement, sort_by_start_date

from models import CourseCategory


def course_category_list(request):
    categories = CourseCategory.get_category_tree(enabled=True)
    return render_to_response('category_list.html', {'categories': categories})


def course_category(request, slug):
    category = get_object_or_404(CourseCategory, slug=slug, enabled=True)
    courses = map(CourseOverview.get_from_id, category.get_course_ids())

    permission_name = configuration_helpers.get_value(
        'COURSE_CATALOG_VISIBILITY_PERMISSION',
        settings.COURSE_CATALOG_VISIBILITY_PERMISSION
    )

    courses = [c for c in courses if has_access(request.user, permission_name, c)]

    if configuration_helpers.get_value(
        "ENABLE_COURSE_SORTING_BY_START_DATE",
        settings.FEATURES["ENABLE_COURSE_SORTING_BY_START_DATE"]
    ):
        courses = sort_by_start_date(courses)
    else:
        courses = sort_by_announcement(courses)

    return render_to_response('category.html', {'courses': courses, 'category': category})
