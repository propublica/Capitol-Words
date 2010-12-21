from django.conf.urls.defaults import *


urlpatterns = patterns('',

        url(r'^$',
            'django.views.generic.simple.direct_to_template',
            {'template': 'index.html',
            },
            name='cwod_docs'),

        (r'^api/', include('cwod.urls')),
)
