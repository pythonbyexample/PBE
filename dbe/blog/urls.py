from django.conf.urls.defaults import *
from dbe.blog.models import *
from dbe.blog.views import PostView, Main, ArchiveMonth

urlpatterns = patterns("dbe.blog.views",
   # (r"^post/(?P<pk>\d+)/$"           , "post", {}, "post"),
   (r"^post/(?P<pk>\d+)/$"           , PostView.as_view(), {}, "post"),
   # (r"^add_comment/(\d+)/$"          , "add_comment", {}, "add_comment"),
   (r"^delete_comment/(\d+)/$"       , "delete_comment", {}, "delete_comment"),
   (r"^delete_comment/(\d+)/(\d+)/$" , "delete_comment", {}, "delete_comment"),
   # (r"^archive_month/(\d+)/(\d+)/$"  , "archive_month", {}, "archive_month"),
   (r"^archive_month/(\d+)/(\d+)/$"  , ArchiveMonth.as_view(), {}, "archive_month"),
   (r""                              , Main.as_view(), {}, "main"),
   # (r""                              , "main", {}, "main"),
)
