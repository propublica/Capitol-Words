from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^search/$', views.search_by_params, name='search_by_params'),
    url(r'^person/(?P<bioguide_id>\w+)/$', views.find_by_bioguide_id, name='find_by_bioguide_id'),
    url(r'^current/$', views.list_current, name='current_congress'),
]
