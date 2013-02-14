Forum
=====


This tutorial will show you how to create a simple Forum app in Django using mcbv (modular CBVs)
library.

You can view or download the code here:

`Browse source files <https://github.com/akulakov/django/tree/master/dbe/>`_

`dbe.tar.gz <https://github.com/akulakov/django/tree/master/dbe.tar.gz>`_

A few custom functions and classes and the MCBV library are used in the tutorials, please look
through the `libraries page <libraries.html>`_ before continuing.

I will focus on the important parts of code in the listings below; I recommend opening the
source files in a separate window to see import lines and other details.


Models
------

I'll start by defining the model for the user profile, it's going to keep track of the # of
posts by the user and the avatar image:

.. sourcecode:: python

    from dbe.settings import MEDIA_URL

    class UserProfile(BaseModel):
        avatar = ImageField("Profile Pic", upload_to="images/", blank=True, null=True)
        posts  = IntegerField(default=0)
        user   = OneToOneField(User, related_name="profile")

        def __unicode__(self):
            return unicode(self.user)

        def increment_posts(self):
            self.posts += 1
            self.save()

        def avatar_image(self):
            return (MEDIA_URL + self.avatar.name) if self.avatar else None

Next we have the `Post` model, with title, body and a `ForeignKey` relationship to `Thread:`

.. sourcecode:: python

    class Post(BaseModel):
        title   = CharField(max_length=60)
        created = DateTimeField(auto_now_add=True)
        creator = ForeignKey(User, blank=True, null=True)
        thread  = ForeignKey(Thread, related_name="posts")
        body    = TextField(max_length=10000)

        class Meta:
            ordering = ["created"]

        def __unicode__(self):
            return u"%s - %s - %s" % (self.creator, self.thread, self.title)

        def short(self):
            created = self.created.strftime("%b %d, %I:%M %p")
            return u"%s - %s\n%s" % (self.creator, self.title, created)

        def profile_data(self):
            p = self.creator.profile
            return p.posts, p.avatar

The `short()` method will be used in "Last Post" columns in forum and thread listings;
`profile_data()` is used where user data is shown on the right side of each post in thread view.

The `Thread` model is similar:

.. sourcecode:: python

    class Thread(BaseModel):
        title   = CharField(max_length=60)
        created = DateTimeField(auto_now_add=True)
        creator = ForeignKey(User, blank=True, null=True)
        forum   = ForeignKey(Forum, related_name="threads")

        class Meta:
            ordering = ["-created"]

        def __unicode__(self):
            return unicode("%s - %s" % (self.creator, self.title))

        def get_absolute_url(self) : return reverse2("thread", dpk=self.pk)
        def last_post(self)        : return first(self.posts.all())
        def num_posts(self)        : return self.posts.count()
        def num_replies(self)      : return self.posts.count() - 1

The `Meta.ordering` list is used to set the default ordering of threads to be descending by
created date/time; I'm also using `utils.first()` to get the first post (posts are sorted in
ascending order) -- there's always guaranteed to be at least one post because a new thread's
body is added as a `Post` record.

.. sourcecode:: python

    class Forum(BaseModel):
        title = CharField(max_length=60)

        def __unicode__(self):
            return self.title

        def get_absolute_url(self):
            return reverse2("forum", dpk=self.pk)

        def num_posts(self):
            return sum([t.num_posts() for t in self.threads.all()])

        def last_post(self):
            """Go over the list of threads and find the most recent post."""
            threads = self.threads.all()
            last    = None
            for thread in threads:
                lastp = thread.last_post()
                if lastp and (not last or lastp.created > last.created):
                    last = lastp
            return last

In the `last_post()` method, I'll return the last post of all the threads in a forum.


Views
-----

The main listing of forums is a simple `ListView:`

.. sourcecode:: python

    from dbe.mcbv.list_custom import ListView, ListRelated

    class Main(ListView):
        list_model    = Forum
        template_name = "forum/list.html"

Next two views are going to serve the `Forum` and `Thread` listings:

.. sourcecode:: python

    class ForumView(ListRelated):
        detail_model  = Forum
        list_model    = Thread
        related_name  = "threads"
        template_name = "forum.html"

    class ThreadView(ListRelated):
        detail_model  = Thread
        list_model    = Post
        related_name  = "posts"
        template_name = "thread.html"

`ListRelated` view combines `Detail` and `List` views, with two models connected by a `ForeignKey`
relationship on the `ListView` model (where `related_name` needs to be specified).

.. sourcecode:: python

    from dbe.mcbv.edit import CreateView, UpdateView

    class EditProfile(UpdateView):
        form_model      = UserProfile
        modelform_class = ProfileForm
        success_url     = '#'
        template_name   = "profile.html"

        def modelform_valid(self, modelform):
            """Resize and save profile image."""
            # remove old image if changed
            name = modelform.cleaned_data.avatar
            pk   = self.kwargs.get("mfpk")
            old  = UserProfile.obj.get(pk=pk).avatar

            if old.name and old.name != name:
                old.delete()

            # save new image to disk & resize new image
            self.modelform_object = modelform.save()
            if self.modelform_object.avatar:
                img = PImage.open(self.modelform_object.avatar.path)
                img.thumbnail((160,160), PImage.ANTIALIAS)
                img.save(img.filename, "JPEG")
            return redir(self.success_url)

`ProfileForm` is inherited from the standard `ModelForm` with `posts` and `user` fields excluded.

I'm doing some standard image processing and resizing in `modelform_valid()` as well as cleanup
of the old image.


.. sourcecode:: python

    class NewTopic(DetailView, CreateView):
        detail_model    = Forum
        form_model      = Post
        modelform_class = PostForm
        title           = "Start New Topic"
        template_name   = "forum/post.html"

        def get_thread(self, modelform):
            title = modelform.cleaned_data.title
            return Thread.obj.create(forum=self.get_detail_object(), title=title, creator=self.user)

        def modelform_valid(self, modelform):
            """Create new thread and its first post."""
            data   = modelform.cleaned_data
            thread = self.get_thread(modelform)

            Post.obj.create(thread=thread, title=data.title, body=data.body, creator=self.user)
            self.user.profile.increment_posts()
            return redir(self.get_success_url())

        def get_success_url(self):
            return self.get_detail_object().get_absolute_url()


In this view we need to inherit from `Detail` and `Create` views, the first of which will handle
references to the current forum (url keyword arg and forum record itself as `detail_object`) and
the second will create a new `Thread` and `Post` with the associated title and body based on the
submitted form.

I'm specifying `Post` as the `form_model` because both this view and the inherited `Reply` view
listed below will create `Post` records in `modelform_valid()` -- the main difference is that
`NewTopic` will also create a new `Thread` in `get_thread().`

It's important that we use `get_detail_object()` because `detail_object` is only created on `GET`
request and we need to handle both `GET` and `POST` in this view.

.. sourcecode:: python

    class Reply(NewTopic):
        detail_model = Thread
        title        = "Reply"

        def get_thread(self, modelform):
            return self.get_detail_object()

        def get_success_url(self):
            return self.get_detail_object().get_absolute_url() + "?page=last"


Here I've changed `detail_model` to `Thread` to use in `get_thread()` and also to redirect to the
last page of the thread in `get_success_url().`

It may be a better design to have a third view to hold all of the common functionality for both
`NewTopic` and `Reply` -- this would make it easier and less error-prone to make changes to both of
them independently. If `Reply` was any more complex than it is now, that would definitely be a
good change to make.

As a general rule, it's best to avoid inheriting from a class which is used as an actual view
in your App, the only reason we can get away with it here is that `Reply` is so simple.

.. sourcecode:: python

    from dbe.shared.utils import ContainerFormMixin

    class PostForm(ContainerFormMixin, ModelForm):
        class Meta:
            model   = Post
            exclude = ["creator", "thread"]

You might have noticed that when I was working with form's `cleaned_data` in `NewTopic,` I was
accessing fields as attributes instead of as dictionary key lookup -- this is made possible by
the `ContainerFormMixin` class which wraps `cleaned_data` in a `Container` class that conveniently
exposes data as attributes.

It's a small matter but I think it makes view logic more readable in many cases.

.. sourcecode:: python

    def forum_context(request):
        return dict(media_url=MEDIA_URL)

Context processor function add context to all templates; it needs to be added to
`TEMPLATE_CONTEXT_PROCESSORS` option in your settings.py file.

Main Listing Template
---------------------

.. sourcecode:: django

    <div class="main">

        <div id="list">
        <table border="0" cellpadding="4" width="100%">
            <tr>
                <td></td>
                <td>Posts</td>
                <td>Last post</td>
                <td></td>
            </tr>

            <!-- List of forums -->

            {% for forum in forum_list %}
            <tr {% if forloop.last %}class="last"{% endif %}>
                <td>
                    <div class="title"><a href="{% url 'forum' dpk=forum.pk %}">{{ forum.title }}</a></div>
                </td>
                <td>{{ forum.num_posts }}</td>
                <td>{{ forum.last_post.short|linebreaksbr }}</td>
                <td><a class="button" href="{% url 'forum' dpk=forum.pk %}">VIEW</a></td>
            </tr>

            {% endfor %}
        </div>

    </div>

The main listing template above is pretty straightforward, but there are a few things to note:
`forum_list` is automatically created by the view based on our model name (`Forum`); I'm using
`forloop.last` flag which is true on the last loop cycle to change the table row style;
`linebreaksbr` filter is used to change newlines to BR tags.

.. image:: _static/img/fl.gif
    :class: screenshot

Forum Template
--------------

.. sourcecode:: django

    <div class="main">

    <a id="new_topic" class="buttont" href="{% url 'new_topic' forum.pk %}">Start New Topic</a>
    <br /> <br />

    <div id="list">
        {% if thread_list %}
            <table border="0" cellpadding="4" width="100%">
              <tr>
                  <td>Topics</td>
                  <td>Replies</td>
                  <td>Last post</td>
                  <td></td>
              </tr>

              <!-- Threads  -->

              {% for thread in thread_list %}
              <tr {% if forloop.last %}class="last"{% endif %}>
                  <td>
                    <div class="title"><a href="{% url 'thread' thread.pk %}">{{ thread.title }}</a></div>
                  </td>
                  <td>{{ thread.num_replies }}</td>
                  <td>{{ thread.last_post.short|linebreaksbr }}</td>
                  <td><a class="button" href="{% url 'thread' thread.pk %}">VIEW</a></td>
              </tr>
              {% endfor %}

            </table>
        {% else %}
            <blockquote>No threads in this forum yet..</blockquote>
        {% endif %}
        </div>

        {% include "paginator.html" %}
    </div>

This template is very similar to the last one but we need to include the paginator at the end
and the "no threads" message.

.. image:: _static/img/ffv.gif
    :class: screenshot

Thread Template
---------------

.. sourcecode:: django

    <div class="main">

        <!-- Title and backlink -->

        <div class="ttitle">{{ thread.title }}</div>
        <div id="back">
            <a href="{% url 'forum' thread.forum.pk %}">&lt;&lt; back to list of topics</a>
        </div>


        <!-- Posts  -->

        <div id="list">
            {% for post in post_list %}
                <div class="post">

                    <!-- Profile pic and info -->

                    <div class="ppic">
                        {% with post.profile_data as pdata %}
                            {% if pdata.1 %}
                                <img src="{{ media_url }}{{ pdata.1 }}" /> <br />
                            {% endif %}
                        {{ post.creator }}<br />
                        Posts: {{ pdata.0 }}<br />
                        Joined: {{ post.creator.date_joined|date:"M d Y" }}
                        {% endwith %}
                    </div>

                    <!-- Title, author and body -->

                    <span class="title">{{ post.title }}</span><br />
                    by {{ post.creator }} | <span class="date">{{ post.created }}</span> <br /><br />

                    {{ post.body|linebreaksbr }} <br />
                    <div class="clear"></div>

                </div>
            {% endfor %}
        </div>

        <!-- Paginator and reply link -->

        {% include "paginator.html" %}
        <br />
        <a class="button" href="{% url 'reply' thread.pk %}">Reply</a>

    </div>

This template is also very straightforward; note the use of `date` filter to simplify display of
join date.

.. image:: _static/img/ftv.gif
    :class: screenshot

New Topic / Reply Template
--------------------------

.. sourcecode:: django

    <div class="main">
        <div id="reply">
        <form action="" method="POST"> {% csrf_token %}
            <table>
                {{ modelform.as_table }}
            </table>
            <input type="submit" value="Submit" />
        </form>
        </div>
    </div>

..and here is what it looks like:

.. image:: _static/img/fr.gif
    :class: screenshot


Edit Profile Template
---------------------

.. sourcecode:: django

    <div class="main">
        <div id="rtitle">Edit Profile</div><br />

        <p>
            <form enctype="multipart/form-data" action="" method="POST"> {% csrf_token %}

                {% if userprofile.avatar_image %}
                    <p><img border="0" alt="Profile Pic" src="{{ userprofile.avatar_image }}" /></p>
                {% endif %}

                {{ modelform.avatar }}
                <input type="submit" value="Submit" id="submit" />
            </form>
        </p>
    </div>

It's important to remember `enctype` form tag attribute when there is a file or image field in
the form. I'm using `userprofile` object here which is automatically added to context by the
`UpdateView` based on the model name; here is the snapshot of this view:

.. image:: _static/img/fp.gif
    :class: screenshot
