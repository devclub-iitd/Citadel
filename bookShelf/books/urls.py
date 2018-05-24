from django.conf.urls import url

from . import views

# from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [
    
    url(r'^$', views.index, name='index'),
    url(r'^upload/$',views.upload,name='upload'),
    url(r'^approve/$', views.approve ,name='approve'),
    url(r'^remove_unapproved_document/$', views.remove_unapproved_document ,name='remove_unapproved_document'),
    url(r'^approve_unapproved_document/$', views.approve_unapproved_document ,name='approve_unapproved_document'),
    url(r'^rename/$', views.rename ,name='rename'),
    url(r'^userlogin/$', views.userlogin ,name='userlogin'),
    url(r'^userlogout/$', views.userlogout ,name='userlogout'),
    url(r'^api/structure$', views.APIstructure ,name='structure'),
    url(r'^heartbeat$', views.heartbeat ,name='heartbeat'),
    url(r'^searchtest$', views.searchtest ,name='searchtest'),
    url(r'^api/search$', views.APIsearch, name='search')
]
