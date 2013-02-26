# -*- coding: utf-8 -*-
import re
import locale
from django import template
from django.template.defaultfilters import stringfilter
from django.conf import settings

locale.setlocale(locale.LC_ALL, '')
register = template.Library()

@register.filter()
def currency(value):
    return locale.currency(value, grouping=True)

@register.filter
@stringfilter
def truncate(value, max_length):
    try:
        max_length = int(max_length)
        if max_length < len(value):
            return str(value)[:max_length] + '…'
        else:
            return value
    except Exception, e:
        return e
truncate.is_safe = True

numeric_test = re.compile("^\d+$")

@register.filter
def getattribute(value, arg):
    """Gets an attribute of an object dynamically from a string name."""
    if hasattr(value, str(arg)):
        return getattr(value, arg)
    elif hasattr(value, 'has_key') and value.has_key(arg):
        return value[arg]
    elif numeric_test.match(str(arg)) and len(value) > int(arg):
        return value[int(arg)]
    else:
        return settings.TEMPLATE_STRING_IF_INVALID
