from django import forms as f
from dbe.portfolio.models import *
from dbe.shared.utils import *

class ImageForm(AKModelForm):
    class Meta:
        model   = Image
        exclude = "image width height hidden group thumbnail1 thumbnail2".split()
        widgets = dict(description=f.Textarea(attrs=dict(cols=70)))

class AddImageForm(AKModelForm):
    class Meta:
        model   = Image
        exclude = "width height hidden group thumbnail1 thumbnail2".split()
        widgets = dict(description=f.Textarea(attrs=dict(cols=70, rows=2)))
