from django.conf.urls.defaults import *
from django.contrib.auth.decorators import login_required
from dbe.social.models import *
from dbe.social.views import *

urlpatterns = patterns("dbe.social.views",
    (r"^social/(?P<pk>\d+)/$"             , ForumView.as_view(), {}, "social"),
    (r"^thread/(?P<pk>\d+)/$"            , ThreadView.as_view(), {}, "thread"),
    (r"^new_topic/(\d+)/$"               , login_required(NewTopic.as_view()), {}, "new_topic"),
    (r"^reply/(\d+)/$"                   , login_required(Reply.as_view()), {}, "reply"),
    (r"^profile/(?P<pk>\d+)/$"           , login_required(EditProfile.as_view()), {}, "profile"),
    (r""                                 , Main.as_view(), {}, "social_main"),
)
