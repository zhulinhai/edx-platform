from random import randint

from django.contrib.auth.models import User


def generate_username(username):
	validate_user = User.objects.filter(username=username).exists()
	while validate_user:
		random = ''.join(["%s" % randint(0, 9) for num in range(0, 4)])
		new_username = username + '_{}'.format(random)
		return new_username

	return username
