from django.db import models
from django.db.models import *
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

from languages.settings import MEDIA_URL

class BaseManager(manager.Manager):
    def get_or_none(self, **kwargs):
        try                            : return self.get(**kwargs)
        except self.model.DoesNotExist : return None


class Language(Model):
    obj         = objects = BaseManager()
    description = CharField(max_length=40, blank=True, null=True)
    code        = CharField(max_length=10)
    name_eng    = CharField(max_length=255)
    name_native = CharField(max_length=255)
    iso639_1    = CharField(max_length=10, blank=True, null=True)
    iso639_2T   = CharField(max_length=10, blank=True, null=True)
    iso639_2B   = CharField(max_length=10, blank=True, null=True)
    iso639_X    = CharField(max_length=10, blank=True, null=True)
    direction   = IntegerField(default=0)
    text_align  = IntegerField(default=0)

    def __unicode__(self):
        return unicode(self.name_eng)


class LanguageProfile(Model):
    obj                     = objects = BaseManager()
    user                    = ForeignKey(User)
    profile_language        = ForeignKey(Language, verbose_name=_("Profile Language"))
    languages               = CharField(_("Language(s)"), max_length=255)
    description_eng         = CharField(_("Description (english)"), max_length=255)
    description_native      = CharField(_("Description (native)"), max_length=255, blank=True, null=True)
    years_experience        = CharField(_("Experience (years)"), max_length=10, blank=True, null=True)

    language_competency     = ForeignKey("TypeLanguageCompetency", verbose_name=_("Language Competency"), blank=True, null=True)
    competency_user_desc    = CharField(_("Language Competency (desc)"), max_length=255, blank=True, null=True)
    certification_level     = ForeignKey("TypeLanguageCertification", verbose_name=_("Language Certification"), blank=True, null=True)
    certification_user_desc = CharField(_("Language Certification (desc)"), max_length=255, blank=True, null=True)
    certification_date      = DateField(_("Certification Date"), blank=True, null=True)
    spoken_level            = ForeignKey("TypeLanguageSpoken", verbose_name=_("Language Spoken"), blank=True, null=True)
    spoken_level_user_desc  = CharField(_("Language Spoken (desc)"), max_length=255, blank=True, null=True)
    written_level           = ForeignKey("TypeLanguageWritten", verbose_name=_("Language Written"), blank=True, null=True)
    written_level_user_desc = CharField(_("Language Written (desc)"), max_length=255, blank=True, null=True)

    def __unicode__(self):
        return unicode("%s profile" % self.profile_language)

    def flag(self):
        return Flag.obj.get(language=self.profile_language)


class Flag(Model):
    obj         = objects = BaseManager()
    language    = ForeignKey(Language)
    icon        = ImageField(upload_to="flags/", max_length=255)
    description = CharField(max_length=255, blank=True, null=True)
    information = CharField(max_length=255, blank=True, null=True)

    def img(self):
        return "<img src='%s%s' alt='%s'>" % (MEDIA_URL, self.icon.name, self.language.name_eng)
    img.tags_allowed = True

    def __unicode__(self):
        return unicode(self.language)


class RIDocumentation(Model):
    obj         = objects = BaseManager()
    user        = ForeignKey(User)
    language    = ForeignKey(Language)
    file        = FileField(upload_to="docs/", max_length=255)
    title       = CharField(max_length=255)
    description = TextField(max_length=2000)

class RIEmploymentHistory(Model):
    obj               = objects = BaseManager()
    user              = ForeignKey(User)
    language          = ForeignKey(Language)
    employer          = CharField(max_length=255)
    position_title    = CharField(max_length=255, blank=True, null=True)
    position_level    = CharField(max_length=255, blank=True, null=True)
    location          = CharField(max_length=255, blank=True, null=True)
    work_type         = ForeignKey("TypeWork")
    commencement_date = DateField(blank=True, null=True)
    completion_date   = DateField(blank=True, null=True)
    duties            = TextField(max_length=2000, blank=True, null=True)

class UserSettings(Model):
    obj                               = objects = BaseManager()
    user                              = ForeignKey(User)
    primary_language                  = ForeignKey(Language, related_name="setting_languages")
    resume_style                      = ForeignKey("TypeResumeStyle")

    display_primary_language          = BooleanField(default=False)
    display_mutiple_languages         = BooleanField(default=False)
    display_single_language           = BooleanField(default=False)
    primary_virtual_keyboard_language = ForeignKey(Language)
    display_primary_virtual_keyboard  = BooleanField(default=False)

# ==== DROPDOWN OPTION MODELS ===================================================================

class TypeIndustrySector(Model):
    obj              = objects = BaseManager()
    language         = ForeignKey(Language)
    description_intl = CharField(max_length=255)
    description_eng  = CharField(max_length=255)
    ordering         = IntegerField()

    def __unicode__(self):
        return self.description_eng

class TypeLanguageCertification(Model):
    obj              = objects = BaseManager()
    language         = ForeignKey(Language)
    description_intl = CharField(max_length=255)
    description_eng  = CharField(max_length=255)
    ordering         = IntegerField()

    def __unicode__(self):
        return self.description_eng

class TypeLanguageCompetency(Model):
    obj              = objects = BaseManager()
    language         = ForeignKey(Language)
    description_intl = CharField(max_length=255)
    description_eng  = CharField(max_length=255)
    ordering         = IntegerField()

    def __unicode__(self):
        return self.description_eng

class TypeLanguageSpoken(Model):
    obj              = objects = BaseManager()
    language         = ForeignKey(Language)
    description_intl = CharField(max_length=255)
    description_eng  = CharField(max_length=255)
    ordering         = IntegerField()

    def __unicode__(self):
        return self.description_eng

class TypeLanguageWritten(Model):
    obj              = objects = BaseManager()
    language         = ForeignKey(Language)
    description_intl = CharField(max_length=255)
    description_eng  = CharField(max_length=255)
    ordering         = IntegerField()

    def __unicode__(self):
        return self.description_eng

class TypeWork(Model):
    obj              = objects = BaseManager()
    language         = ForeignKey(Language)
    description_intl = CharField(max_length=255)
    description_eng  = CharField(max_length=255)
    ordering         = IntegerField()

    def __unicode__(self):
        return self.description_eng

class TypeResumeStyle(Model):
    obj              = objects = BaseManager()
    language         = ForeignKey(Language)
    style            = IntegerField(unique=True)
    name_intl        = CharField(max_length=255)
    name_eng         = CharField(max_length=255)
    description_intl = CharField(max_length=255, blank=True, null=True)
    description_eng  = CharField(max_length=255, blank=True, null=True)

    def __unicode__(self):
        return self.description_eng or "style%02d" % self.style
