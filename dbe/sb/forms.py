from dbe.sb.models import *
from django.forms import *

from dbe.shared.utils import CleanFormMixin

class SearchForm(CleanFormMixin, Form):
    q = CharField(max_length=400, label="", help_text="", required=False)

class CommentForm(CleanFormMixin, ModelForm):
    class Meta:
        model = Comment
        exclude = ["post"]

    def clean_author(self):
        return self.cleaned_data.get("author") or "Anonymous"
