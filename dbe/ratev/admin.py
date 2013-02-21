from ratev.ratev.models import *
from django.contrib import admin

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


admin.site.register(Artist, ArtistAdmin)
admin.site.register(Album, AlbumAdmin)
admin.site.register(Track, TrackAdmin)
admin.site.register(Author, AuthorAdmin)
admin.site.register(Book, BookAdmin)
admin.site.register(Director, DirectorAdmin)
admin.site.register(Film, FilmAdmin)
admin.site.register(AlbumRating, AlbumRatingAdmin)
admin.site.register(TrackRating, TrackRatingAdmin)
admin.site.register(BookRating, BookRatingAdmin)
admin.site.register(FilmRating, FilmRatingAdmin)
admin.site.register(Similarity, SimilarityAdmin)
admin.site.register(Recommendations, RecommendationsAdmin)
