
Django Tutorial: Photo Organizer and Sharing App Part IV
--------------------------------------------------------

Searching and Filtering
=======================

The one last thing we need is a page that will let us filter and sort all images by various
criteria: size, title, tags, albums and ratings. We'll call it "search page" even though it will
do so much more. The url, view and template will all be called `search`.

Let's start with the `urlconf` line and template:

.. sourcecode:: python

   (r"^search/$", "search"),


.. sourcecode:: django

    <!-- Form  -->
    <ul>
        <div class="title">Search</div>
            <form action="{% url photo.views.search %}" method="POST">{% csrf_token %}

            <div class="form">
            Title: <input type="text" name="title" value="{{ prm.title }}" />
            Filename: <input type="text" name="filename" value="{{ prm.filename }}" />
            Tags: <input type="text" name="tags" value="{{ prm.tags }}" /><br />
            </div>

            <div class="form">
            Rating:
            <input size="3" type="text" name="rating_from" value="{{ prm.rating_from }}" /> to
            <input size="3" type="text" name="rating_to" value="{{ prm.rating_to }}" />
            Width:
            <input size="3" type="text" name="width_from" value="{{ prm.width_from }}" /> to
            <input size="3" type="text" name="width_to" value="{{ prm.width_to }}" />
            Height:
            <input size="3" type="text" name="height_from" value="{{ prm.height_from }}" /> to
            <input size="3" type="text" name="height_to" value="{{ prm.height_to }}" />
            </div>

            <div class="form">
            {% for album in albums %}
                {{ album.title }}:
                <input type="checkbox" name="album" value="{{ album.pk }}"
                    {% if album.pk in prm.album %}checked{% endif %} />
            {% endfor %}

            <select name="view">
                <option value="view" {% if prm.view == "view" %}selected{% endif %}>view</option>
                <option value="edit" {% if prm.view == "edit" %}selected{% endif %}>edit</option>
            </select>

            <input type="submit" value="Apply" />
            </div>

        <!-- Results  -->
        <div class="title">Results</div>

            {% for img in results.object_list %}

                <!-- EDIT VIEW  -->
                {% if prm.view == "edit" %}

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

                <!-- COMPACT VIEW  -->
                {% if prm.view == "view" %}
                    <a href="{% url photo.views.image img.pk %}"><img border="0" alt=""
                        src="{{ media_url }}{{ img.thumbnail2.name }}" /></a>
                {% endif %}
            {% endfor %}

            </form>

    </ul>

    <!-- Next/Prev page links  -->
    {% if results.object_list and results.paginator.num_pages > 1 %}
    <div class="pagination">
        <span class="step-links">
            {% if results.has_previous %}
                <a href= "?page={{ results.previous_page_number }}">previous &lt;&lt; </a>
            {% endif %}

            <span class="current">
                &nbsp;Page {{ results.number }} of {{ results.paginator.num_pages }}
            </span>

            {% if results.has_next %}
                <a href="?page={{ results.next_page_number }}"> &gt;&gt; next</a>
            {% endif %}
        </span>
    </div>
    {% endif %}

...and the `search()` view:

.. sourcecode:: python

    @login_required
    def search(request):
        """Search, filter, sort images."""
        try: page = int(request.GET.get("page", '1'))
        except ValueError: page = 1

        p = request.POST
        images = defaultdict(dict)

        # init parameters
        parameters = {}
        keys = "title filename rating_from rating_to width_from width_to height_from height_to tags view"
        keys = keys.split()
        for k in keys:
            parameters[k] = ''
        parameters["album"] = []

        # create dictionary of properties for each image and a dict of search/filter parameters
        for k, v in p.items():
            if k == "album":
                parameters[k] = [int(x) for x in p.getlist(k)]
            elif k in parameters:
                parameters[k] = v
            elif k.startswith("title") or k.startswith("rating") or k.startswith("tags"):
                k, pk = k.split('-')
                images[pk][k] = v
            elif k.startswith("album"):
                pk = k.split('-')[1]
                images[pk]["albums"] = p.getlist(k)

        # save or restore parameters from session
        if page != 1 and "parameters" in request.session:
            parameters = request.session["parameters"]
        else:
            request.session["parameters"] = parameters

        results = update_and_filter(images, parameters)

        # make paginator
        paginator = Paginator(results, 20)
        try:
            results = paginator.page(page)
        except (InvalidPage, EmptyPage):
            request = paginator.page(paginator.num_pages)

        # add list of tags as string and list of album names to each image object
        for img in results.object_list:
            tags = [x[1] for x in img.tags.values_list()]
            img.tag_lst = join(tags, ', ')
            img.album_lst = [x[1] for x in img.albums.values_list()]

        d = dict(results=results, user=request.user, albums=Album.objects.all(), prm=parameters,
            media_url=MEDIA_URL)
        d.update(csrf(request))
        return render_to_response("photo/search.html", d)

One complication that I had to address was that the form has a large number of parameters that are
submitted via `POST` request, while the paginator works through a link which is a `GET` request.
One solution would be to append parameters to the link, but I think it's easier to save them in
session.

The way it works is that when you submit the form, the view will save all parameters in session
dictionary, filter the results and show you the first page. Once you click on the second page,
parameters are loaded from session; if you re-submit the form, you'll go back to the first page
again.

I split off the `update_and_filter()` function from `search()` because it was getting too big and
unwieldy --- I usually try to keep functions from getting longer than one screenful or so.

.. sourcecode:: python

    from django.db.models import Q

    def update_and_filter(images, p):
        """Update image data if changed, filter results through parameters and return results list."""
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

        # filter results by parameters
        results = Image.objects.all()
        if p["title"]       : results = results.filter(title__icontains=p["title"])
        if p["filename"]    : results = results.filter(image__icontains=p["filename"])
        if p["rating_from"] : results = results.filter(rating__gte=int(p["rating_from"]))
        if p["rating_to"]   : results = results.filter(rating__lte=int(p["rating_to"]))
        if p["width_from"]  : results = results.filter(width__gte=int(p["width_from"]))
        if p["width_to"]    : results = results.filter(width__lte=int(p["width_to"]))
        if p["height_from"] : results = results.filter(height__gte=int(p["height_from"]))
        if p["height_to"]   : results = results.filter(height__lte=int(p["height_to"]))

        if p["tags"]:
            tags = p["tags"].split(', ')
            lst = []
            for t in tags:
                if t:
                    results = results.filter(tags=Tag.objects.get(tag=t))

        if p["album"]:
            lst = p["album"]
            or_query = Q(albums=lst[0])
            for album in lst[1:]:
                or_query = or_query | Q(albums=album)
            results = results.filter(or_query).distinct()
        return results

First part of this function is the same as in `update()`; the second part has some good examples
of filtering arguments: `__gte` and `__lte` filter by greater than or equal and less than or
equal, respectively. Tags and Albums are filtered in a different way because it doesn't make much
sense to do `AND` filtering on albums. It's a bit tricky to do `OR` filtering with unknown number
of arguments --- usually you could do something like this:

.. sourcecode:: python

    results.filter(Q(x=a) | Q(x=b) | Q(x=c))

In our case we don't know how many albums we'll have to deal with, therefore we have to create the
`OR` query first; we also need to use the `distinct()` method to avoid duplicates.

The following screenshots illustrate various parameters in our UI:

.. image:: _static/p5.png

.. sourcecode:: python

.. image:: _static/p6.png

.. sourcecode:: python

.. image:: _static/p7.png

.. sourcecode:: python

.. image:: _static/p8.png

.. sourcecode:: python

.. image:: _static/p9.png

Sorting
=======

The last thing I want to add is an option to sort results by a few properties and add a `by user`
filter. Everything is done in the same template and view:

.. sourcecode:: django

    User:
    <select name="user">
        <option value="all" {% if prm.user == "all" %}selected{% endif %}>all</option>
        {% for user in users %}
            <option value="{{ user.pk }}" {% if prm.user == user.pk %}selected{% endif %}>
                {{ user.username }}</option>
        {% endfor %}
    </select>

    Sort:
    <select name="sort">
        <option value="created" {% if prm.sort == "created" %}selected{% endif %}>date</option>
        <option value="rating" {% if prm.sort == "rating" %}selected{% endif %}>rating</option>
        <option value="width" {% if prm.sort == "width" %}selected{% endif %}>width</option>
        <option value="height" {% if prm.sort == "height" %}selected{% endif %}>height</option>
    </select>

    <select name="asc_desc">
        <option value="asc" {% if prm.sort == "asc" %}selected{% endif %}>ascending</option>
        <option value="desc" {% if prm.sort == "desc" %}selected{% endif %}>descending</option>
    </select>

Hopefully you can see where this code needs to be inserted; if not, link to full sources will be
provided at the end of this part.

.. sourcecode:: python

    def search(request):
        # ...

        keys = "title filename rating_from rating_to width_from width_to height_from height_to tags view"\
            " user sort asc_desc"
        keys = keys.split()

        # ...

        for k, v in p.items():
            if k == "album":
                parameters[k] = [int(x) for x in p.getlist(k)]
            elif k == "user":
                if v != "all": v = int(v)
                parameters[k] = v

        # ...

        d = dict(results=results, user=request.user, albums=Album.objects.all(), prm=parameters,
                 users=User.objects.all(), media_url=MEDIA_URL)

    def update_and_filter(images, p):

        # ...

        # sort and filter results by parameters
        order = "created"
        if p["sort"]: order = p["sort"]
        if p["asc_desc"] == "desc": order = '-' + order

        results = Image.objects.all().order_by(order)
        if p["user"] and p["user"] != "all"    : results = results.filter(user__pk=int(p["user"]))

        # ...

I've also added a bit of image data to `edit` view mode:

.. image:: _static/p10.png

.. sourcecode:: python

.. image:: _static/p11.png

.. sourcecode:: python

.. image:: _static/p12.png

`Download full tutorial sources <photosrc.tar.gz>`_

I've added a bit of very basic, "light-duty" security to this App. Make no mistake: a determined
and technically sophisticated user will be able to to look at the images in a non-public album:
all images are available as simple links under `/media/images/` (although he'll have to guess the
filenames since `/media/` does not allow listing of directory contents).

I won't add the following code to the tutorial, but the way to avoid this would be to store images
outside of `/media/` and have Django serve images by itself (this is not a very efficient method
but it may be acceptable for a small app). Here is a small snippet of a view that serves an image
file from disk:

.. sourcecode:: python

    def get_image(request, fn):
        fn = fn.encode("utf-8")
        imgdir = pjoin(MEDIA_ROOT, "../images")
        ifn = pjoin(imgdir, fn)
        return HttpResponse(open(ifn).read(), mimetype='image/jpeg')

Images used in the tutorial were made and copyrighted by:

`<http://www.sxc.hu/profile/reuben4eva>`_
`<http://www.sxc.hu/profile/mike62>`_
`<http://www.sxc.hu/profile/paaseiland>`_
`<http://www.sxc.hu/profile/tijmen>`_
`<http://www.sxc.hu/profile/shark001>`_
`<http://www.sxc.hu/profile/jamie84>`_
`<http://www.sxc.hu/profile/pipp>`_
