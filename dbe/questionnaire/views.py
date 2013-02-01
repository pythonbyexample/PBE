from operator import itemgetter
from collections import OrderedDict

from dbe.shared.utils import *
from dbe.questionnaire.models import *
from dbe.questionnaire.forms import *

from dbe.mcbv.detail import DetailView
from dbe.mcbv.edit import FormView
from dbe.mcbv.list_custom import ListView, ListRelated


class Questionnaires(ListView):
    list_model    = Questionnaire
    template_name = "questionnaires.html"

class UserQuest(DetailView):
    detail_model  = UserQuestionnaire
    template_name = "user-quest.html"

class UserQuests(ListRelated):
    detail_model  = Questionnaire
    list_model    = UserQuestionnaire
    related_name  = "user_questionnaires"
    template_name = "user-quests.html"


class QuestStats(DetailView):
    detail_model  = Questionnaire
    template_name = "quest-stats.html"

    def stats(self):
        user_quests = UserQuestionnaire.obj.filter(questionnaire=self.detail_object)
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


class ViewQuestionnaire(DetailView, FormView):
    form_class    = SectionForm
    detail_model  = Questionnaire
    template_name = "quest.html"

    def get_form_kwargs(self):
        """Get current section (container), add it to kwargs; init some view instance vars."""
        kwargs        = super(ViewQuestionnaire, self).get_form_kwargs()
        object        = self.get_detail_object()
        sn            = int(self.kwargs.get("section", 1))
        self.sections = Section.obj.filter(questionnaire=object)
        section       = self.sections[sn-1]

        self.snum, self.quest, self.section = sn, object, section
        return dict(kwargs, section=section)

    def form_valid(self, form, *args):
        """Create user answer records from form data."""
        data   = form.cleaned_data
        quest  = self.quest
        stotal = self.sections.count()
        uquest = UserQuestionnaire.obj.get_or_create(questionnaire=quest, user=self.user)[0]

        for order, value in data.items():
            question = self.section.questions.get(order=int(order))
            answer   = Answer.obj.get_or_create(user_questionnaire=uquest, question=question)[0]
            answer.update(answer=value)

        # redirect to the next section or to 'done' page
        if self.snum >= stotal : return redir("done")
        else                   : return redir( quest.get_absolute_url(self.snum+1) )
