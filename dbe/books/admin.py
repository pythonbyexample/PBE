from django.contrib import admin
from dbe.books.models import *

class AuthorAdmin(admin.ModelAdmin)   : pass
class BookAdmin(admin.ModelAdmin)     : pass
class ChapterAdmin(admin.ModelAdmin)  : pass
class SectionAdmin(admin.ModelAdmin)  : pass
class SentenceAdmin(admin.ModelAdmin) : pass
class CommentAdmin(admin.ModelAdmin)  : pass
class VoteAdmin(admin.ModelAdmin)     : pass
    # list_display = "__unicode__ title group created".split()
    # list_filter  = ["group"]


admin.site.register(Author, AuthorAdmin)
admin.site.register(Book, BookAdmin)
admin.site.register(Chapter, ChapterAdmin)
admin.site.register(Section, SectionAdmin)
admin.site.register(Sentence, SentenceAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Vote, VoteAdmin)
