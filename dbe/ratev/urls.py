from django.conf.urls.defaults import *


urlpatterns = patterns("django.views.generic.simple",
    (r"^help/$", "direct_to_template", {"template": "help.html"}),
)

urlpatterns += patterns('ratev.ratev.views',
    (r"^(artist|album|author|director)/(\d*)/$", "listitems"),
    (r"^add/(track|album|book|film)/(\d*)/$", "add"),
    (r"^add/(artist|author|director)/$", "add"),
    (r"^recommendations/$", "recommendations"),
    # (r"^updsim_secret/$", "update_similarity"),
    (r"^mkrec_secret/$", "make_recommendations"),
    (r"^stats/$", "stats"),
    (r"", "search"),
)
