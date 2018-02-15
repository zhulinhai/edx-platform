from random import randint

from openedx.core.djangoapps.site_configuration import helpers as configuration_helpers

from django.contrib.auth.models import User


class GeneratorUsername(object):

    def __init__(self):
        self.separator_character = '_'
        self.in_lowercase = True
        self.random = True

    def separator(self, fullname):
        username = fullname.replace(' ', self.separator_character)
        return username

    def lower(self, username):
        if self.in_lowercase:
            return username.lower()
        else:
            return username

    def consecutive_or_random(self):
        if self.random:
            random = ''.join(["%s" % randint(0, 9) for num in range(0, 4)])
            return random


def generate_username(username):
    new_username = username
    user_exists = User.objects.filter(username=new_username).exists()

    generator = GeneratorUsername()
    new_username = generator.lower(username)

    while user_exists:
        subsequent_number = generator.consecutive_or_random()
        new_username = new_username + '_{}'.format(subsequent_number)
        user_exists = User.objects.filter(username=new_username).exists()

    return new_username
