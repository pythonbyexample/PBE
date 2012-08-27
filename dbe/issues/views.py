from pprint import pprint
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.contrib.admin.views.decorators import staff_member_required
from django.forms import forms
from django.utils.functional import curry
from django.core.mail import send_mail

from dbe.shared.utils import *
from dbe.issues.models import *
from dbe.issues.forms import *
from dbe.classviews.edit import *
from dbe.classviews.list import *


@staff_member_required
def update_issue(request, pk, mode=None, action=None):
    """Toggle Done on/off or delete an issue."""
    issue = Issue.obj.get(pk=pk)
    if mode == "delete":
        Issue.obj.filter(pk=pk).delete()
        return HttpResponseRedirect(reverse("admin:issues_issue_changelist"))
    else:
        if mode == "progress" : val = int(action)
        else                  : val = bool(action=="on")
        setattr(issue, mode, val)
        issue.save()
        return HttpResponse('')

@staff_member_required
def delete_comment(request, pk):
    Comment.obj.get(pk=pk).delete()
    return HttpResponseRedirect(referer(request))


class UpdateIssue(UpdateView2):
    """Update an issue."""
    model      = Issue
    form_class = IssueForm
    item_name  = "issue"

    def get_success_url(self):
        return reverse2("issue", pk=self.object.pk)

    def form_valid(self, form):
        """ If form was changed, send notification email the (new) issue owner.

            Note: at the start of the function, FK relationships are already updated in `self.object`,
                  probably in form.is_valid()?
        """
        if form.has_changed() and self.object.owner:
            msg_tpl = "Issue '%s' was updated <%s%s>"
            notify_owner(self.request, self.object, "Issue Updated", msg_tpl)
        return super(UpdateIssue, self).form_valid(form)


class UpdateComment(UpdateView):
    """Update a comment."""
    model      = Comment
    form_class = CommentForm
    item_name  = "comment"

    def get_success_url(self):
        return reverse2("issue", pk=self.object.issue.pk)

class ViewIssue(DetailListCreateView):
    """View issue, comments and new comment form."""
    main_model          = Issue       # model of object to display
    list_model          = Comment     # related obj to list
    related_name        = "comments"  # attribute name linking main object to related obj
    form_class          = CommentForm
    context_object_name = "issue"
    template_name       = "issue.html"

    def get_form_kwargs(self):
        kwargs = super(ViewIssue, self).get_form_kwargs()
        comment = Comment(issue=self.get_mainobj(), creator=self.request.user)
        return updated(kwargs, dict(instance=comment))

    def form_valid(self, form):
        """Send notification email to the issue owner."""
        resp    = super(ViewIssue, self).form_valid(form)
        obj     = self.object
        msg_tpl = "Comment was added to the Issue '%s' <%s%s>\n\n%s"
        notify_owner(self.request, obj.issue, "New Comment", msg_tpl, comment_body=obj.body)
        return resp


class AddIssues(CreateWithFormset):
    """Create new issues."""
    model            = Issue
    form_class       = IssueForm
    item_name        = "issue"
    success_url_name = "admin:issues_issue_changelist"
    template_name    = "add_issues.html"
    extra            = 2

    def form_valid(self, formset):
        for form in formset:
            if form.has_changed():
                form.save()
                msg_tpl = "New Issue '%s' was created <%s%s>"
                notify_owner(self.request, form.instance, "New Issue", msg_tpl)
        return HttpResponseRedirect(reverse(self.success_url_name))


def notify_owner(request, obj, title, msg_tpl, comment_body=None):
    serv_root = request.META["HTTP_ORIGIN"]
    lst       = [obj.name, serv_root, reverse2("issue", pk=obj.pk)]
    if comment_body: lst.append(comment_body)

    msg = msg_tpl % tuple(lst)
    if obj.owner:
        send_mail(title, msg, "IssuesApp", [obj.owner.email], fail_silently=False)
