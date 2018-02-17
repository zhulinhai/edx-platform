"""
API for submitting background tasks by an instructor for a course.
"""
from lms.djangoapps.instructor_task.api_helper import submit_task

from openedx.stanford.lms.djangoapps.instructor_task.tasks import get_course_forums_usage_task
from openedx.stanford.lms.djangoapps.instructor_task.tasks import get_ora2_responses_task
from openedx.stanford.lms.djangoapps.instructor_task.tasks import get_student_forums_usage_task
from openedx.stanford.lms.djangoapps.instructor_task.tasks import get_student_responses_task


_TASK_MAP = {
    'course_forums_usage': get_course_forums_usage_task,
    'ora2_responses': get_ora2_responses_task,
    'student_forums': get_student_forums_usage_task,
    'student_responses': get_student_responses_task,
}


def request_report(request, course_key, task_type, **kwargs):
    """
    Raise AlreadyRunningError if report is already being generated
    """
    task_class = _TASK_MAP[task_type]
    task_input = {}
    task_key = ''
    if 'include_email' in kwargs:
        task_input['include_email'] = kwargs['include_email']
    task = submit_task(request, task_type, task_class, course_key, task_input, task_key)
    return task
