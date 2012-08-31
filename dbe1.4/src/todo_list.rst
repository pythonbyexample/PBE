
Todo List Part I
----------------

We'll start by making a simple todo list manager app and then adding some bells and whistles and
finally, multi-user functionality.

For initial setup and configuration, please refer to the
`Official Django tutorial <http://docs.djangoproject.com/en/1.2/intro/tutorial01/#intro-tutorial01>`_.
To keep things short, I won't repeat anything already explained in the tutorial.

Defining the Model
==================

As always in Django apps, we'll start by defining a model (in todo/models.py):

.. sourcecode:: python

    from django.db.models import *

    class Item(Model):
        name       = CharField(max_length=60)
        created    = DateTimeField(auto_now_add=True)
        priority   = IntegerField(default=0)
        difficulty = IntegerField(default=0)
        done       = BooleanField(default=False)


and admin class in admin.py:

.. sourcecode:: python

    from django.db.models import *

    class ItemAdmin(admin.ModelAdmin):
        list_display  = "name priority difficulty created done".split()
        search_fields = ["name"]

    site.register(Item, ItemAdmin)

and now we can run: `manage.py syncdb; manage.py runserver`

If you browse to `http://localhost:8000/admin/`, you'll be able to add todo items, sort them by
name, priority, difficulty, created time, active/done status and search by name. That's a pretty
impressive amount of functionality for a few lines of code!

There is one small nit to pick here, and, if we want to go beyond a toy example app and into
"useful in real world" territory, we must pick it. Often you might need to add more than a couple
of items at a time; while you can do that with current UI using "save and add another" button,
it's really a hassle.

Adding Multiple Items
=====================

As you know from the Django Tutorial, it's possible to use inline forms in order to add multiple
items that will be associated with another set of objects. How does that help us? --- we don't have
any other set of objects, just our todo items. We'll have to resort to a slightly *hacky*
solution and create a separate model for date-time values; our todo items will be associated with
them and we'll be able to add a bunch at a time:

.. sourcecode:: python

    class DateTime(Model):
        datetime = DateTimeField(auto_now_add=True)

        def __unicode__(self):
            return unicode(self.datetime)

    class Item(Model):
        name       = CharField(max_length=60)
        created    = ForeignKey(DateTime)
        priority   = IntegerField(default=0)
        difficulty = IntegerField(default=0)
        done       = BooleanField(default=False)


.. in admin.py:

.. sourcecode:: python

    class ItemAdmin(ModelAdmin):
        list_display  = "name priority difficulty created done".split()
        search_fields = ["name"]

    class ItemInline(TabularInline):
        model = Item

    class DateAdmin(ModelAdmin):
        list_display = ["datetime"]
        inlines = [ItemInline]

    site.register(Item, ItemAdmin)
    site.register(DateTime, DateAdmin)

This changes our table layout and we'll have to ask Django to reset and recreate tables:

.. sourcecode:: sh

    manage.py reset todo; manage.py syncdb

The inlines are explained in some detail in the Django Tutorial --- I hope you did not miss that
part.  Now we can add a date-time and it will give us a neat, easy interface to add multiple todo
items:

.. image:: _static/tl1.png

Generally, when you have a ForeignKey relationship that needs to be listed in a table in the
Admin, the model class has to have a `__unicode__()` method as shown above in the DateTime class.
Otherwise you'd just see a "DateTime object" in that field --- not very helpful!

Now we need to take care of two small but important usability details: first, in our todo list
view, we need to have a link for adding items using the new method; second, we need to
automatically go back to our listing afterwards.

Customizing Model Template
==========================

You'll first need to locate your Django root directory and copy default Admin templates:

.. sourcecode:: sh

    cp -r django/contrib/admin/templates/admin/ dbe/templates/

You'll need to modify the command depending on where your django installation is located; in a
typical Ubuntu installation django will be in `/usr/local/lib/python2.7/dist-packages/django/`.

Django Admin allows us to specify a custom template for each model. The template is used to show a
list of items. That's exactly where we need our link.

.. sourcecode:: sh

    cd templates
    mkdir -p todo/item
    cp change_list.html todo/item/

Edit the file you copied and add the link right after `{% block content %}`:

.. sourcecode:: sh

    {% block content %}
    <a href="{% url admin:todo_datetime_add %}">Add Todo items</a>

You should use this link when adding items instead of default Django `add item` button, because
the former will add `created` time automatically.

Make sure it's not *before* `{% block content %}` --- that's a common mistake: in derived Django
templates, anything outside of blocks simply won't show up at all, which can lead to much
confusion.

Changing Save Redirect
======================

The next tweak is a bit more complicated --- we'll need to take a chunk of code from one of the
Admin modules (`contrib/admin/options.py`) and add it to `DateAdmin` in `admin.py`. The actual
modification is rather simple, though: we'll change the "item was added" message, set our redirect
at the end to point to `/admin/dbe/item/` and import a few modules that are used in the function.

.. sourcecode:: python

    from django.utils.translation import ugettext as _
    from django.utils.encoding import force_unicode
    from django.http import HttpResponse, HttpResponseRedirect
    from django.core.urlresolvers import reverse

    class DateAdmin(ModelAdmin):
        list_display = ["datetime"]
        inlines = [ItemInline]

        def response_add(self, request, obj, post_url_continue='../%s/'):
            """ Determines the HttpResponse for the add_view stage.  """
            opts = obj._meta
            pk_value = obj._get_pk_val()

            msg = "Item(s) were added successfully."
            # Here, we distinguish between different save types by checking for
            # the presence of keys in request.POST.
            if request.POST.has_key("_continue"):
                self.message_user(request, msg + ' ' + _("You may edit it again below."))
                if request.POST.has_key("_popup"):
                    post_url_continue += "?_popup=1"
                return HttpResponseRedirect(post_url_continue % pk_value)

            if request.POST.has_key("_popup"):
                return HttpResponse(
                  '<script type="text/javascript">opener.dismissAddAnotherPopup(window, "%s", "%s");'
                  '</script>' % (escape(pk_value), escape(obj)))
            elif request.POST.has_key("_addanother"):
                self.message_user(request, msg + ' ' + (_("You may add another %s below.") %
                                                        force_unicode(opts.verbose_name)))
                return HttpResponseRedirect(request.path)
            else:
                self.message_user(request, msg)

                return HttpResponseRedirect(reverse("admin:todo_item_changelist"))

The above code looks like too much trouble for a simple change but the only part we really care
about here is the last line and the "item was added" message, because stock message would tell us
DateTime was added and give us too much information about DateTimes we don't really need.

At this point we're pushing outside the scope of Admin --- at least, it's obvious that Admin was not
designed to make this sort of modification easy or obvious. The only way to know how to do this
type of Admin tweaks is to google for it or, failing that, peruse Admin source code itself, which
isn't very large or intimidating once you spend a bit of time with it.

Still, with relatively little code written we have a pretty capable little todo manager.

Marking task as Done
====================

Let's not stop here --- what else can we improve? How about marking a task as "Done" in change
list?

We need to add a function to views.py where we get the item object and set the `done` field:

.. sourcecode:: python

    from dbe.todo.models import *
    from django.core.urlresolvers import reverse
    from django.contrib.admin.views.decorators import staff_member_required

    @staff_member_required
    def mark_done(request, pk):
        item = Item.objects.get(pk=pk)
        item.done = True
        item.save()
        return HttpResponseRedirect(reverse("admin:todo_item_changelist"))

Corresponding url in urls.py:

.. sourcecode:: python

        (r"^mark_done/(\d*)/$", "dbe.todo.views.mark_done", {}, "mark_done"),

... and finally the link in our change list:

.. sourcecode:: python

    class Item(Model):
        # [...]

        def mark_done(self):
            return "<a href='%s'>Done</a>" % reverse("mark_done", args=[self.pk])
        mark_done.allow_tags = True

Make a note of how we set the `allow_tags` property --- it's documented in Django's Admin docs,
along with many other useful method properties. This property allows us to use html tags in
returned strings.

Customizing DateTime
====================

I just noticed that our DateTime insists on showing us microseconds.. we don't care about that and
it takes up too much screen space; once we're at it, let's also get rid of seconds:

.. sourcecode:: python

    def __unicode__(self):
        return unicode(self.datetime.strftime("%b %d, %Y, %I:%M %p"))

DateTime field will now have the following format: `Jun 30, 2010, 05:05 PM`.

To put two finishing touches, I'll add filters and a link to delete an item quickly, just like
we did with "mark done".

A good exercise for you would be to add the OnHold property. It'll work exactly like "Done"
property except for link toggling On/Off hold. (Don't forget that you'll need to reset the tables
and do `syncdb` after adding a model property as we did above!)

Here's what your UI should look like:

.. image:: _static/tl2.png

Adding Users
============

The next feature will be associating users with tasks. We'll need to add the user property:

.. sourcecode:: python

    from django.contrib.auth.models import User

        # in Item:

        user = ForeignKey(User, blank=True, null=True)

We're setting blank and null because we want to be able to save items without specifying any user.
After DateTime object is saved, right before the redirect, we'll check if `user` is blank and set
it to the current user (the following code goes into response_add() in DateAdmin class):

.. sourcecode:: python

    for item in Item.objects.filter(created=obj):
        if not item.user:
            item.user = request.user
            item.save()
    return HttpResponseRedirect(reverse("admin:todo_item_changelist"))

I hope you'll be impressed how easy it is to add progress bars (this code is in Item class):

.. sourcecode:: python

    progress = models.IntegerField(default=0)

    def progress_(self):
        return "<div style='width: 100px; border: 1px solid #ccc;'>" + \
          "<div style='height: 4px; width: %dpx; background: #555; '></div></div>" % self.progress
    progress_.allow_tags = True

It would be a little cleaner to have a `progress()` function and use a different name for the
property, but I have already reset tables and re-created data before I noticed. Here's our
finished UI:

.. image:: _static/tl3.png

Tada! We made it! (Actually, I made it.)

There is a tiny optimization I've added: noticing that our view functions are almost the same, I
joined them together:

.. sourcecode:: python

    from django.http import HttpResponseRedirect, HttpResponse
    from django.contrib.admin.views.decorators import staff_member_required

    @staff_member_required
    def update_item(request, pk, mode=None, action=None):
        """Toggle Done / Onhold on/off or delete an item."""
        item = Item.objects.get(pk=pk)
        if mode == "delete":
            Item.objects.filter(pk=pk).delete()
        else:
            if mode == "progress" : val = int(action)
            else                  : val = (action=="on")
            setattr(item, mode, val)
            item.save()
        return HttpResponseRedirect(reverse("admin:todo_item_changelist"))


As you can see, we're using `staff_member_required` decorator to make sure only authorized users
can delete or change status of items.

We're also handling all types of updates in the same function since the amount of code is pretty
small.

Url dispatch file has to be updated as follows, now using two separate url lines for deletion and
update. Using regular expressions for mode and action, we can accomodate both simple on/off update
and a numerical update for progress. Note how we're enclosing `delete` mode, even though it's the
only choice on that url line, to make sure it's passed on to the function.

If this seems a bit too complicated, it might work better for you if you split the view into three
functions, one to delete, one to set progress, and the last to toggle onhold/done. Ideally, you
want to end up with code that's easy for you to modify, update and reuse on other sites.

.. sourcecode:: python

    (r"^update_item/(\d+)/(delete)/$", "update_item", {}, "update_item"),
    (r"^update_item/(\d+)/(onhold|done|progress)/(on|off|\d+)/$", "update_item", {}, "update_item"),


`Continue to part II <todo_list2.html>`_.



