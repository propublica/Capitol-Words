from django.conf.urls.defaults import *
from django.conf import settings
from django.http import HttpResponse

from views import *

import piston.resource


if getattr(settings, 'USE_LOCKSMITH', False):
    from locksmith.auth.authentication import PistonKeyAuthentication

    class Authorizer(PistonKeyAuthentication):
        def challenge(self):
            resp = HttpResponse("Authorization Required: \n"
        "obtain a key at http://services.sunlightlabs.com/accounts/register/")
            resp.status_code = 401
            return resp

    authorizer = Authorizer()

else:
    authorizer = None

Resource = piston.resource.Resource


popular_phrase_handler = Resource(PopularPhraseHandler, authentication=authorizer)
phrase_by_category_handler = Resource(PhraseByCategoryHandler, authentication=authorizer)
phrase_over_time_handler = Resource(PhraseOverTimeHandler, authentication=authorizer)
legislator_lookup_handler = Resource(LegislatorLookupHandler, authentication=authorizer)
fulltext_search_handler = Resource(FullTextSearchHandler, authentication=authorizer)


urlpatterns = patterns('',

        url(r'^$',
            'django.views.generic.simple.direct_to_template',
            {'template': 'api/index.html',
            },
            name='cwod_docs'),

        url(r'^dates\.(?P<emitter_format>\w+)$', phrase_over_time_handler),

        url(r'^phrases\/(?P<entity_type>\w+)\.(?P<emitter_format>\w+)$', phrase_by_category_handler),

        url(r'^phrases\.(?P<emitter_format>\w+)$', popular_phrase_handler),

        url(r'^legislators\.(?P<emitter_format>\w+)$', legislator_lookup_handler),

        url(r'^text\.(?P<emitter_format>\w+)$', fulltext_search_handler),

)
