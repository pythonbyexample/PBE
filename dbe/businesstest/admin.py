from django.contrib import admin
from businesstest.models import *
from django.contrib.contenttypes.models import ContentType

class Base(admin.ModelAdmin):
    list_per_page = 100

    def log_deletion(self, request, obj, object_repr):
        pass
        # log_entry(request, obj, delete=True)

    def save_model(self, request, obj, form, change):
        # log_entry(request, obj)
        obj.save()

class TaskAdmin(Base):
    list_display = "number attachment active".split()
    # list_display_links = ["x"]

class SetAdmin(Base):
    list_display = "user created".split()

class EntryAdmin(Base):
    list_display = "task eset".split()
    list_filter = "eset__user".split()

class MessageAdmin(Base):
    list_display = "sender recipient global_msg to_factory created".split()


admin.site.register(Task, TaskAdmin)
admin.site.register(Set, SetAdmin)
admin.site.register(Entry, EntryAdmin)
admin.site.register(Message, MessageAdmin)
