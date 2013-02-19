from django.db.models import *
from django.contrib.auth.models import User
from django.contrib import admin

from dbe.shared.utils import BaseModel

class EntryManager(Manager):
    def date_filter(self, year, month, day=None):
        entries = self.filter(date__year=year, date__month=month)
        if day: entries = entries.filter(date__day=day)
        return entries

class Entry(BaseModel):
    obj     = objects = EntryManager()
    title   = CharField(max_length=40)
    snippet = CharField(max_length=150, blank=True)
    body    = TextField(max_length=10000, blank=True)
    created = DateTimeField(auto_now_add=True)
    date    = DateField(blank=True)
    creator = ForeignKey(User, blank=True, null=True)
    remind  = BooleanField(default=False)

    class Meta:
        verbose_name_plural = "entries"

    def __unicode__(self):
        return self.creator + u" - " + (self.title if self.title else self.snippet[:40])

    def short(self):
        tpl = "<i>%s</i> - %s"
        return tpl % (self.title, self.snippet) if self.snippet else self.title
    short.allow_tags = True


class Settings(BaseModel):
    user             = OneToOneField(User, related_name="settings")
    show_other_users = BooleanField(default=False)
