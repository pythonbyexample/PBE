from django.forms import ModelForm, Form
from django import forms as f

from dbe.langapp.models import *
from dbe.shared.utils import *


class ProfileForm(f.ModelForm):
    class Meta:
        model = LanguageProfile
        exclude = ["user"]

class StylesForm(BaseModelForm):
    class Meta:
        model   = UserSettings
        fields  = ["resume_style"]
        widgets = dict(resume_style=f.RadioSelect)
