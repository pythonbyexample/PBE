Portfolio
=========

This tutorial will show you how to create a simple Portfolio app in Django using mcbv
(modular CBVs) library.

You can view or download the code here:

`Browse source files <https://github.com/akulakov/django/tree/master/dbe/>`_

`dbe.tar.gz <https://github.com/akulakov/django/tree/master/dbe.tar.gz>`_

A few custom functions and classes and the MCBV library are used in the tutorials, please look
through the `libraries page <libraries.html>`_ before continuing.

I will focus on the important parts of code in the listings below; I recommend opening the
source files in a separate window to see import lines and other details.

.. sourcecode:: python

.. image:: _static/img/i-issue.gif
    :class: screenshot

Outline
-------

In the Portfolio App, the user will be able to create Groups (i.e. Albums) and add images to a
Group; both Groups and Images may be hidden, which stops anyone but the owner from viewing the
Image or Group.

A Group needs to have a title and can optionally have a description and a link (for example, a
portfolio entry for a site may have screenshots and the link would point to the site itself).

An Image must have an image file uploaded and also may have a title and a description.

Group model
-----------

.. sourcecode:: python

    link   = "<a href='%s'>%s</a>"

    class Group(BaseModel):
        title       = CharField(max_length=60)
        description = TextField(blank=True, null=True)
        link        = URLField(blank=True, null=True)
        hidden      = BooleanField()

        def __unicode__(self):
            return self.title

        def get_absolute_url(self, show="thumbnails"):
            return reverse2("group", dpk=self.pk, show=show)

        def image_links(self):
            lst = [img.image.name for img in self.images.all()]
            lst = [link % ( MEDIA_URL+img, basename(img) ) for img in lst]
            return ", ".join(lst)
        image_links.allow_tags = True

There will be several types of views available for a group, the type will be specified in an
argument to get_absolute_url(), small thumbnails is the default view.

Image model
-----------

.. sourcecode:: python

    from tempfile import NamedTemporaryFile
    from PIL import Image as PImage
    from django.core.files import File

    imgtag = "<img border='0' alt='' src='%s' />"

    class PhotoManager(Manager):
        def get_or_none(self, **kwargs):
            try:
                return self.get(**kwargs)
            except self.model.DoesNotExist:
                return None


    class Image(BaseModel):
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

        def get_absolute_url(self):
            return reverse2("image", mfpk=self.pk)

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

I'm defining a custom manager to provide the convenient get_or_none() method; in the Image
model I'm doing all the standard PIL image resizing and saving -- two thumbnail sizes are
generated: 64x64 and 128x128.

