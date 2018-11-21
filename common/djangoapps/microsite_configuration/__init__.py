# -*- coding: utf-8 -*-
"""
This file implements a class which is a handy utility to make any
call to the settings completely microsite aware by replacing the:

from django.conf import settings

with:

from microsite_configuration import settings
"""
from django.conf import settings as base_settings

from microsite_configuration import microsite


class MicrositeAwareSettings(object):
    """
    This class is a proxy object of the settings object from django.
    It will try to get a value from the microsite and default to the
    django settings
    """

    def __getattr__(self, name):
        try:
            if isinstance(microsite.get_value(name), dict):
                return microsite.get_dict(name, getattr(base_settings, name))
            return microsite.get_value(name, getattr(base_settings, name))
        except KeyError:
            return getattr(base_settings, name)


from django.core import signals
# from celery.signals import after_task_publish, before_task_publish, task_prerun

from eox_tenant.signals import (
    start_tenant,
    finish_tenant,
    clear_tenant,
    after_task_publish_tenant,
    before_task_publish_tenant,
    task_prerun_tenant,
)

signals.request_started.connect(start_tenant)
signals.request_finished.connect(finish_tenant)
signals.got_request_exception.connect(clear_tenant)

# after_task_publish.connect(after_task_publish_tenant)
# before_task_publish.connect(before_task_publish_tenant)
# task_prerun.connect(task_prerun_tenant)
