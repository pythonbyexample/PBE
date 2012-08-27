from django.template import loader
from django.db.models import *
from django.contrib.auth.models import User
from django.contrib import admin
from django.core.urlresolvers import reverse

from settings import MEDIA_URL


class Tag(Model):
    user = ForeignKey(User, blank=True, null=True)
    tag  = CharField(max_length=30)

class Item(Model):
    user       = ForeignKey(User, related_name="items", blank=True, null=True)
    name       = CharField(max_length=60)
    priority   = IntegerField(default=0)
    difficulty = IntegerField(default=0)
    progress   = IntegerField(default=0)
    notes      = TextField(max_length=3000, default='', blank=True)
    done       = BooleanField(default=False)
    onhold     = BooleanField(default=False)
    datetime   = DateTimeField(auto_now_add=True)
    tags       = OneToManyField(related_name="item")

    btn_tpl    = "<div class='%s' id='%s_%s'><img class='btn' src='%simg/admin/icon-%s.gif' /></div>"

    def progress_(self):
        return loader.render_to_string("progress.html", dict(pk=self.pk))
    progress_.allow_tags = True
    progress_.admin_order_field = "progress"

    def onhold_(self):
        onoff = "on" if self.onhold else "off"
        return self.btn_tpl % ("toggle onhold", 'h', self.pk, MEDIA_URL, onoff)
    onhold_.allow_tags = True
    onhold_.admin_order_field = "onhold"

    def done_(self):
        onoff = "on" if self.done else "off"
        return self.btn_tpl % ("toggle done", 'd', self.pk, MEDIA_URL, onoff)
    done_.allow_tags = True
    done_.admin_order_field = "done"

    def delete(self):
        url = reverse("update_item", args=[self.pk, "delete"])
        return "<a href='%s'>Delete</a>" % url
    delete.allow_tags = True
