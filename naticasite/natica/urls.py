from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^store/$', views.store, name='store'),       # ESSENTIAL
    url(r'^search/$', views.search, name='search'),      # ESSENTIAL
    #url(r'^retrieve/$', views.retrieve, name='retrieve'),# ESSENTIAL

    # eg: /natica/
    #! url(r'^$', views.index, name='index'),
    url(r'^$', views.index, name='index'),
    #url(r'^ingest/$', views.ingest, name='ingest'),
    url(r'^search2/$', views.search2, name='search2'),
    url(r'^prot/$', views.prot, name='prot'),
    url(r'^ana/$', views.analysis, name='analysis'),
    url(r'^query/$', views.query, name='query'),

]


