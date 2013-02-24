from django.db.models import *
from django.contrib.auth.models import User
from django.contrib import admin
from django.core.mail import send_mail

from dbe.shared.utils import *


class Post(BaseModel):
    title   = CharField(max_length=60)
    body    = TextField()
    created = DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created"]

    def __unicode__(self):
        return self.title


class Comment(BaseModel):
    author  = CharField(max_length=60, blank=True)
    body    = TextField()
    post    = ForeignKey(Post, related_name="comments",  blank=True, null=True)
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


class Message(BaseModel):
    sender    = ForeignKey(User, related_name="messages")
    recipient = ForeignKey(User, blank=True, null=True)
    is_read   = BooleanField(default=False)
    created   = DateTimeField(auto_now_add=True)
    body      = TextField(max_length=10000, blank=True, null=True)

    class Meta:
        ordering = ["-created"]

    def __unicode__(self):
        b = self.body if len(self.body) < 50 else self.body[:50] + "..."
        return u"%s - %s" % (self.sender, b)


class Msg(BaseModel):
    sender    = ForeignKey(User, related_name="msgs")
    recipient = ForeignKey(User, blank=True, null=True)
    subject   = CharField(max_length=80, blank=True, null=True)
    cc        = CharField(max_length=250, blank=True, null=True)
    body      = TextField(max_length=10000, blank=True, null=True)

    is_read   = BooleanField(default=False)
    sent      = BooleanField(default=False)     # sender's copy
    inbox     = BooleanField(default=False)     # recipient's copy
    created   = DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created"]

    def __unicode__(self):
        b = self.body if len(self.body) < 50 else self.body[:50] + "..."
        return u"%s - %s" % (self.sender, b)


class SBProfile(BaseModel):
    user                = OneToOneField(User, related_name="sbprofile")
    last_viewed_message = ForeignKey(Message, blank=True, null=True)    # unused
