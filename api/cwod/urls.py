from django.conf.urls.defaults import *
from django.http import HttpResponse

from views import *

from piston.resource import Resource

popular_phrase_handler = Resource(PopularPhraseHandler)
phrase_by_category_handler = Resource(PhraseByCategoryHandler)
phrase_over_time_handler = Resource(PhraseOverTimeHandler)
legislator_lookup_handler = Resource(LegislatorLookupHandler)


urlpatterns = patterns('',

        url(r'^$',
            'django.views.generic.simple.direct_to_template',
            {'template': 'index.html',
            },
            name='cwod_docs'),

        url(r'^dates\.(?P<emitter_format>\w+)$', phrase_over_time_handler),

        url(r'^phrases\/(?P<entity_type>\w+)\.(?P<emitter_format>\w+)$', phrase_by_category_handler),

        url(r'^phrases\.(?P<emitter_format>\w+)$', popular_phrase_handler),

        url(r'^legislators\.(?P<emitter_format>\w+)$', legislator_lookup_handler),

)
