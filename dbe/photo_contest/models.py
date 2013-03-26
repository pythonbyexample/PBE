import os
from PIL import Image as PImage
from settings import MEDIA_ROOT, MEDIA_URL
from os.path import join as pjoin, basename
from tempfile import NamedTemporaryFile

from django.db.models import *
from django.core.files import File
from django.contrib.auth.models import User, Group

from dbe.shared.utils import *

link   = "<a href='%s'>%s</a>"
imgtag = "<img border='0' alt='' src='%s' />"


class Promotion(BaseModel):
    name = CharField(max_length=70, unique=True)

    def __unicode__(self):
        return self.name

class ImageProfile(BaseModel):
    """Profile including submitter's information and uploaded image."""
    promotion     = ForeignKey(Promotion, related_name="images")

    email         = EmailField(unique=True)
    confirm_email = EmailField()
    first_name    = CharField(max_length=30)
    last_name     = CharField(max_length=30)

    personal_info = CharField(max_length=500, blank=True, null=True)
    birthday      = DateField("Birthday (m/d/yyyy)", max_length=10, blank=True, null=True)
    sex           = CharField(choices=(('M', 'M'), ('F', 'F')), max_length=1, blank=True, null=True)
    phone         = CharField("Phone Number (xxx-xxx-xxxx)", max_length=14, blank=True, null=True)

    address1      = CharField(max_length=60, blank=True, null=True)
    address2      = CharField(max_length=60, blank=True, null=True)
    zipcode       = CharField("Zip code / Post code", max_length=20, blank=True, null=True)
    country       = CharField(choices=(('usa', 'USA'), ('canada', 'Canada')), max_length=6, blank=True, null=True)

    image         = ImageField(upload_to="images/", blank=True, null=True)
    thumbnail     = ImageField(upload_to="images/", blank=True, null=True)
    username      = CharField(max_length=30, blank=True, null=True, help_text="will appear on image page")
    caption       = CharField(max_length=150, blank=True, null=True)

    active        = BooleanField("Set Active", default=False)
    banned        = BooleanField("Ban this email", default=False)         # e.g. for submitting an abusive image
    created       = DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created"]

    def __unicode__(self):
        return self.image.name

    def get_absolute_url(self):
        return reverse2("pc-image", dpk=self.pk)

    def get_add_url(self):
        return reverse2("pc-add-image", mfpk=self.pk)

    def save(self, *args, **kwargs):
        """Generate thumbnail."""
        super(ImageProfile, self).save(*args, **kwargs)
        if self.image and not self.thumbnail:
            img = PImage.open(pjoin(MEDIA_ROOT, self.image.name))
            self.save_thumbnail(img, (128,128))
            super(ImageProfile, self).save(*args, **kwargs)

    def save_thumbnail(self, img, size):
        fn, ext = os.path.splitext(self.image.name)
        img.thumbnail(size, PImage.ANTIALIAS)
        thumb_fn = fn + "-thumb" + ext
        tf = NamedTemporaryFile()
        img.save(tf.name, "JPEG")
        self.thumbnail.save(thumb_fn, File(open(tf.name)), save=False)
        tf.close()

    def size(self):
        return "%s x %s" % (self.width, self.height)

    def thumbnail_url(self) : return MEDIA_URL + self.thumbnail.name
    def image_url(self)     : return MEDIA_URL + self.image.name
    def image_tag(self)     : return imgtag % self.image_url()
    def thumbnail_tag(self) : return imgtag % self.thumbnail_url()
