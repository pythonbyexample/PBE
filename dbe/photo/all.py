from django.forms import ModelForm
from django import forms as f
from django.forms.widgets import TextInput

from dbe.photo.models import *
from dbe.shared.utils import *
from dbe.photo.fields import *

sort_choices = [("created", "date")] + [(c,c) for c in "rating title width height albums".split()]

class ImageForm(AKModelForm):
    def __init__(self, *args, **kwargs):
        super(ImageForm, self).__init__(*args, **kwargs)
        tags   = self.fields["tags"]
        albums = self.fields["albums"]
        tags.help_text = albums.help_text = ''  # remove select box help text

    class Meta:
        model   = Image
        exclude = "image thumbnail1 thumbnail2 width height user".split()
        widgets = dict(albums = f.CheckboxSelectMultiple(),
                       rating = f.TextInput( attrs=dict(size=1) ),
                       )

    # We need to pass an empty tuple for the queryset, ModelForm will update it from current Image.
    # Widget can't be specified in Meta.widgets because it only applies to auto-created fields.
    tags = SelectCSVField((), widget=f.TextInput( attrs=dict(size=50) ))


class SearchForm(f.Form):
    title    = f.CharField(max_length=30, required=False)
    tags     = TagParseField(required=False)
    rating   = MinMaxRangeIntField()
    width    = MinMaxRangeIntField()
    height   = MinMaxRangeIntField()
    sort_by  = f.ChoiceField(choices=sort_choices)
    sort_dir = f.ChoiceField(choices=(('-', "descending"), ('', "ascending")), required=False)
    albums   = f.ModelMultipleChoiceField(queryset=Album.obj.all(), widget=f.CheckboxSelectMultiple(),
                                          required=False)
import os
from PIL import Image as PImage
from settings import MEDIA_ROOT, MEDIA_URL
from os.path import join as pjoin, basename
from tempfile import NamedTemporaryFile

from django.db.models import *
from django.contrib.auth.models import User
from django.core.files import File

from dbe.shared.utils import *

link   = "<a href='%s'>%s</a>"
imgtpl = '<img border="0" alt="" src="%s" />'


class PhotoManager(Manager):
    def get_or_none(self, **kwargs):
        try: return self.get(**kwargs)
        except self.model.DoesNotExist: return None


class Album(BasicModel):
    title  = CharField(max_length=60)
    public = BooleanField(default=False)

    def __unicode__(self):
        return self.title

    @permalink
    def get_absolute_url(self):
        return ("album", (), dict(pk=self.pk))

    def image_links(self):
        lst = [x.image.name for x in self.images.all()]
        return cjoin([link % ("/media/"+x, basename(x)) for x in lst])
    image_links.allow_tags = True


class Tag(BasicModel):
    obj = objects = PhotoManager()
    tag = CharField(max_length=50, unique=True)

    def __unicode__(self):
        return self.tag


class Image(BasicModel):
    obj        = objects = PhotoManager()
    title      = CharField(max_length=60, blank=True, null=True)
    image      = ImageField(upload_to="images/")
    thumbnail1 = ImageField(upload_to="images/", blank=True, null=True)
    thumbnail2 = ImageField(upload_to="images/", blank=True, null=True)

    tags       = ManyToManyField(Tag, related_name="images", blank=True)
    albums     = ManyToManyField(Album, related_name="images", blank=True)
    created    = DateTimeField(auto_now_add=True)

    rating     = IntegerField(default=50)
    width      = IntegerField(blank=True, null=True)
    height     = IntegerField(blank=True, null=True)
    user       = ForeignKey(User, related_name="images", blank=True, null=True)

    class Meta:
        ordering = ["created"]

    def __unicode__(self):
        return self.image.name

    @property
    def public(self):
        return any(a.public for a in self.albums.all())

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

    def tags_(self):
        return cjoin(str(x) for x in self.tags.all())

    def albums_(self):
        return cjoin(str(x) for x in self.albums.all())

    def thumbnail1_url(self):
        return MEDIA_URL + self.thumbnail1.name

    def thumbnail2_url(self):
        return MEDIA_URL + self.thumbnail2.name

    def image_url(self):
        return MEDIA_URL + self.image.name

    def thumbnail_(self):
        thumb = imgtpl % (MEDIA_URL + self.thumbnail1.name)
        return link % (MEDIA_URL + self.image.name, thumb)
    thumbnail_.allow_tags = True
from django.core.exceptions import PermissionDenied
from django.db.models import Q

from dbe.photo.models import *
from dbe.photo.forms import *
from settings import MEDIA_URL

from dbe.classviews.list_custom import *
from dbe.classviews.detail_custom import *
from dbe.classviews.base import View


class PermissionMixin(View):
    def dispatch(self, request, *args, **kwargs):
        model = getattr(self, "main_model", self.model)
        obj = get_object_or_404(model, pk=kwargs.get("pk"))
        if not request.user.is_authenticated() and not obj.public:
            raise PermissionDenied      # needs to be raised before self.post() is processed
        return super(PermissionMixin, self).dispatch(request, *args, **kwargs)


class Main(AKListView):
    model               = Album
    context_object_name = "albums"
    paginate_by         = 10
    template_name       = "photo/list.html"

    def get_queryset(self):
        qs = super(Main, self).get_queryset()
        if not self.request.user.is_authenticated():
            qs = qs.filter(public=True)
        return qs


class AlbumView(PermissionMixin, DetailListFormsetView):
    """List of images in an album, optionally with a formset to update image data."""
    main_model          = Album
    list_model          = Image
    related_name        = "images"
    context_object_name = "album"
    form_class          = ImageForm
    paginate_by         = 25
    template_name       = "album.html"

    def do_init(self):
        self.show = self.kwargs.get("show", "thumbnails")
        if self.show == "edit" and not self.request.user.is_authenticated():
            self.show = "thumbnails"

    def form_valid(self, form):
        super(AlbumView, self).form_valid(form)
        url = reverse2("album", pk=self.main_object.pk, show=self.show)
        return redir("%s?%s" % (url, self.request.GET.urlencode()))

    def add_context(self, **kwargs):
        return dict(show=self.show)


class ImageView(PermissionMixin, UpdateView2):
    model               = Image
    form_class          = ImageForm
    context_object_name = "image"
    template_name       = "image.html"

    def get_context_data(self, **kwargs):
        c = super(ImageView, self).get_context_data(**kwargs)
        edit = self.request.GET.get("edit", False)
        if not self.request.user.is_authenticated():
            edit = False
        return updated(c, dict(edit=edit))


class SearchView(ListFilterView):
    model               = Image
    form_class          = SearchForm
    context_object_name = "images"
    paginate_by         = 25
    template_name       = "search.html"

    def form_valid(self, form):
        """ Perform search and sorting and save results to `self.object_list`.

            Note: The search is very slow for users who are not logged in, for better performance,
            `public` field should be added to Image model.
        """
        data = Container(**form.cleaned_data)

        # create all search queries
        if data.title:
            self.q &= Q(title__icontains=data.title)
        for field in "rating width height".split():
            self.range_query(data, field)
        if data.albums:
            self.q &= Q(albums__in=data.albums)     # inclusive filter
        for tag in data.get("tags"):
            self.q &= Q(tags=tag)                   # tests if tag is contained in `tags`

        # apply filter and ordering
        self.object_list = self.model.obj.filter(self.q).order_by( data.sort_dir+data.sort_by )

        if not self.request.user.is_authenticated():
            self.object_list = [i for i in self.object_list if i.public]
        return super(SearchView, self).form_valid(form)

    def range_query(self, data, field):
        value = data.get(field, None)
        if value:
            q0 = {field+"__gte": value[0]}
            q1 = {field+"__lte": value[1]}
            if value[0]: self.q &= Q(**q0)
            if value[1]: self.q &= Q(**q1)


def photo_context(request):
    return dict(user=request.user, media_url=MEDIA_URL)
