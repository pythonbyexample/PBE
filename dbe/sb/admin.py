from django.contrib import admin
from dbe.sb.models import *


class PostAdmin(admin.ModelAdmin):
    search_fields = ["title"]
    list_display = "title created".split()

class CommentAdmin(admin.ModelAdmin):
    list_display = "post author created".split()

class MessageAdmin(admin.ModelAdmin): pass

class MsgAdmin(admin.ModelAdmin):
    list_display = "sender recipient sent inbox subject is_read".split()
    list_filter  = "sent inbox".split()

admin.site.register(Post, PostAdmin)
admin.site.register(Message, MessageAdmin)
admin.site.register(Msg, MsgAdmin)
admin.site.register(Comment, CommentAdmin)
