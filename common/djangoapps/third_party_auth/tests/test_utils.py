import json

import os.path
from contextlib import contextmanager

import django.test
import mock
from mock import MagicMock, patch
from django.conf import settings
from django.test import TestCase
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from mako.template import Template
from provider import constants
from provider.oauth2.models import Client as OAuth2Client
from storages.backends.overwrite import OverwriteStorage

from third_party_auth.models import cache as config_cache
from third_party_auth.models import (
    LTIProviderConfig,
    OAuth2ProviderConfig,
    ProviderApiPermissions,
    SAMLConfiguration,
    SAMLProviderConfig
)
from third_party_auth.saml import EdXSAMLIdentityProvider, get_saml_idp_class
from third_party_auth.utils import UsernameGenerator
from third_party_auth.tests import testutil
from third_party_auth.models import SAMLProviderConfig

from third_party_auth.models import SAMLProviderConfig

AUTH_FEATURES_KEY = 'ENABLE_THIRD_PARTY_AUTH'
AUTH_FEATURE_ENABLED = AUTH_FEATURES_KEY in settings.FEATURES


class GenerateUsernameTestCase(testutil.TestCase):

    def setUp(self):
        self.enable_saml()
        self.user = User.objects.create(
            username='my_self_user'
        )
        self.fullname = 'My Self User'

    def test_separator(self):
        """
        The first step to generate a hinted username is the separator character of the
        full name string. This test makes sure that we are generating a username replacing
        all whitespaces by a character configured in settings or in site_configurations.
        """
        saml = self.configure_saml_provider(
            enabled=True,
            name="Saml Test",
            idp_slug="test",
            backend_name="saml_backend",
            other_settings= {'SEPARATOR': '.'}
        )
        generator = UsernameGenerator(saml.other_settings)
        username = generator.replace_separator(self.fullname)
        return self.assertEqual(username, "My.Self.User")

    def test_generate_username_in_lowercase(self):
        """
        Test if the full name that comes from insert_separator method
        it's converted in lowercase.
        """
        saml = self.configure_saml_provider(
            enabled=True,
            name="Saml Test",
            idp_slug="test",
            backend_name="saml_backend",
            other_settings= {'LOWER': True}
        )
        generator = UsernameGenerator(saml.other_settings)
        new_username = generator.process_case('My_Self_User')
        return self.assertEqual(new_username, 'my_self_user')

    def test_generate_username_not_lowercase(self):
        """
        Test if the full name that comes from insert_separator method
        is not converted in lowercase and preserves their original lowercases and
        uppers cases.
        """
        saml = self.configure_saml_provider(
            enabled=True,
            name="Saml Test",
            idp_slug="test",
            backend_name="saml_backend",
            other_settings= {'LOWER': False}
        )
        generator = UsernameGenerator(saml.other_settings)
        new_username = generator.process_case('My_Self_User')
        return self.assertEqual(new_username, 'My_Self_User')

    def test_generate_username_with_consecutive(self):
        """
        It should return a new user with a consecutive number.
        """
        saml = self.configure_saml_provider(
            enabled=True,
            name="Saml Test",
            idp_slug="test",
            backend_name="saml_backend",
            other_settings= {'RANDOM': False}
        )

        for i in range (1, 6):
            User.objects.create(
                username='my_self_user_{}'.format(i)
            )
        
        generator = UsernameGenerator(saml.other_settings)
        new_username = generator.generate_username(self.user.username)
        # We have 6 users: Five created in the loop with a consecutive
        # number and another one that comes from initial setUp,
        # the first has not consecutive number due to is
        # not neccesary append an differentiator. We expect a new user with
        # the consecutive number 6.
        return self.assertEqual(new_username, 'my_self_user_6')

    @patch('third_party_auth.utils.UsernameGenerator.consecutive_or_random')
    def test_generate_username_with_random(self, mock_random):
        """
        It should return a username with a random integer
        at the end of the username generated.
        """
        saml = self.configure_saml_provider(
            enabled=True,
            name="Saml Test",
            idp_slug="test",
            backend_name="saml_backend",
            other_settings= {'RANDOM': True}
        )
        mock_random.return_value = 4589
        generator = UsernameGenerator(saml.other_settings)
        new_username = generator.generate_username(self.user.username)
        return self.assertEqual(new_username, 'my_self_user_4589')
