
Django Tutorial: Photo Organizer and Sharing App Part III
---------------------------------------------------------

In part III we'll add pages for editing image properties.

Editing Properties
==================

Editing forms will be integrated into the album page --- we'll just add a third view option. Update url
and function will both be called `update`. Here are the `urlconf` lines and the changes we have to
add to `album()` view:

.. sourcecode:: python

   (r"^(\d+)/(full|thumbnails|edit)/$", "album"),
   (r"^update/$", "update"),

.. sourcecode:: python

    def album(request, pk, view="thumbnails"):
        # ...

        # add list of tags as string and list of album objects to each image object
        for img in images.object_list:
            tags = [x[1] for x in img.tags.values_list()]
            img.tag_lst = join(tags, ', ')
            img.album_lst = [x[1] for x in img.albums.values_list()]

        d = dict(album=album, images=images, user=request.user, view=view, albums=Album.objects.all(),
            media_url=MEDIA_URL)
        d.update(csrf(request))
        return render_to_response("photo/album.html", d)

We have to add quite a bit of changes to `album.html`:

.. sourcecode:: django

    <!-- Images  -->
    <ul>
        <div class="title">{{ album.title }}</div>
            <div class="right">
            View:
            <a href="{% url photo.views.album album.pk 'thumbnails' %}">thumbnails</a>
            <a href="{% url photo.views.album album.pk 'full' %}">full</a>
            <a href="{% url photo.views.album album.pk 'edit' %}">edit</a>
            </div>

            {% if view == "edit" %}
                <form action="{% url photo.views.update %}" method="POST">{% csrf_token %}
            {% endif %}
            {% for img in images.object_list %}

                <!-- FULL VIEW  -->
                {% if view == "full" %}
                    <a href="{% url photo.views.image img.pk %}"><img border="0" alt=""
                        src="{{ media_url }}{{ img.image.name }}"
                        {% if img.width > 900 %}width="900"{% endif %} /></a>
                {% endif %}

                <!-- EDIT VIEW  -->
                {% if view == "edit" %}

                    <table>
                    <tr><td>
                    <a href="{% url photo.views.image img.pk %}"><img border="0" alt=""
                        src="{{ media_url }}{{ img.thumbnail2.name }}" /></a>
                        </td>
                        <td>
            Title: <input type="text" name="title-{{ img.pk }}" value="{{ img.title }}" /><br />
            Tags: <input type="text" name="tags-{{ img.pk }}" value="{{ img.tag_lst }}" /><br />
            Rating:
            <input size="3" type="text" name="rating-{{ img.pk }}" value="{{ img.rating }}" /><br />

                    {% for album in albums %}
                        {{ album.title }}:
                        <input type="checkbox" name="album-{{ img.pk }}" value="{{ album.pk }}"
                            {% if album.title in img.album_lst %}checked{% endif %} />
                    {% endfor %}
                    </td></tr></table>
                    <br />

                {% endif %}

                <!-- THUMBNAILS VIEW  -->
                {% if view == "thumbnails" %}
                    <a href="{% url photo.views.image img.pk %}"><img border="0" alt=""
                        src="{{ media_url }}{{ img.thumbnail2.name }}" /></a>
                {% endif %}
            {% endfor %}

            {% if view == "edit" %}
                <div id="update"><input type="submit" value="Update"></form></div>
            {% endif %}

We're adding primary keys to the names of each input element to differentiate them. The rest
should be fairly clear. Obviously, this UI assumes there won't be *too* many albums, otherwise you
might want to use the same type of input box as for tags. I would say that 15-20 albums, maybe up
to 30 should not be a problem.

I'm sure you can't wait to see the `update()` function:

.. sourcecode:: python

    def update(request):
        """Update image title, rating, tags, albums."""
        p = request.POST
        images = defaultdict(dict)

        # create dictionary of properties for each image
        for k, v in p.items():
            if k.startswith("title") or k.startswith("rating") or k.startswith("tags"):
                k, pk = k.split('-')
                images[pk][k] = v
            elif k.startswith("album"):
                pk = k.split('-')[1]
                images[pk]["albums"] = p.getlist(k)

        # process properties, assign to image objects and save
        for k, d in images.items():
            image = Image.objects.get(pk=k)
            image.title = d["title"]
            image.rating = int(d["rating"])

            # tags - assign or create if a new tag!
            tags = d["tags"].split(', ')
            lst = []
            for t in tags:
                if t: lst.append(Tag.objects.get_or_create(tag=t)[0])
            image.tags = lst

            if "albums" in d:
                image.albums = d["albums"]
            image.save()

        return HttpResponseRedirect(request.META["HTTP_REFERER"], dict(media_url=MEDIA_URL))

There are two interesting points I'd like to touch on here: first, take a note of how we set
image.albums to the list of ids as strings --- Django is smart enough to do the right thing;
secondly, we're first creating a dictionary of properties for each image and then setting all of
them before saving --- for performance reasons, rather than setting a property at a time and
saving.

It's also crucial that we create a new tag if it does not exist yet. Fortunately, Django is nice
enough to provide a convenient shortcut to do just that in one line (the function returns a tuple
where second value indicates if a new object was created; we're only interested in the object
itself in this case).

Here's what our pretty edit interface looks like:

.. image:: _static/p4.png

`Next: part IV <photo4.html>`_
