from django import forms as f
from dbe.medtrics.models import *

from dbe.shared.utils import *


class SectionForm(f.Form):
    def __init__(self, *args, **kwargs):
        """ Add a field for every question.
            Field may be CharField, IntegerField, ChoiceField, MultipleChoiceField.
            field name is question.order.
        """
        self.section = kwargs.pop("section")()
        super(SectionForm, self).__init__(*args, **kwargs)

        for question in self.section.questions.all():
            atype   = question.answer_type
            choices = question.choices
            kw      = Container(help_text=question.question)

            if atype == "int":
                fld           = f.IntegerField
                kw.max_length = 6

            elif atype == "text":
                fld           = f.CharField
                kw.max_length = question.max_length or 50

            elif atype == "textarea":
                fld           = f.CharField
                kw.widget     = f.Textarea(attrs=dict(cols=50, rows=5))
                kw.max_length = question.max_length or 3000

            elif atype.startswith("radio"):
                fld        = f.ChoiceField
                choices    = [c.strip() for c in choices.split(',')]
                kw.choices = [(c,c) for c in choices]
                kw.widget = f.RadioSelect()

            elif atype.startswith("checkbox"):
                fld        = f.MultipleChoiceField
                choices    = [c.strip() for c in choices.split(',')]
                kw.choices = [(c,c) for c in choices]

            self.fields[str(question.order)] = fld(**kw)
            # raise
