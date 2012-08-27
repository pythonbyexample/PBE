from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.contrib.admin.views.decorators import staff_member_required

from dbe.todo.models import *


@staff_member_required
def update_item(request, pk, mode=None, action=None):
    """Toggle Done / Onhold on/off or delete an item."""
    item = Item.objects.get(pk=pk)
    if mode == "delete":
        Item.objects.filter(pk=pk).delete()
        return HttpResponseRedirect(reverse("admin:todo_item_changelist"))
    else:
        if mode == "progress" : val = int(action)
        else                  : val = (action=="on")
        setattr(item, mode, val)
        item.save()
        return HttpResponse('')
