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

General architecture of the app will be as follows:

The `Issue` model will have these fields: name, body, creator, owner, priority,
difficulty, progress, closed (boolean), project and tags.

There will be a `Project` model with creator and project (name) fields and the `Tag` model with
creator and tag (name) fields; finally a `Comment` model will have creator, issue and body fields.

There will be four class-based views:

Creation of new issues will be done with `AddIssues(FormSetView)` view which will also notify
issue owner about each new issue.

Viewing an issue and adding comments will be handled by `ViewIssue(DetailListCreateView)` --
where List part is needed to show a list of comments; this view will also notify the owner of a
new comment.

`UpdateIssue` and `UpdateComment` are two simple views inherited from `UpdateView;` `UpdateIssue` will
notify the owner of the change.

There is also a couple of small AJAX function views that will be listed below.


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
            return self.owner or ''
        owner_.admin_order_field = "owner"

        def project_(self):
            return self.project or ''
        project_.admin_order_field = "project"

        def delete_(self):
            return dellink % reverse2("update_issue", self.pk, "delete")
        delete_.allow_tags = True

I'm using two special method properties here: `allow_tags` indicates that an html tag can be
included in the method's return value and `admin_order_field` specifies the field to use for
sorting in admin, so that clicking on 'closed\_' column will sort by closed model field
('closed\_' will actually be displayed as 'closed' because the admin hides the underscore).

I am also using `markdown.markdown` function to allow rich text markup in Issue description.

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

It's a very basic view, but I want to highlight two details: you shouldn't confuse the
`formset_form_class` with `formset_class` -- the former is what the formset uses to create
individual forms and the latter is a class that is used to create the formset itself, by
default it is set to `BaseFormSet.`

Note also that you have to explicitly check if the form has changed, otherwise the formset will
try to create a new record for each unfilled extra form.


ViewIssue
---------

.. sourcecode:: python

    class ViewIssue(DetailListCreateView):
        """View issue, comments and new comment form."""
        detail_model               = Issue
        list_model                 = Comment
        modelform_class            = CommentForm
        related_name               = "comments"
        fk_attr                    = "issue"
        msg_tpl                    = "Comment was added to the Issue '%s' <%s%s>\n\n%s"
        template_name              = "issue.html"

        def modelform_valid(self, modelform):
            """Send notification email to the issue owner."""
            resp = super(ViewIssue, self).modelform_valid(modelform)
            obj  = self.modelform_object
            obj.update(creator=self.user)
            notify_owner(self.request, obj.issue, "New Comment", self.msg_tpl, comment_body=obj.body)
            return resp

`DetailListCreateView` is a composite view that provides a detail of an record, a listing of
related objects, and a create view form to add a record related to the detail object. In this
case we have an issue object, a list of related comments and a form to add a new comment.

We need to specify `fk_attr` which tells `DetailListCreateView` to do the assignment:
new_comment.<fk_attr> = detail_object.

UpdateIssue
-----------

.. sourcecode:: python

    class UpdateIssue(UpdateView):
        form_model      = Issue
        modelform_class = IssueForm
        msg_tpl         = "Issue '%s' was updated <%s%s>\n\n%s"
        template_name   = "issue_form.html"

        def modelform_valid(self, modelform):
            """ If form was changed, send notification email the (new) issue owner.
                Note: at the start of the function, FK relationship is already updated in `modelform_object`.
            """
            if modelform.has_changed() and self.modelform_object.owner:
                notify_owner(self.request, self.modelform_object, "Issue Updated", self.msg_tpl)
            return super(UpdateIssue, self).modelform_valid(modelform)

`UpdateIssue` is a simple `UpdateView` with added notification.

UpdateComment
-------------

.. sourcecode:: python

    class UpdateComment(UpdateView):
        form_model      = Comment
        modelform_class = CommentForm
        template_name   = "issues/comment_form.html"

        def get_success_url(self):
            return self.modelform_object.issue.get_absolute_url()

`UpdateComment` is simpler still: we only need to go back to the Issue view on success.

notify_owner
------------

.. sourcecode:: python

    def notify_owner(request, obj, title, msg_tpl, comment_body=''):
        serv_root = request.META["HTTP_ORIGIN"]
        url       = reverse2("issue", dpk=obj.pk)
        lst       = [obj.name, serv_root, url, comment_body]
        msg       = msg_tpl % tuple(lst)

        if obj.owner:
            send_mail(title, msg, "IssuesApp", [obj.owner.email], fail_silently=False)

This helper function is used by the views listed above.

AJAX views
----------

.. sourcecode:: python

    from django.contrib.admin.views.decorators import staff_member_required

    @staff_member_required
    def update_issue(request, pk, mode=None, action=None):
        """AJAX view, toggle Done on/off, set progress or delete an issue."""
        issue = Issue.obj.get(pk=pk)
        if mode == "delete":
            issue.delete()
            return redir("admin:issues_issue_changelist")
        else:
            if mode == "progress" : val = int(action)
            else                  : val = bool(action=="on")
            setattr(issue, mode, val)
            issue.save()
            return HttpResponse('')

In `update_issue()` I need to handle three action: deletion, progress update, toggle on/off and
deletion. In case of deletion, I need to reload the page to have the issue row removed from the
listing; otherwise I need to return a blank `HttpResponse` because a view always has to return a
response.

.. sourcecode:: python

    @staff_member_required
    def delete_comment(request, pk):
        Comment.obj.get(pk=pk).delete()
        return redir(referer(request))

After a comment is deleted, I'm using `utils.referer()` to reload the initial page.

SelectOrCreateField
-------------------

.. sourcecode:: python

    class SelectAndTextInput(widgets.MultiWidget):
        """A Widget with select and text input field."""
        is_required = False
        input_fields = 1

        def __init__(self, choices=(), initial=None, attrs=None):
            widgets = self.get_widgets(choices, initial, attrs)
            super(SelectAndTextInput, self).__init__(widgets, attrs)

        def get_widgets(self, c, i, attrs):
            return [Select(attrs=attrs, choices=c), TextInput(attrs=attrs)]

        def decompress(self, value):
            return value or [None]*(self.input_fields+1)

        def format_output(self, rendered_widgets):
            return u' '.join(rendered_widgets)

    class SelectOrCreateField(f.MultiValueField):
        """SelectAndTextField - select from a dropdown or add new using text inputs."""
        widgetcls    = SelectAndTextInput
        extra_inputs = 1

        def __init__(self, *args, **kwargs):
            choices = kwargs.pop("choices", ())
            initial = kwargs.pop("initial", {})
            fields = self.get_fields(choices, initial)
            super(SelectOrCreateField, self).__init__(fields, *args, **kwargs)
            self.widget = self.widgetcls(choices, initial)
            self.initial = [initial] + [u'']*self.extra_inputs
            self.required = False

        def get_fields(self, choices, initial):
            return [f.ChoiceField(choices=choices, initial=initial), f.CharField()]

        def to_python(self, value):
            return value

        def set_choices(self, choices):
            self.fields[0].choices = self.widget.widgets[0].choices = choices
            initial = choices[0][0]
            self.fields[0].initial = choices[0][0]
            self.widget.widgets[0].initial = choices[0][0]

        def compress(self, lst):
            choice, new = lst[0], lst[1].strip()
            return (new, True) if new else (choice, False)

This field is used in `AddIssues` / `UpdateIssue` views; it lets you choose an existing project or
create a new project and select it using a combined select / text entry multi-widget.

As you can see, creating custom multi-widgets and fields can be a bit messy in Django.

In my widget, I've overridden `get_widgets()` to return a select a `TextInput` widgets,
`decompress()` to return two `None` values if there was no input and `format_output()` to join
rendered widgets into one string.

In the field's `set_choices()` I need to manually set choices and initial values on both the
first field and the first widget because this method is called after the widgets are already created.

Finally in `compress()` I need to return the tuple `(project_name,` `created)` where created
indicates if a new project needs to be created -- the form will need to properly handle this
return format.

TagsSelectCreateField
---------------------

.. sourcecode:: python

    class MultiSelectCreate(SelectAndTextInput):
        """Widget with multiple select and multiple input fields."""
        input_fields = 6

        def get_widgets(self, c, i, attrs):
            return [SelectMultiple(attrs=attrs, choices=c)] + \
                [TextInput(attrs=attrs) for _ in range(self.input_fields)]

        def format_output(self, lst):
            lst.insert(0, "<table border='0'><tr><td>")
            lst.insert(2, "</td><td>")
            lst.append("</td></tr></table>")
            return u''.join(lst)

    class TagsSelectCreateField(SelectOrCreateField):
        widgetcls    = MultiSelectCreate
        extra_inputs = 6

        def get_fields(self, c, i):
            return [f.MultipleChoiceField(choices=c, initial=i)] + \
                    [f.CharField() for _ in range(self.extra_inputs)]

        def compress(self, lst):
            return [lst[0]] + [x.strip() for x in lst[1:] if x.strip()] if lst else None

`TagsSelectCreateField` is also used in `UpdateIssue` view, it lets you select multiple tags and to
add up to six additional new tags. Both widget and field inherit from the widget and field
discussed above.

This time `get_widgets()` creates a total of seven widgets; `format_output()` wraps fields into a
HTML table.

In `TagsSelectCreateField,` I also need to appropriately handle larger number of fields.

Defining and processing these two fields is the toughest part of this App. Fortunately, once
you have them, it's easy to reuse them in other Apps or to use them as an example to create
other multi-fields.

CreateIssueForm
---------------

.. sourcecode:: python

    class CreateIssueForm(f.ModelForm):
        class Meta:
            model   = Issue
            exclude = "creator project tags closed body_html progress".split()

        def __init__(self, *args, **kwargs):
            """ Set choices filtered by current user, set initial values.

                TODO: change SelectOrCreateField to auto-load foreign key choices and select current one.
            """
            kwargs = copy.copy(kwargs)
            user = self.user = kwargs.pop("user", None)
            super(CreateIssueForm, self).__init__(*args, **kwargs)

            values = Project.obj.all().values_list("pk", "project")
            values = [(0, "---")] + list(values)
            self.fields["project_"] = SelectOrCreateField(choices=values, initial=0)

            values = Tag.obj.all().values_list("pk", "tag")
            if values: self.fields["tags_"].set_choices(values)

            # set initial values
            inst = self.instance
            if inst.pk:
                if inst.project:
                    self.initial["project_"] = [inst.project.pk]
                self.initial["tags_"] = [ [t.pk for t in inst.tags.all()] ]

        def clean(self):
            """ Change instance based on selections, optionally create new records from text inputs.

                TODO: change SelectOrCreateField to be properly handled by ModelForm to create db entries.
            """
            data         = self.cleaned_data
            inst         = self.instance
            inst.creator = self.user

            proj, new = data["project_"]
            if new:
                inst.project = Project.obj.get_or_create(project=proj)[0]
            elif int(proj):
                inst.project = Project.obj.get(pk=proj)

            inst.save()
            tags = data["tags_"]
            if tags:
                selected, new = tags[0], tags[1:]
                inst.tags = [Tag.obj.get(pk=pk) for pk in selected]  # need this in case tags were deselected
                for tag in new:
                    inst.tags.add( Tag.obj.get_or_create(tag=tag)[0] )

            return data


        fldorder   = "name body owner priority difficulty progress closed project_ tags_".split()
        s3widget   = f.TextInput(attrs=dict(size=3))

        priority   = f.IntegerField(widget=s3widget, required=False, initial=0)
        difficulty = f.IntegerField(widget=s3widget, required=False, initial=0)
        project_   = SelectOrCreateField()
        tags_      = TagsSelectCreateField()
        body       = f.CharField( widget=f.Textarea( attrs=dict(cols=80, rows=18) ), required=False )


    class IssueForm(CreateIssueForm):
        """Like CreateIssueForm but with `progress` and `closed` fields."""
        class Meta:
            model   = Issue
            exclude = "creator project tags body_html".split()

        progress   = f.IntegerField(widget=CreateIssueForm.s3widget, required=False, initial=0)

Unforunately these fields require some extra legwork on both initialization and cleanup;
perhaps they can be improved to be initialized automatically by the `ModelForm` logic.

Since the fields are created on the fly, it's necessary to specify field order in `fldorder`
attribute, which will be used by the template.

It makes sense to exclude some fields from `CreateIssueForm` form; `IssueForm` then overrides
`CreateIssueForm` and adds the excluded fields back.

.. image:: _static/img/i-list.gif
    :class: screenshot

AddIssues Template
------------------

.. sourcecode:: django

    <div class="main">
        <form action="" method="POST">{% csrf_token %}
        <div id="submit"><input id="submit-btn" type="submit" value="Save"></div>
        <div class="clear"></div>
            {{ formset.management_form }}

            <!-- FOR EACH FORM -->
            {% for form in formset %}
                <fieldset class="module aligned">
                    {{ form.id }}

                    <!-- FOR EACH FIELD -->
                    {% for fld in form %}
                        <div class="form-row">
                            <label class="{% if fld.field.required %} required {% endif %}">{{ fld.label }}</label>
                            {{ fld }}
                        </div>
                    {% endfor %}

                </fieldset><br />
            {% endfor %}

            <div id="submit"><input id="submit-btn" type="submit" value="Save"></div>
        </form>
    </div>

Nothing unusual here, make sure to remember `management_form!`

.. image:: _static/img/i-add.gif
    :class: screenshot

ViewIssue Template
------------------

.. sourcecode:: django

    <div class="main">

        <!-- ISSUE -->

        <blockquote>
            <div class="issue">
            <div class="title">{{ issue.name }}</div>
            <blockquote>
                <div class="time">{{ issue.created }}
                    | <a href="{% url 'update_issue_detail' mfpk=issue.pk %}">edit</a>
                </div>
                <div class="body">{{ issue.body_html|safe }}</div>
            </blockquote>
            </div>

            <!-- LIST OF COMMENTS -->

            {% if comment_list %} <p>Comments:</p> {% endif %}

            {% for comment in comment_list %}
                <div class="comment">
                    <div class="time">{{ comment.created }} | {{ comment.creator }}
                    {% if request.user.is_staff %}
                        <div class="edit-links">
                        <a href="{% url 'update_comment' mfpk=comment.pk %}">edit</a>
                        | <a href="{% url 'delete_comment' comment.pk %}">delete</a>
                        </div>
                    {% endif %}
                    </div>
                    <div class="body">{{ comment.body_html|safe }}</div>
                </div>
            {% endfor %}

            <!-- // LIST OF COMMENTS -->


            <p>{% include "paginator.html" %}</p>

            <!-- COMMENT FORM -->

            <div id="addc"><b>Add a comment</b>
            <form action="" method="POST">{% csrf_token %}
                <div id="cform">
                    <p> {{ modelform.body }} {{ modelform.body.errors }} </p>
                </div>
                <div id="submit"> <input type="submit" value="Submit" /> </div>
            </form>
            </div>

            <!-- // COMMENT FORM -->

        </blockquote>
    </div>

..a standard boring detail / list / create template.. and the screenshot:

.. image:: _static/img/i-issue.gif
    :class: screenshot


UpdateIssue Template
--------------------

.. sourcecode:: django

    {% load issues %}
    {% block content %}
    <style type="text/css" media="screen">
        #id_body { width: 600px; height: 250px; }
    </style>
    <div class="main">

        <form action="" method="POST">{% csrf_token %}
            <fieldset class="module aligned">

            {% for name in modelform.fldorder %}
                {% with modelform|get:name as fld %}
                    <div class="form-row">
                        <label class="{% if fld.field.required %} required {% endif %}">{{ fld.label }}</label>
                        {{ fld }}
                    </div>
                {% endwith %}
            {% endfor %}

            </fieldset>
            <div id="submit"><input id="submit-btn" type="submit" value="Save"></div>
        </form>

    </div>
    {% endblock %}

Here we finally get to use the `fldorder` defined in our `IssueForm;` the custom get tag is loaded
from templatetags/issues.py:

.. sourcecode:: python

    def get(value, arg):
        return value[arg]

    register.filter("get", get)

This simple tag allows you to get the form field by name stored in a variable.

AJAX Stuff
----------

Detailed discussion of AJAX code is outside the scope of this tutorial but you can look at the
following source files to see the implementation of clickable progress bar, closed toggle
switch and delete issue button:

* `<https://github.com/akulakov/django/tree/master/dbe/media/js/issues.js>`_
* `<https://github.com/akulakov/django/tree/master/dbe/templates/admin/issues/change_list.html>`_
* `<https://github.com/akulakov/django/tree/master/dbe/templates/issues/progress.html>`_
