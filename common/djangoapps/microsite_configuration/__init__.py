"""
This file implements a class which is a handy utility to make any
call to the settings completely microsite aware by replacing the:

from django.conf import settings

with:

from microsite_configuration import settings
"""
from django.conf import settings as base_settings
from django.conf import settings, UserSettingsHolder

from microsite_configuration import microsite

from eox_tenant.proxy import override_settings


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

# settings = MicrositeAwareSettings()  # pylint: disable=invalid-name


class EdxUserSettingsHolder(UserSettingsHolder):

    def __getattr__(self, name):
        return override_settings(self.default_settings, name)
        # return getattr(self.default_settings, name)


override = EdxUserSettingsHolder(settings._wrapped)
old_wrapped = settings._wrapped
settings._wrapped = override
print(type(override))
print(UserSettingsHolder)
print("PASSED--------------------------------")
