from operator import itemgetter
from collections import OrderedDict

from dbe.shared.utils import *
from dbe.questionnaire.models import *
from dbe.questionnaire.forms import *

from dbe.generic.detail import *
from dbe.generic.list import *
from dbe.generic.edit import *
from dbe.cbv.list_custom import ListRelated


class Questionnaires(ListView):
    list_model               = Questionnaire
    list_context_object_name = "questionnaires"
    template_name            = "questionnaires.html"

class UserQuest(DetailView):
    detail_model               = UserQuestionnaire
    detail_context_object_name = "user_quest"
    template_name              = "user-quest.html"

class UserQuests(ListRelated):
    detail_model             = Questionnaire
    list_model               = UserQuestionnaire
    list_context_object_name = "user_quests"
    related_name             = "user_questionnaires"
    template_name            = "user-quests.html"


class QuestStats(DetailView):
    detail_model               = Questionnaire
    detail_context_object_name = "quest_stats"
    template_name              = "quest-stats.html"

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
            return redir("questionnaire", dpk=quest.pk, section=self.snum+1)
