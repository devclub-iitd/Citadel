from django.conf.urls import url

from . import views

# from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [
    
    url(r'^$', views.index, name='index'),
    
    url(r'^view/(?P<path>.*)/$',views.browse,name='browse'),
    url(r'^view/(?P<path>)$',views.browse,name='browse'), ## so that /view/ works without any path

    url(r'^upload/$',views.upload,name='upload'),

	url(r'^approve/$', views.approve ,name='approve'),
    
    url(r'^remove_unapproved_document/$', views.remove_unapproved_document ,name='remove_unapproved_document'),
    url(r'^approve_unapproved_document/$', views.approve_unapproved_document ,name='approve_unapproved_document'),
    url(r'^rename/$', views.rename ,name='rename'),
    
    url(r'^userlogin/$', views.userlogin ,name='userlogin'),
    url(r'^userlogout/$', views.userlogout ,name='userlogout'),
    
    # url(r'^dark/$', views.index, name='index'),
    # url(r'^light/$', views.indexl, name='indexl'),
    # url(r'^dark/view/$', views.display ,name='display'),
    # url(r'^light/view/$', views.displayl ,name='displayl'),

    
	# url(r'^dark/upload/$', views.model_form_upload ,name='upload'),
    # url(r'^light/upload/$', views.model_form_uploadl ,name='uploadl'),
	# url(r'^light/thanks/$', views.thanksl ,name='thanksl'),
	# url(r'^dark/thanks/$', views.thanks ,name='thanks'),


    # url(r'^api/structure$', views.APIstructure ,name='structure'),
    # url(r'^api/upload$', views.APIupload ,name='upload'),


 #    url(r'^api/departments/$', views.DepartmentList.as_view() ),
 #    url(r'^api/course_codes/$', views.Course_codeList.as_view() ),
 #    url(r'^api/document/$', views.DocumentList.as_view() ),
]

## This is not needed and was conflicting with /view/A.b type of requests - ozym4nd145
# urlpatterns = format_suffix_patterns(urlpatterns)
