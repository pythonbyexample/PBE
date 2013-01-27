from dbe.portfolio.models import *
from dbe.portfolio.forms import *
from settings import MEDIA_URL

from dbe.mcbv.detail import DetailView
from dbe.mcbv.list import ListView
from dbe.mcbv.list_custom import ListRelated, DetailListFormsetView
from dbe.mcbv.edit_custom import FormSetView, UpdateView

from dbe.shared.utils import *

class Main(ListView):
    list_model               = Group
    list_context_object_name = "groups"
    paginate_by              = 10
    template_name            = "portfolio/list.html"


class SlideshowView(ListRelated):
    """Show images in a group."""
    list_model               = Image
    detail_model             = Group
    related_name             = "images"
    list_context_object_name = "images"
    template_name            = "slideshow.html"


class AddImages(DetailView, FormSetView):
    """Add images to a group view."""
    detail_model       = Group
    formset_model      = Image
    formset_form_class = AddImageForm
    template_name      = "add_images.html"
    extra              = 10

    def formset_valid(self, formset):
        for form in formset:
            if form.has_changed():
                img = form.save(commit=False)
                img.group = self.detail_object
                img.save()
        obj = self.get_detail_object()
        return redir(reverse2("group", dpk=obj.pk))


class GroupView(DetailListFormsetView):
    """List of images in an group, optionally with a formset to update image data."""
    detail_model               = Group
    formset_model              = Image
    related_name               = "images"
    detail_context_object_name = "group"
    formset_form_class         = ImageForm
    paginate_by                = 25
    template_name              = "group.html"

    def initsetup(self, request):
        self.show = self.kwargs.get("show", "thumbnails")
        if self.show == "edit" and not self.request.user.is_authenticated():
            self.show = "thumbnails"

    def formset_valid(self, formset):
        super(GroupView, self).formset_valid(formset)
        obj = self.get_detail_object()
        url = reverse2("group", dpk=obj.pk, show=self.show)

        # keep page num
        url = "%s?%s" % (url, self.request.GET.urlencode())
        return redir(url)

    def add_context(self):
        return dict(show=self.show)


class ImageView(UpdateView):
    form_model                    = Image
    modelform_class               = ImageForm
    modelform_context_object_name = "image"
    template_name                 = "portfolio/image.html"

    def get_modelform_context_data(self, **kwargs):
        context = super(ImageView, self).get_modelform_context_data(**kwargs)
        R       = self.request
        edit    = R.GET.get("edit", False)
        if not R.user.is_authenticated():
            edit = False
        return dict(context, edit=edit)


def portfolio_context(request):
    return dict(user=request.user, media_url=MEDIA_URL)
