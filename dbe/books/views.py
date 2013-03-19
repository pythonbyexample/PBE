from settings import MEDIA_URL
from django.utils.http import urlencode

from dbe.mcbv.detail import DetailView, View
from dbe.mcbv.list_custom import ListRelated, DetailListFormSetView, ListView
from dbe.mcbv.edit_custom import FormSetView, UpdateView, CreateView

from dbe.shared.utils import *

from dbe.books.models import *
from dbe.books.forms import *


class PageContext(object):
    def add_context(self):
        return dict( page=urlencode(self.request.GET.items()) )


class VoteView(View):
    def get(self, *args, **kwargs):
        comment = BComment.objects.get(pk=self.kwargs.get("dpk"))
        # vote    = Vote.obj.get_or_create(comment=comment, creator=self.user)[0]
        vote    = Vote.obj.create(comment=comment, creator=self.user)
        vote.update( value=self.kwargs.get("vote") )
        return redir(reverse2("book", comment.content_object.book.pk) + '?' +
                     urlencode(self.request.GET.items()))


class Books(ListView):
    list_model    = Book
    paginate_by   = 30
    template_name = "books.haml"

class BookView(PageContext, ListRelated):
    list_model    = Section
    detail_model  = Book
    paginate_by   = 2
    related_name  = "sections"
    template_name = "book.haml"

class AddComment(PageContext, DetailView):
    detail_model  = Section
    template_name = "add-comment.haml"
