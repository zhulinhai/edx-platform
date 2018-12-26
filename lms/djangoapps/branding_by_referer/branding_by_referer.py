"""
Set user logo and other visual elements according to referrer
"""
from openedx.core.djangoapps.site_configuration import helpers as configuration_helpers
import collections
import copy
import json
from datetime import datetime, timedelta
from openedx.core.djangoapps.user_api.models import UserPreference
from django.utils.deprecation import MiddlewareMixin
from django.utils.six.moves.urllib.parse import urlparse
from django.utils.six import iteritems
from django.conf import settings
from django.shortcuts import redirect
import edx_oauth2_provider


class SetBrandingByReferer(MiddlewareMixin):
    """
    If the referrer is valid -meaning one that exists in
    site_configuration- we used its configurations on current_theme_match
    and we store the referer on cookie/UserPreference for any future requests
    """
    MARKETING_SITE_REFERER = 'MARKETING_SITE_REFERER'
    COOKIE_MARKETING_SITE_REFERER = 'COOKIE_MARKETING_SITE_REFERER'

    def process_request(self, request):
        """
        Process request middleware method
        """
        self.pending_cookie = None
        options_dict = configuration_helpers.get_value('THEME_OPTIONS', {'default': True})
        referer_domain = urlparse(request.META.get('HTTP_REFERER', '')).netloc
        branding_overrides = options_dict.get('BRANDING_BY_REFERER', {}).get(referer_domain, None)

        if branding_overrides:
            self.pending_cookie = referer_domain
        else:
            referer_domain = None
            stored_referer_data = self.get_stored_referer_data(request)
            if stored_referer_data:
                is_valid = stored_referer_data['site_domain'] == request.get_host()
                referer_domain = stored_referer_data['referer_domain'] if is_valid else None
                branding_overrides = options_dict.get('BRANDING_BY_REFERER', {}).get(referer_domain, None)

        SetBrandingByReferer.user_referer = referer_domain
        SetBrandingByReferer.current_theme_match = branding_overrides or {}

    def get_stored_referer_data(self, request):
        stored_referer_data = None
        if request.user.is_authenticated:
            stored_referer_data = UserPreference.get_value(request.user, self.MARKETING_SITE_REFERER)
            if stored_referer_data:
                try:
                    stored_referer_data = json.loads(stored_referer_data)
                except ValueError:
                    # Supporting legacy 'string' version
                    stored_referer_data = {
                        'referer_domain': stored_referer_data,
                        'site_domain': request.get_host()
                    }
                    self.update_user_referer_data(request, stored_referer_data)

        if not stored_referer_data:
            referer_on_cookie = request.COOKIES.get(self.COOKIE_MARKETING_SITE_REFERER)
            if referer_on_cookie:
                # Stored on cookie, now lets store it more permanently on UserPreference
                stored_referer_data = {
                    'referer_domain': referer_on_cookie,
                    'site_domain': request.get_host()
                }
                self.update_user_referer_data(request, stored_referer_data)
        return stored_referer_data

    def update_user_referer_data(self, request, data):
        if request.user.is_authenticated:
            UserPreference.objects.update_or_create(
                user=request.user,
                key=self.MARKETING_SITE_REFERER,
                defaults={
                    'value': json.dumps(data)
                }
            )

    def process_response(self, request, response):
        """
        Process response middleware method
        """
        if self.pending_cookie:
            max_age = 30 * 24 * 60 * 60
            expires = datetime.strftime(datetime.utcnow() + timedelta(seconds=max_age), "%a, %d-%b-%Y %H:%M:%S GMT")
            response.set_cookie(
                self.COOKIE_MARKETING_SITE_REFERER,
                self.pending_cookie,
                max_age=max_age,
                expires=expires,
                domain=settings.SESSION_COOKIE_DOMAIN,
                secure=settings.SESSION_COOKIE_SECURE or None
            )
            self.pending_cookie = None

        if SetBrandingByReferer.user_referer:
            # Logic edx-platform/common/djangoapps/student/views/login.py
            oauth_client_ids = request.session.get(edx_oauth2_provider.constants.AUTHORIZED_CLIENTS_SESSION_KEY, [])
            user_referer = '//{}'.format(SetBrandingByReferer.user_referer)
            referer_path = urlparse(request.META.get('HTTP_REFERER', '')).path
            url_resolver_name = getattr(request.resolver_match, 'url_name', None)

            if referer_path == '/logout':
                return redirect(user_referer)

            if url_resolver_name == 'logout' and not oauth_client_ids:
                if response.has_header('Location'):
                    response['Location'] = user_referer

        return response


def get_branding_referer_url_for_current_user():
    """ get valid referer url saved for this user """
    if not getattr(SetBrandingByReferer, 'user_referer', None):
        return None
    return '//{}'.format(getattr(SetBrandingByReferer, 'user_referer'))


def update(target, data):
    """ recursive dict.update """
    for key, value in iteritems(data):
        if isinstance(value, collections.Mapping):
            target[key] = update(target.get(key, {}), value)
        else:
            target[key] = value
    return target


def get_options_with_overrides_for_current_user():
    """
    Helper method to access current overrides dict (e.g. {"logo_src":"example.jpg"})
    """
    options_dict = configuration_helpers.get_value('THEME_OPTIONS', {})
    overrides = copy.deepcopy(getattr(SetBrandingByReferer, 'current_theme_match', {}))
    return update(options_dict, overrides)
