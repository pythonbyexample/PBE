from django import forms as f
from django.contrib.comments.forms import CommentForm

from dbe.books.models import *
from dbe.shared.utils import *

class BCommentForm(CommentForm):
    def get_comment_model(self):
        return BComment
