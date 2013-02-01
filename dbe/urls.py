from django.conf.urls.defaults import *
from django.contrib import admin
from django.views.generic.simple import direct_to_template
import settings
admin.autodiscover()
admin.site.root_path = "/admin/"

urlpatterns = patterns('',
    (r'^admin/'          , include(admin.site.urls)),
    (r'^accounts/'       , include('registration.urls')),
    (r'^bombquiz/'       , include('dbe.bombquiz.urls')),
    (r'^forum/'          , include('dbe.forum.urls')),
    (r'^portfolio/'      , include('dbe.portfolio.urls')),
    (r'^questionnaires/' , include('dbe.questionnaire.urls')),
    (r'^blog/'           , include('dbe.blog.urls')),
    (r'^sb/'             , include('dbe.sb.urls')),
    (r'^issues/'         , include('dbe.issues.urls')),

    # (r''                     , 'django.views.generic.simple.redirect_to', {'url': '/questionnaires/'}),

    # (r'^todo/'      , include('dbe.todo.urls')),
    # (r'^social/'     , include('dbe.social.urls')),
    # (r'^social/'     , include('dbe.social.urls')),
    # (r'^photo/'     , include('dbe.photo.urls')),
    # (r'^static/(?P<path>.*)$' , 'django.views.static.serve', {'document_root': settings.STATIC_ROOT}),
    # (r'^photo/'              , include('dbe.photo.urls')),
    # (r'^cal/'                , include('dbe.cal.urls')),
    # (r''                     , 'django.views.generic.simple.redirect_to', {'url': '/questionnaires/'}),

    # (r'^dbe/', include('dbe.todo.urls')),
    # (r"^comments/", include("django.contrib.comments.urls")),
    # (r'^objperms/', include('dbe.operms.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs'
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^static/(?P<path>.*)$' , 'django.views.static.serve', {'document_root': settings.STATIC_ROOT}),
        (r'^media/(?P<path>.*)$' , 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
   )

urlpatterns += patterns('',
    (r''                 , direct_to_template, {'template': "index.html"}),
)
