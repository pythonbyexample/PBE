Django Tutorial: Calendar App - Part II
---------------------------------------

Monthly View
============

Let's go ahead and add monthly view, with url, function and template all named `month`. The
`urlconf` lines and the function should be:

.. sourcecode:: python

    (r"^month/(\d+)/(\d+)/(prev|next)/$", "month"),
    (r"^month/(\d+)/(\d+)/$", "month"),
    (r"^month$", "month"),

.. sourcecode:: python

    from datetime import date, datetime, timedelta
    import calendar

    @login_required
    def month(request, year, month, change=None):
        """Listing of days in `month`."""
        year, month = int(year), int(month)

        # apply next / previous change
        if change in ("next", "prev"):
            now, mdelta = date(year, month, 15), timedelta(days=31)
            if change == "next":   mod = mdelta
            elif change == "prev": mod = -mdelta

            year, month = (now+mod).timetuple()[:2]

        # init variables
        cal = calendar.Calendar()
        month_days = cal.itermonthdays(year, month)
        nyear, nmonth, nday = time.localtime()[:3]
        lst = [[]]
        week = 0

        # make month lists containing list of days for each week
        # each day tuple will contain list of entries and 'current' indicator
        for day in month_days:
            entries = current = False   # are there entries for this day; current day?
            if day:
                entries = Entry.objects.filter(date__year=year, date__month=month, date__day=day)
                if day == nday and year == nyear and month == nmonth:
                    current = True

            lst[week].append((day, entries, current))
            if len(lst[week]) == 7:
                lst.append([])
                week += 1

        return render_to_response("cal/month.html", dict(year=year, month=month, user=request.user,
                            month_days=lst, mname=mnames[month-1]))

In order to change the month display to next/previous months, we're using an optional function
argument `change` and `timedelta()` function of `datetime` module, which lets you add or subtract periods
of time. Once you do that, you will end up with another datetime object that has a `timetuple()`
method that returns time in the same format as `time.localtime()`.

In the next code block we take advantage of Python's `calendar` module --- specifically its
`itermonthdays()` method which returns a list of all days in a month, conveniently padding both
beginning and ending weeks with zeroes, so that a month that starts on Wednesday will return
`0,0,1,2,3,4,5,...`.

We could split the month into separate weeks in the template but I find it easier and clearer to
handle this type of manipulations in Python code.

In this template I will use a `table` element because the table cells will need to expand to
show any number of entries:

.. sourcecode:: django

    <a href= "{% url cal.views.month year month "prev" %}">&lt;&lt; Prev</a>
    <a href= "{% url cal.views.month year month "next" %}">Next &gt;&gt;</a>

    <h4>{{ mname }} {{ year }}</h4>

    <div class="month">
        <table>

        <tr>
            <td class="empty">Mon</td>
            <td class="empty">Tue</td>
            <td class="empty">Wed</td>
            <td class="empty">Thu</td>
            <td class="empty">Fri</td>
            <td class="empty">Sat</td>
            <td class="empty">Sun</td>
        </tr>

        {% for week in month_days %}
            <tr>
            {% for day, entries, current in week %}

                <!-- TD style: empty | day | current; onClick handler and highlight  -->
                <td class= {% if day == 0 %}"empty"{% endif %}
                {% if day != 0 and not current %}"day"{% endif %} 
                {% if day != 0 and current %}"current"{% endif %}
                {% if day != 0 %}
                    onClick="parent.location='{% url cal.views.day year month day %}'"
                    onMouseOver="this.bgColor='#eeeeee';"
                    onMouseOut="this.bgColor='white';"
                {% endif %} >

                <!-- Day number and entry snippets -->
                {% if day != 0 %}
                    {{ day }}
                    {% for entry in entries %}
                        <br />
                        <b>{{ entry.creator }}</b>: {{ entry.short|safe }}
                    {% endfor %}
                {% endif %}
                </td>
            {% endfor %}
            </tr>
        {% endfor %}
        </table>

        <div class="clear"></div>
    </div>

As you can see I have used Javascript `onClick` method to be able to click anywhere in a day's
table cell. Notice that we can use `url` tag to insert the link just like we do with `href` tags.
We need to use `safe` filter to let Django display HTML markup in the entry listing.

The screenshot shows the current day highlight (Sunday) and two entries:

.. image:: _static/c3.png

Looks really nice, doesn't it? The next thing we'll add is the daily view.

Day View
========

The day view will display forms to edit existing entries and a single blank form for new entries.
The url, template and function will all be called `day`. I'm not going to add next/previous links
to keep things simple but that's something you can certainly do yourself as an excercise. Copy the
following code to your `urlconf` file and `views` file:

.. sourcecode:: python

    (r"^day/(\d+)/(\d+)/(\d+)/$", "day"),

.. sourcecode:: python

    from django.core.urlresolvers import reverse
    from django.core.context_processors import csrf
    from django.forms.models import modelformset_factory

    @login_required
    def day(request, year, month, day):
        """Entries for the day."""
        EntriesFormset = modelformset_factory(Entry, extra=1, exclude=("creator", "date"),
                                              can_delete=True)

        if request.method == 'POST':
            formset = EntriesFormset(request.POST)
            if formset.is_valid():
                # add current user and date to each entry & save
                entries = formset.save(commit=False)
                for entry in entries:
                    entry.creator = request.user
                    entry.date = date(int(year), int(month), int(day))
                    entry.save()
                return HttpResponseRedirect(reverse("dbe.cal.views.month", args=(year, month)))

        else:
            # display formset for existing enties and one extra form
            formset = EntriesFormset(queryset=Entry.objects.filter(date__year=year,
                date__month=month, date__day=day, creator=request.user))
        return render_to_response("cal/day.html", add_csrf(request, entries=formset, year=year,
                month=month, day=day))


    def add_csrf(request, ** kwargs):
        """Add CSRF and user to dictionary."""
        d = dict(user=request.user, ** kwargs)
        d.update(csrf(request))
        return d

A lot of things are going on here --- let's look at them one by one. First I've created a
modelformset factory based on the `Entry` model. The `extra=1` and `can_delete` options show one
empty form for adding entries and display a checkbox to delete an entry. Next I handle formset
submission which works very similar to form submissions we've done before; I have used `commit=False`
argument to get at `entries` list without committing to the database and then I assign current
user and day to each entry before saving it.

Finally, we create a formset from a queryset filtered by year, month, day, and creator --- since
we only want to let users edit their own entries (although we'll still show other users' entries,
more on that below).

The template is short and easy:

.. sourcecode:: django

    <h4>My Entries</h4>
    <form action="{% url cal.views.day year month day %}" method="POST"> {% csrf_token %}

    {{ entries.management_form }}

    {% for entry in entries.forms %}
        {{ entry.id }}
        <div class="entry">
            <div class="del">Delete {{ entry.DELETE }}</div>
            <div id="inp1">
                <p>Title: {{ entry.title }}</p>
                <p>Snippet: {{ entry.snippet }}</p>
            </div>
            <p>Remind: {{ entry.remind }}</p>
            {{ entry.body }}
        </div>
    {% endfor %}

    <input type="submit" value="Save" /> </form>

Existing entry is on top and a blank form below:

.. image:: _static/c4.png

When displaying formsets manually, you must always include `formset.management_form` and `form.id`
as shown above. If you let Django handle formset rendering by using `{{ entries }}`, that would
not be necessary but you'll probably find Django's autmatic formatting inadequate for most needs.

Notice that we use the `DELETE` property to display the deletion checkbox --- this is not
described in the Django Docs so make a note of how that's done. Normally you'd also want to
display possible errors next to each field, but to keep things simple I won't do that; the only
thing that can be wrong here is a missing title, and the users should hopefully be able to figure
that one out.

`Continue to part III <cal3.html>`_
