from django.conf.urls import url
from . import views

urlpatterns = [
    # eg: /natica/
    #! url(r'^$', views.index, name='index'),

    url(r'^$', views.index, name='index'),
    url(r'^ingest/$', views.ingest, name='ingest'),
    url(r'^search/$', views.search, name='search'),
    url(r'^prot/$', views.prot, name='prot'),

]

