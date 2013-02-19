from dbe.cal.models import *
from django.contrib import admin

class EntryAdmin(admin.ModelAdmin):
    list_display  = ["creator", "date", "title", "snippet"]
    search_fields = ["title", "snippet"]
    list_filter   = ["creator"]

admin.site.register(Entry, EntryAdmin)
