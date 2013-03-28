import re

from django.core.mail import send_mail
from django.utils.decorators import method_decorator
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404

from dbe.photo_contest.models import *
from dbe.photo_contest.forms import *

from dbe.mcbv import DetailView, ListView, UpdateView, CreateView, ModelFormSetView, CreateUpdateView
from dbe.mcbv import ArchiveIndexView

from dbe.shared.utils import *
from dbe.shared.utils import group_required

SHA1_RE = re.compile('^[a-f0-9]{40}$')

rejection_tpl = """
    Your photo was rejected for the following reason:\n
        %s\n
    Please try again by submitting a new photo at this url:\n
        %s
    """


class Main(ListView):
    list_model    = ImageProfile
    paginate_by   = 40
    template_name = "photo_contest/list.html"

    def get_list_queryset(self):
        return ImageProfile.obj.filter(active=True)


class DateList(ArchiveIndexView):
    paginate_by      = 40
    allow_empty      = True
    date_list_period = "month"
    template_name    = "photo_contest/list.html"

    def get_dated_queryset(self, ordering=None, **lookup):
        return ImageProfile.obj.filter(active=True)


class ImageView(DetailView):
    detail_model  = ImageProfile
    template_name = "photo_contest/image.html"

    def get_detail_queryset(self):
        return ImageProfile.obj.filter(active=True)


class AddImage(UpdateView):
    """Creates ImageProfile if it does not exists, updates otherwise."""
    form_model      = ImageProfile
    modelform_class = AddImageForm
    template_name   = "photo_contest/add_image.html"

    def get_modelform_object(self):
        """Get ImageProfile based on `activation_key`."""
        key = self.kwargs["key"]
        if SHA1_RE.search(key):
            eprofile = get_object_or_404(EmailProfile, activation_key=key)
            # p = Promotion.obj.get(pk=1)
            # return ImageProfile.obj.get_or_create(email_profile=eprofile, promotion=p)[0]
            return ImageProfile.obj.get_or_create(email_profile=eprofile)[0]
        else:
            raise Http404

    def modelform_valid(self, form):
        """Save & reset `activation_key`."""
        profile = form.save()
        profile.email_profile.update(activation_key='')
        return HttpResponse("Thank you for your submission")


class SignUpView(CreateView):
    form_model      = EmailProfile
    modelform_class = SignUpForm
    template_name   = "signup.html"

    def modelform_valid(self, form):
        """Create email profile, generate key & send image upload url."""
        profile = form.save()
        key     = profile.make_activation_key()
        tpl     = "Your registration was successful! Please upload your photo at the following url:\n\n\t%s"
        url     = "http://127.0.0.1:8001" + profile.get_add_url(key)
        profile.update(activation_key=key)
        send_mail("Registration successful", tpl % url, "noreply@domain", [profile.email])
        return HttpResponse("Your submission url was emailed to you")


class ModerateView(ModelFormSetView):
    """Moderate image profiles."""
    formset_model      = ImageProfile
    formset_form_class = ModerationForm
    success_url        = '#'
    paginate_by        = 10
    template_name      = "moderation.html"

    @method_decorator(group_required("moderators"))
    def dispatch(self, *args, **kwargs):
        return super(ModerateView, self).dispatch(*args, **kwargs)

    def get_formset_queryset(self):
        return ImageProfile.obj.filter(active=False, banned=False, email_profile__activation_key='')
        # return qs.exclude(image='')

    def process_form(self, form):
        """Do approval/rejection of a single image submission (runs for each submission in Formset)."""
        data     = form.cleaned_data
        profile  = form.instance
        def_expl = "Does not comply with photo guidelines."

        # delete image, send email with explanation and a URL to re-submit a new one
        if data.delete_image:
            key         = profile.email_profile.make_activation_key()
            url         = "http://127.0.0.1:8001" + profile.email_profile.get_add_url(key)
            msg         = rejection_tpl % (data.explanation or def_expl, url)

            # image is set to blank string to be consistent with 'clear' action of stock ImageField
            profile.update(image='')
            profile.email_profile.update(activation_key=key)
            send_mail("Photo rejected", msg, "noreply@domain", [profile.email])

        # blacklist email for submitting an offensive image
        elif data.banned:
            # image is set to blank string to be consistent with 'clear' action of stock ImageField
            profile.update(image='', banned=True)

        # set image public & send email with image URL
        elif data.active:
            tpl = "Your photo was accepted! It's now posted at the following url:\n\n\t%s"
            msg = tpl % profile.get_absolute_url()
            send_mail("Photo accepted", msg, "noreply@domain", [profile.email])
        form.save()
