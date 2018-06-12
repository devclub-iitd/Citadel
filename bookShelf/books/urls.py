from django.conf.urls import url

from . import views

# from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [
    
    url(r'^$', views.index, name='index'),
    url(r'^upload/$',views.upload, name='upload'),
    url(r'^approve/$', views.approve, name='approve'),
    url(r'^remove_unapproved_document/$', views.remove_unapproved_document, name='remove_unapproved_document'),
    url(r'^approve_unapproved_document/$', views.approve_unapproved_document, name='approve_unapproved_document'),
    url(r'^download_course/$', views.download_course, name='download_course'),
    url(r'^bulk_approve/$', views.bulk_approve, name='bulk_approve'),
    url(r'^force_integrity/$', views.force_integrity, name='force_integrity'),
    url(r'^finalize_approvals/$', views.finalize_approvals, name='finalize_approvals'),
    url(r'^rename/$', views.rename, name='rename'),
    url(r'^userlogin/$', views.userlogin, name='userlogin'),
    url(r'^userlogout/$', views.userlogout, name='userlogout'),
    url(r'^api/structure$', views.APIstructure, name='structure'),
    url(r'^api/search$', views.APIsearch, name='search'),
]
