from django.forms import ModelForm
from django import forms as f
from django.forms.widgets import TextInput

from dbe.photo.models import *
from dbe.shared.utils import *
from dbe.photo.fields import *

sort_choices = [("created", "date")] + [(c,c) for c in "rating title width height albums".split()]

class ImageForm(AKModelForm):
    def __init__(self, *args, **kwargs):
        super(ImageForm, self).__init__(*args, **kwargs)
        tags   = self.fields["tags"]
        albums = self.fields["albums"]
        tags.help_text = albums.help_text = ''  # remove select box help text

    class Meta:
        model   = Image
        exclude = "image thumbnail1 thumbnail2 width height user".split()
        widgets = dict(albums = f.CheckboxSelectMultiple(),
                       rating = f.TextInput( attrs=dict(size=1) ),
                       )

    # We need to pass an empty tuple for the queryset, ModelForm will update it from current Image.
    # Widget can't be specified in Meta.widgets because it only applies to auto-created fields.
    tags = SelectCSVField((), widget=f.TextInput( attrs=dict(size=50) ))


class SearchForm(f.Form):
    title    = f.CharField(max_length=30, required=False)
    tags     = TagParseField(required=False)
    rating   = MinMaxRangeIntField()
    width    = MinMaxRangeIntField()
    height   = MinMaxRangeIntField()
    sort_by  = f.ChoiceField(choices=sort_choices)
    sort_dir = f.ChoiceField(choices=(('-', "descending"), ('', "ascending")), required=False)
    albums   = f.ModelMultipleChoiceField(queryset=Album.obj.all(), widget=f.CheckboxSelectMultiple(),
                                          required=False)
