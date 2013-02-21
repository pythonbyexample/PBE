from django import forms as f
from dbe.ratev.models import *
from dbe.shared.utils import ContainerFormMixin

choices = ((c,c) for c in "author artist director film".split())

class SearchForm(ContainerFormMixin, f.Form):
    q     = f.CharField(max_length=400, label="", help_text="", required=False)
    stype = f.CharField(max_length=50, choices=choices, label="", help_text="", required=False)
