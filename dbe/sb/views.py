# Imports {{{
import time
from calendar import month_name
from django.utils.html import escape

from dbe.sb.models import *
from dbe.sb.forms import *
from dbe.shared.utils import *

from dbe.mcbv.detail import DetailView
from dbe.mcbv.edit_custom import SearchFormView, CreateUpdateView, CreateView
from dbe.mcbv.list_custom import DetailListCreateView, ListFilterView, PaginatedSearch, ListView
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
    list_model    = Comment
    form_class    = SearchForm
    paginate_by   = 2
    start_blank   = False
    template_name = "csearch.html"

    def get_query(self, q):
        return Q(body__icontains=q)

    def get_list_queryset(self):
        order_by = self.request.GET.get("order_by", "period")
        return super(CommentSearch, self).get_list_queryset().order_by(order_by)


class ChatView(ListView, CreateView, DetailView):
    detail_model    = User
    list_model      = Message
    form_model      = Message
    modelform_class = MessageForm
    paginate_by     = 4
    success_url     = "#"
    template_name   = "chat.html"

    def get_list_queryset(self):
        other = self.get_detail_object()
        user  = self.user
        return Message.objects.filter( Q(sender=user, recipient=other) | Q(sender=other, recipient=user) )

    def list_get(self, request, *args, **kwargs):
        context  = super(ChatView, self).list_get(request, *args, **kwargs)
        messages = Message.obj.filter(recipient=self.user)
        if messages:
            profile = SBProfile.obj.get_or_create(user=self.user)[0]
            profile.update( last_viewed_message=first(messages) )
        return context

    def modelform_valid(self, form):
        body = escape(form.cleaned_data.get("body"))
        self.modelform_object = Message.obj.create(body=body, sender=self.user, recipient=self.get_detail_object())
        return redir(self.get_success_url())


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


def new_messages(user):
    """Return True if `user` has any new message(s)."""
    messages = Messages.obj.filter(recipient=user)
    profile  = SBProfile.obj.get_or_create(user=user)[0]
    if messages and first(messages) != profile.last_viewed_message:
        return True
