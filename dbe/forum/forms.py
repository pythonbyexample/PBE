from django.forms import ModelForm
from dbe.forum.models import *
from dbe.shared.utils import CleanFormMixin

class ProfileForm(CleanFormMixin, ModelForm):
    class Meta:
        model   = UserProfile
        exclude = ["posts", "user"]

class PostForm(CleanFormMixin, ModelForm):
    class Meta:
        model   = Post
        exclude = ["creator", "thread"]
