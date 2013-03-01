from django.conf.urls import *
from dbe.books.models import *
from dbe.books.views import *

urlpatterns = patterns("dbe.books.views",
   (r"^book/(?P<dpk>\d+)/"                      , BookView.as_view(), {}, "book"),
   (r"^add-comment/(?P<dpk>\d+)/$"              , AddComment.as_view(), {}, "add_comment"),
   (r"^$"                                       , Books.as_view(), {}, "books"),
   # (r"^image/(?P<mfpk>\d+)/"              , ImageView.as_view(), {}, "image"),
   # (r"^image/"                            , ImageView.as_view(), {}, "image"),
)
