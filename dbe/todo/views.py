from pprint import pprint
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse, reverse_lazy
from django.contrib.admin.views.decorators import staff_member_required
from django.forms import forms
from django.utils.functional import curry
from django.shortcuts import get_object_or_404

from dbe.todo.models import *
from dbe.todo.forms import *
from dbe.classviews.edit_custom import *


class RemindersWrapper(object):
    def load_reminders(self, request):
        """Load tasks using reminders.py"""
        t = self.load_tasks()
        if t:
            for item in t.get_new():
                rtype = Type.objects.get_or_create(creator=request.user, type="reminder")[0]
                itemobj = Item.obj.get_or_create(name=item.task, type=rtype)[0]
                itemobj.priority = item.late()
                itemobj.notes = "every: %s" % item.every
                itemobj.save()
            t.save()
        ref = request.META["HTTP_REFERER"].split('?')[1:]
        return HttpResponseRedirect(reverse("admin:todo_item_changelist") + ('?'+ref[0] if ref else ''))

    def delete_task(self, item):
        if item.type.type == "reminder":
            tasksobj = self.load_tasks()
            if tasksobj:
                tasksobj.mark_done(item.name)
                tasksobj.save()

    def load_tasks(self):
        import sys
        pypath = "/home/ak/.vim/python/"
        if pypath not in sys.path: sys.path.append(pypath)
        try:
            from reminders import *
            return Tasks()
        except ImportError:
            return None

def load_reminders(request):
    return RemindersWrapper().load_reminders(request)

@staff_member_required
def update_item(request, pk, mode=None, action=None):
    """Toggle Done / Onhold on/off or delete an item."""
    item = get_object_or_404(Item, pk=pk)
    if mode == "delete":
        ref = request.META["HTTP_REFERER"].split('?')[1:]
        RemindersWrapper().delete_task(item)
        item.delete()
        return HttpResponseRedirect(reverse("admin:todo_item_changelist") + ('?'+ref[0] if ref else ''))
    else:
        if mode == "progress" : val = int(action)
        else                  : val = (action=="on")
        setattr(item, mode, val)
        item.save()
        return HttpResponse('')


class UpdateItem(UpdateOwnObjView):
    """Update a todo item."""
    model       = Item
    form_class  = ItemForm
    item_name   = "item"
    success_url = reverse_lazy("admin:todo_item_changelist")


class AddItems(FormView):
    """Add todo items."""
    model            = Item
    form_class       = ItemForm
    item_name        = "item"
    success_url_name = "admin:todo_item_changelist"
    template_name    = "add_items.html"

    def get_form(self, form_class=None):
        ItemFormset = forms.formsets.formset_factory(ItemForm, extra=6)
        ItemFormset.form = staticmethod(curry(ItemForm, user=self.request.user))
        return ItemFormset(**self.get_form_kwargs())

    def post(self, request, *args, **kwargs):
        self.object = None
        formset = self.get_form()
        if formset.is_valid():
            return self.form_valid(formset)
        else:
            return self.form_invalid(formset)

    def form_valid(self, formset):
        for form in formset:
            if form.has_changed(): form.save()
        return HttpResponseRedirect(reverse(self.success_url_name))

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))

    def get_context_data(self, **kwargs):
        context = super(AddItems, self).get_context_data(**kwargs)
        context["formset"] = self.get_form()
        return context
