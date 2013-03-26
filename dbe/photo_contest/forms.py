from django import forms as f
from dbe.photo_contest.models import *
from dbe.shared.utils import *


class ModerationForm(FormsetModelForm):
    delete_image = f.BooleanField(help_text="Delete image from ImageProfile", required=False)
    attrs        = dict(cols=60, rows=4)
    explanation  = f.CharField(max_length=300, required=False, widget=f.Textarea(attrs=attrs))

    class Meta:
        model   = ImageProfile
        fields  = ["active", "banned"]

    def __init__(self, *args, **kw):
        super(ModerationForm, self).__init__(*args, **kw)
        self.fields.keyOrder.remove("banned")   # move banned to the end
        self.fields.keyOrder.append("banned")

    def clean(self):
        data = Container(**self.cleaned_data)
        if data.delete_image and data.active:
            msg = "An image profile must be either marked as active OR image to be deleted"
            raise f.ValidationError(msg)

        if data.explanation and data.banned or data.explanation and not data.delete_image:
            raise f.ValidationError("Explanation should only be given when an image is deleted")

        if data.banned and (data.active or data.delete_image):
            msg = "An image profile must be either marked as active OR banned OR image to be deleted"
            raise f.ValidationError(msg)

        return data


class AddImageForm(f.ModelForm):
    accept_terms = f.BooleanField("Accept Site Terms")
    waive_rights = f.BooleanField("Waive image rights")

    class Meta:
        model   = ImageProfile
        exclude = "active banned confirm_email created thumbnail".split()
        # exclude = "active email confirm_email created promotion thumbnail".split()
        attrs   = dict(cols=60, rows=4)
        widgets = dict( personal_info=f.Textarea(attrs=attrs) )

    def clean_image(self):
        img = self.cleaned_data["image"]
        if not img: raise f.ValidationError("Select the image file to upload")
        return img
