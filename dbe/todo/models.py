from django.template import loader
from django.db.models import *
from django.contrib.auth.models import User
from django.contrib import admin
from django.core.urlresolvers import reverse

from settings import MEDIA_URL

btn_tpl  = "<div class='%s' id='%s_%s'><img class='btn' src='%simg/admin/icon-%s.gif' /></div>"
namelink = "<a href='%s'>%s</a>"
dellink  = "<a href='%s'>Delete</a>"


class Type(Model):
    creator = ForeignKey(User, blank=True, null=True)
    type    = CharField(max_length=30)

    def __unicode__(self):
        return self.type

class Project(Model):
    creator = ForeignKey(User, blank=True, null=True)
    project = CharField(max_length=60)

    def __unicode__(self):
        return self.project

class Tag(Model):
    creator = ForeignKey(User, blank=True, null=True)
    tag     = CharField(max_length=30)

    def __unicode__(self):
        return self.tag

class Item(Model):
    obj        = objects = Manager()
    creator    = ForeignKey(User, related_name="items", blank=True, null=True)
    name       = CharField(max_length=60)
    priority   = IntegerField(default=0, blank=True, null=True)
    difficulty = IntegerField(default=0, blank=True, null=True)
    progress   = IntegerField(default=0)
    done       = BooleanField(default=False)
    onhold     = BooleanField(default=False)

    created    = DateTimeField(auto_now_add=True)
    type       = ForeignKey(Type, related_name="items", blank=True, null=True)
    project    = ForeignKey(Project, related_name="items", blank=True, null=True)
    tags       = ManyToManyField(Tag, related_name="items", blank=True, null=True)
    notes      = TextField(max_length=3000, default='', blank=True)

    def __unicode__(self):
        return self.name

    def name_(self):
        link = reverse("update_item_detail", kwargs=dict(pk=self.pk))
        return namelink % (link, self.name)
    name_.allow_tags = True

    def progress_(self):
        return loader.render_to_string("progress.html", dict(pk=self.pk))
    progress_.allow_tags = True
    progress_.admin_order_field = "progress"

    def onhold_(self):
        onoff = "on" if self.onhold else "off"
        return btn_tpl % ("toggle onhold", 'h', self.pk, MEDIA_URL, onoff)
    onhold_.allow_tags = True
    onhold_.admin_order_field = "onhold"

    def done_(self):
        onoff = "on" if self.done else "off"
        return btn_tpl % ("toggle done", 'd', self.pk, MEDIA_URL, onoff)
    done_.allow_tags = True
    done_.admin_order_field = "done"

    def created_(self):
        return self.created.strftime("%b %d %Y")
    created_.admin_order_field = "created"

    def type_(self):
        return self.type if self.type else ''
    type_.admin_order_field = "type"

    def project_(self):
        return self.project if self.project else ''
    project_.admin_order_field = "project"

    def delete_(self):
        return dellink % reverse( "update_item", args=[self.pk, "delete"] )
    delete_.allow_tags = True
