from django.conf.urls import *
from dbe.cal.models import *
from dbe.cal.views import *
from django.contrib.auth.decorators import login_required

urlpatterns = patterns("dbe.cal.views",
    (r"^month/(\d+)/(\d+)/(-?1)/$" , login_required(MonthView.as_view()), {}, "month"),

    (r"^month/(\d+)/(\d+)/$"       , login_required(MonthView.as_view()), {}, "month"),
    (r"^day/(\d+)/(\d+)/(\d+)/$"   , login_required(DayView.as_view()), {}, "day"),
    (r"^settings/(?P<dpk>\d+)/$"   , login_required(SettingsView.as_view()), {}, "settings"),
    (r"^(\d+)$"                    , login_required(MainView.as_view()), {}, "main"),
    (r"^$"                         , login_required(MainView.as_view()), {}, "main"),

    # (r"^month/(\d+)/(\d+)/$", "month"),
    # (r"^month$", "month"),
    # (r"^day/(\d+)/(\d+)/(\d+)/$", "day"),
    # (r"^settings/$", "settings"),
    # (r"^(\d+)/$", "main"),
    # (r"", "main"),
)
