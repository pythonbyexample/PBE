# Imports {{{
import time
from calendar import month_name

from dbe.blog.models import *
from dbe.blog.forms import *
from dbe.shared.utils import *
from dbe.classviews.list import DetailListCreateView, ListView
# }}}


class PostView(DetailListCreateView):
    """Show post, associated comments and an 'add comment' form."""
    main_model          = Post
    list_model          = Comment
    form_class          = CommentForm
    related_name        = "comments"
    context_object_name = "post"
    template_name       = "post.html"

    def get_form_kwargs(self):
        kwargs = super(PostView, self).get_form_kwargs()
        return updated(kwargs, dict( instance = Comment(post=self.get_mainobj()) ))


class Main(ListView):
    """Main listing."""
    model         = Post
    paginate_by   = 10
    template_name = "list.html"

    def mkmonth_lst(self):
        """Make a list of months to show archive links."""
        if not Post.objects.count(): return []

        # set up variables
        current_year, current_month = time.localtime()[:2]
        first       = Post.objects.order_by("created")[0]
        first_year  = first.created.year
        first_month = first.created.month
        months      = []

        # loop over years and months
        for year in range(current_year, first_year-1, -1):
            start, end = 12, 0
            if year == current_year : start = current_month
            if year == first_year   : end = first_month - 1

            for month in range(start, end, -1):
                months.append((year, month, month_name[month]))
        return months

    def get_context_data(self, **kwargs):
        c = super(Main, self).get_context_data(**kwargs)
        return updated(c, dict(months=self.mkmonth_lst()))


class ArchiveMonth(Main):
    """Monthly archive."""
    paginate_by = None

    def get_queryset(self):
        year, month = self.args
        return Post.objects.filter(created__year=year, created__month=month)

    def get_context_data(self, **kwargs):
        c = super(ArchiveMonth, self).get_context_data(**kwargs)
        return updated(c, dict(archive=True))


def delete_comment(request, post_pk, pk=None):
    """Delete comment(s) with primary key `pk` or with pks in POST."""
    if request.user.is_staff:
        pklst = [pk] if pk else request.POST.getlist("delete")
        for pk in pklst:
            Comment.objects.get(pk=pk).delete()
    return redir("post", pk=post_pk)
