from operator import itemgetter
from collections import OrderedDict

from dbe.shared.utils import *
from dbe.questionnaire.models import *
from dbe.questionnaire.forms import *
from dbe.classviews.edit import *
from dbe.classviews.list import *
from dbe.classviews.detail_custom import *


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
