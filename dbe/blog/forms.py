from django.forms import *
from dbe.blog.models import *

class CommentForm(ModelForm):
    def clean_author(self):
        return self.cleaned_data.get("author") or "Anonymous"

    class Meta:
        model = Comment
        exclude = ["post"]
