"""  URLConf for Django user registration and authentication.

    Activation keys get matched by \w+ instead of the more specific [a-fA-F0-9]{40} because a bad
    activation key should still get to the view; that way it can return a sensible "invalid key"
    message instead of a confusing 404.
"""

from django.conf.urls.defaults import *
# from django.views.generic.simple import direct_to_template
from django.views.generic.base import TemplateView
from django.contrib.auth import views as auth_views

from dbe.cregistration.views import *


urlpatterns = patterns('',
    url(r'^register/$', Register.as_view(), name='reg_register'),
    url(r'^register/complete/$', RegistrationComplete.as_view(), name='reg_complete'),
    url(r'^activate/(?P<activation_key>\w+)/$', Activate.as_view(), name='reg_activate'),


    # AUTH VIEWS

    url(r'^login/$', auth_views.login, {'template_name': 'login.html'}, name='auth_login'),
    url(r'^logout/$', auth_views.logout, {'template_name': 'logout.html'}, name='auth_logout'),

    url(r'^password/reset/done/$', auth_views.password_reset_done,
        dict(template_name="pwd_reset_done.html"), name='auth_password_reset_done'),

    url(r'^password/change/$', auth_views.password_change,
        dict(template_name="pwd_change.html"), name='auth_password_change'),

    url(r'^password/change/done/$', auth_views.password_change_done,
        dict(template_name="pwd_change_done.html"), name='auth_password_change_done'),

    url(r'^password/reset/$', auth_views.password_reset,
        dict(template_name="pwd_reset.html"), name='auth_password_reset'),

    url(r'^password/reset/confirm/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$',
       auth_views.password_reset_confirm,
       dict(template_name="pwd_reset_confirm.html"),
       name='auth_password_reset_confirm'),

    url(r'^password/reset/complete/$', auth_views.password_reset_complete,
       dict(template_name="pwd_reset_fin.html"),
       name='auth_password_reset_complete'),

   )
