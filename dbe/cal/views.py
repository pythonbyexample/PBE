import time
import calendar
from datetime import date, datetime, timedelta

from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, render_to_response
from django.core.context_processors import csrf
from django.forms.models import modelformset_factory
from django.template import RequestContext
from django.contrib.auth.models import User

from dbe.cal.models import *
from dbe.cal.forms import *
from dbe.mcbv.edit import FormView
from dbe.mcbv.base import TemplateView

month_names = list(calendar.month_name)


def _show_users(request):
    return request.session.setdefault("show_users", True)

@login_required
def settings(request):
    """Settings screen."""
    s = request.session
    _show_users(request)
    if request.method == "POST":
        s["show_users"] = (True if "show_users" in request.POST else False)
    return render_to_response("cal/settings.html", add_csrf(request, show_users=s["show_users"]))

class SettingsView(UpdateRelatedView):
    detail_model  = User
    form_model    = Settings
    form_class    = SettingsForm
    related_name  = "settings"
    fk_attr       = "user"
    template_name = "settings.html"


def reminders(request):
    """Return the list of reminders for today and tomorrow."""
    year, month, day = time.localtime()[:3]
    reminders = Entry.objects.filter(date__year=year, date__month=month,
                                   date__day=day, creator=request.user, remind=True)
    tomorrow = datetime.now() + timedelta(days=1)
    year, month, day = tomorrow.timetuple()[:3]
    return list(reminders) + list(Entry.objects.filter(date__year=year, date__month=month,
                                   date__day=day, creator=request.user, remind=True))

class MainView(TemplateView):
    """Main listing, years and months; three years per page."""
    template_name = "cal/main.html"

    def add_context(self):
        localtime = time.localtime()
        start_year = first(self.args, default=localtime[0])

        nowy, nowm = localtime[:2]
        years = []

        # create a list of months for each year, indicating ones that contain entries and current
        for year in (start_year, start_year+1, start_year+2):
            months = []
            for n, month in enumerate(month_names)[1:]:
                entries = Entry.obj.filter(date__year=year, date__month=n)
                if not _show_users(self.request):
                    entries = entries.filter(creator=self.user)

                current = bool(y == nowy and n == nowm)   # current month
                months.append(dict(n=n, name=month, entries=enties, current=current))
            years.append((year, months))

        return dict(years=years, year=start_year, reminders=reminders(request))


class MonthView(TemplateView):
    template_name = "cal/month.html"

    def month(self):
        """Listing of days in `month`."""
        year, month = self.args
        change      = self.kwargs.get("change")

        # apply next / previous change
        if change:
            now, mdelta = date(year, month, 15), timedelta(days=30)
            newdate     = now + change*mdelta
            year, month = newdate.timetuple()[:2]

        # init variables
        cal = calendar.Calendar()
        month_days = cal.itermonthdays(year, month)
        cur_year, cur_month, cur_day = time.localtime()[:3]
        days = [[]]
        week = 0

        # make month lists containing list of days for each week
        # each day tuple will contain list of entries and 'current' indicator
        for day in month_days:
            entries = current = False   # are there entries for this day; current day?
            if day:
                entries = Entry.obj.filter(date__year=year, date__month=month, date__day=day)
                if not _show_users(self.request):
                    entries = entries.filter(creator=self.user)
                if day == cur_day and year == cur_year and month == cur_month:
                    current = True

            days[week].append((day, entries, current))
            if len(days[week]) == 7:
                days.append([])
                week += 1

        return dict(year=year, month=month, month_days=days, mname=month_names[month],
                    reminders=reminders(self.request))

@login_required
def day(request, year, month, day):
    """Entries for the day."""
    EntriesFormset = modelformset_factory(Entry, extra=1, exclude=("creator", "date"),
                                          can_delete=True)
    other_entries = []
    if _show_users(request):
        other_entries = Entry.objects.filter(date__year=year, date__month=month,
                                       date__day=day).exclude(creator=request.user)

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
            month=month, day=day, other_entries=other_entries, reminders=reminders(request)))


def add_csrf(request, **kwargs):
    """Add CSRF and user to dictionary."""
    d = dict(user=request.user, **kwargs)
    d.update(csrf(request))
    return d
