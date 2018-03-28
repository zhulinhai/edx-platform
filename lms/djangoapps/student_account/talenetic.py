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
    ID_KEY = 'username'
    STATE_PARAMETER = True
    AUTHORIZATION_URL = settings_dict.get('AUTH_URL') # https://staging-alj.talenetic.com/jobseekers?clientId={clientid}&secretkey={secretkey}&urlredirect={redirecturl}
    ACCESS_TOKEN_URL = settings_dict.get('ACCESS_TOKEN_URL') # https://staging-alj.talenetic.com/api/sso/Getjwttoken?uid=
    ACCESS_TOKEN_METHOD = 'POST'
    REFRESH_TOKEN_URL = settings_dict.get('REFRESH_TOKEN_URL') # https://staging-alj.talenetic.com/api/sso/RefreshjwtToken?uid=NzIzMzUyOWYtZDkyYi00ZGUwLThhODMtNjBiOTk0NzZlMjVj
    REFRESH_TOKEN_METHOD = 'POST'
    RESPONSE_TYPE = 'code jwt_token'
    REDIRECT_IS_HTTPS = True
    REVOKE_TOKEN_URL = settings_dict.get('LOGOUT_URL') # 'https://staging-alj.talenetic.com/api/logout'
    REVOKE_TOKEN_METHOD = 'GET'

    # The order of the default scope is important
    DEFAULT_SCOPE = ['openid', 'profile']


    # def extra_data(self, user, uid, response, details=None, *args, **kwargs):
    #     """
    #     Return access_token and extra defined names to store in extra_data field
    #     """
    #     data = super(HarambeeOAuth2, self).extra_data(user, uid, response, details, *args, **kwargs)
    #     data['id_token'] = kwargs['request_id_token']
    #     return data


    def auth_params(self, state=None):
        client_id, client_secret = self.get_key_and_secret()
        
        uri = self.get_redirect_uri(state)
        if self.REDIRECT_IS_HTTPS:
            uri = uri.replace('http://', 'https://')
        
        params = {
            'client_id': client_id,
            'client_secret': client_secret,
            'redirect_uri': uri
        }
        if self.STATE_PARAMETER and state:
            params['state'] = state
        if self.RESPONSE_TYPE:
            params['response_type'] = self.RESPONSE_TYPE
        return params


    def auth_complete_params(self, state=None):
        uri = self.get_redirect_uri(state)
        if self.REDIRECT_IS_HTTPS:
            uri = uri.replace('http://', 'https://')
        return {
            'uid': ''  # request auth code
        }

    def get_user_details(self, response):
    	log.error("this is response {}".format(response))
        data = jwt.decode(response.get('id_token'), verify=False)
        return {'username': data.get('firstname'),
                'email': data.get('emailaddress'),
                'fullname': data.get('firstname'),
                'first_name': data.get('firstname')}


    def user_data(self, access_token, *args, **kwargs):
        """Loads user data from service. Implement in subclass"""
        data = jwt.decode(access_token, verify=False)
        return {'username': data.get('firstname'),
                'email': data.get('emailaddress'),
                'fullname': data.get('firstname'),
                'first_name': data.get('firstname')}


    def auth_headers(self):
        return {'Content-Type': 'application/x-www-form-urlencoded',
                'Accept': 'application/json'}


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

        user_profile = user.profile
        new_meta = {'username': user.email.split('@')[0][0:-6]}

        if len(user_profile.meta) > 0:
            previous_meta = json.loads(user_profile.meta)
            mixed_dicts =\
                (previous_meta.items() + new_meta.items())
            new_meta =\
                {key: value for (key, value) in mixed_dicts}

        user_profile.meta = json.dumps(new_meta)
        user_profile.save()

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
