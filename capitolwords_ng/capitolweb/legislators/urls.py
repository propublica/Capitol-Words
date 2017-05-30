from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^person/(?P<name>\w+)/$', views.find_by_name, name='search_by_speaker'),
    url(r'^person/lookup/(?P<person_id>\d+)/$', views.find_by_id, name='search_by_id'),
    url(r'^person/by_bgid/(?P<bioguide_id>\w+)/$', views.find_by_bioguide_id, name='search_by_id'),
    url(r'^current/$', views.list_current, name='current_congress'),
]
