from django import forms as f
from dbe.questionnaire.models import *

null_choice = [("---", "---")]

class SectionForm(f.Form):
    def __init__(self, *args, **kwargs):
        """ Add a field for every question.

            Field may be CharField or ChoiceField; field name is question.order.

            Note: `self.order` keeps a list of field names in right order; probably not really
            necessary since fields are already created in right order and simple iteration in
            template should always (?) work right.  (removed `self.order` for now)
        """
        section = kwargs.pop("section")
        super(SectionForm, self).__init__(*args, **kwargs)

        for question in section.questions.all():
            choices = question.choices
            fld     = f.CharField
            kw      = dict(help_text=question.question)

            if choices:
                choices       = [c.strip() for c in choices.split(',')]
                choices       = null_choice + [(c,c) for c in choices]
                fld           = f.ChoiceField
                kw["choices"] = choices
            else:
                kw["max_length"] = 200

            self.fields[str(question.order)] = fld(**kw)
from string import join
from django.db.models import *
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from dbe.shared.utils import *

link = "<a href='%s'>%s</a>"


class Questionnaire(BasicModel):
    name = CharField(max_length=60, unique=True)

    def __unicode__(self):
        return self.name

    def section_links(self):
        section_url = "admin:questionnaire_section_change"
        lst         = [(c.pk, c.name) for c in self.sections.all()]
        lst         = [ (reverse2(section_url, pk), name) for pk, name in lst ]
        return join([link % c for c in lst], ', ')
    section_links.allow_tags = True


class UserQuestionnaire(BasicModel):
    user          = ForeignKey(User, related_name="questionnaires", blank=True, null=True)
    questionnaire = ForeignKey(Questionnaire, related_name="user_questionnaires", blank=True, null=True)
    created       = DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return "%s - %s" % (self.user, self.questionnaire)

    class Meta:
        ordering = ["user", "created"]


class Section(BasicModel):
    """Container for a few questions, shown on a single page."""
    name          = CharField(max_length=60, blank=True, null=True)
    questionnaire = ForeignKey(Questionnaire, related_name="sections", blank=True, null=True)
    order         = IntegerField()

    class Meta:
        ordering        = ["order"]
        unique_together = [["questionnaire", "order"]]

    def __unicode__(self):
        n = (' ' + self.name) if self.name else ''
        return "[%s] (%s)%s" % (self.questionnaire, self.order, n)

    def title(self):
        n = self.name
        return "(%s)%s" % (self.order, (' ' + n) if n else '')



class Question(BasicModel):
    question    = CharField(max_length=200)
    choices     = CharField(max_length=500, blank=True, null=True)
    answer_type = CharField(max_length=6, choices=(("str", "str"), ("int", "int")))
    section     = ForeignKey(Section, related_name="questions", blank=True, null=True)
    order       = IntegerField()

    class Meta:
        ordering        = ["order"]
        unique_together = [["section", "order"]]

    def __unicode__(self):
        return "%s: %s" % (self.section, self.question)


class Answer(BasicModel):
    answer             = CharField(max_length=200)
    question           = ForeignKey(Question, related_name="answers", blank=True, null=True)
    user_questionnaire = ForeignKey(UserQuestionnaire, related_name="answers", blank=True, null=True)

    def __unicode__(self):
        return "%s - %s" % (self.user_questionnaire, self.answer)

    class Meta:
        ordering = ["question__section__order", "question__order"]
from operator import itemgetter
from collections import OrderedDict

from dbe.shared.utils import *
from dbe.questionnaire.models import *
from dbe.questionnaire.forms import *
from dbe.classviews.edit import *
from dbe.classviews.list import *
from dbe.classviews.detail import *


class Questionnaires(ListView):
    model               = Questionnaire
    context_object_name = "questionnaires"
    template_name       = "questionnaires.html"

class UserQuest(DetailView):
    model               = UserQuestionnaire
    context_object_name = "user_quest"
    template_name       = "user-quest.html"

class UserQuests(ListView):
    model               = UserQuestionnaire
    context_object_name = "user_quests"
    template_name       = "user-quests.html"

    def get_queryset(self):
        quest = Questionnaire.obj.get(pk=self.args[0])
        return super(UserQuests, self).get_queryset().filter(questionnaire=quest)


class QuestStats(DetailView2):
    model               = Questionnaire
    context_object_name = "quest_stats"
    template_name       = "quest-stats.html"

    def stats(self):
        """Calculate statistics for current questionnaire."""
        user_quests = UserQuestionnaire.obj.filter(questionnaire=self.object)
        d           = DefaultOrderedDict

        #             quests    sections  questions answers:nums
        quests      = d( lambda:d( lambda:d( lambda:d(int) ) ) )

        for user_quest in user_quests:
            quest = user_quest.questionnaire.name

            # add each answer in user questionnaire to respective sections sub-dict, add to counter
            for answer in user_quest.answers.all():
                question = answer.question
                answer   = answer.answer
                q        = question.question
                section  = question.section.name

                quests[quest][section][q][answer] += 1

        # sort to have most frequent answers first
        for quest in quests.values():
            for section in quest.values():
                for name, question in section.items():
                    answers       = sorted(question.items(), key=itemgetter(1), reverse=True)
                    section[name] = OrderedDict(answers)

        return defdict_to_odict(quests)

    def add_context(self, **kwargs):
        return dict(stats=self.stats())


class ViewQuest(FormView):
    """View questions in a questionnaire section."""
    template_name = "quest.html"

    def get_form(self, form_class):
        """Get current section (container), init the form based on questions in the section."""
        pk            = self.kwargs["questionnaire"]
        sn            = int(self.kwargs.get("section", 1))
        quest         = Questionnaire.obj.get(pk=pk)
        self.sections = Section.obj.filter(questionnaire=quest)
        section       = self.sections[sn-1]

        self.snum, self.quest, self.section = sn, quest, section
        return SectionForm(section=section, **self.get_form_kwargs())

    def form_valid(self, form):
        """Create user answer records from form data."""
        data   = form.cleaned_data
        user   = self.request.user
        quest  = self.quest
        uquest = UserQuestionnaire.obj.get_or_create(questionnaire=quest, user=user)[0]

        for order, value in data.items():
            question = self.section.questions.get(order=int(order))
            answer = Answer.obj.get_or_create(user_questionnaire=uquest, question=question)[0]
            answer.update(answer=value)

        # redirect to the next section or to 'done' page
        if self.snum >= self.sections.count():
            return redir("done")
        else:
            return redir("questionnaire", questionnaire=quest.pk, section=self.snum+1)
