from django import forms as f
from dbe.books.models import *
from dbe.shared.utils import *

class CommentForm(f.ModelForm):
    class Meta:
        model   = Comment
        fields  = ["body"]
        attrs   = dict(cols=40, rows=5)
        widgets = dict( body=f.Textarea(attrs=attrs) )
