from django import forms as f
from django.forms import widgets
from django.forms.widgets import *
from django.utils.safestring import mark_safe

from dbe.todo.forms import SelectOrCreateField, TagsSelectCreateField
from dbe.issues.models import *


class CommentForm(f.ModelForm):
    class Meta:
        model   = Comment
        exclude = "creator issue created body_html".split()

    textarea = f.Textarea( attrs=dict(cols=65, rows=18) )
    body     = f.CharField(widget=textarea, required=False)


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
