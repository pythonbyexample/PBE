from pprint import pprint
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse, reverse_lazy
from django.contrib.admin.views.decorators import staff_member_required
from django.forms import forms
from django.core.mail import send_mail

from dbe.shared.utils import *
from dbe.issues.models import *
from dbe.issues.forms import *

from dbe.generic.edit import *
from dbe.generic.list import *
from dbe.cbv.list import DetailListCreateView


@staff_member_required
def update_issue(request, pk, mode=None, action=None):
    """AJAX view, toggle Done on/off or delete an issue."""
    issue = Issue.obj.get(pk=pk)
    if mode == "delete":
        Issue.obj.filter(pk=pk).delete()
        return HttpResponseRedirect( reverse("admin:issues_issue_changelist") )
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


class UpdateIssue(UpdateView):
    modelform_model = Issue
    modelform_class = IssueForm
    msg_tpl         = "Issue '%s' was updated <%s%s>\n\n%s"
    item_name       = "issue"

    def get_success_url(self):
        return reverse2("issue", pk=self.object.pk)

    def modelform_valid(self, form):
        """ If form was changed, send notification email the (new) issue owner.

            Note: at the start of the function, FK relationships are already updated in `self.object`,
                  probably in form.is_valid()?
        """
        if form.has_changed() and self.modelform_object.owner:
            notify_owner(self.request, self.modelform_object, "Issue Updated", self.msg_tpl)
        return super(UpdateIssue, self).modelform_valid(form)


class UpdateComment(UpdateView):
    """Update a comment."""
    modelform_model = Comment
    modelform_class = CommentForm
    item_name       = "comment"

    def get_success_url(self):
        return reverse2("issue", pk=self.object.issue.pk)


class ViewIssue(DetailListCreateView):
    """View issue, comments and new comment form."""
    detail_model               = Issue
    list_model                 = Comment
    modelform_class            = CommentForm
    related_name               = "comments"
    detail_context_object_name = "issue"
    msg_tpl                    = "Comment was added to the Issue '%s' <%s%s>\n\n%s"
    template_name              = "issue.html"

    def get_modelform_kwargs(self):
        kwargs  = super(ViewIssue, self).get_modelform_kwargs()
        comment = Comment(issue=self.detail_object, creator=self.request.user)
        return dict(kwargs, instance=comment)

    def modelform_valid(self, form):
        """Send notification email to the issue owner."""
        resp    = super(ViewIssue, self).modelform_valid(form)
        obj     = self.object
        notify_owner(self.request, obj.issue, "New Comment", self.msg_tpl, comment_body=obj.body)
        return resp


class AddIssues(FormSetView):
    """Create new issues."""
    formset_model      = Issue
    formset_form_class = IssueForm
    item_name          = "issue"
    success_url        = reverse_lazy("admin:issues_issue_changelist")
    msg_tpl            = "New Issue '%s' was created <%s%s>\n\n%s"
    extra              = 2
    template_name      = "add_issues.html"

    def form_valid(self, formset):
        for form in formset:
            if form.has_changed():
                form.save()
                notify_owner(self.request, form.instance, "New Issue", self.msg_tpl)
        return HttpResponseRedirect(self.success_url)


def notify_owner(request, obj, title, msg_tpl, comment_body=''):
    serv_root = request.META["HTTP_ORIGIN"]
    url       = reverse2("issue", pk=obj.pk)
    lst       = [obj.name, serv_root, url, comment_body]
    msg       = msg_tpl % tuple(lst)

    if obj.owner:
        send_mail(title, msg, "IssuesApp", [obj.owner.email], fail_silently=False)
