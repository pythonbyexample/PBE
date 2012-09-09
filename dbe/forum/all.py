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
from django.db.models import *
from django.contrib.auth.models import User
from django.contrib import admin
from django.db.models.signals import post_save


class Forum(Model):
    title = CharField(max_length=60)

    def __unicode__(self):
        return self.title

    def num_posts(self):
        return sum([t.num_posts() for t in self.threads.all()])

    def last_post(self):
        threads = self.threads.all()
        if threads:
            last = None
            for thread in threads:
                lastp = thread.last_post()
                if lastp:
                    if not last or lastp.created > last.created:
                        last = lastp
            return last


class Thread(Model):
    title   = CharField(max_length=60)
    created = DateTimeField(auto_now_add=True)
    creator = ForeignKey(User, blank=True, null=True)
    forum   = ForeignKey(Forum, related_name="threads")

    class Meta:
        ordering = ["-created"]

    def __unicode__(self):
        return unicode("%s - %s" % (self.creator, self.title))

    def num_posts(self):
        return self.posts.count()

    def num_replies(self):
        return self.posts.count() - 1

    def last_post(self):
        posts = self.posts.all()
        if posts:
            return posts.order_by("created")[0]


class Post(Model):
    title   = CharField(max_length=60)
    created = DateTimeField(auto_now_add=True)
    creator = ForeignKey(User, blank=True, null=True)
    thread  = ForeignKey(Thread, related_name="posts")
    body    = TextField(max_length=10000)

    class Meta:
        ordering = ["created"]

    def __unicode__(self):
        return u"%s - %s - %s" % (self.creator, self.thread, self.title)

    def short(self):
        return u"%s - %s\n%s" % (self.creator, self.title, self.created.strftime("%b %d, %I:%M %p"))
    short.allow_tags = True

    def profile_data(self):
        p = self.creator.user_profile
        return p.posts, p.avatar


class UserProfile(Model):
    avatar = ImageField("Profile Pic", upload_to="images/", blank=True, null=True)
    posts  = IntegerField(default=0)
    user   = OneToOneField(User, related_name="user_profile")

    def __unicode__(self):
        return unicode(self.user)
# Imports {{{
from PIL import Image as PImage

from dbe.settings import MEDIA_ROOT, MEDIA_URL
from dbe.forum.models import *
from dbe.shared.utils import *

from dbe.classviews.list_custom import ListView, ListRelated
from dbe.classviews.edit_custom import CreateView, UpdateView2

from forms import ProfileForm, PostForm
# }}}


class Main(ListView):
    """Main listing."""
    model               = Forum
    context_object_name = "forums"
    template_name       = "forum/list.html"


class ForumView(ListRelated):
    """Listing of threads in a forum."""
    model               = Thread
    related_model       = Forum
    foreign_key_field   = "forum"
    context_object_name = "threads"
    template_name       = "forum.html"


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
    template_name = "forum/post.html"

    def increment_post_counter(self):
        """Increment counter of user's posts."""
        profile = self.request.user.user_profile
        profile.posts += 1
        profile.save()

    def get_thread(self, form):
        data  = form.cleaned_data
        forum = Forum.objects.get(pk=self.args[0])
        return Thread.objects.create(forum=forum, title=data["title"], creator=self.request.user)

    def form_valid(self, form):
        """Create new topic."""
        data   = form.cleaned_data
        thread = self.get_thread(form)
        Post.objects.create(thread=thread, title=data["title"], body=data["body"], creator=self.request.user)
        self.increment_post_counter()
        return self.get_success_url()

    def get_success_url(self):
        return redir("forum", pk=self.args[0])


class Reply(NewTopic):
    title = "Reply"

    def get_success_url(self):
        return redir(reverse2("thread", pk=self.args[0]) + "?page=last")

    def get_thread(self, form):
        return Thread.objects.get(pk=self.args[0])


def forum_context(request):
    return dict(media_url=MEDIA_URL)
