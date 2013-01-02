from django.conf.urls.defaults import *
from django.contrib import admin

admin.autodiscover()


urlpatterns = patterns('',


        (r'^api/', include('cwod_api.urls')),
        (r'^api/1/', include('cwod_api.urls')),

        (r'^accounts/login/$', 'django.contrib.auth.views.login'),

        (r'^admin/', include(admin.site.urls)),

        (r'^', include('cwod.urls')),
)

