# -*- coding: utf-8 -*-
# Imports {{{
import time
from string import join
from collections import defaultdict
from time import localtime, strftime, mktime

from django.core.context_processors import csrf
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.template import RequestContext, Template, Context, loader, TemplateSyntaxError
from django.db.models import Q
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.contrib import messages
from django.utils.html import strip_tags, escape
from django.views.generic import ListView, FormView, TemplateView
from django.views.generic.list import *
from django.views.generic.edit import *

from businesstest.models import *
from businesstest.forms import *
# }}}

class Test:
    def __init__(self, request):
        self.request = request

    def test(self, num):
        num      = int(num)
        task     = Task.objects.all()[num-1]
        eset, _  = Set.objects.get_or_create(user=self.request.user, finished=False)
        entry, _ = Entry.objects.get_or_create(eset=eset, task=task)
        formcls  = forms[task.tasktype]
        options  = str(task.options).split("\r\n") if task.options else None
        if options:
            options = [(o,o) for o in options]

        if self.request.method == "POST":
            form = formcls(self.request.POST, options=options)
            if form.is_valid():
                if task.tasktype == "multi":
                    answer = []
                    for x in range(len(options)):
                        answer.append(form.cleaned_data["answer%s" % x])
                    answer = join(answer, '\n')
                else:
                    answer = form.cleaned_data["answer"]

                # save time_taken
                sec = time.time() - mktime(entry.created.timetuple())
                entry.update(answer=answer, time_taken=sec2hms(sec))

                # redirect to next task OR finish
                if num+1 <= Task.objects.count():
                    return redir("businesstest.views.test", [num+1])
                else:
                    eset.update(finished=True)
                    return redir("businesstest.views.test_done")
        else:
            form = formcls(options=options)

        return render(self.request, "test.html", form=form, task=task, num=num)

@login_required
def test(request, num=1):
    return Test(request).test(num)

def test_done(request):
    return HttpResponse("Thanks for taking this test!")


########  UTILITY  ################################################################################


def redir(to, args=None):
    if not (to.startswith('/') or to.startswith("http://")):
        to = reverse(to, args=(args or []))
    return HttpResponseRedirect(to)

def add_csrf(request, **kwargs):
    """Add CSRF to dictionary and wrap in a RequestContext (needed for context processor!)."""
    d = dict(user=request.user, **kwargs)
    d.update(csrf(request))
    return RequestContext(request, d)

def render(request, tpl, **kwargs):
    return render_to_response(tpl, add_csrf(request, **kwargs))

def sec2hms(sec):
    m, s = divmod(sec, 60)
    h, m = divmod(m, 60)
    return "%d:%02d:%02d" % (h, m, s)
