from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^search/speaker/(?P<name>.*)/$', views.search_by_speaker, name='search_by_speaker'),
    url(r'^search/title/(?P<title>.*)/$', views.search_by_title, name='search_by_title'),
    url(r'^search/entities/$', views.search_by_entities, name='search_by_entities'),
    url(r'^search/multi/$', views.search_by_params, name='search_by_params'),
    url(r'^count/$', views.count_of_term_in_content, name='count_of_term_in_content'),

]
