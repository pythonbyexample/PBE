from django.conf.urls.defaults import *
from dbe.sb.models import *
from dbe.sb.views import *

urlpatterns = patterns("dbe.sb.views",
   (r"^search/$"                      , CommentSearch.as_view(), {}, "csearch"),
   (r"^post/(?P<dpk>\d+)/$"           , PostView.as_view(), {}, "sbpost"),
   (r"^archive_month/(\d+)/(\d+)/$"   , ArchiveMonth.as_view(), {}, "sb_archive_month"),

   (r"^send/(?P<dpk>\d+)/$"           , SendView.as_view(), {}, "send"),
   (r"^msg/(?P<dpk>\d+)/$"            , MsgView.as_view(), {}, "msg"),
   (r"^msglist/(?P<inbox>(1|0))/$"    , MsgListView.as_view(), {}, "msglist"),

   (r"^chat/(?P<dpk>\d+)/$"           , ChatView.as_view(), {}, "chat"),
   (r""                               , Main.as_view(), {}, "main"),
   # (r"^delete_comment/(\d+)/$"       , "delete_comment", {}, "delete_comment"),
)
