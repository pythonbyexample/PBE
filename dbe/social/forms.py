from django.forms import ModelForm
from dbe.social.models import *

class ProfileForm(ModelForm):
    class Meta:
        model   = UserProfile
        exclude = ["posts", "user"]

class PostForm(ModelForm):
    class Meta:
        model   = Post
        exclude = ["creator", "thread"]
