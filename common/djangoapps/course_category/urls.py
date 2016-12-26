from django.conf.urls import patterns, url

import views


urlpatterns = patterns(
    '',
    url(r'^$', views.course_category_list, name='course_category_list'),
    url(r'^(?P<slug>\w+)$', views.course_category, name='course_category'),
)

