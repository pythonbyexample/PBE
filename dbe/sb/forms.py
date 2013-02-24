from dbe.sb.models import *
from django.forms import *

from dbe.shared.utils import ContainerFormMixin

class SearchForm(ContainerFormMixin, Form):
    q = CharField(max_length=400, label="", help_text="", required=False)


class CommentForm(ContainerFormMixin, ModelForm):
    class Meta:
        model = Comment
        exclude = ["post"]

    def clean_author(self):
        return self.cleaned_data.get("author") or "Anonymous"


class MessageForm(ModelForm):
    class Meta:
        model   = Message
        exclude = ["sender", "recipient", "created"]

class MsgForm(ContainerFormMixin, ModelForm):
    class Meta:
        model   = Msg
        exclude = ["sender", "recipient", "created", "sent", "inbox", "is_read"]
        widgets = dict(
                       subject=TextInput(attrs=dict(size=30)),
                       cc=TextInput(attrs=dict(size=30)),
                       body=Textarea(attrs=dict(cols=60, rows=20)),
                       )

class MsgDelForm(ModelForm):
    """ We need a separate delete form with empty fields list because:

        if fields are in the form but not rendered on page, formset gets blank POST for these
        fields and thinks they were changed to blank, & updates them to be blank on the instance.
    """
    class Meta:
        model   = Msg
        fields  = []
