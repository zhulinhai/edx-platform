"""
A tiny app that checks for a status message.
"""

import logging
from openedx.core.djangoapps.site_configuration import helpers as configuration_helpers
from django.conf import settings
from .models import GlobalStatusMessage

log = logging.getLogger(__name__)


def get_site_status_msg(course_key):
    """
    Pull the status message from the database.

    Caches the message by course.
    """
    must_show_message = configuration_helpers.get_value('show_global_message', settings.SHOW_GLOBAL_MESSAGE)
    if must_show_message:
        try:
            # The current() value for GlobalStatusMessage is cached.
            if not GlobalStatusMessage.current().enabled:
                return None

            return GlobalStatusMessage.current().full_message(course_key)
        # Make as general as possible, because something broken here should not
        # bring down the whole site.
        except:  # pylint: disable=bare-except
            log.exception("Error while getting a status message.")
            return None
