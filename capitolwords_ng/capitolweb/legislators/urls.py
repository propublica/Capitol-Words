from django.conf.urls import url

from . import views
from rest_framework.documentation import include_docs_urls

urlpatterns = [
    url(r'^docs/', include_docs_urls(title='Legislator API')),
    url(r'^search/$', views.search_by_params, name='search_by_params'),
    url(r'^person/(?P<bioguide_id>\w+)/$', views.find_by_bioguide_id, name='find_by_bioguide_id'),
    url(r'^current/$', views.list_current, name='current_congress'),
]
