from base import View, TemplateView, RedirectView
from dates import (ArchiveIndexView, YearArchiveView, MonthArchiveView,
                                     WeekArchiveView, DayArchiveView, TodayArchiveView,
                                     DateDetailView)
from detail import DetailView
from edit import FormView, FormSetView, ModelFormSetView, CreateView, UpdateView, \
        CreateUpdateView, DeleteView
from list import ListView

__version__ = "0.3.2"

class GenericViewError(Exception):
    """A problem in a generic view."""
    pass
