from dbe.portfolio.models import *
from dbe.portfolio.forms import *
from settings import MEDIA_URL

from dbe.classviews.list_custom import *
from dbe.classviews.edit_custom import *


class Main(AKListView):
    model               = Group
    context_object_name = "groups"
    paginate_by         = 10
    template_name       = "portfolio/list.html"


class SlideshowView(ListRelated):
    """Slideshow"""
    model               = Image
    related_model       = Group
    foreign_key_field   = "group"
    context_object_name = "images"
    template_name       = "slideshow.html"
    paginate_by         = None


class AddImages(CreateWithFormset):
    """Create new images."""
    model            = Image
    form_class       = AddImageForm
    item_name        = "image"
    template_name    = "add_images.html"
    extra            = 10

    def form_valid(self, formset):
        group = get_object_or_404(Group, pk=self.kwargs["pk"])
        for form in formset:
            if form.has_changed():
                img = form.save(commit=False)
                img.group = group
                img.save()
        return HttpResponseRedirect(reverse2("group", pk=group.pk))


class GroupView(DetailListFormsetView):
    """List of images in an group, optionally with a formset to update image data."""
    main_model          = Group
    list_model          = Image
    related_name        = "images"
    context_object_name = "group"
    form_class          = ImageForm
    paginate_by         = 25
    template_name       = "group.html"

    def do_init(self):
        self.show = self.kwargs.get("show", "thumbnails")
        if self.show == "edit" and not self.request.user.is_authenticated():
            self.show = "thumbnails"

    def form_valid(self, form):
        super(GroupView, self).form_valid(form)
        url = reverse2("group", pk=self.main_object.pk, show=self.show)
        return redir("%s?%s" % (url, self.request.GET.urlencode()))     # keep page num.

    def add_context(self, **kwargs):
        return dict(show=self.show)


class ImageView(UpdateView2):
    model               = Image
    form_class          = ImageForm
    context_object_name = "image"
    template_name       = "portfolio/image.html"

    def get_context_data(self, **kwargs):
        c = super(ImageView, self).get_context_data(**kwargs)
        edit = self.request.GET.get("edit", False)
        if not self.request.user.is_authenticated():
            edit = False
        return updated(c, dict(edit=edit))


def portfolio_context(request):
    return dict(user=request.user, media_url=MEDIA_URL)
