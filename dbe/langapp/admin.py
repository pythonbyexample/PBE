from langapp.models import *
from django.contrib import admin
from django.conf import settings

class LanguageAdmin(admin.ModelAdmin):
    list_display = ["name_eng"]

class FlagAdmin(admin.ModelAdmin):
    list_display = ["language"]

class UserSettingsAdmin(admin.ModelAdmin):
    list_display = ["user"]

class LanguageProfileAdmin(admin.ModelAdmin):
    list_display = "profile_language languages".split()

class LanguageProfileAdmin(admin.ModelAdmin):
    list_display = "profile_language languages".split()

class TypeIndustrySectorAdmin(admin.ModelAdmin):
    list_display = ["description_eng"]

class TypeLanguageCertificationAdmin(admin.ModelAdmin):
    list_display = ["description_eng"]

class TypeLanguageCompetencyAdmin(admin.ModelAdmin):
    list_display = ["description_eng"]

class TypeLanguageSpokenAdmin(admin.ModelAdmin):
    list_display = ["description_eng"]

class TypeLanguageWrittenAdmin(admin.ModelAdmin):
    list_display = ["description_eng"]

class TypeWorkAdmin(admin.ModelAdmin):
    list_display = ["description_eng"]

class TypeResumeStyleAdmin(admin.ModelAdmin):
    list_display = ["name_eng"]


admin.site.register(TypeResumeStyle, TypeResumeStyleAdmin)
admin.site.register(TypeWork, TypeWorkAdmin)
admin.site.register(TypeLanguageWritten, TypeLanguageWrittenAdmin)
admin.site.register(TypeLanguageSpoken, TypeLanguageSpokenAdmin)
admin.site.register(TypeLanguageCompetency, TypeLanguageCompetencyAdmin)
admin.site.register(TypeLanguageCertification, TypeLanguageCertificationAdmin)
admin.site.register(TypeIndustrySector, TypeIndustrySectorAdmin)
admin.site.register(LanguageProfile, LanguageProfileAdmin)
admin.site.register(UserSettings, UserSettingsAdmin)
admin.site.register(Flag, FlagAdmin)
admin.site.register(Language, LanguageAdmin)
