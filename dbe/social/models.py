from django.db.models import *
from django.contrib.auth.models import User


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
                lastpost = thread.last_post()
                if lastpost:
                    if not last or lastpost.created > last.created:
                        last = lastpost
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
    points = IntegerField(default=0)
    user   = OneToOneField(User, related_name="user_profile")

    def __unicode__(self):
        return unicode(self.user)
