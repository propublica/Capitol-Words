from django.conf.urls import url

from . import views
from rest_framework.documentation import include_docs_urls

urlpatterns = [
    url(r'^docs/', include_docs_urls(title='Legislator API')),
    url(r'^person/(?P<name>\w+)/$', views.find_by_name, name='search_by_speaker'),
    url(r'^person/lookup/(?P<person_id>\d+)/$', views.find_by_id, name='search_by_id'),
    url(r'^person/by_bgid/(?P<bioguide_id>\w+)/$', views.find_by_bioguide_id, name='search_by_bioguide_id'),
    url(r'^current/$', views.list_current, name='current_congress'),
]
