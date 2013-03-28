import os
import hashlib
import random

from os.path import join as pjoin, basename
from tempfile import NamedTemporaryFile

from PIL import Image as PImage
from django.db.models import *
from django.core.files import File
from django.contrib.auth.models import User, Group

from settings import MEDIA_ROOT, MEDIA_URL
from dbe.shared.utils import *

link            = "<a href='%s'>%s</a>"
imgtag          = "<img border='0' alt='' src='%s' />"
country_choices = (('usa', 'USA'), ('canada', 'Canada'))


class Promotion(BaseModel):
    name = CharField(max_length=70, unique=True)

    def __unicode__(self):
        return self.name


class EmailProfile(BaseModel):
    email          = EmailField(unique=True)
    confirm_email  = EmailField()
    activation_key = CharField(max_length=40, blank=True, null=True)

    def make_activation_key(self):
        """Returns activation key; based on code from django-registration."""
        salt = hashlib.sha1(str(random.random())).hexdigest()[:5]
        email = self.email
        if isinstance(email, unicode):
            email = email.encode('utf-8')
        return hashlib.sha1(salt+email).hexdigest()

    def get_add_url(self, key):
        return reverse2("pc-add-image", key=key)


class ImageProfile(BaseModel):
    """Profile including submitter's information and uploaded image."""
    # promotion      = ForeignKey(Promotion, related_name="images")
    email_profile  = ForeignKey(EmailProfile, related_name="images")
    first_name     = CharField(max_length=30)
    last_name      = CharField(max_length=30)

    personal_info  = CharField(max_length=500, blank=True, null=True)
    birthday       = DateField("Birthday (m/d/yyyy)", max_length=10, blank=True, null=True)
    sex            = CharField(choices=(('M', 'M'), ('F', 'F')), max_length=1, blank=True, null=True)
    phone          = CharField("Phone Number (xxx-xxx-xxxx)", max_length=14, blank=True, null=True)

    address1       = CharField(max_length=60, blank=True, null=True)
    address2       = CharField(max_length=60, blank=True, null=True)
    zipcode        = CharField("Zip code / Post code", max_length=20, blank=True, null=True)
    country        = CharField(choices=country_choices, max_length=6, blank=True, null=True)

    image          = ImageField(upload_to="images/", blank=True, null=True)
    username       = CharField(max_length=30, blank=True, null=True, help_text="will appear on image page")
    caption        = CharField(max_length=140, blank=True, null=True)

    active         = BooleanField("Set Active", default=False)
    banned         = BooleanField("Ban this email", default=False)         # e.g. for submitting an abusive image
    created        = DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created"]

    def __unicode__(self):
        return unicode(self.image.name if self.image else self.email_profile.email)

    def get_absolute_url(self):
        return reverse2("pc-image", dpk=self.pk)

    @property
    def email(self):
        return self.email_profile.email

    def image_url(self) : return MEDIA_URL + self.image.name
    def image_tag(self) : return imgtag % self.image_url()
