from django.forms import ModelForm
from dbe.forum.models import *

class ProfileForm(ModelForm):
    class Meta:
        model   = UserProfile
        exclude = ["posts", "user"]

class PostForm(ModelForm):
    class Meta:
        model   = Post
        exclude = ["creator", "thread"]
