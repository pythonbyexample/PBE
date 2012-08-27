from django.conf.urls.defaults import *
from dbe.portfolio.models import *
from dbe.portfolio.views import *

urlpatterns = patterns("dbe.portfolio.views",
   (r"^group/(?P<pk>\d+)/(?P<show>\S+)/" , GroupView.as_view(), {}, "group"),
   (r"^group/(?P<pk>\d+)/"               , GroupView.as_view(), {}, "group"),
   (r"^add-images/(?P<pk>\d+)/"          , AddImages.as_view(), {}, "add_images"),
   (r"^slideshow/(?P<pk>\d+)/"           , SlideshowView.as_view(), {}, "slideshow"),
   (r"^image/(?P<pk>\d+)/"               , ImageView.as_view(), {}, "image"),
   (r""                                  , Main.as_view(), {}, "main"),
)
