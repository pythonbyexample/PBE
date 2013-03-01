from settings import MEDIA_URL
from django.utils.http import urlencode

from dbe.mcbv.detail import DetailView
from dbe.mcbv.list import ListView
from dbe.mcbv.list_custom import ListRelated, DetailListFormSetView
from dbe.mcbv.edit_custom import FormSetView, UpdateView, CreateView

from dbe.shared.utils import *

from dbe.books.models import *
from dbe.books.forms import *


class Books(ListView):
    list_model    = Book
    paginate_by   = 30
    template_name = "books.haml"


class BookView(ListRelated):
    list_model    = Section
    detail_model  = Book
    related_name  = "sections"
    paginate_by   = 2
    template_name = "book.haml"

    def add_context(self):
        return dict(page=urlencode(self.request.GET.items()))


class AddComment(DetailView):
    detail_model  = Section
    template_name = "add-comment.haml"
