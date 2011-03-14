from django.conf.urls.defaults import *

from cwod.views import *


urlpatterns = patterns('',

        url(r'^congress\/?$',
            congress_list,
            {},
            name='cwod_congress_list'),

        url(r'^congress\/(?P<congress>\d+)\/?$',
            congress_detail,
            {},
            name='cwod_congress_detail'),

        url(r'^congress\/(?P<congress>\d+)\/(?P<session>\d+)\/?$',
            congress_session_detail,
            {},
            name='cwod_congress_session_detail'),

        url(r'^congress\/(?P<congress>\d+)\/(?P<session>\d+)\/(?P<pagerange>[-A-Z0-9]+)\/?$',
            congress_pagerange_detail,
            {},
            name='cwod_congress_pagerange_detail'),

        url(r'^legislator\/?$',
            legislator_list,
            {},
            name='cwod_legislator_list'),

        url(r'legislator\/(?P<bioguide_id>[A-Z][0-9]+)\/?$',
            legislator_detail,
            {},
            name='cwod_legislator_detail'),

        url(r'^state\/?$',
            state_list,
            {},
            name='cwod_state_list'),

        url(r'^state\/(?P<state>[A-Z]+)?$',
            state_detail,
            {},
            name='cwod_state_detail'),

        url(r'^party\/?$',
            party_list,
            {},
            name='cwod_party_list'),

        url(r'^party\/(?P<party>\w+)?$',
            party_detail,
            {},
            name='cwod_party_detail'),

        url(r'^wordtree\/?$',
            wordtree,
            {},
            name='cwod_wordtree'),

        url(r'^$',
            'django.views.generic.simple.direct_to_template',
            {'template': 'index.html',
            },
            name='cwod_home'),

)
