from django.contrib.auth import login
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.http import Http404
from django.http import HttpResponse


def superuser_login_as(request, username):
    if not request.user.is_superuser:
        raise Http404()
    try:
        u1 = User.objects.get(
            username=username,
        )
    except User.DoesNotExist:
        return HttpResponse('User not found')
    u1.backend = 'django.contrib.auth.backends.ModelBackend'
    logout(request)
    login(request, u1)
    return HttpResponse(
        "You are now logged in as {username}".format(
            username=username,
        )
    )
