
Django Tutorial: Calendar App - Part I
--------------------------------------

Today we'll look at making a Calendar App. It will feature yearly, monthly, daily views; adding
notes to dates, a settings screen, shared views for multiple users, and alerts for upcoming
events; on the technical side, we'll learn how to use formsets based on models. I hope you can
think of a few things to add to the list of features as an exercise for yourself; I'll throw in a
few ideas at the end.

Defining the Model
==================

Let's start by defining the model class (in `cal/models.py`) --- this time around the model is quite
simple:

.. sourcecode:: python

    from django.db import models
    from django.contrib.auth.models import User
    from django.contrib import admin


    class Entry(models.Model):
        title = models.CharField(max_length=40)
        snippet = models.CharField(max_length=150, blank=True)
        body = models.TextField(max_length=10000, blank=True)
        created = models.DateTimeField(auto_now_add=True)
        date = models.DateField(blank=True)
        creator = models.ForeignKey(User, blank=True, null=True)
        remind = models.BooleanField(default=False)

        def __unicode__(self):
            if self.title:
                return unicode(self.creator) + u" - " + self.title
            else:
                return unicode(self.creator) + u" - " + self.snippet[:40]

        def short(self):
            if self.snippet:
                return "<i>%s</i> - %s" % (self.title, self.snippet)
            else:
                return self.title
        short.allow_tags = True

        class Meta:
            verbose_name_plural = "entries"


    ### Admin

    class EntryAdmin(admin.ModelAdmin):
        list_display = ["creator", "date", "title", "snippet"]
        list_filter = ["creator"]

    admin.site.register(Entry, EntryAdmin)

I have used the `verbose_name_plural` attribute to change the link to the list of entries in the
Admin --- otherwise Django tacks an 's' to make a plural, ending up with "Entrys".

As always, you should run `manage.py syncdb; manage.py runserver` to add tables and start Django.

Yearly View
===========

Let's go ahead and add the first view --- it will display three years, starting with current, with a
list of months for each year. The url, function and template will all be called `main`. Here are
the `urlconf` lines and the function code:

.. sourcecode:: python

    (r"^(\d+)/$", "main"),
    (r"", "main"),

.. sourcecode:: python

    import time
    from django.contrib.auth.decorators import login_required
    from django.http import HttpResponseRedirect, HttpResponse
    from django.shortcuts import get_object_or_404, render_to_response

    from dbe.cal.models import *

    mnames = "January February March April May June July August September October November December"
    mnames = mnames.split()


    @login_required
    def main(request, year=None):
        """Main listing, years and months; three years per page."""
        # prev / next years
        if year: year = int(year)
        else:    year = time.localtime()[0]

        nowy, nowm = time.localtime()[:2]
        lst = []

        # create a list of months for each year, indicating ones that contain entries and current
        for y in [year, year+1, year+2]:
            mlst = []
            for n, month in enumerate(mnames):
                entry = current = False   # are there entry(s) for this month; current month?
                entries = Entry.objects.filter(date__year=y, date__month=n+1)

                if entries:
                    entry = True
                if y == nowy and n+1 == nowm:
                    current = True
                mlst.append(dict(n=n+1, name=month, entry=entry, current=current))
            lst.append((y, mlst))

        return render_to_response("cal/main.html", dict(years=lst, user=request.user, year=year,
                                                       reminders=reminders(request)))

The `enumerate()` function returns month numbers starting with `0`; since all Python modules
dealing with dates count months from `1`, we need to increment `n` everywhere.

Our template will contain links to previous and next three years; starting year will be passed as
an optional argument. We are creating a dictionary for each month, containing month number, name,
whether it is current month and whether there are entries in it.

Let's look at the template:

.. sourcecode:: django

    {% extends "cal/base.html" %}
    <!-- ... -->

    <a href="{% url cal.views.main year|add:'-3' %}">&lt;&lt; Prev</a>
    <a href="{% url cal.views.main year|add:'3' %}">Next &gt;&gt;</a>

        {% for year, months in years %}
            <div class="clear"></div>
            <h4>{{ year }}</h4>
            {% for month in months %}
                <div class=
                {% if month.current %}"current"{% endif %}
                {% if not month.current %}"month"{% endif %} >
                    {% if month.entry %}<b>{% endif %}
                    <a href="{% url cal.views.month year month.n %}">{{ month.name }}</a>
                    {% if month.entry %}</b>{% endif %}
                </div>

                {% if month.n == 6 %}<br />{% endif %}
            {% endfor %}
        {% endfor %}

I'm using `base.html` as the base template for the site --- I won't show it here because it's almost
the same as the ones we used in other tutorials.

The `next` and `prev` links make use of the `add` filter, which, (with some ingenuity), can also
be used to subtract!  Notice how we use the `if` tags to apply different styles to the same `DIV`
element.  Months that contain entries will be shown in bold; current month will have a light
yellow background. I've used `float: left` css style to line up the months. Take a look:

.. image:: _static/c1.png

After clicking `Prev`:

.. image:: _static/c2.png


`Continue to part II <cal2.html>`_
