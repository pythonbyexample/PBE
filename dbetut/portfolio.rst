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

Outline
-------

In the Portfolio App, the user will be able to create `Groups` (i.e. Albums) and add images to
a `Group`.

A `Group` needs to have a title and can optionally have a description and a link (for example, a
portfolio entry for a site may have screenshots and the link would point to the site itself).

An `Image` must have an image file uploaded and also may have a title and a description.

There will be three "display" views: main listing of groups, group view (with several modes)
and a javascript slideshow view.

In addition, there is a view to add multiple images and a combined display/edit `ImageView`.

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
argument to `get_absolute_url(),` large thumbnails is the default view.

Image model
-----------

.. sourcecode:: python

    from tempfile import NamedTemporaryFile
    from PIL import Image as PImage
    from django.core.files import File

    imgtag = "<img border='0' alt='' src='%s' />"

    class Image(BaseModel):
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

In the `Image` model I'm doing all the standard PIL image resizing and saving -- two thumbnail
sizes are generated: 64x64 and 128x128.

Main and Slideshow Views
------------------------

.. sourcecode:: python

    from dbe.mcbv.list_custom import ListRelated, DetailListFormsetView

    class Main(ListView):
        list_model    = Group
        paginate_by   = 10
        template_name = "portfolio/list.html"

    class SlideshowView(ListRelated):
        list_model    = Image
        detail_model  = Group
        related_name  = "images"
        template_name = "slideshow.html"

`ListRelated` is a composite `mcbv` view with detail of one object and a list of related objects.

GroupView
---------

.. sourcecode:: python

    class GroupView(DetailListFormsetView):
        """List of images in an group, optionally with a formset to update image data."""
        detail_model       = Group
        formset_model      = Image
        formset_form_class = ImageForm
        related_name       = "images"
        paginate_by        = 25
        template_name      = "group.html"

        def add_context(self):
            return dict( show=self.kwargs.get("show", "thumbnails") )

        def process_form(self, form):
            if self.user.is_authenticated(): form.save()

        def get_success_url(self):
            return "%s?%s" % (self.detail_absolute_url(), self.request.GET.urlencode()) # keep page num

This view does a lot of different things at once: it's a detail view for the group, a list view
for group images and a formset view allowing you to edit images; the following modes are
supported: small thumbnail, large thumbnail, full size images and edit mode.

Since the listing is paginated, we need to keep GET args after the formset is saved.

In `process_form()` I need to make sure the user is logged in. For the sake of simplicity this
app allows all logged in users to edit images -- if multi-user support was required, the App
would need to store and check image ownership and allow shared ownership and / or copying and
moving images between users.


AddImages and ImageView
-----------------------

.. sourcecode:: python

    class AddImages(DetailView, FormSetView):
        """Add images to a group view."""
        detail_model       = Group
        formset_model      = Image
        formset_form_class = AddImageForm
        template_name      = "add_images.html"
        extra              = 10

        def process_form(self, form):
            form.instance.update( group=self.get_detail_object() )

        def get_success_url(self):
            return self.detail_absolute_url()

`AddImages` view allows you to add up to 10 new images via a formset.

As we process each image form, we need to set instance's group appropriately.

.. sourcecode:: python

    class ImageView(UpdateView):
        form_model      = Image
        modelform_class = ImageForm
        template_name   = "portfolio/image.html"

        def form_valid(self, form):
            if self.user.is_authenticated(): form.save()

        def edit(self):
            return self.user.is_authenticated() and self.request.GET.get("edit")

A context processor is used to add a couple of objects to template context:

.. sourcecode:: python

    def portfolio_context(request):
        return dict(user=request.user, media_url=MEDIA_URL)

Forms
-----

.. sourcecode:: python

    class ImageForm(FormsetModelForm):
        class Meta:
            model   = Image
            exclude = "image width height hidden group thumbnail1 thumbnail2".split()
            attrs   = dict(cols=70)
            widgets = dict( description=f.Textarea(attrs=attrs) )

    class AddImageForm(f.ModelForm):
        class Meta:
            model   = Image
            exclude = "width height hidden group thumbnail1 thumbnail2".split()
            attrs   = dict(cols=70, rows=2)
            widgets = dict( description=f.Textarea(attrs=attrs) )

Due to an issue with modelformset factory, I'm using `utils.FormsetModelForm` to omit the id
field when displaying the formset.

Main Listing Template
---------------------

.. sourcecode:: django

    <!-- Groups  -->
    <ul>
        {% for group in group_list %}
            <div class="group">
            <div class="header">
                <div class="ltitle">
                <a href="{% url 'slideshow' group.pk %}">{{ group.title }}</a> ({{ group.images.count }} slides)
                {% if user.is_authenticated %}
                    <span class="edit"><a href="{{ group.get_absolute_url }}">edit</a></span>
                {% endif %}
                </div>
                {{ group.description }}
            </div>

            <ul class="group">
                {% for img in group.images.all|slice:":6" %}
                    <a href="{{ img.get_absolute_url }}">
                        <img border="0" alt="" src="{{ img.thumbnail2_url }}" /></a>
                {% endfor %}
                {% if group.images.count > 6 %}
                    <a class="more" href="{{ group.get_absolute_url }}">...</a>
                {% endif %}
            </ul>
            </div>
        {% endfor %}
    </ul>

    {% include "paginator.html" %}

Nothing unusual here except for the use of `slice` filter to limit the number of displayed images.

.. image:: _static/img/pf-list.gif
    :class: screenshot

SlideshowView
-------------

.. sourcecode:: django

    <div class="main">
        <div class="title">{{ group.title }}</div>

            <!-- EDIT LINK -->
            {% if user.is_authenticated %}
                <div class="right"> <a href="{% url 'group' group.pk 'edit' %}">edit</a> </div>
                <br /> <br />
            {% endif %}

            <div id="slides">
            <div class="slides_container">
            {% for img in image_list %}

                <!-- SLIDE -->
                <div class="slide">
                    <a href="{{ img.image_url }}">
                    <img border="0" alt="" src="{{ img.image_url }}"
                            {% if img.height > 540 %} height="540" {% endif %}>
                    </a>
                  <div class="caption" style="bottom:0">
                      <p>{% if img.title %} {{ img.title }} - {% endif %}{{ img.description }}</p>
                  </div>
                </div>

            {% endfor %}

            </div>
            <a href="#" class="prev"><img src="{{ media_url }}img/arrow-prev.png" width="24" height="43" alt="Arrow Prev"></a>
            <a href="#" class="next"><img src="{{ media_url }}img/arrow-next.png" width="24" height="43" alt="Arrow Next"></a>
            </div>
        </div>
    </div>

I am omitting slideshow javascript code to keep things short -- you can view it in
portfolio.html file.

.. image:: _static/img/pf-slide.gif
    :class: screenshot

GroupView
---------

.. sourcecode:: django

    <div class="main">

            <div class="title">{{ group.title }}</div>
                <div class="right">
                View:
                <a href="{% url 'group' group.pk 'thumbnails' %}">thumbnails</a>
                <a href="{% url 'group' group.pk 'thumbnails2' %}">small thumbnails</a>
                <a href="{% url 'group' group.pk 'full' %}">full</a>
                {% if user.is_authenticated %}
                    <a href="{% url 'group' group.pk 'edit' %}">edit</a> |
                    <a href="{% url 'add_images' group.pk %}">add images</a>
                {% endif %}
                </div>
                <br /> <br />
                {% include "messages.html" %}
                <br />

                {% if show == "edit" %}
                    <form action="" method="POST">{% csrf_token %}
                    {{ formset.management_form }}
                {% endif %}

                {% for form in formset %}
                    {{ form.id }}
                    {% with form.instance as img %}

                    <!-- FULL VIEW  -->
                    {% if show == "full" %}
                        <div>
                          <h1>{{ img.title }}</h1>
                            <a href="{{ img.image_url }}">
                            <img border="0" alt="" src="{{ img.image_url }}" alt="Slide {{ forloop.counter|add:'1' }}">
                            </a>
                          <p>{{ img.description }}</p>
                        </div>
                    {% endif %}

                    <!-- EDIT VIEW  -->
                    {% if show == "edit" %}
                        <div class="edit">
                        <a href="{{ img.get_absolute_url }}" >
                            <img class="edit-thumb" border="0" alt="" src="{{ img.thumbnail2_url }}" /></a>

                        <table class="edit-table">
                            {% for fld in form %}
                                <tr><td>{{ fld.label }}</td>
                                <td class="field">{{ fld }} {{ fld.errors }}</td>
                                </tr>
                            {% endfor %}
                        </table>
                        <div class="clear"></div>
                        </div>
                    {% endif %}

                    <!-- THUMBNAILS VIEW  -->
                    {% if show == "thumbnails" or show == "thumbnails2" %}

                    <div class="{% if show == "thumbnails" %}thumbnails{% else %}thumbnails2{% endif %}">
                        <a href="{{ img.get_absolute_url }}"><img border="0" alt="" src="{% if show == "thumbnails" %}{{ img.thumbnail1_url }}{% else %}{{ img.thumbnail2_url }}{% endif %}" /></a>
                        <br />
                        <div class="thumbnail">{{ img.title }}&nbsp;{% if img.rating %}[{{ img.rating }}]{% endif %}</div>
                    </div>
                    {% endif %}

                    {% endwith %}
                {% endfor %}

                {% if show == "edit" %}
                    <div id="update"><input type="submit" value="Update"></form></div>
                {% endif %}
            </div>

        {% include "paginator.html" %}
    </div>

Three screenshots below show three view modes:

.. image:: _static/img/pf-group.gif
    :class: screenshot

.. image:: _static/img/pf-small.gif
    :class: screenshot

.. image:: _static/img/pf-edit.gif
    :class: screenshot

AddImages View
--------------

.. sourcecode:: django

    <div class="main">
        <form action="" method="POST" enctype="multipart/form-data">{% csrf_token %}
        <div id="submit"><input id="submit-btn" type="submit" value="Save"></div>
        <div class="clear"></div>
            {{ formset.management_form }}

            <!-- FOR EACH FORM -->
            {% for form in formset %}
                <fieldset class="module aligned">
                    {{ form.id }}

                    <!-- FOR EACH FIELD -->
                    {% for fld in form %}
                        <div class="form-row">
                            <label class="{% if fld.field.required %} required {% endif %}">{{ fld.label }}</label>
                            {{ fld }}
                        </div>
                    {% endfor %}

                </fieldset><br />
            {% endfor %}

            <div id="submit"><input id="submit-btn" type="submit" value="Save"></div>
        </form>
    </div>


..standard formset template, and the here's what it looks like:

.. image:: _static/img/pf-add.gif
    :class: screenshot

ImageView
---------

.. sourcecode:: django

    <div class="main">
        <!-- Image -->
        {% if image.title %}
            <div class="title">{{ image.title }}</div>
        {% endif %}

        <div id="img-desc">
            <img border="0" alt="" src="{{ image.image_url }}" {% if image.width > 800 %} width="800" {% endif %} />

            <div id="edit-view">
                {% if not view.edit and user.is_authenticated %} <a href="?edit=1">edit</a> {% endif %}
            </div>

            <form id="image" action="" method="post" accept-charset="utf-8">{% csrf_token %}
                {% if view.edit %}
                <table id="update-form">

                    <tr>
                    {% for field in modelform %}
                        <td>{{ field.label }}</td>
                    {% endfor %}
                    </tr>

                    <tr>
                    {% for field in modelform %}
                        <td>{{ field }} {{ field.errors }}</td>
                    {% endfor %}
                    </tr>
                </table>
                <ul><input type="submit" value="Update" /></ul>
            {% else %}
                <p>{{ image.description }}</p>
            {% endif %}
            </form>
        </div>

    </div>

This template is a good example of displaying / editing a record with the same template and view.

.. image:: _static/img/pf-image.gif
    :class: screenshot
