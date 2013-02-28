from django.conf.urls import patterns, include, url
from django.contrib.auth.views import login, logout
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib.auth.decorators import login_required

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from django.contrib.auth.decorators import login_required
admin.autodiscover()

import settings
from dbe.langapp.views import *


urlpatterns = patterns('',
    url(r"^$"                               , login_required(ProfilesView.as_view()), {}, "profiles"),
    url(r"^profile/$"                       , login_required(CreateUpdateProfile.as_view()), {}, "profile"),
    url(r"^profile/(?P<mfpk>\d+)/$"         , login_required(CreateUpdateProfile.as_view()), {}, "profile"),
    # url(r"^styles/(?P<mfpk>\d+)/$"          , login_required(StylesView.as_view()), {}, "styles"),
    url(r"^styles/$"                        , login_required(StylesView.as_view()), {}, "styles"),
    url(r"^delete-profile/(?P<dpk>\d+)/$"   , login_required(DeleteProfile.as_view()), {}, "delete_profile"),
    url(r"^duplicate-profile/(?P<dpk>\d+)/$", login_required(DuplicateProfile.as_view()), {}, "duplicate_profile"),

    (r'^i18n/', include('django.conf.urls.i18n')),
)
