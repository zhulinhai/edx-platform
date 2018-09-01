"""
App Configuration for RocketChat
"""

from __future__ import absolute_import, division, print_function, unicode_literals
from django.apps import AppConfig


class RocketChatAppConfig(AppConfig):
    """
    App Configuration for RocketChat
    """
    name = 'common.djangoapps.rocket_chat'
    verbose_name = 'RocketChat'

    def ready(self):
        from .tasks import *  # pylint: disable=unused-variable
