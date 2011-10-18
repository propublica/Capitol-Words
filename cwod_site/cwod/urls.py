from django.conf.urls.defaults import *
from django.conf import settings
from django.views.generic.simple import direct_to_template

from cwod.views import *


urlpatterns = patterns('',

        url(r'^about\/?$',
            direct_to_template,
            {'template': 'cwod/about.html', },
            name='cwod_about'),
        
        url(r'^contact\/?$',
            direct_to_template,
            {'template': 'cwod/contact.html', },
            name='cwod_contact'),

        url(r'^search\/?$',
            search,
            {},
            name='cwod_search'),

        url(r'^date\/(?P<year>\d{4})\/(?P<month>\d\d)\/(?P<day>\d\d)\/(?P<page_id>[-A-Z0-9]+)-(?P<slug>[-\w]+)\/?$',
            entry_detail,
            {},
            name='cwod_entry_detail'),

        url(r'^date\/(?P<year>\d{4})\/(?P<month>\d\d)\/(?P<day>\d\d)\/?$',
            date_detail,
            {},
            name='cwod_date_detail'),

        url(r'^date\/(?P<year>\d{4})\/(?P<month>\d\d)\/?$',
            month_detail,
            {},
            name='cwod_month_detail'),

        url(r'^date\/?$',
            calendar,
            {},
            name='cwod_calendar'),

        url(r'^term\/(?P<term>.*?)\/?$',
            faster_term_detail,
            {},
            name='cwod_term_detail'),

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

        url(r'legislator\/(?P<bioguide_id>[A-Z][0-9]+)-(?P<slug>[-\w]+)?\/?$',
            legislator_detail,
            {},
            name='cwod_legislator_detail'),

        url(r'legislator\/(?P<bioguide_id>[A-Z][0-9]+)\/?$',
            legislator_detail,
            {}),

        url(r'^state\/?$',
            state_list,
            {},
            name='cwod_state_list'),

        url(r'^state\/(?P<state>[A-Z]+)\/?$',
            state_detail,
            {},
            name='cwod_state_detail'),

        url(r'^party\/?$',
            party_list,
            {},
            name='cwod_party_list'),

        url(r'^party\/(?P<party>\w+)\/?$',
            party_detail,
            {},
            name='cwod_party_detail'),

        url(r'^wordtree\/?$',
            wordtree,
            {},
            name='cwod_wordtree'),

        url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),

        url(r'^embed\/(?P<code>.+)\/?$',
            decode_embed,
            {},
            name='cwod_decode_embed'),

        url(r'^embed\/?$',
            encode_embed,
            {},
            name='cwod_embed'),

        url(r'^embed.js$',
            js_embed,
            {},
            name='cwod_embed_js'),

        url(r'^$',
            index,
            {},
            name='cwod_home'),


)
