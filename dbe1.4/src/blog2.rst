
Django Tutorial: A Simple Blog, Part II
---------------------------------------

We'll start off Part II with a set of monthly links that will go on the front page.

Archive Sidebar
===============

Our url will be `/blog/month/{year}/{month}/`, we'll use `month()` function and the same template
we're using for the main listing.

We won't need pagination for the new view. I split off the `mkmonth_lst()` function since we'll
need the list of months in the new view as well:

.. sourcecode:: python

    import time
    from calendar import month_name

    def mkmonth_lst():
        """Make a list of months to show archive links."""

        if not Post.objects.count(): return []

        # set up vars
        year, month = time.localtime()[:2]
        first = Post.objects.order_by("created")[0]
        fyear = first.created.year
        fmonth = first.created.month
        months = []

        # loop over years and months
        for y in range(year, fyear-1, -1):
            start, end = 12, 0
            if y == year: start = month
            if y == fyear: end = fmonth-1

            for m in range(start, end, -1):
                months.append((y, m, month_name[m]))
        return months

    def month(request, year, month):
        """Monthly archive."""
        posts = Post.objects.filter(created__year=year, created__month=month)
        return render_to_response("list.html", dict(post_list=posts, user=request.user,
                                                    months=mkmonth_lst(), archive=True))

As you can see, we're starting with current month and going back to the month of our first
post. We don't care too much if there are months with no posts --- hopefully there won't be too many
of those. Lucky for us, Django allows filtering dates by year and month, which makes it really
easy to make the `month()` function.

Since we'd like to reuse the same template, having no paginator presents a slight problem: we're
looping over `posts.object_list`, but now we just have a plain list of posts. Possibly the easiest
way to get around this is to simply send the list along with the paginator in `main()`:

.. sourcecode:: python

    return render_to_response("list.html", dict(posts=posts, user=request.user,
                                                post_list=posts.object_list, months=mkmonth_lst()))


...and we'll test for archive argument in `list.html` (also adding the monthly sidebar, of course):

.. sourcecode:: django

    {% block sidebar %}
        <style type="text/css">
            #sidebar { float: right; border: 1px dotted #ccc; padding: 4px; }
        </style>
        <div id="sidebar">
            Monthly Archive<br />
            {% for month in months %}
                <a href="{% url blog.views.month month.0 month.1 %}">{{ month.2 }}</a> <br />
            {% endfor %}
        </div>
    {% endblock %}

    {% block content %}
    [ ... ]

        <!-- Posts  -->
        <ul>
            {% for post in post_list %}
                <div class="title">{{ post.title }}</div>
                <ul>
                    <div class="time">{{ post.created }}</div>
                    <div class="body">{{ post.body|linebreaks }}</div>
                    <div class="commentlink"><a href="{% url blog.views.post post.pk %}">Comments</a></div>
                </ul>
            {% endfor %}
        </ul>

        <!-- Next/Prev page links  -->
        {% if not archive and posts.object_list and posts.paginator.num_pages > 1 %}
        [ ... ]

Not to forget the new url in `urls.py`:

.. sourcecode:: python

   (r"^month/(\d+)/(\d+)/$", "month"),

Doesn't look like much because we only have one month worth of posts, but there it is:

.. image:: _static/b4.png

One tiny cosmetic change in `list.html` to avoid printing year for each line:

.. sourcecode:: django

    {% for month in months %}
        {% ifchanged month.0 %} {{ month.0 }} <br /> {% endifchanged %}
        <a href="{% url blog.views.month month.0 month.1 %}">{{ month.2 }}</a> <br />
    {% endfor %}

Going back to comments for a second, here's how we are going to show the number of comments in
our main listing and archive list:

.. sourcecode:: django

    <a href="{% url blog.views.post post.pk %}">Comments ({{ post.comment_set.count }})</a>

Comment Notification
====================

As every blog author knows, spam can be an infuriating issue to deal with --- for this reason we
really need to make removing offending comments as painless as possible.

First, of course, we need to know that a comment was posted:

.. sourcecode:: python

    from django.core.mail import send_mail

    def save(self, *args, **kwargs):
        """Email when a comment is added."""
        if "notify" in kwargs and kwargs["notify"] == True:
            message = "Comment was was added to '%s' by '%s': \n\n%s" % (self.post, self.author,
                                                                         self.body)
            from_addr = "no-reply@example.com"
            recipient_list = ["myemail@domain.com"]
            send_mail( "New comment added", message, from_addr, recipient_list)

        if "notify" in kwargs: del kwargs["notify"]

        super(Comment, self).save(*args, ** kwargs)


This function will override the default Comment save method; it should go under `Comment` class.
We have to delete the `notify` flag in args dictionary because the default `save` will not accept
it. In `add_comment()`, we'll only set the `notify` flag if the comment is added by someone else:

.. sourcecode:: python

    notify = True
    if request.user.username == "ak": notify = False

    comment.save(notify=notify)

Your `settings.py` has to be set up for email (DEFAULT_FROM_EMAIL and SERVER_EMAIL can be set to
the same valid address):

.. sourcecode:: python

    EMAIL_HOST = ""
    EMAIL_HOST_USER = ""
    EMAIL_HOST_PASSWORD = ""
    DEFAULT_FROM_EMAIL = ""
    SERVER_EMAIL = ""

Comment Deletion
================

At this point I'd like to add two methods of deleting comments. We'll be able to click a button to
delete a single comment OR check any number of comments to delete at once. Our url will be
`/blog/delete_comment/` for multiple deletion and the same url followed by primary key for single
deletion; function name will be `delete_comment()`.

.. sourcecode:: python

    (r"^delete_comment/(\d+)/$", "delete_comment"),
    (r"^delete_comment/(\d+)/(\d+)/$", "delete_comment"),

.. sourcecode:: python

    def delete_comment(request, post_pk, pk=None):
        """Delete comment(s) with primary key `pk` or with pks in POST."""
        if request.user.is_staff:
            if not pk: pklst = request.POST.getlist("delete")
            else: pklst = [pk]

            for pk in pklst:
                Comment.objects.get(pk=pk).delete()
            return HttpResponseRedirect(reverse("dbe.blog.views.post", args=[post_pk]))

Make a note of how we use `getlist()` method to get multiple checked comments: if you use the
usual method --- with dictionary key lookup, it will only give you the last checked value (it's an
easy mistake to make and I've made it a number of times).

It's also important to return to the same post url if we're deleting comments one by one. We could
do this by looking up a comment's post primary key but it's just a little easier to use request's
`HTTP_REFERER` which stores the URL we came from.

And here's our template (this code goes in `post.html`):

.. sourcecode:: django

    <form action="{% url blog.views.delete_comment post.pk %}" method="POST">{% csrf_token %}
    {% for comment in comments %}
        <div class="comment">
            <div class="time">{{ comment.created }} | {{ comment.author }}</div>
            <div class="body">{{ comment.body|linebreaks }}</div>
            {% if user.is_staff %}
                <input type="checkbox" name="delete" value="{{ comment.pk }}">
                <a href="{% url blog.views.delete_comment post.pk comment.id %}">delete</a>
            {% endif %}
        </div>
    {% endfor %}

    {% if user.is_staff and comments %}
        <p><input type="submit" value="Delete all selected"></p>
        <br />
    {% endif %}
    </form>

...and that's that! Here's how we can now delete these obnoxious comments:

.. image:: _static/b5.png

If something's not working for you, here are the full sources:
`blogsrc.tar.gz <blogsrc.tar.gz>`_.
