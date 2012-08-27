from django.contrib import admin
from dbe.photo.models import *


class AlbumAdmin(admin.ModelAdmin):
    search_fields = ["title"]
    list_display = ["title", "image_links", "public"]

class TagAdmin(admin.ModelAdmin):
    list_display = ["tag"]

class ImageAdmin(admin.ModelAdmin):
    list_display = "__unicode__ title user rating size tags_ albums_ thumbnail_ created".split()
    list_filter  = ["tags", "albums", "user"]

    def save_model(self, request, obj, form, change):
        if not obj.user: obj.user = request.user
        obj.save()


admin.site.register(Album, AlbumAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Image, ImageAdmin)
