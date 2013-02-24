# Imports {{{
import time
from calendar import month_name
from django.utils.html import escape

from dbe.sb.models import *
from dbe.sb.forms import *
from dbe.shared.utils import *

from dbe.mcbv.detail import DetailView
from dbe.mcbv.edit_custom import SearchFormView, CreateUpdateView, CreateView, ModelFormSetView
from dbe.mcbv.list_custom import DetailListCreateView, ListFilterView, PaginatedModelFormSetView, ListView
# }}}

####  CHAT

def sbcontext(request):
    return dict(unread=new_msgs(request.user))

def new_messages(user):
    return Message.obj.filter(recipient=user, is_read=False)


class ChatView(ListView, CreateView, DetailView):
    detail_model    = User
    list_model      = Message
    form_model      = Message
    modelform_class = MessageForm
    paginate_by     = 4
    success_url     = "#"
    template_name   = "chat.haml"

    def get_list_queryset(self):
        u = self.get_detail_object()
        return Message.obj.filter( Q(sender=self.user, recipient=u) | Q(sender=u, recipient=self.user) )

    def list_get(self, request, *args, **kwargs):
        context = super(ChatView, self).list_get(request, *args, **kwargs)
        unread  = new_messages(self.user)
        context.update( dict(unread=list(unread)) )   # need list() because next line will clear queryset
        unread.update(is_read=True)
        return context

    def modelform_valid(self, form):
        body = escape(form.cleaned_data.get("body"))
        Message.obj.create(body=body, sender=self.user, recipient=self.detail_object)
        return redir(self.success_url)


####  inbox messages (Msg model)

def new_msgs(user):
    return Msg.obj.filter(recipient=user, inbox=True, is_read=False)

class SendView(CreateView, DetailView):
    detail_model    = User
    form_model      = Msg
    modelform_class = MsgForm
    template_name   = "send.haml"

    def modelform_valid(self, form):
        """TODO: validate cc users in form."""
        data   = form.cleaned_data
        to     = self.detail_object
        kwargs = dict(body=escape(data.body), sender=self.user, recipient=to, subject=escape(data.subject))

        Msg.obj.create(sent=True, **kwargs)
        Msg.obj.create(inbox=True, **kwargs)
        for name in data.cc.split():
            user = first(User.objects.filter(username=name))
            if user:
                Msg.obj.create( **dict(kwargs, recipient=user, inbox=True) )
        return redir("msglist", inbox=1)


class MsgListView(PaginatedModelFormSetView):
    """ Inbox or Sent Folder view.

        NOTE: when a msg is deleted from Sent folder, the copy still exists in recipient's Inbox.
        TODO: add pagination mixin.
    """
    list_model         = Msg
    formset_model      = Msg
    formset_form_class = MsgDelForm
    can_delete         = True
    paginate_by        = 3
    success_url        = '#'
    template_name      = "msglist.haml"

    def get_list_queryset(self):
        """ Note: we need to use get_list_queryset() instead of get_formset_queryset() because ListView
            adds pagination info to context based on get_list_queryset().
        """
        self.inbox = bool( int(self.kwargs.get("inbox")) )      # used in template

        if self.inbox : return Msg.obj.filter(recipient=self.user, inbox=True)
        else          : return Msg.obj.filter(sender=self.user, sent=True)


class MsgView(DetailView):
    detail_model  = Msg
    template_name = "msg.haml"

    def add_context(self):
        self.detail_object.update(is_read=True)
        reply = bool(self.detail_object.recipient==self.user)
        return dict(reply=reply)


####  BLOG


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

class PostView(DetailListCreateView):
    """Show post, associated comments and an 'add comment' form."""
    detail_model    = Post
    list_model      = Comment
    modelform_class = CommentForm
    related_name    = "comments"
    fk_attr         = "post"
    template_name   = "sb/post.html"


class CommentSearch(ListFilterView):
    list_model    = Comment
    form_class    = SearchForm
    paginate_by   = 2
    start_blank   = False
    template_name = "csearch.html"

    def get_query(self, q):
        return Q(body__icontains=q)

    def get_list_queryset(self):
        order_by = self.request.GET.get("order_by", "created")
        return super(CommentSearch, self).get_list_queryset().order_by(order_by)
