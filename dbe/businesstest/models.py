# -*- coding: utf-8 -*-

# Imports {{{
from django.contrib.auth.models import User, Group
from django.db import models, IntegrityError
from django.db.models import *
# }}}

task_choices = (
                ("single", "Single Text Area"),
                ("multi", "Multiple Text Boxes"),
                ("multichoice", "Multiple Choice"),
               )


class Base(Model):
    class Meta:
        abstract = True

    def update(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
        self.save()

class Task(Base):
    number     = FloatField()
    question   = TextField(max_length=2000)
    attachment = FileField(upload_to="task_files", max_length=100, blank=True, null=True)
    active     = BooleanField(default=True)
    created    = DateTimeField(auto_now_add=True)
    tasktype   = CharField(choices=task_choices, max_length=20, default="single")
    options    = TextField(max_length=2000, blank=True, null=True)

    def __unicode__(self):
        return u"%s - active:%s, %s" % (self.number, self.active, self.attachment)

    class Meta:
        ordering = ["number"]

class Set(Base):
    user       = ForeignKey(User, blank=True, null=True)
    created    = DateTimeField(auto_now_add=True)
    finished   = BooleanField(default=False)
    time_taken = CharField(max_length=8, null=True, blank=True)
    # number     = IntegerField()

    def __unicode__(self):
        return u"%s - %s" % (self.user, self.created)

    def current(self, user):
        return self.objects.filter(user=user, finished=False).order_by("-number")[0]

    class Meta:
        ordering = ["created"]

class Entry(Base):
    task       = ForeignKey("Task", related_name="entries")
    eset       = ForeignKey("Set", related_name="entries")
    created    = DateTimeField(auto_now_add=True)
    answer     = CharField(max_length=500)
    time_taken = CharField(max_length=8, null=True, blank=True)

    class Meta:
        verbose_name_plural = "Entries"
