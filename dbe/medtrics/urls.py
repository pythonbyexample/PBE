from django.conf.urls import *
from dbe.medtrics.views import *
from dbe.mcbv.base import TemplateView
from django.contrib.auth.decorators import login_required

urlpatterns = patterns("dbe.medtrics.views",
    (r"^$", login_required(MedForms.as_view()), {}, "medforms"),

    (r"^medform/(?P<dpk>\d+)/$",
     login_required( ViewMedForm.as_view() ), {}, "medform"),

    (r"^submissions/(?P<dpk>\d+)/$",
     login_required( FormSubmissions.as_view() ), {}, "submissions"),

    (r"^submission/(?P<dpk>\d+)/$",
     login_required( Submission.as_view() ), {}, "submission"),

    (r"^medstats/(?P<dpk>\d+)/$",
     login_required( Stats.as_view() ), {}, "medstats"),
)

urlpatterns += patterns("",
    (r"^done/$", TemplateView.as_view(template_name="medtrics/done.html"), {}, "done"),
)
