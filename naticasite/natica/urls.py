from django.conf.urls import url
from . import views

urlpatterns = [
    # eg: /natica/
    #! url(r'^$', views.index, name='index'),

    url(r'^$', views.index, name='index'),
]

