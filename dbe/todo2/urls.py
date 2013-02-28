from django.conf.urls import *

urlpatterns = patterns("dbe.todo.views",
    (r"^update_item/(\d+)/(delete)/$", "update_item", {}, "update_item"),
    (r"^update_item/(\d+)/(onhold|done|progress)/(on|off|\d+)/$", "update_item", {}, "update_item"),
)
