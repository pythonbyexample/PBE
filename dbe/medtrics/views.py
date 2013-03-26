from operator import itemgetter
from collections import OrderedDict

from django.forms.formsets import formset_factory, BaseFormSet, all_valid

from dbe.shared.utils import *
from dbe.medtrics.models import *
from dbe.medtrics.forms import *

from dbe.mcbv import DetailView, FormView, ListView, FormSetView
from dbe.mcbv.list_custom import ListRelated

def item_gen(items):
    for i in items: yield i


class MedForms(ListView):
    list_model    = MedForm
    template_name = "medforms.html"

class FormSubmissions(ListRelated):
    detail_model  = MedForm
    list_model    = FormSubmission
    related_name  = "submissions"
    template_name = "submissions.html"

class Submission(DetailView):
    detail_model  = FormSubmission
    template_name = "submission.html"


class Stats(DetailView):
    detail_model  = MedForm
    template_name = "medtrics/stats.html"

    def stats(self):
        submissions = FormSubmission.obj.filter(form=self.detail_object)
        d           = DefaultOrderedDict
        #             forms     sections  questions answers:nums
        medforms    = d( lambda:d( lambda:d( lambda:d(int) ) ) )

        for submission in submissions:
            medform = submission.form.name

            # add each answer in user questionnaire to respective sections sub-dict, add to counter
            for answer in submission.answers.all():
                question = answer.question
                answer   = answer.answer
                q        = question.question
                section  = question.section.name

                medforms[medform][section][q][answer] += 1

        # sort to have most frequent answers first
        for medform in medforms.values():
            for section in medform.values():
                for name, question in section.items():
                    answers       = sorted(question.items(), key=itemgetter(1), reverse=True)
                    section[name] = OrderedDict(answers)

        return defdict_to_odict(medforms)


class ViewMedForm(DetailView, FormSetView):
    detail_model       = MedForm
    formset_form_class = SectionForm
    success_url        = "medforms"
    template_name      = "medform.html"

    def get_formset(self, form_class=None):
        """We need to pass the items generator to make sure each form gets the right section instance."""
        form_class   = SectionForm
        sections     = self.detail_object.sections.all()
        section_gen  = item_gen(sections)
        Formset      = formset_factory(form_class, extra=sections.count(), can_delete=self.can_delete)
        Formset.form = staticmethod(curry(form_class, section=lambda: section_gen.next()))
        return Formset(**self.get_formset_kwargs())

    def formset_valid(self, formset):
        """Create user answer records using form data."""
        submission = FormSubmission.obj.create(form=self.detail_object, user=self.user)

        for form in formset:
            for order, value in form.cleaned_data.items():
                question = form.section.questions.get(order=int(order))
                if question.answer_type.startswith("checkbox"):
                    value = ", ".join(value)

                Answer.obj.create(submission=submission, question=question, answer=value)
        return redir(self.success_url)
