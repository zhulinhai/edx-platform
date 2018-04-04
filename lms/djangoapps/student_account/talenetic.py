from six.moves.urllib_parse import urlencode, unquote
import jwt
import json
from django.conf import settings
from student.models import Registration, UserProfile
from social_core.backends.oauth import BaseOAuth2
from django.contrib.auth.models import User
import uuid
import logging
import social_django

log = logging.getLogger(__name__)

class TaleneticOAuth2(BaseOAuth2):
    """
    Talenetic OAuth2 authentication backend

    """
    settings_dict = settings.CUSTOM_BACKENDS.get('talenetic')
    name = 'talenetic-oauth2'
    REDIRECT_STATE = False
    ID_KEY = 'emailaddress'
    STATE_PARAMETER = False
    AUTHORIZATION_URL = settings_dict.get('AUTH_URL') # https://staging-alj.talenetic.com/jobseekers?clientId={clientid}&secretkey={secretkey}&urlredirect={redirecturl}
    ACCESS_TOKEN_URL = settings_dict.get('ACCESS_TOKEN_URL') # https://staging-alj.talenetic.com/api/sso/Getjwttoken?uid=
    ACCESS_TOKEN_METHOD = 'GET'
    REFRESH_TOKEN_URL = settings_dict.get('REFRESH_TOKEN_URL') # https://staging-alj.talenetic.com/api/sso/RefreshjwtToken?uid=NzIzMzUyOWYtZDkyYi00ZGUwLThhODMtNjBiOTk0NzZlMjVj
    REFRESH_TOKEN_METHOD = 'POST'
    RESPONSE_TYPE = 'code jwt_token'
    REDIRECT_IS_HTTPS = False
    REVOKE_TOKEN_URL = settings_dict.get('LOGOUT_URL') # 'https://staging-alj.talenetic.com/api/logout'
    REVOKE_TOKEN_METHOD = 'GET'

    def get_scope_argument(self):
        return {}


    def auth_complete(self, *args, **kwargs):
        """Completes login process, must return user instance"""
        self.process_error(self.data)
        state = self.validate_state()
        access_url = "{}?uid={}".format(self.access_token_url(), self._get_uid())
        response = self.request_access_token(
            access_url,
            data=self._get_creds(),
            headers=self._get_creds(),
            auth=self.auth_complete_credentials(),
            method=self.ACCESS_TOKEN_METHOD
        )
        self.process_error(response)
        return self.do_auth(response['jwt_token'], response=response,
                            *args, **kwargs)

    def do_auth(self, jwt_token, *args, **kwargs):
        data = self.user_data(jwt_token, *args, **kwargs)
        response =  kwargs.get('response') or {}
        response.update(data or {})
        if 'access_token' not in response:
            response['access_token'] = jwt_token
        kwargs.update({'response': response, 'backend': self})
        return self.strategy.authenticate(*args, **kwargs)



    def _get_uid(self):
        return self.data['uid']


    def auth_params(self, state=None):
        client_id, client_secret = self.get_key_and_secret()

        uri = self.get_redirect_uri(state)
        if self.REDIRECT_IS_HTTPS:
            uri = uri.replace('http://', 'https://')

        params = {
            'urlredirect': uri,
            'clientId': client_id,
            'secretkey': client_secret
        }
        return params

    def get_user_id(self, details, response):
        return details.get('email')


    def get_user_details(self, response):
        response = self._fill_fields(response)
        return {'username': response.get('username'),
                'email': response.get('emailaddress'),
                'fullname': response.get('firstname'),
                'first_name': response.get('firstname')}


    def _fill_fields(self, data):
        if data.get('firstname') is None:
            data['firstname'] = data.get('email').split('@')[0]
        if data.get('username') is None:
            data['username'] = data.get('email').split('@')[0]
        
        return data


    def user_data(self, access_token, *args, **kwargs):
        """Loads user data from service. Implement in subclass"""
        data = self._fill_fields(kwargs.get('response'))
        return {'username': data.get('firstname'),
                'email': data.get('emailaddress'),
                'fullname': data.get('firstname'),
                'first_name': data.get('firstname')}

    def _get_creds(self):
        client_id, client_secret = self.get_key_and_secret()
        return {
            'secretkey': client_secret,
            'clientId': client_id
            }


    def auth_headers(self):
        return {'Accept': 'application/json'}


    def pipeline(self, pipeline, pipeline_index=0, *args, **kwargs):
        """
        This is a special override of the pipeline method.
        This will grab the user from the actual ran pipeline and
        add the incomming guid as a username field to the meta field on the user profile
        """
        out = self.run_pipeline(pipeline, pipeline_index, *args, **kwargs)
        if not isinstance(out, dict):
            return out

        user = out.get('user')

        if user:
            user.social_user = out.get('social')
            user.is_new = out.get('is_new')

        return user


    def revoke_token_params(self, token, uid):
        social_user = social_django.models.DjangoStorage.user.get_social_auth(provider=self.name, uid=uid)
        return {
            'id_token_hint': social_user.extra_data['jwt_token'],
            'state': self.get_session_state()
        }


    def auth_url(self):
        """Return redirect url"""
        params = self.auth_params()
        params = urlencode(params)
        if not self.REDIRECT_STATE:
            # redirect_uri matching is strictly enforced, so match the
            # providers value exactly.
            params = unquote(params)
        return '{0}?{1}'.format(self.authorization_url(), params)