from django.db import models
from django.db.models import *
from django.contrib.auth.models import User


class Language(Model):
    description = CharField(max_length=40)
    code        = CharField(max_length=10)
    name_eng    = CharField(max_length=255)
    name_native = CharField(max_length=255)
    iso639_1    = CharField(max_length=10, blank=True, null=True)
    iso639_2T   = CharField(max_length=10, blank=True, null=True)
    iso639_2B   = CharField(max_length=10, blank=True, null=True)
    iso639_X    = CharField(max_length=10, blank=True, null=True)
    direction   = IntegerField(default=0)
    text_align  = IntegerField(default=0)
    # alt_name_eng    = CharField(max_length=255, blank=True, null=True)
    # alt_name_native = CharField(max_length=255, blank=True, null=True)

class Flag(Model):
    language    = ForeignKey(Language)
    icon        = ImageField(upload_to="flags/", max_length=255)
    description = CharField(max_length=255)
    information = CharField(max_length=255)

class RIDocumentation(Model):
    user        = ForeignKey(User)
    language    = ForeignKey(Language)
    file        = FileField(upload_to="docs/", max_length=255)
    title       = CharField(max_length=255)
    description = TextField(max_length=2000)

class RIEmploymentHistory(Model):
    user              = ForeignKey(User)
    language          = ForeignKey(Language)
    employer          = CharField(max_length=255)
    position_title    = CharField(max_length=255, blank=True, null=True)
    position_level    = CharField(max_length=255, blank=True, null=True)
    location          = CharField(max_length=255, blank=True, null=True)
    work_type         = ForeignKey(TypeWork)
    commencement_date = DateField(blank=True, null=True)
    completion_date   = DateField(blank=True, null=True)
    duties            = TextField(max_length=2000, blank=True, null=True)

class RIUserSettings(Model):
    user                              = ForeignKey(User)
    primary_language                  = ForeignKey(Language)
    resume_style                      = ForeignKey(TypeResumeStyle)

    display_primary_language          = BooleanField(default=False)
    display_mutiple_languages         = BooleanField(default=False)
    display_single_language           = BooleanField(default=False)
    primary_virtual_keyboard_language = ForeignKey(UserLanguage)
    display_primary_virtual_keyboard  = BooleanField(default=False)


class LanguageProfile(Model):
    user                    = ForeignKey(User)
    profile_language        = ForeignKey(Language)
    languages               = CharField(max_length=255)
    description_intl        = CharField(max_length=255)
    description_eng         = CharField(max_length=255)
    description_native      = CharField(max_length=255)

    flag                    = ForeignKey(Flag)
    description             = CharField(max_length=255)
    years_experience        = CharField(max_length=10, blank=True, null=True)

    language_competency     = ForeignKey("TypeLanguageCompetency")
    competency_user_desc    = CharField(max_length=255, blank=True, null=True)
    certification_level     = ForeignKey("TypeLanguageCertification")
    certification_user_desc = CharField(max_length=255, blank=True, null=True)
    certification_date      = DateField(blank=True, null=True)
    spoken_level            = ForeignKey("TypeLanguageSpoken")
    spoken_level_user_desc  = CharField(max_length=255, blank=True, null=True)
    written_level           = ForeignKey("TypeLanguageWritten")
    written_level_user_desc = CharField(max_length=255, blank=True, null=True)


# ==== DROPDOWN OPTION MODELS ===================================================================

class TypeIndustrySector(Model):
    language         = ForeignKey(Language)
    description_intl = CharField(max_length=255)
    description_eng  = CharField(max_length=255)
    ordering         = IntegerField()

class TypeLanguageCertification(Model):
    language         = ForeignKey(Language)
    description_intl = CharField(max_length=255)
    description_eng  = CharField(max_length=255)
    ordering         = IntegerField()

class TypeLanguageCompetency(Model):
    language         = ForeignKey(Language)
    description_intl = CharField(max_length=255)
    description_eng  = CharField(max_length=255)
    ordering         = IntegerField()

class TypeLanguageSpoken(Model):
    language         = ForeignKey(Language)
    description_intl = CharField(max_length=255)
    description_eng  = CharField(max_length=255)
    ordering         = IntegerField()

class TypeLanguageWritten(Model):
    language         = ForeignKey(Language)
    description_intl = CharField(max_length=255)
    description_eng  = CharField(max_length=255)
    ordering         = IntegerField()

class TypeWork(Model):
    language         = ForeignKey(Language)
    description_intl = CharField(max_length=255)
    description_eng  = CharField(max_length=255)
    ordering         = IntegerField()

class TypeResumeStyle(Model):
    language         = ForeignKey(Language)
    style            = IntegerField()
    name_intl        = CharField(max_length=255)
    name_eng         = CharField(max_length=255)
    description_intl = CharField(max_length=255)
    description_eng  = CharField(max_length=255)


# ==== UNUSED  ==================================================================================

class UserLanguage(Model):
    user     = ForeignKey(User)
    language = ForeignKey(Language)

class LanguageNativeList(Model):
    language = ForeignKey(Language)
