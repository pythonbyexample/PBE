
Django Tutorial: Photo Organizer and Sharing App Part I
-------------------------------------------------------

Our next project will be an app similar to flickr. We'll implement tags, ratings, albums,
sharing, searching, filtering and sorting.

Defining the Model
==================

As with previous tutorials, we'll start by defining a model (in photo/models.py):

.. sourcecode:: python

    from django.db import models
    from django.contrib.auth.models import User
    from django.contrib import admin

    class Album(models.Model):
        title = models.CharField(max_length=60)
        public = models.BooleanField(default=False)
        def __unicode__(self):
            return self.title

    class Tag(models.Model):
        tag = models.CharField(max_length=50)
        def __unicode__(self):
            return self.tag

    class Image(models.Model):
        title = models.CharField(max_length=60, blank=True, null=True)
        image = models.FileField(upload_to="images/")
        tags = models.ManyToManyField(Tag, blank=True)
        albums = models.ManyToManyField(Album, blank=True)
        created = models.DateTimeField(auto_now_add=True)
        rating = models.IntegerField(default=50)
        width = models.IntegerField(blank=True, null=True)
        height = models.IntegerField(blank=True, null=True)
        user = models.ForeignKey(User, null=True, blank=True)

        def __unicode__(self):
            return self.image.name

    class AlbumAdmin(admin.ModelAdmin):
        search_fields = ["title"]
        list_display = ["title"]

    class TagAdmin(admin.ModelAdmin):
        list_display = ["tag"]

    class ImageAdmin(admin.ModelAdmin):
        search_fields = ["title"]
        list_display = ["__unicode__", "title", "user", "rating", "created"]
        list_filter = ["tags", "albums"]

    admin.site.register(Album, AlbumAdmin)
    admin.site.register(Tag, TagAdmin)
    admin.site.register(Image, ImageAdmin)


... and running: `manage.py syncdb; manage.py runserver`

We also need to create a location for uploaded images and set up our `settings.py` to point to it:

.. sourcecode:: python

    MEDIA_ROOT = '/home/username/dbe/media/'
    MEDIA_URL = 'http://127.0.0.1:8000/media/'

Admin will need to have its CSS, images and javascript code in this location --- you'll have to
copy them from `django/contrib/admin/media/`. You should also create `images` dir under `media`.

At this point, you can go ahead and add a few images in the Admin so that you have something to
play with.

Enhancing Admin
===============

I'm not yet sure if we'll even need the Admin by the end of this tutorial, but adding a few useful
features is just too easy (this will also be good as an illustration --- it may be that what we'll
do with the Admin alone will be enough for your needs):

.. sourcecode:: python

    from string import join

    import os
    from PIL import Image as PImage
    from settings import MEDIA_ROOT

    class Image(models.Model):
        # ...

        def save(self, *args, **kwargs):
            """Save image dimensions."""
            super(Image, self).save(*args, **kwargs)
            im = PImage.open(os.path.join(MEDIA_ROOT, self.image.name))
            self.width, self.height = im.size
            super(Image, self).save(*args, ** kwargs)

        def size(self):
            """Image size."""
            return "%s x %s" % (self.width, self.height)

        def __unicode__(self):
            return self.image.name

        def tags_(self):
            lst = [x[1] for x in self.tags.values_list()]
            return str(join(lst, ', '))

        def albums_(self):
            lst = [x[1] for x in self.albums.values_list()]
            return str(join(lst, ', '))

        def thumbnail(self):
            return """<a href="/media/%s"><img border="0" alt="" src="/media/%s" height="40" /></a>""" % (
                                                                        (self.image.name, self.image.name))
        thumbnail.allow_tags = True


    class ImageAdmin(admin.ModelAdmin):
        # search_fields = ["title"]
        list_display = ["__unicode__", "title", "user", "rating", "size", "tags_", "albums_",
            "thumbnail", "created"]
        list_filter = ["tags", "albums", "user"]

        def save_model(self, request, obj, form, change):
            obj.user = request.user
            obj.save()


If you want to save image dimensions, you'll need to install PIL module (`python-imaging` module
in Ubuntu/Debian). In `save()` we're overriding the default save method to process the image and
save dimensions. In `tags_()` and `albums_()` we're getting a list of values from a `Many-to-Many`
object, which has a method `values_list()` that returns tuples with primary keys and values --- we
are only interested in values in this case.

You can click the thumbnail to see full-sized image. We could easily add a view to resize the
image and show a back button or open an image in a popup window.

Finally, we're overriding the `save_model()` method to assign current user as the owner of the
image. And that's what we have so far:

.. image:: _static/p1.png

We can't do much more with the admin, except for one small thing: we'll add a list of links to
images in the Album listing (you'll also have to add the `images` field to AlbumAdmin):

.. sourcecode:: python

    class Album(models.Model):
        # ...
        def images(self):
            lst = [x.image.name for x in self.image_set.all()]
            lst = ["<a href='/media/%s'>%s</a>" % (x, x.split('/')[-1]) for x in lst]
            return join(lst, ', ')
        images.allow_tags = True

The `image_set` object is automatically created as a part of `Many-to-Many` relationship between
two models.

Generating Thumbnails
=====================

There is a pretty significant performance issue with the way thumbnails are handled right now. If
you're loading a hundred images in the Admin view, the page will load full-sized images and only
then resize them for displaying. That's not good! Thinking ahead, we know we'll need thumbnails
for other views, as well, and we also know we'll probably want to have more than one size of
thumbnails.

For the sake of simplicity, let's say we want to store two different thumbnails for each image and
to generate them when an image is added. PIL to the rescue, again!

.. sourcecode:: python

    from django.core.files import File
    from os.path import join as pjoin
    from tempfile import *

    class Image(models.Model):
        # ...

        thumbnail2 = models.ImageField(upload_to="images/", blank=True, null=True)

        def save(self, *args, **kwargs):
            """Save image dimensions."""
            super(Image, self).save(*args, **kwargs)
            im = PImage.open(pjoin(MEDIA_ROOT, self.image.name))
            self.width, self.height = im.size

            # large thumbnail
            fn, ext = os.path.splitext(self.image.name)
            im.thumbnail((128,128), PImage.ANTIALIAS)
            thumb_fn = fn + "-thumb2" + ext
            tf2 = NamedTemporaryFile()
            im.save(tf2.name, "JPEG")
            self.thumbnail2.save(thumb_fn, File(open(tf2.name)), save=False)
            tf2.close()

            # small thumbnail
            im.thumbnail((40,40), PImage.ANTIALIAS)
            thumb_fn = fn + "-thumb" + ext
            tf = NamedTemporaryFile()
            im.save(tf.name, "JPEG")
            self.thumbnail.save(thumb_fn, File(open(tf.name)), save=False)
            tf.close()

            super(Image, self).save(*args, ** kwargs)

There are a few fine points here I need to address: firstly, we have to save to a temporary
filename using Python's `tempfile` module --- the reason is that if we save it to the proper
location (which we already know), saving the whole Model will result in a duplicate file because
`ImageField` will refuse to overwrite the old file. Secondly, we have to set `save=False` when saving
thumbnails, otherwise we'll get an infinite recursive loop (not exactly sure why) --- instead,
we're letting both thumbnails be saved with the Model.

You also have to update the thumbnail image display in the listing, but that should be
straightforward enough (if not, no worry --- full sources will be linked at the end as always).

And that's that for the Admin.

`Go on to the part II <photo2.html>`_
