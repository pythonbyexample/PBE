# Imports {{{
from PIL import Image as PImage

from dbe.settings import MEDIA_ROOT, MEDIA_URL
from dbe.social.models import *
from dbe.shared.utils import *

from dbe.classviews.list_custom import ListView, ListRelated
from dbe.classviews.edit_custom import CreateView, UpdateView2

from forms import ProfileForm, PostForm
# }}}


class Main(ListView):
    """Main listing."""
    model               = Forum
    context_object_name = "socials"
    template_name       = "social/list.html"


class ForumView(ListRelated):
    """Listing of threads in a social."""
    model               = Thread
    related_model       = Forum
    foreign_key_field   = "social"
    context_object_name = "threads"
    template_name       = "social.html"


class ThreadView(ListRelated):
    """Listing of posts in a thread."""
    model               = Post
    related_model       = Thread
    foreign_key_field   = "thread"
    context_object_name = "posts"
    template_name       = "thread.html"


class EditProfile(UpdateView2):
    model         = UserProfile
    form_class    = ProfileForm
    success_url   = '#'
    template_name = "profile.html"

    def form_valid(self, form):
        """Resize and save profile image."""
        # remove old image if changed
        name = form.cleaned_data.get("avatar", None)
        old = UserProfile.objects.get( pk=self.kwargs.get("pk") ).avatar
        if old.name and old.name != name:
            old.delete()

        # save new image to disk & resize new image
        self.object = form.save()
        if self.object.avatar:
            img = PImage.open(self.object.avatar.path)
            img.thumbnail((160,160), PImage.ANTIALIAS)
            img.save(img.filename, "JPEG")
        return redir(self.success_url)

    def add_context(self):
        img = ("/media/" + self.object.avatar.name) if self.object.avatar else None
        return dict(img=img)


class NewTopic(CreateView):
    model         = Post
    form_class    = PostForm
    title         = "Start New Topic"
    template_name = "social/post.html"

    def increment_post_counter(self):
        """Increment counter of user's posts."""
        profile = self.request.user.user_profile
        profile.posts += 1
        profile.save()

    def get_thread(self, form):
        data  = form.cleaned_data
        social = Forum.objects.get(pk=self.args[0])
        return Thread.objects.create(social=social, title=data["title"], creator=self.request.user)

    def form_valid(self, form):
        """Create new topic."""
        data   = form.cleaned_data
        thread = self.get_thread(form)
        Post.objects.create(thread=thread, title=data["title"], body=data["body"], creator=self.request.user)
        self.increment_post_counter()
        return self.get_success_url()

    def get_success_url(self):
        return redir("social", pk=self.args[0])


class Reply(NewTopic):
    title = "Reply"

    def get_success_url(self):
        return redir(reverse2("thread", pk=self.args[0]) + "?page=last")

    def get_thread(self, form):
        return Thread.objects.get(pk=self.args[0])


def social_context(request):
    return dict(media_url=MEDIA_URL)
