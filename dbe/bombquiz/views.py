from django.core.urlresolvers import reverse, reverse_lazy
from django.db.models import Count, Avg
from django.http import Http404

from dbe.shared.utils import *
from dbe.bombquiz.models import *
from dbe.bombquiz.forms import *
from dbe.classviews.edit import *
from dbe.classviews.base_custom import *

seconds       = 30
lose_question = 20


class NewPlayer(CreateView):
    model               = PlayerRecord
    form_class          = NewPlayerForm
    context_object_name = "new_player"
    template_name       = "question.html"
    success_url         = reverse_lazy("question")

    def form_valid(self, form):
        url = super(NewPlayer, self).form_valid(form)
        self.request.session.update( dict(player_record=self.object, question=1, left=seconds) )
        return url


class Done(TemplateView2):
    template_name = "bombquiz/done.html"

    def add_context(self, **kwargs):
        return dict(left=self.request.session.get("left"))


class Stats(TemplateView2):
    template_name = "stats.html"

    def add_context(self, **kwargs):
        ans = PlayerRecord.obj.filter(passed=False).annotate(anum=Count("answers"))
        return dict( ans_failed=ans.aggregate(avg=Avg("anum")) )


class QuestionView(FormView):
    """View question."""
    template_name = "question.html"

    def get_form(self, form_class):
        """Get current section (container), init the form based on questions in the section."""
        session     = self.request.session
        self.player = session.get("player_record", None)
        self.qn     = session.get("question", 1)
        if not self.player: raise Http404

        self.questions = Question.obj.all()
        if not self.questions: raise Http404
        self.question = self.questions[self.qn-1]
        return QuestionForm(question=self.question, **self.get_form_kwargs())

    def form_valid(self, form):
        """Create user answer records from form data."""
        session = self.request.session
        left    = session.get("left", seconds)
        answer  = form.cleaned_data.get("answer")
        correct = bool(answer == self.question.answer)

        # subtract time left and create the answer object
        if not correct:
            left -= lose_question
            session["left"] = left
        Answer.obj.create(question=self.question, player_record=self.player, correct=correct, answer=answer)

        # redirect to the next question or to 'done' page
        if self.qn >= self.questions.count() or left <= 0:
            self.player.update( passed=bool(left>0) )
            return redir("done")
        else:
            session["question"] = session.get("question", 1) + 1
            return redir("question")

    def get_context_data(self, **kwargs):
        c = super(QuestionView, self).get_context_data(**kwargs)
        session = self.request.session
        return updated(c, dict(qnum=self.qn, total=self.questions.count(), left=session["left"]))
