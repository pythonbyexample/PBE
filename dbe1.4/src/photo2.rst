
Django Tutorial: Photo Organizer and Sharing App Part II
--------------------------------------------------------

Main Listing
============

We'll start by creating a listing of all albums with a few thumbnails of images. A lot of the code
will be similar to the Blog App. Our url will be `/photo/`, function will be called `main()` and
we'll keep `list.html` as the template name. Here's our view:

.. sourcecode:: python

    from django.http import HttpResponseRedirect, HttpResponse
    from django.shortcuts import get_object_or_404, render_to_response
    from django.contrib.auth.decorators import login_required
    from django.core.context_processors import csrf
    from django.core.paginator import Paginator, InvalidPage, EmptyPage
    from django.forms import ModelForm
    from settings import MEDIA_URL

    from dbe.photo.models import *

    def main(request):
        """Main listing."""
        albums = Album.objects.all()
        if not request.user.is_authenticated():
            albums = albums.filter(public=True)

        paginator = Paginator(albums, 10)
        try: page = int(request.GET.get("page", '1'))
        except ValueError: page = 1

        try:
            albums = paginator.page(page)
        except (InvalidPage, EmptyPage):
            albums = paginator.page(paginator.num_pages)

        for album in albums.object_list:
            album.images = album.image_set.all()[:4]

        return render_to_response("photo/list.html", dict(albums=albums, user=request.user,
            media_url=MEDIA_URL))

We're only listing albums that are set to `public` for users who aren't logged in. I'll speak in
more detail about security at the end of the tutorial. Here is the `urlconf` line:

.. sourcecode:: python

   (r"", "main"),

...and `list.html` (don't forget to change links in `pbase.html`):

.. sourcecode:: django

    {% extends "pbase.html" %}

    {% block content %}
        <div class="main">

            <!-- Albums  -->
            <ul>
                {% for album in albums.object_list %}
                    <div class="title">{{ album.title }} ({{ album.image_set.count }} images)</div>
                    <ul>
                        {% for img in album.images %}
                            <a href="{{ media_url }}{{ img.image.name }}"><img border="0" alt=""
                                src="{{ media_url }}{{ img.thumbnail2.name }}" /></a>
                        {% endfor %}
                    </ul>
                {% endfor %}
            </ul>

            <!-- Next/Prev page links  -->
            {% if albums.object_list and albums.paginator.num_pages > 1 %}
            <div class="pagination">
                <span class="step-links">
                    {% if albums.has_previous %}
                        <a href= "?page={{ albums.previous_page_number }}">previous &lt;&lt; </a>
                    {% endif %}

                    <span class="current">
                        &nbsp;Page {{ albums.number }} of {{ albums.paginator.num_pages }}
                    </span>

                    {% if albums.has_next %}
                        <a href="?page={{ albums.next_page_number }}"> &gt;&gt; next</a>
                    {% endif %}
                </span>
            </div>
            {% endif %}

        </div>

    {% endblock %}

Here's our beautiful, amazing front page (with a bit of styling added):

.. image:: _static/p2.png

As you can see, we're using medium-sized thumbnails. You could also add an option to
switch between the two sizes and add more sizes, as well.

Album View
==========

Let's add a view for a single album: the url will be: `/photo/{id}/`, function name:
`album()`, template: `album.html`.

We'll need to add the link to main listing:

.. sourcecode:: django

    <div class="title"><a href="{% url photo.views.album album.pk %}">{{ album.title }}</a>
        ({{ album.image_set.count }} images)</div>

Here's our view and the `urlconf` line:

.. sourcecode:: python

    def album(request, pk):
        """Album listing."""
        album = Album.objects.get(pk=pk)
        if not album.public and not request.user.is_authenticated():
            return HttpResponse("Error: you need to be logged in to view this album.")

        images = album.image_set.all()
        paginator = Paginator(images, 30)
        try: page = int(request.GET.get("page", '1'))
        except ValueError: page = 1

        try:
            images = paginator.page(page)
        except (InvalidPage, EmptyPage):
            images = paginator.page(paginator.num_pages)

        return render_to_response("photo/album.html", dict(album=album, images=images, user=request.user,
            media_url=MEDIA_URL))

.. sourcecode:: python

   (r"^(\d+)/$", "album"),

I will only show the main loop since the template is almost the same:

.. sourcecode:: django

    <!-- Images  -->
    <ul>
        <div class="title">{{ album.title }}</div>
        <ul>
            {% for img in images.object_list %}
                <a href="{{ media_url }}{{ img.image.name }}"><img border="0" alt=""
                    src="{{ media_url }}{{ img.thumbnail2.name }}" /></a>
            {% endfor %}
        </ul>
    </ul>

In exactly the same way, the next thing to do is to add a page for a single image: url, function
and template will all be called `image`:

.. sourcecode:: python

   (r"^image/(\d+)/$", "image"),

.. sourcecode:: python

    def image(request, pk):
        """Image page."""
        img = Image.objects.get(pk=pk)
        return render_to_response("photo/image.html", dict(image=img, user=request.user,
             backurl=request.META["HTTP_REFERER"], media_url=MEDIA_URL))

.. sourcecode:: django

    <a href="{{ backurl }}">&lt;&lt; back</a>
    <!-- Image -->
    <ul>
        {% if image.title %}
            <div class="title">{{ image.title }}</div>
        {% endif %}

        <ul>
            <img border="0" alt="" src="{{ media_url }}{{ image.image.name }}" width="900" />
        </ul>
    </ul>

Slideshow
=========

The next logical thing to do is to have some sort of slideshow functionality. I'm not going to add
a javascript slideshow since I want to concentrate on Django, but that's something you could
easily do yourself. I will just have a page with full-size images stacked vertically.

First we'll change the view function to allow full or thumbnail view and add a `urlconf` line:

.. sourcecode:: python

    def album(request, pk, view="thumbnails"):
        """Album listing."""
        num_images = 30
        if view == "full": num_images = 10

        album = Album.objects.get(pk=pk)
        images = album.image_set.all()
        paginator = Paginator(images, num_images)
        try: page = int(request.GET.get("page", '1'))
        except ValueError: page = 1

        try:
            images = paginator.page(page)
        except (InvalidPage, EmptyPage):
            images = paginator.page(paginator.num_pages)

        return render_to_response("photo/album.html", dict(album=album, images=images,
            user=request.user, view=view, media_url=MEDIA_URL))

.. sourcecode:: python

    (r"^(\d+)/(full|thumbnails)/$", "album"),

Since it's common to have images that are larger than full screen, we'll limit width to 900 pixels
in `album.html` to make full view manageable:

.. sourcecode:: django

        <!-- Images  -->
        <ul>
            <div class="title">{{ album.title }}</div>
                <div class="right">
                View:
                <a href="{% url photo.views.album album.pk 'thumbnails' %}">thumbnails</a>
                <a href="{% url photo.views.album album.pk 'full' %}">full</a>&nbsp;
                </div>
                {% for img in images.object_list %}
                    {% if view == "full" %}
                        <a href="{% url photo.views.image img.pk %}"><img border="0" alt=""
                            src="{{ media_url }}{{ img.image.name }}"
                            {% if img.width > 900 %}width="900"{% endif %} /></a>
                    {% else %}
                        <a href="{% url photo.views.image img.pk %}"><img border="0" alt=""
                            src="{{ media_url }}{{ img.thumbnail2.name }}" /></a>
                    {% endif %}
                {% endfor %}
        </ul>

And here's our full album view:

.. image:: _static/p3.png

`On to part III! <photo3.html>`_
