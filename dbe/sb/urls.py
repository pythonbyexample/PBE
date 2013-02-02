from django.conf.urls.defaults import *
from dbe.sb.models import *
from dbe.sb.views import PostView, Main, ArchiveMonth, CommentSearch

urlpatterns = patterns("dbe.sb.views",
   (r"^search/$"                      , CommentSearch.as_view(), {}, "csearch"),
   (r"^post/(?P<dpk>\d+)/$"           , PostView.as_view(), {}, "sbpost"),
   (r"^archive_month/(\d+)/(\d+)/$"   , ArchiveMonth.as_view(), {}, "archive_month"),
   (r""                               , Main.as_view(), {}, "main"),
   # (r"^delete_comment/(\d+)/$"       , "delete_comment", {}, "delete_comment"),
)
