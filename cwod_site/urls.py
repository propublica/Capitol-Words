from django.conf.urls.defaults import *
from django.contrib import admin
from django.views.generic.simple import redirect_to

admin.autodiscover()


urlpatterns = patterns('',

        (r'^api/$', redirect_to, {'url': '/api/1/'})
        (r'^api/', include('cwod_api.urls')),
        (r'^api/1/', include('cwod_api.urls')),

        (r'^accounts/login/$', 'django.contrib.auth.views.login'),

        (r'^admin/', include(admin.site.urls)),

        (r'^', include('cwod.urls')),
)
