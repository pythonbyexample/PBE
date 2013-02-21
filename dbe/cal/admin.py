from dbe.cal.models import *
from django.contrib import admin

class EntryAdmin(admin.ModelAdmin):
    list_display  = ["creator", "date", "title", "snippet"]
    search_fields = ["title", "snippet"]
    list_filter   = ["creator"]

class SettingsAdmin(admin.ModelAdmin):
    pass

admin.site.register(Entry, EntryAdmin)
admin.site.register(Settings, SettingsAdmin)
