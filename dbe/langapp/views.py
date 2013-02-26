# Imports {{{
import json
from string import capwords

from django.template import Context, RequestContext, loader
from django.http import HttpResponse, HttpResponseRedirect, HttpResponsePermanentRedirect, Http404
from django.shortcuts import get_object_or_404, render_to_response, render
from django.views.generic import ListView
from django.views.generic.simple import direct_to_template
from django.contrib.auth.decorators import user_passes_test
from django.core.urlresolvers import reverse_lazy
from django.contrib import messages
from django.template import RequestContext, Template, Context, loader
from django.utils.translation import ugettext as _
from django.utils import translation

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q

from shared.utils import *
from django.shortcuts import render

from languages import settings
from langapp.models import *
from langapp.forms import *

from classviews.list import MultipleObjectMixin
from classviews.list_custom import ListFilterView
from classviews.edit import FormView, UpdateView, CreateView, DeleteView

max_profiles = 11
# }}}

# --- CLASS VIEWS --- #

class ProfilesView(ListView):
    model               = LanguageProfile
    context_object_name = "profiles"
    template_name       = "profiles.html"

    def get_context_data(self, **kwargs):
        c = super(ProfilesView, self).get_context_data(**kwargs)
        pmax = bool(LanguageProfile.obj.filter(user=self.request.user).count() >= max_profiles)
        return updated(c, dict(pmax=pmax, max_profiles=max_profiles))


class NewProfile(CreateView):
    model               = LanguageProfile
    form_class          = NewProfileForm
    success_url         = reverse_lazy("profiles")
    context_object_name = "profile"
    template_name       = "profile.html"

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.user = self.request.user
        instance.save()
        return redir(self.success_url)

    def get_context_data(self, **kwargs):
        c = super(NewProfile, self).get_context_data(**kwargs)
        return updated(c, dict(new=1, edit=1))


class UpdateProfile(UpdateView):
    model               = LanguageProfile
    form_class          = EditProfileForm
    context_object_name = "profile"
    template_name       = "profile.html"

    def form_valid(self, form):
        instance = form.save()
        messages.success(self.request, "Profile was updated")
        return redir(reverse2("profile", pk=self.object.pk))

    def get(self, request, *args, **kwargs):
        translation.activate( self.request.session.get("django_language", "en") )

        self.object = self.get_object()
        if self.object.user != self.request.user:
            return HttpResponse("You don't have permissions to view this profile.")
        return super(UpdateProfile, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        c        = super(UpdateProfile, self).get_context_data(**kwargs)
        edit     = self.request.GET.get("edit", False)

        # render preview
        style   = UserSettings.obj.get(user=self.request.user).resume_style.style
        profile = self.object
        fields  = [(f.name, getattr(profile, f.name)) for f in profile._meta.fields]
        exclude = "id user".split()
        fields  = dict([(spc(name), val) for name, val in fields if val and name not in exclude])
        preview = loader.get_template("styles/style%d.html" % style).render( Context(dict(fields=fields)) )


        return updated(c, dict(edit=edit, preview=preview, context_instance=RequestContext(self.request)))

class StylesView(FormView):
    """ Pick users's style. """
    form_class     = StylesForm
    template_name  = "styles.html"

    def get_form(self, form_class=None):
        self.settings = UserSettings.obj.get(user=self.request.user)
        style = self.settings.resume_style or TypeResumeStyle.obj.get(style=1)
        return self.form_class(style.pk, **self.get_form_kwargs())

    def form_valid(self, form):
        self.settings.resume_style = TypeResumeStyle.obj.get( pk=form.cleaned_data.get("style") )
        self.settings.save()
        return redir( self.request.GET.get("back", None) or reverse2("profiles") )


@login_required
def delete_profile(request, pk=None):
    p = LanguageProfile.obj.get(pk=pk)
    if p.user != request.user:
        return HttpResponse("You don't have permissions to edit this profile.")
    p.delete()
    return redir("profiles")

@login_required
def duplicate_profile(request, pk=None):
    if LanguageProfile.obj.filter(user=request.user).count() >= max_profiles:
        return

    p = LanguageProfile.obj.get(pk=pk)
    if p.user != request.user:
        return HttpResponse("You don't have permissions to duplicate this profile.")
    fields = dict((f.name, getattr(p, f.name)) for f in p._meta.fields)
    del fields["id"]
    LanguageProfile.obj.create(**fields)
    return redir("profiles")

def spc(val):
    return capwords(val.replace('_', ' '))
