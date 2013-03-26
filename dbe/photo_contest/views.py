from django.core.mail import send_mail
from django.utils.decorators import method_decorator

from dbe.photo_contest.models import *
from dbe.photo_contest.forms import *

from dbe.mcbv import DetailView, ListView, UpdateView, ModelFormSetView

from dbe.shared.utils import *
from dbe.shared.utils import group_required


class Main(ListView):
    list_model    = ImageProfile
    paginate_by   = 20
    template_name = "photo_contest/list.html"

    def get_list_queryset(self):
        return ImageProfile.obj.filter(active=True)

class ImageView(DetailView):
    detail_model  = ImageProfile
    template_name = "photo_contest/image.html"

class AddImage(UpdateView):
    form_model      = ImageProfile
    modelform_class = AddImageForm
    template_name   = "photo_contest/add_image.html"


class ModerateView(ModelFormSetView):
    """Moderate image profiles."""
    formset_model      = ImageProfile
    formset_form_class = ModerationForm
    # can_delete         = True
    success_url        = '#'
    paginate_by        = 25
    template_name      = "moderation.html"

    @method_decorator(group_required("moderator"))
    def dispatch(self, *args, **kwargs):
        return super(ModerateView, self).dispatch(*args, **kwargs)

    def get_formset_queryset(self):
        return ImageProfile.obj.filter(active=False, banned=False).exclude(image='')

    def process_form(self, form):
        data     = form.cleaned_data
        profile  = form.instance
        def_expl = "Does not comply with photo guidelines."

        if data.delete_image:
            tpl = "Your photo was rejected for the following reasons:\n\n\t%s"
            explanation = data.get("explanation") or def_expl

            # image is set to blank string to be consistent with 'clear' action of stock ImageField
            profile.update(image='', thumbnail='')
            send_mail("Photo rejected", tpl % explanation, "noreply@domain", [profile.email])

        elif data.banned:
            # image is set to blank string to be consistent with 'clear' action of stock ImageField
            profile.update(image='', thumbnail='', banned=True)

        elif data.active:
            tpl = "Your photo was accepted! It's now posted at the following url:\n\n\t%s"
            msg = tpl % profile.get_absolute_url()
            send_mail("Photo accepted", msg, "noreply@domain", [profile.email])
        form.save()
