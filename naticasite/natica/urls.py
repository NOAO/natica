from django.conf.urls import url
from . import views

urlpatterns = [
    # eg: /natica/
    #! url(r'^$', views.index, name='index'),

    url(r'^$', views.index, name='index'),
    url(r'^ingest/$', views.ingest_fits, name='ingest_fits'),
    url(r'^search/$', views.search, name='search'),

]

