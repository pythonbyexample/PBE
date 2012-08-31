
Django Tutorial: A Simple Blog, Part I
--------------------------------------

Our next project will be a simple blog system. We'll learn how to work with views, pagination,
comments and plenty of other good things.

Defining the Model
==================

As always in Django apps, we'll start by defining a model (in blog/models.py):

.. sourcecode:: python

    class Post(models.Model):
        title = models.CharField(max_length=60)
        body = models.TextField()
        created = models.DateTimeField(auto_now_add=True)

        def __unicode__(self):
            return self.title


    ### Admin

    class PostAdmin(admin.ModelAdmin):
        search_fields = ["title"]

    admin.site.register(Post, PostAdmin)

... and running: `manage.py syncdb; manage.py runserver`

Front Page view
===============

Let's go ahead and add the usual blog front page view for the visitors:

.. sourcecode:: python

    from django.core.paginator import Paginator, InvalidPage, EmptyPage
    from django.core.urlresolvers import reverse

    from dbe.blog.models import *

    def main(request):
        """Main listing."""
        posts = Post.objects.all().order_by("-created")
        paginator = Paginator(posts, 2)

        try: page = int(request.GET.get("page", '1'))
        except ValueError: page = 1

        try:
            posts = paginator.page(page)
        except (InvalidPage, EmptyPage):
            posts = paginator.page(paginator.num_pages)

        return render_to_response("list.html", dict(posts=posts, user=request.user))

The pagination code requires a little explanation: first line creates the paginator with 2 items
per page. Normally you'd set it to something like 10 or 15, but in this case we want to create
just a few posts to illustrate pagination. The list of posts is ordered by created time in reverse
order.

The way pagination works is that your next/previous link at the bottom of the page will send the
page number in `GET` request and we'll tell paginator object to use that page when sending a list
of posts to our template. When no page is given, we set page number to `1`.

Finally, if there's an error setting the page to given number, which usually means the page number
is too high (that can happen, for instance, if we delete some items and then use an old link) ---
the sensible thing to do is to return the last page.

Our base template and front page template will be in `templates/blog/bbase.html` and
`templates/blog/list.html`:

.. sourcecode:: django

    <?xml version="1.0" encoding="UTF-8"?>
    <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
        "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
    <html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
    <head> <title>{% block title %}MyBlog{% endblock %}</title> </head>

    <body>
        <div id="sidebar"> {% block sidebar %} {% endblock %} </div>
        <div id="container">
            <div id="menu">
                {% block nav-global %}

                    <!-- MENU -->
                    <h3>MyBlog</h3>
                    {% if user.is_staff %}
                    <a href="{% url admin:index %}">Admin</a>
                    <a href="{% url admin:blog_post_add %}">Add post</a>
                    {% endif %}

                {% endblock %}
            </div>

            <div id="content">
                {% block content %}{% endblock %}
            </div>
        </div>

    </body>
    </html>


.. sourcecode:: django

    {% extends "bbase.html" %}

    {% block content %}
        <div class="main">

            <!-- Posts  -->
            <ul>
                {% for post in posts.object_list %}
                    <div class="title">{{ post.title }}</div>
                    <ul>
                        <div class="time">{{ post.created }}</div>
                        <div class="body">{{ post.body|linebreaks }}</div>
                    </ul>
                {% endfor %}
            </ul>

            <!-- Next/Prev page links  -->
            {% if posts.object_list and posts.paginator.num_pages > 1 %}
            <div class="pagination" style="margin-top: 20px; margin-left: -20px; ">
                <span class="step-links">
                    {% if posts.has_previous %}
                        <a href= "?page={{ posts.previous_page_number }}">newer entries &lt;&lt; </a>
                    {% endif %}

                    <span class="current">
                        &nbsp;Page {{ posts.number }} of {{ posts.paginator.num_pages }}
                    </span>

                    {% if posts.has_next %}
                        <a href="?page={{ posts.next_page_number }}"> &gt;&gt; older entries</a>
                    {% endif %}
                </span>
            </div>
            {% endif %}

        </div>

    {% endblock %}

...and a line in urls.py:

.. sourcecode:: python

    urlpatterns = patterns('dbe.blog.views',
       (r"", "main"),
    )

If you're wondering about `linebreaks` filter I've added after the body, it simply converts
newlines in body text into html line breaks.

I've also added a bit of styling and some sample blog posts (can you tell that I *love*
Wikipedia?)


.. image:: _static/b1.png

Second page:

.. image:: _static/b2.png

If you still remember the first tutorial, we made a small customization of `change_list` template
to show a link for adding multiple todo items. We need to do exactly the same thing here, except
that the template will live in `blog/post/change_list.html` and the link will be as follows:

.. sourcecode:: html

    <a href="{% url dbe.blog.views.main %}">Back to Blog Frontpage</a>

Post Page
=========

We'll also need a separate page for each post with visitors' comments and full post text (if we
later decide to limit post body shown on front page). Here's how I plan to set things up: the url
will be `/blog/post/{pk}/` where pk is the primary key of post's object; template will be called
`post.html` and the view function will be `post()`.

The main listing will show a simple link:

.. sourcecode:: django

    <div class="commentlink"><a href="{% url blog.views.post post.pk %}">Comments</a></div>

Add this to `urls.py`:

.. sourcecode:: python

   (r"^(\d+)/$", "post"),

All the interesting code will go into the view and template:

.. sourcecode:: python

    def post(request, pk):
        """Single post with comments and a comment form."""
        post = Post.objects.get(pk=int(pk))
        d = dict(post=post, user=request.user)
        return render_to_response("post.html", d)

Most of the page is the same as `list.html`, but we don't need the paginator stuff anymore and
we'll add comments code soon:

.. sourcecode:: django

    <div class="title">{{ post.title }}</div>
    <ul>
        <div class="time">{{ post.created }}</div>
        <div class="body">{{ post.body|linebreaks }}</div>
    </ul>

    <!-- Comments  -->

And that's that! We are now officially ready to add comments.

Comments
========

Here's the setup we'll use: model name is `Comment`; the url will be `/blog/add_comment/{pk}/`
and function will be `add_comment()`.

First, the model:

.. sourcecode:: python

    class Comment(models.Model):
        created = models.DateTimeField(auto_now_add=True)
        author = models.CharField(max_length=60)
        body = models.TextField()
        post = models.ForeignKey(Post)

        def __unicode__(self):
            return unicode("%s: %s" % (self.post, self.body[:60]))

    class CommentAdmin(admin.ModelAdmin):
        display_fields = ["post", "author", "created"]

    admin.site.register(Comment, CommentAdmin)

Add the urlconf line; the number here will refer to the Post object, not Comment object:

.. sourcecode:: python

   (r"^add_comment/(\d+)/$", "add_comment"),

We're not going to do any sort of validation on comments --- if `Name` is empty, we'll simply have
it set to "Anonymous". If both fields are empty, we'll redirect right back:

.. sourcecode:: python

    from django.forms import ModelForm

    class CommentForm(ModelForm):
        class Meta:
            model = Comment
            exclude = ["post"]

    def add_comment(request, pk):
        """Add a new comment."""
        p = request.POST

        if p.has_key("body") and p["body"]:
            author = "Anonymous"
            if p["author"]: author = p["author"]

            comment = Comment(post=Post.objects.get(pk=pk))
            cf = CommentForm(p, instance=comment)
            cf.fields["author"].required = False

            comment = cf.save(commit=False)
            comment.author = author
            comment.save()
        return HttpResponseRedirect(reverse("dbe.blog.views.post", args=[pk]))

When Django creates the form from `Comment` model, the form will require `Name` to be filled in
because `author` property is not null. Validation is performed when form object is saved --- we have
to turn the requirement off before that call. Even so, we can't commit it because the model itself
will complain about a blank author: therefore we have to save without committing, set the author
and then save the model. That's quite a few hoops we have to jump through here, but what can you
do.

`CommentForm` class should be clear enough --- the only detail is that we're ommitting the `post`
property from fields, otherwise the post pulldown would be shown in the form, and we definitely
don't want that.

The `post()` view will have to provide a list of comments and a blank form now:

.. sourcecode:: python

    from django.core.context_processors import csrf

    def post(request, pk):
        """Single post with comments and a comment form."""
        post = Post.objects.get(pk=int(pk))
        comments = Comment.objects.filter(post=post)
        d = dict(post=post, comments=comments, form=CommentForm(), user=request.user)
        d.update(csrf(request))
        return render_to_response("post.html", d)

Hopefully all of this looks clear; I won't delve into csrf at this point but it should be enough
to know that this code is required in Django 1.2 when you have a POST form and it will protect you
and your visitors from CSRF attacks.

Finally, this will be our addition to `post.html`:

.. sourcecode:: django

    <!-- Comments  -->
    {% if comments %}
        <p>Comments:</p>
    {% endif %}

    {% for comment in comments %}
        <div class="comment">
            <div class="time">{{ comment.created }} | {{ comment.author }}</div>
            <div class="body">{{ comment.body|linebreaks }}</div>
        </div>
    {% endfor %}

    <div id="addc">Add a comment</div>
    <!-- Comment form  -->
    <form action="{% url blog.views.add_comment post.id %}" method="POST">{% csrf_token %}
        <div id="cform">
            Name: {{ form.author }}
            <p>{{ form.body|linebreaks }}</p>
        </div>
        <div id="submit"><input type="submit" value="Submit"></div>
    </form>

Take a note of the `csrf_token`! Again, it's required since Django 1.2 for all POST forms.

.. image:: _static/b3.png

`..continue to Part II of MyBlog Tutorial <blog2.html>`_
