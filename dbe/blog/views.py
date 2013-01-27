# Imports {{{
import time
from calendar import month_name

from dbe.blog.models import *
from dbe.blog.forms import *
from dbe.shared.utils import *

from dbe.mcbv.list import ListView
from dbe.mcbv.list_custom import DetailListCreateView
# }}}


class PostView(DetailListCreateView):
    """Show post, associated comments and an 'add comment' form."""
    detail_model               = Post
    list_model                 = Comment
    modelform_class            = CommentForm
    related_name               = "comments"
    fk_attr                    = "post"
    detail_context_object_name = "post"
    list_context_object_name   = "comments"
    template_name              = "blog/post.html"

    def get_modelform_kwargs(self):
        kwargs  = super(PostView, self).get_modelform_kwargs()
        comment = Comment(post=self.get_detail_object())
        return dict(kwargs, instance=comment)


class Main(ListView):
    """Main listing."""
    list_model    = Post
    paginate_by   = 10
    template_name = "blog/list.html"

    def mkmonth_lst(self):
        """Make a list of months to show archive links."""
        if not Post.obj.count(): return []

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
                if Post.obj.filter(created__year=year, created__month=month):
                    months.append((year, month, month_name[month]))
        return months

    def get_list_context_data(self, **kwargs):
        context = super(Main, self).get_list_context_data(**kwargs)
        return dict(context, months=self.mkmonth_lst())


class ArchiveMonth(Main):
    """Monthly archive."""
    paginate_by = None

    def get_list_queryset(self):
        year, month = self.args
        return Post.obj.filter(created__year=year, created__month=month).order_by("created")

    def get_list_context_data(self, **kwargs):
        context = super(ArchiveMonth, self).get_list_context_data(**kwargs)
        return dict(context, archive=True)


def delete_comment(request, post_pk, pk=None):
    """Delete comment(s) with primary key `pk` or with pks in POST."""
    if request.user.is_staff:
        pklst = [pk] if pk else request.POST.getlist("delete")
        for pk in pklst:
            Comment.obj.get(pk=pk).delete()
    return redir("post", pk=post_pk)
