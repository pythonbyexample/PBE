from django.db.models import *
from django.contrib.auth.models import User
from django.contrib import admin

from dbe.shared.utils import BaseModel

class Entry(BaseModel):
    title   = CharField(max_length=40)
    snippet = CharField(max_length=150, blank=True)
    body    = TextField(max_length=10000, blank=True)
    created = DateTimeField(auto_now_add=True)
    date    = DateField(blank=True)
    creator = ForeignKey(User, blank=True, null=True)
    remind  = BooleanField(default=False)

    def __unicode__(self):
        return self.creator + u" - " + (self.title if self.title else self.snippet[:40])

    def short(self):
        tpl = "<i>%s</i> - %s"
        return tpl % (self.title, self.snippet) if self.snippet else self.title
    short.allow_tags = True

    class Meta:
        verbose_name_plural = "entries"

class Settings(BaseModel):
    user             = OneToOneField(User, related_name="settings")
    show_other_users = BooleanField(default=False)
