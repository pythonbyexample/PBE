from django import forms as f
from dbe.portfolio.models import *
from dbe.shared.utils import *

class ImageForm(AKModelForm):
    class Meta:
        model   = Image
        exclude = "image width height hidden group thumbnail1 thumbnail2".split()
        widgets = dict(description=f.Textarea(attrs=dict(cols=70)))

class AddImageForm(AKModelForm):
    class Meta:
        model   = Image
        exclude = "width height hidden group thumbnail1 thumbnail2".split()
        widgets = dict(description=f.Textarea(attrs=dict(cols=70, rows=2)))
import os
from PIL import Image as PImage
from settings import MEDIA_ROOT, MEDIA_URL
from os.path import join as pjoin, basename
from tempfile import NamedTemporaryFile

from django.db.models import *
from django.core.files import File

from dbe.shared.utils import *

link   = "<a href='%s'>%s</a>"
imgtag = "<img border='0' alt='' src='%s' />"


class PhotoManager(Manager):
    def get_or_none(self, **kwargs):
        try: return self.get(**kwargs)
        except self.model.DoesNotExist: return None


class Group(BasicModel):
    title       = CharField(max_length=60)
    description = TextField(blank=True, null=True)
    link        = URLField(blank=True, null=True)
    hidden      = BooleanField()

    def __unicode__(self):
        return self.title

    @permalink
    def get_absolute_url(self):
        return ("group", (), dict(pk=self.pk))

    def image_links(self):
        lst = [x.image.name for x in self.images.all()]
        lst = [link % ( "/media/"+x, basename(x) ) for x in lst]
        return cjoin(lst)
    image_links.allow_tags = True


class Image(BasicModel):
    obj         = objects = PhotoManager()
    title       = CharField(max_length=60, blank=True, null=True)
    description = TextField(blank=True, null=True)
    image       = ImageField(upload_to="images/")
    thumbnail1  = ImageField(upload_to="images/", blank=True, null=True)
    thumbnail2  = ImageField(upload_to="images/", blank=True, null=True)

    width       = IntegerField(blank=True, null=True)
    height      = IntegerField(blank=True, null=True)
    hidden      = BooleanField()
    group       = ForeignKey(Group, related_name="images", blank=True)
    created     = DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created"]

    def __unicode__(self):
        return self.image.name

    @permalink
    def get_absolute_url(self):
        return ("image", (), dict(pk=self.pk))

    def save(self, *args, **kwargs):
        """Save image dimensions."""
        super(Image, self).save(*args, **kwargs)
        img = PImage.open(pjoin(MEDIA_ROOT, self.image.name))
        self.width, self.height = img.size
        self.save_thumbnail(img, 1, (128,128))
        self.save_thumbnail(img, 2, (64,64))
        super(Image, self).save(*args, **kwargs)

    def save_thumbnail(self, img, num, size):
        fn, ext = os.path.splitext(self.image.name)
        img.thumbnail(size, PImage.ANTIALIAS)
        thumb_fn = fn + "-thumb" + str(num) + ext
        tf = NamedTemporaryFile()
        img.save(tf.name, "JPEG")
        thumbnail = getattr(self, "thumbnail%s" % num)
        thumbnail.save(thumb_fn, File(open(tf.name)), save=False)
        tf.close()

    def size(self):
        """Image size."""
        return "%s x %s" % (self.width, self.height)

    def thumbnail1_url(self):
        return MEDIA_URL + self.thumbnail1.name

    def thumbnail2_url(self):
        return MEDIA_URL + self.thumbnail2.name

    def image_url(self):
        return MEDIA_URL + self.image.name
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
