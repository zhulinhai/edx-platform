import logging
from celery import task  # pylint: disable=no-name-in-module
# from opaque_keys.edx.keys import CourseKey

# from django.contrib.auth.models import User

# from microsite_configuration import microsite
# from lms.djangoapps.completion.utils import GenerateCompletionReport
from django.core.urlresolvers import reverse

from student.models import CourseEnrollmentManager
from xmodule.modulestore.django import modulestore

from rocket_chat.utils import (
    get_rocket_chat_settings,
    initialize_api_rocket_chat,
    get_subscriptions,
)

LOG = logging.getLogger(__name__)


@task()
def send_email_notification():

    courses = [course for course in modulestore().get_courses() if course.rocket_chat_email_notifications]

    for course in courses:
        users = CourseEnrollmentManager().users_enrolled_in(course.id)
        rocket_chat_settings = get_rocket_chat_settings()
        api_rocket_chat = initialize_api_rocket_chat(rocket_chat_settings)

        course_url = reverse('course_root', args=[course.id])
        course_name = course.display_name
        if api_rocket_chat:

            for user in users:
                username = user.username
                response = api_rocket_chat.users_create_token(username=username)
                response = response.json()

                data = response.get('data', {})

                auth_token = data.get('authToken', None)
                user_id = data.get('userId', None)

                names = "//".join([s["name"] for s in get_subscriptions(api_rocket_chat, auth_token, user_id, True)])
                LOG.info("user %s, channels %s, course %s, url %s", username, names, course_name, course_url )

    LOG.info("This is a task test")
    return 4
