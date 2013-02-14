IssuesApp
=========

This tutorial will show you how to create a simple Issue Tracker app in Django using mcbv
(modular CBVs) library and using the builtin Django admin to handle Issue listings, filtering
and sorting.

Since an issue tracker has a lot of common functionality with a todo list app -- an issue has
priority, progress, closed status, an associated project and tags -- this tutorial can be very
easily adapted to create a Todo List App similar to one that was featured in a previous
iteration of this guide.

You can view or download the code here:

`Browse source files <https://github.com/akulakov/django/tree/master/dbe/>`_

`dbe.tar.gz <https://github.com/akulakov/django/tree/master/dbe.tar.gz>`_

A few custom functions and classes and the MCBV library are used in the tutorials, please look
through the `libraries page <libraries.html>`_ before continuing.

I will focus on the important parts of code in the listings below; I recommend opening the
source files in a separate window to see import lines and other details.

Outline
-------

.. image:: _static/img/fp.gif
    :class: screenshot

.. sourcecode:: python

General architecture of the app will be as follows:

The central model will be called Issue with these fields: name, body, creator, owner, priority,
difficulty, progress, closed toggle, project and tags.

There will be a Project model with creator and project (name) fields and the Tag model with
creator and tag (name) fields; finally a Comment model will have creator, issue and body fields.

There will be four class-based views:

Creation of new issues will be done with AddIssues(FormSetView) view which will also notify
issue owner about each new issue.

Viewing an issue and adding comments will be handled by ViewIssue(DetailListCreateView) --
where List part is needed to show a list of comments; this view will also notify the owner of a
new comment.

UpdateIssue and UpdateComment are two simple views inherited from UpdateView; UpdateIssue will
notify the owner.

There is also a couple of small AJAX function views.


Issue Model
-----------

.. sourcecode:: python

    btn_tpl  = "<div class='%s' id='%s_%s'><img class='btn' src='%simg/admin/icon-%s.gif' /></div>"
    namelink = "<a href='%s'>%s</a> <a style='float:right; font-size:0.6em;' href='%s'>edit</a>"
    dellink  = "<a href='%s'>Delete</a>"


    class Issue(BaseModel):
        name       = CharField(max_length=60)
        creator    = ForeignKey(User, related_name="created_issues", blank=True, null=True)
        body       = TextField(max_length=3000, default='', blank=True)
        body_html  = TextField(blank=True, null=True)

        owner      = ForeignKey(User, related_name="issues", blank=True, null=True)
        priority   = IntegerField(default=0, blank=True, null=True)
        difficulty = IntegerField(default=0, blank=True, null=True)
        progress   = IntegerField(default=0)

        closed     = BooleanField(default=False)
        created    = DateTimeField(auto_now_add=True)
        project    = ForeignKey(Project, related_name="issues", blank=True, null=True)
        tags       = ManyToManyField(Tag, related_name="issues", blank=True, null=True)

        def get_absolute_url(self):
            return reverse2("issue", dpk=self.pk)

        def save(self):
            self.body_html = markdown(self.body)
            super(Issue, self).save()

        def name_(self):
            link    = reverse2("issue", dpk=self.pk)
            editlnk = reverse2("update_issue_detail", mfpk=self.pk)
            return namelink % (link, self.name, editlnk)
        name_.allow_tags = True

        def progress_(self):
            return loader.render_to_string("progress.html", dict(pk=self.pk))
        progress_.allow_tags = True
        progress_.admin_order_field = "progress"

        def closed_(self):
            onoff = "on" if self.closed else "off"
            return btn_tpl % ("toggle closed", 'd', self.pk, MEDIA_URL, onoff)
        closed_.allow_tags = True
        closed_.admin_order_field = "closed"

        def created_(self):
            return self.created.strftime("%b %d %Y")
        created_.admin_order_field = "created"

        def owner_(self):
            return self.owner if self.owner else ''
        owner_.admin_order_field = "owner"

        def project_(self):
            return self.project if self.project else ''
        project_.admin_order_field = "project"

        def delete_(self):
            return dellink % reverse2("update_issue", self.pk, "delete")
        delete_.allow_tags = True

I'm using two special method properties here: allow_tags indicates that an html tag can be
included in the method's return value and admin_order_field specifies the field to use for
sorting in admin, so that clicking on 'closed_' column will sort by closed model field
('closed_' will actually be displayed as 'closed' because the admin hides the underscore).

I am also using markdown.markdown function to allow rich text markup in Issue description.

Progress bar is displayed as a visual bar with 10% increments using some HTML and CSS code in
progress.html which is loaded with django.template.loader.


Other Models
------------

.. sourcecode:: python

    class Project(BaseModel):
        creator = ForeignKey(User, related_name="projects", blank=True, null=True)
        project = CharField(max_length=60)

        def __unicode__(self):
            return self.project

    class Tag(BaseModel):
        creator = ForeignKey(User, related_name="tags", blank=True, null=True)
        tag     = CharField(max_length=30)

        def __unicode__(self):
            return self.tag

    class Comment(BaseModel):
        creator   = ForeignKey(User, related_name="comments", blank=True, null=True)
        issue     = ForeignKey(Issue, related_name="comments", blank=True, null=True)
        created   = DateTimeField(auto_now_add=True)
        body      = TextField(max_length=3000)
        body_html = TextField()

        def save(self):
            self.body_html = markdown(self.body)
            super(Comment, self).save()

        def __unicode__(self):
            return unicode(self.issue.name if self.issue else '') + " : " + self.body[:20]

AddIssues View
--------------

.. sourcecode:: python

    class AddIssues(FormSetView):
        """Create new issues."""
        formset_model      = Issue
        formset_form_class = IssueForm
        success_url        = reverse_lazy("admin:issues_issue_changelist")
        msg_tpl            = "New Issue '%s' was created <%s%s>\n\n%s"
        extra              = 2
        template_name      = "add_issues.html"

        def form_valid(self, formset):
            for form in formset:
                if form.has_changed():
                    form.save()
                    notify_owner(self.request, form.instance, "New Issue", self.msg_tpl)
            return redir(self.success_url)

It's a pretty simple view, but I want to highlight two details: you shouldn't confuse the
formset_form_class with formset_class -- the former is what the formset uses to create
individual forms and the latter is a class that is used to create the formset itself, by
default it is set to BaseFormSet.

Note also that you have to explicitly check if the form has changed, otherwise the formset will
try to create a new record for each unfilled extra form.
