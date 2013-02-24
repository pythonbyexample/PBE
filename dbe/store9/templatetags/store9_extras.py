# -*- coding: utf-8 -*-
import locale
from django import template
from django.template.defaultfilters import stringfilter

locale.setlocale(locale.LC_ALL, '')
register = template.Library()

@register.filter()
def currency(value):
    return locale.currency(value, grouping=True)

# there's not actually a 'truncate' filter but there ought to be
# so I'm appending '2' to the name in case that gets added at some point
# adapted from a comment here: http://blog.awarelabs.com/2008/dynamic-length-truncate-tag/
# Django auto-converts to '&hellip;' ... or perhaps '&#8230;'
@register.filter
@stringfilter
def truncate2(value, arg):
    try:
        max_length = int(arg)
        if max_length < len(value):
            return str(value)[:max_length] + '…'
        else:
            return value
    except Exception, e:
        return e
truncate2.is_safe = True
