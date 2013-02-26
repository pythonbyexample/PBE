# -*- coding: utf-8 -*-

# Imports {{{
import re
from types import *

from django.utils.html import escape
from django.forms import *
from django.contrib.auth.models import User, Group

from businesstest.models import Message
# }}}

oldclean = fields.CharField.clean

def stripclean(self, value):
    """Strip all CharField fields before cleaning."""
    if isinstance(value, basestring):
        value = value.strip()
    return oldclean(self, value)


def add_required_label_tag(original_function):
    """Adds the 'required' CSS class and an asterisks to required field labels."""
    def required_label_tag(self, contents=None, attrs=None):
        contents = contents or escape(self.label)
        if self.field.required:
            attrs = {'class': 'required'}
        return original_function(self, contents, attrs)

    return required_label_tag

fields.CharField.clean = stripclean
forms.BoundField.label_tag = add_required_label_tag(forms.BoundField.label_tag)


class EntryForm(Form):
    def __init__(self, *args, **kwargs):
        self._options = kwargs.pop("options", None)
        Form.__init__(self, *args, **kwargs)

class EntryFormSingle(EntryForm):
    answer = CharField(label="answer", widget=Textarea(), required=True)

class EntryFormMulti(EntryForm):
    def __init__(self, *args, **kwargs):
        EntryForm.__init__(self, *args, **kwargs)
        for n, option in enumerate(self._options):
            self.fields["answer%s" % n] = CharField(label=option[1], required=False)

class EntryFormMultiChoice(EntryForm):
    def __init__(self, *args, **kwargs):
        EntryForm.__init__(self, *args, **kwargs)
        self.fields["answer"].choices = self._options
    answer = ChoiceField(label="answer", choices=(), required=True)
