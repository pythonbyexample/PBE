from django.forms import ModelForm, Form
from django import forms as f

from langapp.models import *


class NewProfileForm(f.ModelForm):
    class Meta:
        model = LanguageProfile
        exclude = "user".split()
        # exclude = "reminder creator".split()

class EditProfileForm(f.ModelForm):
    class Meta:
        model = LanguageProfile
        exclude = "user".split()

class StylesForm(f.Form):
    def __init__(self, style, *args, **kwargs):
        super(StylesForm, self).__init__(*args, **kwargs)
        styles = [(s.pk, s.name_eng) for s in TypeResumeStyle.obj.all()]
        self.fields["style"] = f.ChoiceField(choices=styles, initial=style, widget=f.RadioSelect)
