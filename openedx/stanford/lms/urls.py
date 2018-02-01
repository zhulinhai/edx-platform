from django.conf import settings
from django.conf.urls import url


urlpatterns = [
    url(
        r'^course_sneakpeek/{}/$'.format(
            settings.COURSE_ID_PATTERN,
        ),
        'student.views.setup_sneakpeek',
        name='course_sneakpeek',
    ),
    url(
        r'^get_analytics_answer_dist/',
        'courseware.views.views.get_analytics_answer_dist',
        name='get_analytics_answer_dist',
    ),
]
if settings.SHIB_ONLY_SITE:
    urlpatterns += [
        url(
            r'^backup_login$',
            'student_account.views.login_and_registration_form',
            {'initial_mode': 'login'},
            name='backup_signin_user',
        ),
        url(
            r'^backup_register$',
            'student_account.views.login_and_registration_form',
            {'initial_mode': 'register'},
            name='backup_register_user',
        ),
    ]
if settings.FEATURES.get('ENABLE_SUPERUSER_LOGIN_AS'):
    urlpatterns += [
        url(
            r'^su_login_as/(?P<username>[\w.@+-]+)/?$',
            'student.views.superuser_login_as',
            name='impersonate',
        ),
    ]
