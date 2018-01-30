from django.conf.urls import url


from student.views2 import contactanos


urlpatterns = (
    # PAYU CAMPUS ROMERO ENDPOINTS
    url(r'^contactanos$', contactanos.as_view(), name='contactanos'),

)
