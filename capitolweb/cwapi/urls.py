from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^term_counts_by_day/$', views.term_counts_by_day, name='term_counts_by_day'),
    url(r'^search/$', views.search_text_match, name='search_text_match'),
    url(r'^count/$', views.search_results_page, name='search_results_page'),
]
