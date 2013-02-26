from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.urlresolvers import reverse_lazy

from dbe.cregistration.forms import RegistrationForm
from dbe.cregistration.models import RegistrationProfile

from dbe.mcbv.base import TemplateView
from dbe.mcbv.edit import FormView
from dbe.shared.utils import redir

class RegistrationComplete(TemplateView):
    template_name = "register_done.html"

class Register(FormView):
    form_class    = RegistrationForm
    template_name = "register.html"

    def form_valid(self, form):
        form.save()
        return redir("reg_complete")

class Activate(TemplateView):
    template_name = "activate.html"

    def add_context(self):
        activation_key = self.kwargs.get("activation_key").lower()
        account        = RegistrationProfile.objects.activate_user(activation_key)
        return dict(account=account, expiration_days=settings.ACCOUNT_ACTIVATION_DAYS)
