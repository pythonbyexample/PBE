from django.conf.urls.defaults import *
from django.contrib.auth import views as auth_views
from django.views.generic.simple import direct_to_template, redirect_to
from businesstest.views import Messages

urlpatterns = patterns("businesstest.views",
    # (r"messages/$", "message_list"),
    (r"messages/$", Messages.as_view(), {}, "messages"),
    (r"(\d+)/$", "test"),
    (r"test_done/$", "test_done"),
    # (r"^melting-temp-rc/$", "melting_temp_rc"),
    # (r"^search/(oligo|half|construct|parse|project)/(toggledir|up|down)/(.+)/$", "search", {}, "parse9_search"),
    (r"^$", redirect_to, {"url": "/bt/1/"}),
)

urlpatterns += patterns('',
    (r"^account/", include("registration.urls")),
)
