from django.conf.urls import *
from django.contrib import admin
from django.views.generic.base import TemplateView
import settings
admin.autodiscover()
admin.site.root_path = "/admin/"

urlpatterns = patterns('',
    # (r'^accounts/'       , include('dbe.cregistration.urls')),
    (r'^admin/'          , include(admin.site.urls)),
    (r'^bombquiz/'       , include('dbe.bombquiz.urls')),
    (r'^forum/'          , include('dbe.forum.urls')),
    (r'^portfolio/'      , include('dbe.portfolio.urls')),
    (r'^questionnaires/' , include('dbe.questionnaire.urls')),
    (r'^blog/'           , include('dbe.blog.urls')),
    (r'^sb/'             , include('dbe.sb.urls')),
    (r'^issues/'         , include('dbe.issues.urls')),
    (r'^cal/'            , include('dbe.cal.urls')),
    (r'^store9/'         , include('dbe.store9.urls')),
    (r'^langapp/'        , include('dbe.langapp.urls')),
    (r'^comments/'       , include('dbe.comments.urls')),
    (r'^medtrics/'       , include('dbe.medtrics.urls')),
    (r'^photo_contest/'  , include('dbe.photo_contest.urls')),

    # (r'^books/'     , include('dbe.books.urls')),
    # (r'^todo/'      , include('dbe.todo.urls')),
    # (r'^social/     , include('dbe.social.urls')),
    # (r'^photo/'     , include('dbe.photo.urls')),
    # (r"^comments/"  , include("django.contrib.comments.urls")),
    # (r'^objperms/'  , include('dbe.operms.urls')),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^static/(?P<path>.*)$' , 'django.views.static.serve', {'document_root': settings.STATIC_ROOT}),
        (r'^media/(?P<path>.*)$' , 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
   )

urlpatterns += patterns('',
    (r''                 , TemplateView.as_view(template_name="index.html"), {}, "index"),
)
