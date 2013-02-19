from ratev.ratev.models import *
from django.contrib import admin

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
