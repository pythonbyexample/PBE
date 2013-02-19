from django import forms as f

class SettingsForm(f.ModelForm):
    class Meta:
        exclude = ["user"]

class EntryForm(f.ModelForm):
    class Meta:
        exclude = ["creator", "date"]
