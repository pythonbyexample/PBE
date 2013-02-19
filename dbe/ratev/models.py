from string import join
from django.db import models
from django.contrib.auth.models import User
from django.contrib import admin


class Artist(models.Model):
    name = models.CharField(max_length=80)
    added_by = models.ForeignKey(User, blank=True, null=True)

    def __unicode__(self):
        return self.name

    def url(self):
        return "<a href='/ratev/artist/%s/'>artist page</a>" % self.id
    url.allow_tags = True

class Album(models.Model):
    name = models.CharField(max_length=140)
    genre = models.CharField(max_length=80, blank=True)
    added = models.DateField(auto_now_add=True)
    added_by = models.ForeignKey(User, blank=True, null=True)
    year = models.CharField(max_length=4, blank=True)
    artist = models.ManyToManyField(Artist)
    rated = models.BooleanField(default=False)

    def __unicode__(self):
        return self.name

    def artists(self):
        names = [a.name for a in self.artist.all()]
        return join(names, ', ')

class Track(models.Model):
    name = models.CharField(max_length=140)
    album = models.ForeignKey(Album, blank=True)
    artist = models.ManyToManyField(Artist, blank=True)
    length = models.CharField(max_length=6, blank=True)
    added_by = models.ForeignKey(User, blank=True, null=True)
    rated = models.BooleanField(default=False)
    def __unicode__(self):
        # return "%s - %s - %s" % (self.artist, self.album, self.name)
        return "%s - %s" % (unicode(self.album), unicode(self.name))

    def artists(self):
        names = [a.name for a in self.artist.all()]
        return join(names, ', ')

class Author(models.Model):
    name = models.CharField(max_length=80)
    added_by = models.ForeignKey(User, blank=True, null=True)
    def __unicode__(self):
        return self.name

class Book(models.Model):
    name = models.CharField(max_length=80)
    genre = models.CharField(max_length=80, blank=True)
    added = models.DateField(auto_now_add=True)
    added_by = models.ForeignKey(User, blank=True, null=True)
    year = models.CharField(max_length=4, blank=True)
    author = models.ManyToManyField(Author)
    rated = models.BooleanField(default=False)

    def __unicode__(self):
        return self.name

    def authors(self):
        names = [a.name for a in self.author.all()]
        return join(names, ', ')

class Director(models.Model):
    name = models.CharField(max_length=80)
    added_by = models.ForeignKey(User, blank=True, null=True)
    def __unicode__(self):
        return self.name

class Film(models.Model):
    name = models.CharField(max_length=80)
    genre = models.CharField(max_length=80, blank=True)
    added = models.DateField(auto_now_add=True)
    added_by = models.ForeignKey(User, blank=True, null=True)
    year = models.CharField(max_length=4, blank=True)
    director = models.ManyToManyField(Director)
    rated = models.BooleanField(default=False)

    def __unicode__(self):
        return self.name

    def directors(self):
        names = [a.name for a in self.director.all()]
        return join(names, ', ')

class AlbumRating(models.Model):
    album = models.ForeignKey(Album)
    user = models.ForeignKey(User)
    # setting blank=True as a workaround to be able to get_or_create the rating and then setting
    # rating afterwards, but it should never be blank.
    rating = models.PositiveSmallIntegerField(blank=True, null=True)

class TrackRating(models.Model):
    track = models.ForeignKey(Track)
    user = models.ForeignKey(User)
    rating = models.PositiveSmallIntegerField(blank=True, null=True)

    def __unicode__(self):
        return "%s - %s - %s" % (self.track, self.user, self.rating)

class BookRating(models.Model):
    book = models.ForeignKey(Book)
    user = models.ForeignKey(User)
    rating = models.PositiveSmallIntegerField(blank=True, null=True)

class FilmRating(models.Model):
    film = models.ForeignKey(Film)
    user = models.ForeignKey(User)
    rating = models.PositiveSmallIntegerField(blank=True, null=True)

class Similarity(models.Model):
    user1 = models.ForeignKey(User, related_name="user1")
    user2 = models.ForeignKey(User, related_name="user2")
    similarity = models.PositiveSmallIntegerField(blank=True)

class Recommendations(models.Model):
    user = models.ForeignKey(User)
    itype = models.CharField(max_length=20)
    itemid = models.PositiveIntegerField()
    rating = models.PositiveSmallIntegerField()


# --ADMINS--------------------------------------------------------------------------------------

class ArtistAdmin(admin.ModelAdmin):
    list_display = ("name", "url")
    search_fields = ["name"]

class AlbumAdmin(admin.ModelAdmin):
    list_display = ("name", "artists", "genre", "added", "added_by")
    raw_id_fields = ("artist", "added_by")

class TrackAdmin(admin.ModelAdmin):
    list_display = ("name", "album", "artists")

class AuthorAdmin(admin.ModelAdmin):
    list_display = ("name",)

class BookAdmin(admin.ModelAdmin):
    raw_id_fields = ("author", "added_by")
    list_display = ("name", "genre", "added", "added_by", "year")

class DirectorAdmin(admin.ModelAdmin):
    list_display = ("name",)

class FilmAdmin(admin.ModelAdmin):
    list_display = ("name", "genre", "added", "added_by", "year")
    raw_id_fields = ("director", "added_by")

class AlbumRatingAdmin(admin.ModelAdmin):
    raw_id_fields = ("album",)
    list_display = ("album", "rating")

class TrackRatingAdmin(admin.ModelAdmin):
    list_display = ("user", "track", "rating")
    raw_id_fields = ("track",)

class BookRatingAdmin(admin.ModelAdmin):
    list_display = ("book", "rating")
    raw_id_fields = ("book",)

class FilmRatingAdmin(admin.ModelAdmin):
    list_display = ("film", "rating")
    raw_id_fields = ("film",)

class SimilarityAdmin(admin.ModelAdmin):
    list_display = ("user1", "user2", "similarity")

class RecommendationsAdmin(admin.ModelAdmin):
    list_display = ("user", "itype", "itemid", "rating")
