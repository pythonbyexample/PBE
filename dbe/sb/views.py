# Imports {{{
import time
from calendar import month_name

from dbe.sb.models import *
from dbe.sb.forms import *
from dbe.shared.utils import *

from dbe.mcbv.list import ListView
from dbe.mcbv.edit import CreateUpdateView
from dbe.mcbv.edit_custom import SearchFormView
from dbe.mcbv.list_custom import DetailListCreateView, ListFilterView, PaginatedSearch
# }}}


class PostView(DetailListCreateView):
    """Show post, associated comments and an 'add comment' form."""
    detail_model    = Post
    list_model      = Comment
    modelform_class = CommentForm
    related_name    = "comments"
    fk_attr         = "post"
    template_name   = "sb/post.html"


class CommentSearch2(PaginatedSearch):
    form_class               = SearchForm
    paginate_by              = 2
    list_context_object_name = "comments"
    template_name            = "csearch.html"

    def form_valid(self, form):
        q                = form.cleaned_data.q.strip()
        self.object_list = Comment.obj.filter(body__icontains=q) if q else None
        return dict(form=form)


class CommentSearch(ListFilterView):
    list_model               = Comment
    form_class               = SearchForm
    paginate_by              = 2
    start_blank              = False
    list_context_object_name = "comments"
    template_name            = "csearch.html"

    def get_query(self, q):
        return Q(body__icontains=q)


class Main(ListView):
    list_model    = Post
    paginate_by   = 10
    template_name = "sb/list.html"

    def months(self):
        """Make a list of months to show archive links."""
        if not Post.obj.count(): return list()

        # set up variables
        current_year, current_month = time.localtime()[:2]
        first       = Post.obj.order_by("created")[0]
        first_year  = first.created.year
        first_month = first.created.month
        months      = list()

        # loop over years and months
        for year in range(current_year, first_year-1, -1):
            start, end = 12, 0
            if year == current_year : start = current_month
            if year == first_year   : end = first_month - 1

            for month in range(start, end, -1):
                if Post.obj.filter(created__year=year, created__month=month):
                    months.append((year, month, month_name[month]))
        return months


class ArchiveMonth(Main):
    paginate_by = None

    def get_list_queryset(self):
        year, month = self.args
        return Post.obj.filter(created__year=year, created__month=month).order_by("created")
