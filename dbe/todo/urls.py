from django.conf.urls import *
from dbe.todo.views import *
from django.contrib.auth.decorators import login_required

urlpatterns = patterns("dbe.todo.views",
    (r"^update_item/(\d+)/(delete)/$", "update_item", {}, "update_item"),
    (r"^update_item/(\d+)/(onhold|done|progress)/(on|off|\d+)/$", "update_item", {}, "update_item"),
    (r"^update_item_detail/(?P<pk>\d+)/$", UpdateItem.as_view(), {}, "update_item_detail"),
    (r"^reminders/$", "load_reminders", {}, "reminders"),
    (r"^add-items/$", login_required(AddItems.as_view()), {}, "add_items"),
)
