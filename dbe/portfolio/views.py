from dbe.portfolio.models import *
from dbe.portfolio.forms import *
from settings import MEDIA_URL

from dbe.mcbv.detail import DetailView
from dbe.mcbv.list import ListView
from dbe.mcbv.list_custom import ListRelated, DetailListFormsetView
from dbe.mcbv.edit_custom import FormSetView, UpdateView

from dbe.shared.utils import *


class Main(ListView):
    list_model    = Group
    paginate_by   = 10
    template_name = "portfolio/list.html"


class SlideshowView(ListRelated):
    """Show images in a group."""
    list_model    = Image
    detail_model  = Group
    related_name  = "images"
    template_name = "slideshow.html"


class AddImages(DetailView, FormSetView):
    """Add images to a group view."""
    detail_model       = Group
    formset_model      = Image
    formset_form_class = AddImageForm
    template_name      = "add_images.html"
    extra              = 10

    def formset_valid(self, formset):
        obj = self.get_detail_object()
        for form in formset:
            if form.has_changed():
                img = form.save(commit=False)
                img.group = obj
                img.save()
        return redir(obj.get_absolute_url())


class GroupView(DetailListFormsetView):
    """List of images in an group, optionally with a formset to update image data."""
    detail_model       = Group
    formset_model      = Image
    formset_form_class = ImageForm
    related_name       = "images"
    paginate_by        = 25
    template_name      = "group.html"

    def add_context(self):
        show = self.kwargs.get("show", "thumbnails")
        if show == "edit" and not self.user.is_authenticated():
            show = "thumbnails"
        return dict(show=show)

    def get_success_url(self):
        url = self.get_detail_object().get_absolute_url()
        return "%s?%s" % (url, self.request.GET.urlencode())    # keep page num


class ImageView(UpdateView):
    form_model      = Image
    modelform_class = ImageForm
    template_name   = "portfolio/image.html"

    def edit(self):
        return self.user.is_authenticated() and self.request.GET.get("edit")


def portfolio_context(request):
    return dict(user=request.user, media_url=MEDIA_URL)
