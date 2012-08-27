from django.db.models import *
from django.contrib.auth.models import User
from django.contrib import admin
from django.core.mail import send_mail


class Post(Model):
    title   = CharField(max_length=60)
    body    = TextField()
    created = DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.title

class Comment(Model):
    author  = CharField(max_length=60, blank=True)
    body    = TextField()
    post    = ForeignKey(Post, related_name="comments")
    created = DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return u"%s: %s" % (self.post, self.body[:60])

    def save(self, *args, **kwargs):
        """Email when a comment is added."""
        if kwargs.pop("notify", False):
            message = "Comment was was added to '%s' by '%s': \n\n%s" % (self.post, self.author, self.body)
            from_addr = "no-reply@mydomain.com"
            recipient_list = ["myemail@mydomain.com"]
            send_mail("New comment added", message, from_addr, recipient_list)
        super(Comment, self).save(*args, **kwargs)
