from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^search/speaker/(?P<name>\w+)/$', views.search_by_speaker, name='search_by_speaker'),
    url(r'^search/title/(?P<title>\w+)/$', views.search_by_title, name='search_by_title'),
    url(r'^search/multi/$', views.search_by_params, name='search_by_params'),

]
