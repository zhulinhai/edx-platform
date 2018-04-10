from django.core.urlresolvers import reverse

from student.models import CourseEnrollment
from util.keyword_substitution import get_keywords_supported


def data_download_section_data(course_key):
    course_id = unicode(course_key)
    course_id_deprecated = course_key.to_deprecated_string()
    data = {
        'delete_report_download_url': reverse(
            'delete_report_download',
            kwargs={
                'course_id': course_id,
            },
        ),
        'get_course_forums_usage_url': reverse(
            'get_course_forums_usage',
            kwargs={
                'course_id': course_id_deprecated,
            },
        ),
        'get_ora2_email_responses_url': reverse(
            'get_ora2_responses',
            kwargs={
                'course_id': course_id_deprecated,
                'include_email': True,
            },
        ),
        'get_ora2_responses_url': reverse(
            'get_ora2_responses',
            kwargs={
                'course_id': course_id_deprecated,
                'include_email': False,
            },
        ),
        'get_student_forums_usage_url': reverse(
            'get_student_forums_usage',
            kwargs={
                'course_id': course_id,
            },
        ),
        'get_student_responses_url': reverse(
            'get_student_responses',
            kwargs={
                'course_id': course_id_deprecated,
            },
        ),
        'graph_course_forums_usage_url': reverse(
            'graph_course_forums_usage',
            kwargs={
                'course_id': course_id,
            },
        ),
    }
    return data


def metrics_section_data(course_key):
    enrollment = CourseEnrollment.num_enrolled_in(course_key)
    data = {
        'enrollment': enrollment,
    }
    return data


def send_email_section_data():
    keywords = get_keywords_supported()
    data = {
        'keywords_supported': keywords,
    }
    return data


def student_admin_section_data(course_key):
    course_id = unicode(course_key)
    data = {
        'get_blank_lti_url': reverse(
            'get_blank_lti',
            kwargs={
                'course_id': course_id,
            },
        ),
        'upload_lti_url': reverse(
            'upload_lti',
            kwargs={
                'course_id': course_id,
            },
        ),
    }
    return data
