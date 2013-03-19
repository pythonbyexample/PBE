from django.contrib import admin
from dbe.medtrics.models import *


class SectionInline(admin.TabularInline):
    model = Section
    extra = 5

class QuestionInline(admin.TabularInline):
    model = Question
    extra = 4


class MilestoneAdmin(admin.ModelAdmin):
    list_display = ["name"]

class MedFormAdmin(admin.ModelAdmin):
    list_display = ["name"]
    inlines      = [SectionInline]

class QuestionAdmin(admin.ModelAdmin):
    list_display = "question choices answer_type section".split()

class FormSubmissionAdmin(admin.ModelAdmin):
    list_display = "user form created".split()

class AnswerAdmin(admin.ModelAdmin):
    list_display = "answer question submission".split()
    list_filter  = "submission answer".split()


class SectionAdmin(admin.ModelAdmin):
    list_display = "name medform".split()
    inlines      = [QuestionInline]


admin.site.register(Milestone, MilestoneAdmin)
admin.site.register(MedForm, MedFormAdmin)
admin.site.register(FormSubmission, FormSubmissionAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Answer, AnswerAdmin)
admin.site.register(Section, SectionAdmin)
