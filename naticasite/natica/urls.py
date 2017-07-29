from django.conf.urls import url
from . import views

urlpatterns = [
    # eg: /natica/
    #! url(r'^$', views.index, name='index'),

    url(r'^$', views.index, name='index'),
    url(r'^ingest/$', views.ingest, name='ingest'),
    url(r'^search/$', views.search, name='search'),
    url(r'^search2/$', views.search2, name='search2'),
    url(r'^prot/$', views.prot, name='prot'),
    url(r'^query/$', views.query, name='query'),

]

