from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from dbe.todo.models import *


class RemindersFilter(SimpleListFilter):
    title          = "Reminder"
    parameter_name = "reminders"

    def lookups(self, request, model_admin):
        return (("reminder", "Reminder"),
                ("notreminder", "Not Reminder"),
        )

    def queryset(self, request, queryset):
        reminder = Type.objects.get(type="reminder")
        if self.value() == "reminder":
            return queryset.filter(type=reminder)
        elif self.value() == "notreminder":
            return queryset.exclude(type=reminder)


class TypeAdmin(admin.ModelAdmin):
    list_display = ["type"]

class ProjectAdmin(admin.ModelAdmin):
    list_display = ["project"]

class TagsAdmin(admin.ModelAdmin):
    list_display = ["tag"]

class ItemAdmin(admin.ModelAdmin):
    list_display   = "name_ delete_ priority difficulty type_ project_ created_ progress_ onhold_ done_".split()
    list_filter    = "priority difficulty type project tags onhold done".split()
    list_filter    = [RemindersFilter] + "priority difficulty type onhold done".split()
    date_hierarchy = "created"
    # search_fields = ["name", "tags"]


admin.site.register(Item, ItemAdmin)
admin.site.register(Type, TypeAdmin)
admin.site.register(Project, ProjectAdmin)
admin.site.register(Tag, TagsAdmin)
