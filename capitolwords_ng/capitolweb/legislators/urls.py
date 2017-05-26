from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^person/(?P<name>\w+)/$', views.find_by_name, name='search_by_speaker')

]
