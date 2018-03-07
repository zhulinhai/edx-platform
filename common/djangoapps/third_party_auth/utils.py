from random import randint

from django.contrib.auth.models import User


class UsernameGenerator(object):
    """It Allows to customize the way the username is created based on the fullname"""

    def __init__(self, generator_settings={}):
        default_settings = {
            'SEPARATOR': '_',
            'LOWER': True,
            'RANDOM': False
        }

        self.separator_character = generator_settings.get('SEPARATOR', default_settings['SEPARATOR'])
        self.in_lowercase = generator_settings.get('LOWER', default_settings['LOWER'])
        self.random = generator_settings.get('RANDOM', default_settings['RANDOM'])

    def replace_separator(self, fullname):
        """
        Allows set a custom separator character for each whitespace
        in the fullname string. By default, the separator characte is underscore.
        """
        username = fullname.replace(' ', self.separator_character)
        return username

    def process_username(self, username):
        """
        Allows set the username in lowercase. If value is False,
        it will take the original username that SAML providers give.
        """
        if self.in_lowercase:
            return username.lower()
        else:
            return username

    def consecutive_or_random(self, current_number=0):
        """
        If a username already exists, a subsecuent number will be
        append at the end of the username string. This method allows
        if this subsecuent number be a random or consecutive.
        """
        if self.random:
            subsequent_number = ''.join(["%s" % randint(0, 9) for num in range(0, 4)])
        else:
            subsequent_number = current_number + 1

        return subsequent_number

    def generate_username(self, username):
        """Util function that generates the username"""
        new_username = username
        user_exists = User.objects.filter(username=new_username).exists()
        initial_username = self.process_username(username)

        if not user_exists:
            new_username = initial_username

        counter = 1
        while user_exists:
            subsequent_number = self.consecutive_or_random(counter)
            new_username = '{}_{}'.format(initial_username, subsequent_number)
            user_exists = User.objects.filter(username=new_username).exists()
            counter = counter + 1

        return new_username

    def hint_username(self, fullname):
        """.
        Returns a unique username based on the provided
        full name string.
        """
        username = self.replace_separator(fullname)
        return self.generate_username(username)
