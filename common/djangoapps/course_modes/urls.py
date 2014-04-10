from django.conf.urls import include, patterns, url
from django.views.generic import TemplateView

from course_modes import views

urlpatterns = patterns(
    '',
    url(r'^choose/(?P<course_id>[^/]+/[^/]+/[^/]+)$', views.ChooseModeView.as_view(), name="course_modes_choose"),
    url(r'^manual_registration/(?P<course_id>[^/]+/[^/]+/[^/]+)$', views.ChosedManualView.as_view(), name="course_modes_manual"),
)
