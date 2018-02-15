from random import randint

from django.contrib.auth.models import User


def generate_username(username):
    new_username = username
    user_exists = User.objects.filter(username=new_username).exists()

    while user_exists:
        random = ''.join(["%s" % randint(0, 9) for num in range(0, 4)])
        new_username = username + '_{}'.format(random)
        user_exists = User.objects.filter(username=new_username).exists()

    return new_username
