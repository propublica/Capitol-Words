from django.conf.urls.defaults import *
from django.conf import settings
from django.http import HttpResponse
from django.views.generic.simple import direct_to_template

from views import *
import emitters

#from mongo_views import *

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
phrase_tree_handler = Resource(PhraseTreeHandler, authentication=authorizer)
phrase_by_category_handler = Resource(PhraseByCategoryHandler, authentication=authorizer)
phrase_over_time_handler = Resource(PhraseOverTimeHandler, authentication=authorizer)
chart_handler = Resource(ChartHandler, authentication=authorizer)
legislator_lookup_handler = Resource(LegislatorLookupHandler, authentication=authorizer)
fulltext_search_handler = Resource(FullTextSearchHandler, authentication=authorizer)
doclist_handler = Resource(DocListHandler, authentication=authorizer)
docdetail_handler = Resource(DocDetailHandler, authentication=authorizer)
billdetail_handler = Resource(BillDetailHandler, authentication=authorizer)
bill_list_handler = Resource(BillListHandler, authentication=authorizer)
similar_document_handler = Resource(SimilarDocumentHandler, authentication=authorizer)
similar_entity_handler = Resource(SimilarEntityHandler, authentication=authorizer)
month_list_handler = Resource(MonthListHandler, authentication=authorizer)
dates_in_month_handler = Resource(DatesInMonthHandler, authentication=authorizer)


urlpatterns = patterns('',

        url(r'^$',
            direct_to_template,
            #'django.views.generic.simple.direct_to_template',
            {'template': 'api/docs.html',
             'extra_context': {
                'page': 'index',
                }
            },
            name='cwod_docs'),

        (r'^locksmith/', include('locksmith.auth.urls')),

        url(r'^dates\.(?P<emitter_format>\w+)$', phrase_over_time_handler),

        url(r'^chart\/(?P<chart_type>\w+)\.(?P<emitter_format>\w+)$', chart_handler),

        url(r'^phrases\/(?P<entity_type>\w+)\.(?P<emitter_format>\w+)$', phrase_by_category_handler),

        url(r'^phrases\.(?P<emitter_format>\w+)$', popular_phrase_handler),

        url(r'^tree\.(?P<emitter_format>\w+)$', phrase_tree_handler),

        url(r'^legislators\.(?P<emitter_format>\w+)$', legislator_lookup_handler),

        url(r'^text\.(?P<emitter_format>\w+)$', fulltext_search_handler),

        url(r'^documents\.(?P<emitter_format>\w+)$', doclist_handler),

        url(r'^document\.(?P<emitter_format>\w+)$', docdetail_handler),

        #url(r'^bill\.(?P<emitter_format>\w+)$', billdetail_handler),

        #url(r'^bills\.(?P<emitter_format>\w+)$', bill_list_handler),

        url(r'^similar\.(?P<emitter_format>\w+)$', similar_document_handler),

        url(r'^_similar\.(?P<emitter_format>\w+)$', similar_entity_handler),

        url(r'^_month_list\.(?P<emitter_format>\w+)$', month_list_handler),

        url(r'^_dates_in_month\.(?P<emitter_format>\w+)$', dates_in_month_handler),

)
