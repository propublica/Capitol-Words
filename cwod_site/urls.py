from django.conf.urls.defaults import *


urlpatterns = patterns('',

        (r'^api/', include('cwod_api.urls')),

        (r'^', include('cwod.urls')),
)
