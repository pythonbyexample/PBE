from django.conf.urls import *
from dbe.photo_contest.models import *
from dbe.photo_contest.views import *

urlpatterns = patterns("dbe.photo_contest.views",
   (r"^image/(?P<dpk>\d+)/"               , ImageView.as_view(), {}, "pc-image"),
   (r"^add-image/(?P<key>\w+)/"           , AddImage.as_view(), {}, "pc-add-image"),
   (r"^moderation/"                       , ModerateView.as_view(), {}, "moderation"),
   (r"^signup/"                           , SignUpView.as_view(), {}, "signup"),
   (r"^$"                                 , Main.as_view(), {}, "pc-main"),
)
