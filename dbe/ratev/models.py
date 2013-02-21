from string import join
from django.db.models import *
from django.contrib.auth.models import User
from django.contrib import admin

from dbe.shared.utils import *

href = "<a href='%s'>%s</a>"


class Artist(BaseModel):
    name     = CharField(max_length=80)
    added_by = ForeignKey(User, blank=True, null=True)

    def __unicode__(self):
        return self.name

    def url(self):
        return href % (reverse2("artist", self.pk), "artist page")
    url.allow_tags = True

class Album(BaseModel):
    name     = CharField(max_length=140)
    genre    = CharField(max_length=80, blank=True)
    added    = DateField(auto_now_add=True)
    added_by = ForeignKey(User, related_name="albums", blank=True, null=True)
    year     = CharField(max_length=4, blank=True)
    artist   = ManyToManyField(Artist, related_name="albums")
    rated    = BooleanField(default=False)

    def __unicode__(self):
        return self.name

    def artists(self):
        return cjoin([a.name for a in self.artist.all()])

class Track(BaseModel):
    name     = CharField(max_length=140)
    album    = ForeignKey(Album, related_name="tracks", blank=True)
    artist   = ManyToManyField(Artist, related_name="tracks", blank=True)
    length   = CharField(max_length=6, blank=True)
    added_by = ForeignKey(User, related_name="tracks", blank=True, null=True)
    rated    = BooleanField(default=False)

    def __unicode__(self):
        return "%s - %s" % (unicode(self.album), unicode(self.name))

    def artists(self):
        return cjoin([a.name for a in self.artist.all()])

class Author(BaseModel):
    name     = CharField(max_length=80)
    added_by = ForeignKey(User, related_name="authors", blank=True, null=True)

    def __unicode__(self):
        return self.name

class Book(BaseModel):
    name     = CharField(max_length=80)
    genre    = CharField(max_length=80, blank=True)
    added    = DateField(auto_now_add=True)
    added_by = ForeignKey(User, related_name="books", blank=True, null=True)
    year     = CharField(max_length=4, blank=True)
    author   = ManyToManyField(Author, related_name="books")
    rated    = BooleanField(default=False)

    def __unicode__(self):
        return self.name

    def authors(self):
        return cjoin([a.name for a in self.author.all()])

def cjoin(seq):
    return ", ".join(seq)

class Director(BaseModel):
    name     = CharField(max_length=80)
    added_by = ForeignKey(User, related_name="directors", blank=True, null=True)

    def __unicode__(self):
        return self.name

class Film(BaseModel):
    name     = CharField(max_length=80)
    genre    = CharField(max_length=80, blank=True)
    added    = DateField(auto_now_add=True)
    added_by = ForeignKey(User, related_name="films", blank=True, null=True)
    year     = CharField(max_length=4, blank=True)
    director = ManyToManyField(Director, related_name="films")
    rated    = BooleanField(default=False)

    def __unicode__(self):
        return self.name

    def directors(self):
        return cjoin([a.name for a in self.director.all()])

class AlbumRating(BaseModel):
    album = ForeignKey(Album, related_name="ratings")
    user  = ForeignKey(User, related_name="album_ratings")
    # setting blank=True as a workaround to be able to get_or_create the rating and then setting
    # rating afterwards, but it should never be blank.
    rating = PositiveSmallIntegerField(blank=True, null=True)

class TrackRating(BaseModel):
    track  = ForeignKey(Track, related_name="ratings")
    user   = ForeignKey(User, related_name="track_ratings")
    rating = PositiveSmallIntegerField(blank=True, null=True)

    def __unicode__(self):
        return "%s - %s - %s" % (self.track, self.user, self.rating)

class BookRating(BaseModel):
    book   = ForeignKey(Book, related_name="ratings")
    user   = ForeignKey(User, related_name="book_ratings")
    rating = PositiveSmallIntegerField(blank=True, null=True)

class FilmRating(BaseModel):
    film   = ForeignKey(Film, related_name="ratings")
    user   = ForeignKey(User, related_name="film_ratings")
    rating = PositiveSmallIntegerField(blank=True, null=True)

class Similarity(BaseModel):
    user1      = ForeignKey(User, related_name="user1")
    user2      = ForeignKey(User, related_name="user2")
    similarity = PositiveSmallIntegerField(blank=True)

class Recommendations(BaseModel):
    user   = ForeignKey(User, related_name="recommendations")
    itype  = CharField(max_length=20)
    itemid = PositiveIntegerField()
    rating = PositiveSmallIntegerField()
