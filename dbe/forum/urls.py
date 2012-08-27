from django.conf.urls.defaults import *
from django.contrib.auth.decorators import login_required
from dbe.forum.models import *
from dbe.forum.views import *

urlpatterns = patterns("dbe.forum.views",
    (r"^forum/(?P<pk>\d+)/$"             , ForumView.as_view(), {}, "forum"),
    (r"^thread/(?P<pk>\d+)/$"            , ThreadView.as_view(), {}, "thread"),
    (r"^new_topic/(\d+)/$"               , login_required(NewTopic.as_view()), {}, "new_topic"),
    (r"^reply/(\d+)/$"                   , login_required(Reply.as_view()), {}, "reply"),
    (r"^profile/(?P<pk>\d+)/$"           , login_required(EditProfile.as_view()), {}, "profile"),
    (r""                                 , Main.as_view(), {}, "forum_main"),
)
