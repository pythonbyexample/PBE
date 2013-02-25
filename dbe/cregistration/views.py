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


class Register(FormView):
    form_class    = RegistrationForm
    template_name = "registration_form.html"
    success_url   = reverse_lazy("registration_complete")

class RegistrationComplete(TemplateView):
    template_name = "registration_complete.html"


class Activate(TemplateView):
    template_name = "activate.html"

    def add_context(self):
        activation_key = self.kwargs.get("activation_key").lower()
        account        = RegistrationProfile.objects.activate_user(activation_key)
        return dict(account=account, expiration_days=settings.ACCOUNT_ACTIVATION_DAYS)


# UNUSED

def activate(request, activation_key, template_name='registration/activate.html', extra_context=None):
    activation_key = activation_key.lower()
    account = RegistrationProfile.objects.activate_user(activation_key)

    if extra_context is None:
        extra_context = {}

    context = RequestContext(request)
    for key, value in extra_context.items():
        context[key] = callable(value) and value() or value
    d = { 'account': account, 'expiration_days': settings.ACCOUNT_ACTIVATION_DAYS }
    return render_to_response(template_name, d, context_instance=context)

def register(request, success_url=None,
             form_class=RegistrationForm, profile_callback=None,
             template_name='registration/registration_form.html',
             extra_context=None):
    if request.method == 'POST':
        form = form_class(data=request.POST, files=request.FILES)
        if form.is_valid():
            new_user = form.save(profile_callback=profile_callback)
            # success_url needs to be dynamically generated here; setting a
            # a default value using reverse() will cause circular-import
            # problems with the default URLConf for this application, which
            # imports this file.
            return HttpResponseRedirect(success_url or reverse('registration_complete'))
    else:
        form = form_class()

    if extra_context is None:
        extra_context = {}
    context = RequestContext(request)
    for key, value in extra_context.items():
        context[key] = callable(value) and value() or value
    return render_to_response(template_name,
                              { 'form': form },
                              context_instance=context)
