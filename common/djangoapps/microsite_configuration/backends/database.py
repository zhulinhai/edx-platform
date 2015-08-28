"""
Microsite backend that reads the configuration from the database

"""
import os.path
import threading
import edxmako
import json

from django.conf import settings
from microsite_configuration.backends.filebased import SettingsFileMicrositeBackend
from microsite_configuration.models import Microsite


class DatabaseMicrositeBackend(SettingsFileMicrositeBackend):
    """
    Microsite backend that reads the microsites definitions
    from a table in the database according to the models.py file
    """

    def has_configuration_set(self):
        """
        Returns whether there is any Microsite configuration settings
        """
        if Microsite.objects.count():
            return True
        else:
            return False

    def set_config_by_domain(self, domain):
        """
        For a given request domain, find a match in our microsite configuration
        and then assign it to the thread local in order to make it available
        to the complete Django request processing
        """
        if not self.has_configuration_set() or not domain:
            return

        candidates = Microsite.objects.all()
        for microsite in candidates:
            subdomain = microsite.subdomain
            if subdomain and domain.startswith(subdomain):
                values = json.loads(microsite.values)
                values['microsite_name'] = microsite.key
                self._set_microsite_config_from_obj(subdomain, domain, values)
                return

        # if no match on subdomain then see if there is a 'default' microsite
        # defined in the db. If so, then use it
        try:
            microsite = Microsite.objects.get(key='default')
            values = json.loads(microsite.values)
            self._set_microsite_config_from_obj(subdomain, domain, values)
            return
        except Microsite.DoesNotExist:
            return

    def get_template_path(self, relative_path, **kwargs):
        """
        Returns a path (string) to a Mako template, which can either be in
        a microsite directory (as an override) or will just return what is passed in which is
        expected to be a string
        """

        leading_slash = kwargs.get('leading_slash', False)

        if not self.is_request_in_microsite():
            return '/' + relative_path if leading_slash else relative_path

        template_dir = str(self.get_value('template_dir', self.get_value('microsite_name')))

        if template_dir:
            search_path = os.path.join(
                settings.MICROSITE_ROOT_DIR,
                template_dir,
                'templates',
                relative_path
                )

            if os.path.isfile(search_path):
                path = '/{0}/templates/{1}'.format(
                    template_dir,
                    relative_path
                )
                return path

        return '/' + relative_path if leading_slash else relative_path

    def enable_microsites(self, log):
        """
        Enable the use of microsites, from a dynamic defined list in the db
        """
        if not settings.FEATURES['USE_MICROSITES']:
            return

        microsites_root = settings.MICROSITE_ROOT_DIR

        if microsites_root.isdir():
            settings.TEMPLATE_DIRS.append(microsites_root)
            edxmako.paths.add_lookup('main', microsites_root)
            settings.STATICFILES_DIRS.insert(0, microsites_root)

            log.info('Loading microsite path at %s', microsites_root)
        else:
            log.error(
                'Error loading %s. Directory does not exist',
                microsites_root
            )

    def get_value_for_org(self, org, val_name, default):
        """
        Returns a configuration value for a microsite which has an org_filter that matches
        what is passed in
        """
        if not self.has_configuration_set():
            return default

        # Filter at the db
        candidates = Microsite.objects.all()
        for microsite in candidates:
            current = json.loads(microsite.values)
            org_filter = current.get('course_org_filter')
            if org_filter:
                return current.get(val_name, default)

        return default

    def get_all_orgs(self):
        """
        This returns a set of orgs that are considered within all microsites.
        This can be used, for example, to do filtering
        """
        org_filter_set = set()
        if not self.has_configuration_set():
            return org_filter_set

        # Get the orgs in the db
        candidates = Microsite.objects.all()
        for microsite in candidates:
            current = json.loads(microsite.values)
            org_filter = current.get('course_org_filter')
            if org_filter:
                org_filter_set.add(org_filter)

        return org_filter_set

    def _set_microsite_config_from_obj(self, subdomain, domain, microsite_object):
        """
        Helper internal method to actually find the microsite configuration
        """
        config = microsite_object.copy()
        config['subdomain'] = subdomain
        config['site_domain'] = domain
        self.current_request_configuration.data = config
