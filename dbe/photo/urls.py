from django.conf.urls.defaults import *
from dbe.photo.models import *
from dbe.photo.views import *

urlpatterns = patterns("dbe.photo.views",
   # (r"^search/$", "search"),
   (r"^search/"                          , SearchView.as_view(), {}, "search"),
   (r"^album/(?P<pk>\d+)/(?P<show>\S+)/" , AlbumView.as_view(), {}, "album"),
   (r"^album/(?P<pk>\d+)/"               , AlbumView.as_view(), {}, "album"),
   (r"^image/(?P<pk>\d+)/"               , ImageView.as_view(), {}, "image"),
   (r""                                  , Main.as_view(), {}, "main"),
)
