from string import join
from django.db.models import *
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from ordered_model.models import OrderedModel

from dbe.shared.utils import *

link = "<a href='%s'>%s</a>"

answer_choices = (
                  ("int"       , "Number Field"),
                  ("text"      , "Text Field"),
                  ("textarea"  , "Text Area"),
                  ("radio1"    , "Radio (single choice)"),
                  ("radio2"    , "Radio (single choice) - large"),
                  ("checkbox1" , "Checkbox (multiple choice)"),
                  ("checkbox2" , "Checkbox (multiple choice) - large"),
                  )


class Milestone(BaseModel):
    name = CharField(max_length=60, blank=True, null=True)

    def __unicode__(self):
        return self.name


class MedForm(BaseModel):
    name = CharField(max_length=60, unique=True)

    def __unicode__(self):
        return self.name

    def get_absolute_url(self, section=1):
        return reverse2("medform", self.pk, section)

    def section_links(self):
        section_url = "admin:medtrics_section_change"
        lst         = [(c.pk, c.name) for c in self.sections.all()]
        lst         = [ (reverse2(section_url, pk), name) for pk, name in lst ]
        return ", ".join( [link % c for c in lst] )
    section_links.allow_tags = True


class FormSubmission(BaseModel):
    user    = ForeignKey(User, related_name="submissions", blank=True, null=True)
    form    = ForeignKey(MedForm, related_name="submissions", blank=True, null=True)
    created = DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return "%s - %s" % (self.user, self.form)

    class Meta:
        ordering = ["user", "created"]


class Section(OrderedModel, BaseModel):
    """Container for a few questions."""
    name        = CharField(max_length=50)
    description = TextField(max_length=300, blank=True, null=True)
    medform     = ForeignKey(MedForm, related_name="sections", blank=True, null=True)

    def __unicode__(self):
        return "[%s] (%s) %s" % (self.medform, self.order, self.name or '')

    def title(self):
        return "(%s) %s" % (self.order, self.name or '')


class Question(OrderedModel, BaseModel):
    question    = CharField(max_length=200)
    choices     = CharField(max_length=500, blank=True, null=True)
    answer_type = CharField(max_length=15, choices=answer_choices)
    max_length  = IntegerField(blank=True, null=True)
    milestone   = ManyToManyField(Milestone, blank=True, null=True)
    section     = ForeignKey(Section, related_name="questions", blank=True, null=True)

    class Meta:
        unique_together = [["section", "order"]]

    def __unicode__(self):
        return "%s: %s" % (self.section, self.question)


class Answer(BaseModel):
    answer      = CharField(max_length=300, blank=True, null=True)
    text_answer = TextField(max_length=3000, blank=True, null=True)
    num_answer  = IntegerField(blank=True, null=True)
    question    = ForeignKey(Question, related_name="answers", blank=True, null=True)
    submission  = ForeignKey(FormSubmission, related_name="answers", blank=True, null=True)

    def __unicode__(self):
        return "%s - %s" % (self.submission, self.answer)

    class Meta:
        ordering = ["question__section__order", "question__order"]
