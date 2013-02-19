import time
import calendar
from datetime import date, datetime, timedelta

from django.contrib.auth.models import User

from dbe.cal.models import *
from dbe.cal.forms import *
from dbe.mcbv.base import TemplateView
from dbe.mcbv.edit_custom import FormView, FormSetView, UpdateRelatedView

month_names = list(calendar.month_name)


class CalMixin(object):
    def show_other_users(self):
        s = first(Settings.obj.all())
        return s.show_other_users if s else False

    def reminders(self):
        """Return the list of reminders for today and tomorrow."""
        today     = time.localtime()[:3]
        tomorrow  = datetime.now() + timedelta(days=1)
        tomorrow  = tomorrow.timetuple()[:3]
        for y,m,d in (today, tomorrow):
            yield Entry.obj.date_filter(y, m, d).filter(creator=self.user, remind=True)


class SettingsView(UpdateRelatedView):
    detail_model  = User
    form_model    = Settings
    form_class    = SettingsForm
    related_name  = "settings"
    fk_attr       = "user"
    template_name = "settings.html"


class MainView(TemplateView, CalMixin):
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
                if not self.show_other_users():
                    entries = entries.filter(creator=self.user)

                current = bool(y == nowy and n == nowm)   # current month
                months.append(dict(n=n, name=month, entries=enties, current=current))
            years.append((year, months))

        return dict(years=years, year=start_year)


class MonthView(TemplateView, CalMixin):
    template_name = "cal/month.html"

    def add_context(self):
        """Listing of weeks / days in a month."""
        year, month = self.args
        change      = self.kwargs.get("change")

        # apply next / previous change
        if change:
            mdelta      = timedelta(days=30)
            newdate     = date(year, month, 15) + change*mdelta
            year, month = newdate.timetuple()[:2]

        # init variables
        month_days = calendar.Calendar().monthdayscalendar(year, month)
        weeks      = []

        cur_year, cur_month, cur_day = time.localtime()[:3]

        # each day tuple will contain list of entries and 'current' indicator
        for week in month_days:
            days = []
            for day in week:
                entries = False
                current = bool(day == cur_day and year == cur_year and month == cur_month)

                if day:
                    entries = Entry.obj.date_filter(year, month, day)
                    if not self.show_other_users():
                        entries = entries.filter(creator=self.user)

                days.append((day, entries, current))
            weeks.append(days)

        return dict(year=year, month=month, month_days=weeks, mname=month_names[month])


class DayView(FormSetView, CalMixin):
    """ Day View
        self.args: year, month, day
    """
    formset_model      = Entry
    formset_form_class = EntryForm
    extra              = 1
    can_delete         = True
    template_name      = "cal/day.html"

    def get_formset_queryset(self):
        return self.formset_model.obj.date_filter(*self.args).filter(creator=self.user)

    def process_form(self, form):
        form.instance.update( creator=self.user, date=date(*self.args) )

    def get_success_url(self):
        return reverse2("month", self.args[0], self.args[1])

    def add_context(request):
        y, m, d       = self.args
        other_entries = []
        if self.show_other_users():
            other_entries = Entry.obj.date_filter(y, m, d).exclude(creator=request.user)
        return dict(year=y, month=m, day=d, other_entries=other_entries)
