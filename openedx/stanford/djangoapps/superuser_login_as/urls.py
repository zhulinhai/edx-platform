from django.conf.urls import url


urlpatterns = [
    url(
        r'^su_login_as/(?P<username>[\w.@+-]+)/?$',
        'openedx.stanford.djangoapps.superuser_login_as.views.superuser_login_as',
        name='impersonate',
    ),
]
