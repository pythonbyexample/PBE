Blog
====


This tutorial will demonstrate how to create a Blog app in Django using mcbv (modular CBVs)
library.

You can view or download the code here:

https://github.com/akulakov/django/tree/master/dbe/

I will focus on the important parts of code in the listings below; I recommend opening the
source files in a separate window to see import lines and other details.


Models
------

I'll start by defining model classes for a blog post and a comment:

.. sourcecode:: python

    notify = False

    class Post(BaseModel):
        title   = CharField(max_length=60)
        body    = TextField()
        created = DateTimeField(auto_now_add=True)

        class Meta:
            ordering = ["-created"]

        def __unicode__(self):
            return self.title


    class Comment(BaseModel):
        author  = CharField(max_length=60, blank=True)
        body    = TextField()
        post    = ForeignKey(Post, related_name="comments",  blank=True, null=True)
        created = DateTimeField(auto_now_add=True)

        def __unicode__(self):
            return u"%s: %s" % (self.post, self.body[:60])

        def save(self, *args, **kwargs):
            """Email when a comment is added."""
            if notify:
                tpl            = "Comment was was added to '%s' by '%s': \n\n%s"
                message        = tpl % (self.post, self.author, self.body)
                from_addr      = "no-reply@mydomain.com"
                recipient_list = ["myemail@mydomain.com"]

                send_mail("New comment added", message, from_addr, recipient_list)
            super(Comment, self).save(*args, **kwargs)


The `save()` method shows how to send an email notification. If you wish to toggle the `notify`
setting without restarting the server, you can also create a Settings model and move the `notify`
option there as a boolean field.

Let's add the views for the main listing, archive listing and the individual post view.

The main listing will show 10 most recent posts, with the last one on top and archive links in
a box on top of the page and with pagination links on the bottom.

The archive listing is similar but the posts will be shown in order of creation (with earliest
post on top), and will have no pagination because the number of posts per month isn't very
large, hopefully!

Finally the post view will show the post itself, a list of comments and a form to add a new comment.

I'm inheriting all three views from mcbv class-based views: `ListView` and `DetailListCreateView.`


PostView
--------

.. sourcecode:: python

    from dbe.mcbv.list_custom import DetailListCreateView

    class PostView(DetailListCreateView):
        """Show post, associated comments and an 'add comment' form."""
        detail_model    = Post
        list_model      = Comment
        modelform_class = CommentForm
        related_name    = "comments"
        fk_attr         = "post"
        template_name   = "blog/post.html"


The `DetailListCreateView` needs to specify the detail model, list model and the modelform used
to create a new record, as well as relation field names.

The `related_name` setting needs to be the same as in Comment.post model field.

The `fk_attr` setting is used to save the detail object (Post) as the foreign key relation on the
newly created comment.

Main
----

.. sourcecode:: python

    from dbe.mcbv.list import ListView

    class Main(ListView):
        list_model    = Post
        paginate_by   = 10
        template_name = "blog/list.html"

        def months(self):
            """Make a list of months to show archive links."""
            if not Post.obj.count(): return list()

            # set up variables
            current_year, current_month = time.localtime()[:2]
            first       = Post.obj.order_by("created")[0]
            first_year  = first.created.year
            first_month = first.created.month
            months      = list()

            # loop over years and months
            for year in range(current_year, first_year-1, -1):
                start, end = 12, 0
                if year == current_year : start = current_month
                if year == first_year   : end = first_month - 1

                for month in range(start, end, -1):
                    if Post.obj.filter(created__year=year, created__month=month):
                        months.append((year, month, month_name[month]))
            return months



The mcbv `ListView` is similar to generic `ListView` but the model is specified with `list_model`
class attribute (to allow combining with other mcbv views).

Note that I'll be using ModelClass.obj attribute to refer to the manager for convenience --
this is inherited from `BaseModel.`

The months method is used directly from the template; it needs to go over the years and months
and assign posts to each month.

CommentForm
-----------

The comment form is a standard `ModelForm` except that I'm setting the author as Anonymous if
the author field is not filled in:

.. sourcecode:: python

    class CommentForm(ModelForm):
        class Meta:
            model = Comment
            exclude = ["post"]

        def clean_author(self):
            return self.cleaned_data.get("author") or "Anonymous"


ArchiveMonth
------------

The only two things we need in `ArchiveMonth` is to disable pagination and to get year/month from
view arguments and override sorting direction:

.. sourcecode:: python

    class ArchiveMonth(Main):
        paginate_by = None

        def get_list_queryset(self):
            year, month = self.args
            return Post.obj.filter(created__year=year, created__month=month).order_by("created")


List template
-------------

In the list template, I'll use the `ifchanged` tag to insert year labels in the sidebar; to show
posts I'll iterate over `post_list` which is automatically created by `ListView.`

.. sourcecode:: djangohtml

    <!-- SIDEBAR -->

    {% block sidebar %}
        <div id="sidebar">
            Monthly Archive
            <p>
            {% for ym in view.months %}
                {% ifchanged ym.0 %} {{ ym.0 }} <br /> {% endifchanged %}
                <a href="{% url 'archive_month' ym.0 ym.1 %}">{{ ym.2 }}</a> <br />
            {% endfor %}
            </p>
        </div>
    {% endblock %}

    <!-- LIST OF POSTS -->

    {% block content %}
        <div class="main">
                {% for post in post_list %}
                    <div class="title">{{ post.title }}</div>
                    <ul>
                        <div class="time">{{ post.created }}</div>
                        <div class="body">{{ post.body|linebreaks }}</div>
                        <div class="commentlink">
                            <a href="{% url 'post' post.pk %}">Comments ({{ post.comments.count }})</a>
                        </div>
                    </ul>
                {% endfor %}

            {% include "paginator.html" %}
        </div>
    {% endblock %}


.. image:: _static/img/bl.png
    :class: screenshot

Post template
-------------

In post template I need to show the post, the list of comments and a form to add a new comment;
note that mcbv `CreateView` form is named `modelform,` not `form.`

.. sourcecode:: djangohtml

    {% block content %}
        <div class="main">

            <div class="title">{{ post.title }}</div>
            <ul>
                <div class="time">{{ post.created }}</div>
                <div class="body">{{ post.body|linebreaks }}</div>
            </ul>

            <hr />

            {% for comment in comment_list %}
                <ul>
                    <div class="time">{{ comment.author }}</div>
                    <div class="body">{{ comment.body|linebreaks }}</div>
                </ul>
            {% endfor %}


            <div id="reply">
            <form action="" method="POST"> {% csrf_token %}
                <table>
                    {{ modelform.as_table }}
                </table>
                <input type="submit" value="Submit" />
            </form>
            </div>
        </div>
    {% endblock %}

.. image:: _static/img/bp.png
    :class: screenshot
