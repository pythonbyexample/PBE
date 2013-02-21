from django import forms as f
from dbe.cal.models import *


class SettingsForm(f.ModelForm):
    class Meta:
        model   = Settings
        exclude = ["user"]

class EntryForm(f.ModelForm):
    class Meta:
        model   = Entry
        exclude = ["creator", "date"]
