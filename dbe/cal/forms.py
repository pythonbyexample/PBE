from django import forms as f

class SettingsForm(f.ModelForm):
    class Meta:
        exclude = ["user"]
