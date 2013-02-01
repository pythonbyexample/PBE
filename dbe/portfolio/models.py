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
    def get_absolute_url(self, show="thumbnails"):
        return ("group", (), dict(dpk=self.pk, show=show))

    def image_links(self):
        lst = [x.image.name for x in self.images.all()]
        lst = [link % ( "/media/"+x, basename(x) ) for x in lst]
        return ", ".join(lst)
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
        return ("image", (), dict(mfpk=self.pk))

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
        return "%s x %s" % (self.width, self.height)

    def thumbnail1_url(self) : return MEDIA_URL + self.thumbnail1.name
    def thumbnail2_url(self) : return MEDIA_URL + self.thumbnail2.name
    def image_url(self)      : return MEDIA_URL + self.image.name
