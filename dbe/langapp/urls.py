from django.conf.urls.defaults import patterns, include, url
from django.contrib.auth.views import login, logout
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib.auth.decorators import login_required

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from django.contrib.auth.decorators import login_required
admin.autodiscover()

import settings
from langapp.views import *


urlpatterns = patterns('',
    url(r"^$"                               , login_required(ProfilesView.as_view()), {}, "profiles"),
    url(r"^profile/$"                       , login_required(NewProfile.as_view()), {}, "new_profile"),
    url(r"^profile/(?P<pk>\d+)/$"           , login_required(UpdateProfile.as_view()), {}, "profile"),
    url(r"^styles/$"                        , login_required(StylesView.as_view()), {}, "styles"),
    url(r"^delete-profile/(?P<pk>\d+)/$"    , "langapp.views.delete_profile", {}, "delete_profile"),
    url(r"^duplicate-profile/(?P<pk>\d+)/$" , "langapp.views.duplicate_profile", {}, "duplicate_profile"),

    (r'^i18n/', include('django.conf.urls.i18n')),

    # ajax urls
    # url(r"^ajax/get_leaderboard/$"     , get_leaderboard),
)
