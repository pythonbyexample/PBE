
Django Tutorial: A Simple Forum - Part I
----------------------------------------

Forums are one of the cornerstones of the Web --- they are integral for organizing niche
communities for anything from Orchids to DIY audio components. After reading this tutorial, you'll
be able to make one!

Defining the Model
==================

Let's start by defining the model classes (in forum/models.py):

.. sourcecode:: python

    from django.db import models
    from django.contrib.auth.models import User
    from django.contrib import admin
    from string import join
    from settings import MEDIA_ROOT

    class Forum(models.Model):
        title = models.CharField(max_length=60)
        def __unicode__(self):
            return self.title

    class Thread(models.Model):
        title = models.CharField(max_length=60)
        created = models.DateTimeField(auto_now_add=True)
        creator = models.ForeignKey(User, blank=True, null=True)
        forum = models.ForeignKey(Forum)

        def __unicode__(self):
            return unicode(self.creator) + " - " + self.title

    class Post(models.Model):
        title = models.CharField(max_length=60)
        created = models.DateTimeField(auto_now_add=True)
        creator = models.ForeignKey(User, blank=True, null=True)
        thread = models.ForeignKey(Thread)
        body = models.TextField(max_length=10000)

        def __unicode__(self):
            return u"%s - %s - %s" % (self.creator, self.thread, self.title)

        def short(self):
            return u"%s - %s\n%s" % (self.creator, self.title, self.created.strftime("%b %d, %I:%M %p"))
        short.allow_tags = True

    ### Admin

    class ForumAdmin(admin.ModelAdmin):
        pass

    class ThreadAdmin(admin.ModelAdmin):
        list_display = ["title", "forum", "creator", "created"]
        list_filter = ["forum", "creator"]

    class PostAdmin(admin.ModelAdmin):
        search_fields = ["title", "creator"]
        list_display = ["title", "thread", "creator", "created"]

    admin.site.register(Forum, ForumAdmin)
    admin.site.register(Thread, ThreadAdmin)
    admin.site.register(Post, PostAdmin)

As always, you should run `manage.py syncdb; manage.py runserver` to add tables and start Django.

If you ever used a forum site, you already know that front page will show a list of available
forums, each forum page will show a list of threads with the latest on top and each thread page
will show a list of posts sorted with the latest showing up at the bottom. The forum page will
also let you add a new topic and the thread page will let you post a reply.

That's the most basic forum functionality in a nutshell and that will be our first task. To begin,
let's outline the url, function and template naming scheme: frontpage --- `/forum/`, `main()` and
`list.html`; forum --- `/forum/{id}/`, `forum()` and `forum.html`; thread: `/forum/thread/{id}/`,
`thread()` and `thread.html`.

Your `urlconf` lines and main listing view should be as follows:

.. sourcecode:: python

    (r"", "main"),
    (r"^forum/(\d+)/$", "forum"),
    (r"^thread/(\d+)/$", "thread"),

.. sourcecode:: python

    from django.core.urlresolvers import reverse
    from settings import MEDIA_ROOT, MEDIA_URL

    def main(request):
        """Main listing."""
        forums = Forum.objects.all()
        return render_to_response("forum/list.html", dict(forums=forums, user=request.user))

Forum listings usually show the total number of posts as well as the author and subject of the latest
post. That's something we can easily add to our models:

.. sourcecode:: python


    class Forum(models.Model):
        # ...

        def num_posts(self):
            return sum([t.num_posts() for t in self.thread_set.all()])

        def last_post(self):
            if self.thread_set.count():
                last = None
                for t in self.thread_set.all():
                    l = t.last_post()
                    if l:
                        if not last: last = l
                        elif l.created > last.created: last = l
                return last

    class Thread(models.Model):
        # ...

        def num_posts(self):
            return self.post_set.count()

        def num_replies(self):
            return self.post_set.count() - 1

        def last_post(self):
            if self.post_set.count():
                return self.post_set.order_by("created")[0]

When a `ForeignKey` or a `Many-to-Many` relationship is created, the related model instances get
an automatic handle to the original objects --- in our case, `Thread` will have `self.post_set`
QuerySet object (keep in mind it's not a list and can't be used as one!), and Forum will have
`self.thread_set` object.

Front Page
==========

Here is the main loop of the template I used for main listing:

.. sourcecode:: django

    <!-- Forums  -->
    <div id="list">
    <table border="0" cellpadding="4" width="100%">
        <tr>
            <td></td>
            <td>Posts</td>
            <td>Last post</td>
            <td></td>
        </tr>

        {% for forum in forums %}
        <tr>
            <td {% if forloop.last %}class="last"{% endif %}>
            <div class="title"> <a href="{% url forum.views.forum forum.pk %}">{{ forum.title }}</a>
                </div></td>
            <td {% if forloop.last %}class="last"{% endif %}>{{ forum.num_posts }}</td>
            <td {% if forloop.last %}class="last"{% endif %}>
                {{ forum.last_post.short|linebreaksbr }}</td>
            <td {% if forloop.last %}class="last"{% endif %}>
                <a class="button" href="{% url forum.views.forum forum.pk %}">VIEW</a>
            </td>
        </tr>

        {% endfor %}
    </div>

The `forloop.last` construct is used here to assign the css class that won't have a bottom border
--- the other rows will have one as you will soon see in the screenshot. Take a note of
 `linebreaksbr` filter that converts new lines to `<br />` tags.

.. image:: _static/f1.png

Forum View
==========

Now for the forum view.. Again, both view and template are called `forum`:

.. sourcecode:: python

    def add_csrf(request, ** kwargs):
        d = dict(user=request.user, ** kwargs)
        d.update(csrf(request))
        return d

    def mk_paginator(request, items, num_items):
        """Create and return a paginator."""
        paginator = Paginator(items, num_items)
        try: page = int(request.GET.get("page", '1'))
        except ValueError: page = 1

        try:
            items = paginator.page(page)
        except (InvalidPage, EmptyPage):
            items = paginator.page(paginator.num_pages)
        return items


    def forum(request, pk):
        """Listing of threads in a forum."""
        threads = Thread.objects.filter(forum=pk).order_by("-created")
        threads = mk_paginator(request, threads, 20)
        return render_to_response("forum/forum.html", add_csrf(request, threads=threads, pk=pk))

I've separated functions that add csrf dictionary and create paginator since we'll need to use
these often.

The template is fairly close to the main listing but now we need pagination and a button to add a
new topic:

.. sourcecode:: django

    <!-- Threads  -->
    <a id="new_topic" class="buttont" href=
    "{% url forum.views.post 'new_thread' pk %}">Start New Topic</a>
    <br />
    <br />

    <div id="list">
    <table border="0" cellpadding="4" width="100%">
        <tr>
            <td>Topics</td>
            <td>Replies</td>
            <td>Last post</td>
            <td></td>
        </tr>

        {% for thread in threads.object_list %}
        <tr>
            <td {% if forloop.last %}class="last"{% endif %}>
            <div class="title"> <a href="{% url forum.views.thread thread.pk %}">{{ thread.title }}</a>
                </div></td>
            <td {% if forloop.last %}class="last"{% endif %}>{{ thread.num_replies }}</td>
            <td {% if forloop.last %}class="last"{% endif %}>
                {{ thread.last_post.short|linebreaksbr }}</td>
            <td {% if forloop.last %}class="last"{% endif %}>
                <a class="button" href="{% url forum.views.thread thread.pk %}">VIEW</a>
            </td>
        </tr>

        {% endfor %}
    </table>
    </div>

    <!-- Next/Prev page links  -->
    {% if threads.object_list and threads.paginator.num_pages > 1 %}
    <div class="pagination">
        <span class="step-links">
            {% if threads.has_previous %}
                <a href= "?page={{ threads.previous_page_number }}">previous &lt;&lt; </a>
            {% endif %}

            <span class="current">
                &nbsp;Page {{ threads.number }} of {{ threads.paginator.num_pages }}
            </span>

            {% if threads.has_next %}
                <a href="?page={{ threads.next_page_number }}"> &gt;&gt; next</a>
            {% endif %}
        </span>
    </div>
    {% endif %}

Thread View
===========

At last, our thread view (both function and template are called `thread`):

.. sourcecode:: python

    def thread(request, pk):
        """Listing of posts in a thread."""
        posts = Post.objects.filter(thread=pk).order_by("created")
        posts = mk_paginator(request, posts, 15)
        title = Thread.objects.get(pk=pk).title
        return render_to_response("forum/thread.html", add_csrf(request, posts=posts, pk=pk,
            title=title, media_url=MEDIA_URL))

As you can see, we're sorting in the opposite order compared to the forum view.

.. sourcecode:: django


    <!-- Posts  -->
    <div class="ttitle">{{ title }}</div>
    <div id="list">

        {% for post in posts.object_list %}
            <div class="post">
                <span class="title">{{ post.title }}</span><br />
                by {{ post.creator }} | <span class="date">{{ post.created }}</span> <br /><br />
                {{ post.body }} <br />
            </div>
        {% endfor %}
    </div>

    <!-- Next/Prev page links
        ...
    -->

    <a class="button" href="{% url forum.views.post 'reply' pk %}">Reply</a>

I skipped pagination since it's the same as in previous listing. Here's what we have so far:

.. image:: _static/f2.png

.. sourcecode:: django

.. image:: _static/f3.png

Posting Replies and New Topics
==============================

Of course, we also need to add a way to post replies and new threads. I'll use the same template
for both and call it `post.html` and the method names will be: `post()` to show the form and
`new_thread()` and `reply()` to submit; urls will be: `/forum/post/(new_thread|reply)/{id}/` and
`/forum/new_thread/{id}/` and `/forum/reply/{id}/`. I've added these `urlconf` lines:

.. sourcecode:: python

   (r"^post/(new_thread|reply)/(\d+)/$", "post"),
   (r"^reply/(\d+)/$", "reply"),
   (r"^new_thread/(\d+)/$", "new_thread"),

...and `post()`:

.. sourcecode:: python

    def post(request, ptype, pk):
        """Display a post form."""
        action = reverse("dbe.forum.views.%s" % ptype, args=[pk])
        if ptype == "new_thread":
            title = "Start New Topic"
            subject = ''
        elif ptype == "reply":
            title = "Reply"
            subject = "Re: " + Thread.objects.get(pk=pk).title

        return render_to_response("forum/post.html", add_csrf(request, subject=subject,
            action=action, title=title))

When adding a new Topic, we'll need both the subject and body text --- I will silently return to forum
listing otherwise to keep things simple for the tutorial (although normally you should show an error
and highlight required fields).

.. sourcecode:: python

    def new_thread(request, pk):
        """Start a new thread."""
        p = request.POST
        if p["subject"] and p["body"]:
            forum = Forum.objects.get(pk=pk)
            thread = Thread.objects.create(forum=forum, title=p["subject"], creator=request.user)
            Post.objects.create(thread=thread, title=p["subject"], body=p["body"], creator=request.user)
        return HttpResponseRedirect(reverse("dbe.forum.views.forum", args=[pk]))


Here we have the `reply()` function which is very similar to `new_thread()`:

.. sourcecode:: python

    def reply(request, pk):
        """Reply to a thread."""
        p = request.POST
        if p["body"]:
            thread = Thread.objects.get(pk=pk)
            post = Post.objects.create(thread=thread, title=p["subject"], body=p["body"],
                creator=request.user)
        return HttpResponseRedirect(reverse("dbe.forum.views.thread", args=[pk]) + "?page=last")

This is an outrage! Firefox does not know what a mossery is? I shall be writing a stern letter.
(Also: passing? It may be so, for now, but it will surely come back!)

.. image:: _static/f4.png

One tiny usability improvement: we already have a link on every page that goes to frontpage (it's
the one that says `ForumApp` in upper left corner), but a user won't be able to go back from
thread page to the forum page easily. We need to add these lines to `thread()` and `thread.html`
to create a backlink:

.. sourcecode:: python

    t = Thread.objects.get(pk=pk)
    return render_to_response("forum/thread.html", add_csrf(request, posts=posts, pk=pk, title=t.title,
                                                           forum_pk=t.forum.pk))

.. sourcecode:: django

    <a href="{% url forum.views.forum forum_pk %}">&lt;&lt; back to list of topics</a>

`Continue to part II <forum2.html>`_
