Django Tutorial: Calendar App - Part III
----------------------------------------

Alerts
======

The next feature I'll add will be a sidebar with alerts about upcoming events. For the sake of
simplicity we'll only show tomorrow's and today's events, but it'd be very easy to make this a
configurable setting.

Since we would like to see the alerts on all pages, I'll add the sidebar to `base.html` template;
our function will be `reminders()` and it will be called in both yearly and monthly view:

.. sourcecode:: python

    def reminders(request):
        """Return the list of reminders for today and tomorrow."""
        year, month, day = time.localtime()[:3]
        reminders = Entry.objects.filter(date__year=year, date__month=month,
                                       date__day=day, creator=request.user, remind=True)
        tomorrow = datetime.now() + timedelta(days=1)
        year, month, day = tomorrow.timetuple()[:3]
        return list(reminders) + list(Entry.objects.filter(date__year=year, date__month=month,
                                       date__day=day, creator=request.user, remind=True))


We're using `timedelta()` again to find out tomorrow's date; `list()` function is a Python
built-in that converts querysets to simple lists because querysets can't be added to one another
otherwise. In `main()` function, reminders have to be passed on to the template:

.. sourcecode:: python

    return render_to_response("cal/main.html", dict(years=lst, user=request.user, year=year,
                                                   reminders=reminders(request)))

Add the same change to `month()`, as well, and add the following section to `base.html`:

.. sourcecode:: django

    {% if reminders %}
    <div class="reminders">
        <div class="gr">Alerts</div>
        {% for reminder in reminders %}<p> {{ reminder.short|safe }}</p>
        {% endfor %}
    </div>
    {% endif %}

I checked the remind box in tomorrow's entry and here it is, in huge red letters!

.. image:: _static/c5.png

Settings Page
=============

The next feature I'd like to add is a very simple settings screen with just a single option:
whether to show other users' events or not. The url, function and template will all be called `settings`:

.. sourcecode:: python

    (r"^settings/$", "settings"),

.. sourcecode:: python

    def _show_users(request):
        """Return show_users setting; if it does not exist, initialize it."""
        s = request.session
        if not "show_users" in s:
            s["show_users"] = True
        return s["show_users"]

    @login_required
    def settings(request):
        """Settings screen."""
        s = request.session
        _show_users(request)
        if request.method == "POST":
            s["show_users"] = (True if "show_users" in request.POST else False)
        return render_to_response("cal/settings.html", add_csrf(request, show_users=s["show_users"]))

The setting will be stored in user's session; I have added a small utility function that will set
`show_users` the first time it's called. In `settings()` I'm using a Python construct you may be
unfamiliar with: `myvar = x if <condition> else y`. Brackets are optional; I find the construct
very expressive and handy but an `if/else` block would work just as well.

The template is almost too easy:

.. sourcecode:: django

    <h4>Settings</h4>
    <form action="" method="POST"> {% csrf_token %}
    Show other users' entries:
        <input type="checkbox" name="show_users" {% if show_users %}checked{% endif %} />
    <input type="submit" value="Save" />
    </form>

And, last but not least, we do need to make use of the setting in all three views we have:

.. sourcecode:: python

    # main()

    entries = Entry.objects.filter(date__year=y, date__month=n+1)
    if not _show_users(request):
        entries = entries.filter(creator=request.user)

    # month() is exactly the same!

    # day()
    other_entries = []
    if _show_users(request):
        other_entries = Entry.objects.filter(date__year=year, date__month=month,
                                       date__day=day).exclude(creator=request.user)

    return render_to_response("cal/day.html", add_csrf(request, entries=formset, year=year,
            month=month, day=day, other_entries=other_entries, reminders=reminders(request)))

In `day()` we're using `exclude()` method --- we haven't used it before --- it's similar to `filter()` except that it removes matching records from queryset.

The `other_entries` will be listed on top of the day view:

.. sourcecode:: django

    {% for entry in other_entries %}
        <div class="entry">
        {{ entry.creator }} |
        {{ entry.short|safe }}<br />
        {{ entry.body }}<br />
        </div>
    {% endfor %} <br />

We can see other users' entries because that option is on at this time:

.. image:: _static/c6.png

...and in daily view:

.. image:: _static/c7.png


Hope you liked the Calendar Tutorial. Here are some things you may want to do as an exercise: add
an option to the settings page to show the alert X days before the event; add times to events;
have an option to have more than one user associated with an event --- or think of something else
entirely!

`Download Full Sources <calsrc.tar.gz>`_
