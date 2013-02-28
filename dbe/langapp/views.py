# Imports {{{
from django.core.urlresolvers import reverse_lazy
from django.core.exceptions import PermissionDenied
from django.utils import translation
from django.contrib import messages

from dbe import settings

from dbe.shared.utils import *
from dbe.langapp.models import *
from dbe.langapp.forms import *

from dbe.langapp.models import max_profiles

from dbe.mcbv.detail import DetailView, View, BaseDetailView
from dbe.mcbv.edit import FormView, UpdateView, CreateUpdateView, DeleteView
from dbe.mcbv.list_custom import ListView, ListFilterView

# }}}

def check_permission(f):
    """Object permission decorator."""
    def wrapped(self):
        profile_error = "You don't have permissions to access this profile."
        obj           = f(self)
        if obj.user != self.user:
            raise PermissionDenied(profile_error)
        return obj

    return wrapped


class ProfileMixin(object):
    @check_permission
    def get_detail_object(self):
        return super(ProfileMixin, self).get_detail_object()


class ProfilesView(ListView):
    list_model    = LanguageProfile
    template_name = "profiles.html"

    def get_list_queryset(self):
        return LanguageProfile.obj.select_related().filter(user=self.user)

    def add_context(self):
        return dict(can_add=self.object_list.can_add(), max_profiles=max_profiles)


class CreateUpdateProfile(CreateUpdateView, DetailView, ProfileMixin):
    """Note: too complex for combined create/update, would be better as separate classes."""
    form_model             = LanguageProfile
    modelform_class        = ProfileForm
    modelform_create_class = ProfileForm
    template_name          = "langapp/profile.html"

    def get_detail_object(self):
        return UserSettings.obj.get(user=self.user)

    @check_permission
    def get_modelform_object(self):
        return super(CreateUpdateProfile, self).get_modelform_object()

    def modelform_valid(self, form):
        form.instance.update(user=self.user)
        messages.success(self.request, "Profile was " + ("Updated" if self.is_update else "Created"))
        return redir('#') if self.is_update else redir("profiles")

    def add_context(self, **kwargs):
        translation.activate( self.request.session.get("django_language", "en") )
        self.edit = self.request.GET.get("edit")

        if self.is_update:
            style        = self.detail_object.resume_style
            fields       = self.get_modelform_object().show_fields()
            self.preview = style.render(fields)


class StylesView(UpdateView):
    form_model      = UserSettings
    modelform_class = StylesForm
    template_name   = "styles.html"

    def get_modelform_object(self) : return UserSettings.obj.get(user=self.user)
    def get_success_url(self)      : return self.request.GET.get("back")


class DeleteProfile(DeleteView, ProfileMixin):
    detail_model  = LanguageProfile
    success_url   = reverse_lazy("profiles")
    confirm       = False
    template_name = "delete_profile.html"


class DuplicateProfile(DetailView, ProfileMixin):
    detail_model  = LanguageProfile

    def get(self, request, *args, **kwargs):
        if LanguageProfile.obj.filter(user=self.user).can_add():
            obj    = self.get_detail_object()
            obj.id = None
            obj.save()
        return redir("profiles")
