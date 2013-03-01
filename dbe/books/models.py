import os
from settings import MEDIA_ROOT, MEDIA_URL
from os.path import join as pjoin, basename

from django.db.models import *
from django.core.files import File
from django.contrib.auth.models import User

from dbe.shared.utils import *


class Author(BaseModel):
    first_name  = CharField(max_length=50)
    last_name   = CharField(max_length=50)
    description = TextField(blank=True, null=True)

    class Meta: ordering = ["last_name"]

    def __unicode__(self):
        return self.first_name + ' ' + self.last_name

    def get_absolute_url(self):
        return reverse2("author", self.pk)


class Book(BaseModel):
    name        = CharField(max_length=99)
    isbn        = CharField(max_length=40)
    author      = ForeignKey(Author, related_name="books")
    description = TextField(blank=True, null=True)
    # author   = ManyToManyField(Author, related_name="books")

    class Meta: ordering = ["name"]

    def __unicode__(self):
        return unicode(self.author) + ' - ' + unicode(self.name)

    def get_absolute_url(self):
        return reverse2("book", self.pk)


class Chapter(BaseModel):
    name     = CharField(max_length=99)
    book     = ForeignKey(Book, related_name="chapters")
    ordering = IntegerField(default=1)

    class Meta: ordering = ["ordering"]

    def __unicode__(self):
        return unicode(self.name)


class Section(BaseModel):
    name     = CharField(max_length=99, blank=True, null=True)
    chapter  = ForeignKey(Chapter, related_name="sections")
    book     = ForeignKey(Book, related_name="sections")
    ordering = IntegerField(default=1)

    class Meta: ordering = ["ordering"]

    def __unicode__(self):
        return unicode(self.name)


class Sentence(BaseModel):
    body     = TextField()
    section  = ForeignKey(Section, related_name="sentences")
    ordering = IntegerField(default=1)

    class Meta: ordering = ["ordering"]

    def __unicode__(self):
        return self.body


class Comment(BaseModel):
    section = ForeignKey(Section, related_name="comments", blank=True, null=True)
    comment = ForeignKey("Comment", related_name="comments", blank=True, null=True)
    creator = ForeignKey(User, related_name="book_comments", blank=True, null=True)
    created = DateTimeField(auto_now_add=True)
    body    = TextField(max_length=3000)

    class Meta: ordering = ["created"]

    def __unicode__(self):
        return unicode(self.creator) + ' ' + unicode(self.created)

    def score(self):
        return sum(v.value for v in self.votes)

    def author(self):
        return self.creator or "Anonymous"


class Vote(BaseModel):
    comment = ForeignKey(Comment, related_name="votes")
    creator = ForeignKey(User, related_name="votes")
    value   = IntegerField(default=1)

    def __unicode__(self):
        return unicode(self.creator) + ' ' + unicode(self.value)
