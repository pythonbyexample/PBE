from django.forms import formsets
from django.contrib import messages
from django.db.models import Q
from django.forms.formsets import formset_factory, BaseFormSet, all_valid

from detail import *
from edit import *


class SearchFormViewMixin(BaseFormView):
    ignore_get_keys = ("page", )

    def get_form_kwargs(self):
        """Returns the keyword arguments for instantiating the form."""
        r = self.request
        kwargs = dict(initial=self.get_initial())
        if r.method in ("POST", "PUT"):
            kwargs.update(dict(data=r.POST, files=r.FILES))
        elif r.GET:
            # do get form processing if there's get data that's not in ignore list
            if [k for k in r.GET.keys() if k not in self.ignore_get_keys]:
                kwargs.update(dict(data=r.GET))
        return kwargs

    def get(self, request):
        form = self.get_form()
        if self.request.GET:
            if form.is_valid():
                self.process_form(form)
            else:
                return self.form_invalid(form)
        return self.render_to_response(self.get_context_data(form=form))


class SearchFormView(FormView, SearchFormViewMixin):
    """FormView for search pages."""


class OwnObjMixin(SingleObjectMixin):
    """Access object, checking that it belongs to current user."""
    item_name   = None          # used in permissions error message
    owner_field = "creator"     # object's field to compare to current user to check permission

    def permission_error(self):
        name = self.item_name or self.object.__class__.__name__
        return HttpResponse("You don't have permissions to access this %s." % name)

    def validate(self, obj):
        if getattr(obj, self.owner_field) == self.request.user:
            return True

    def get_object(self, queryset=None):
        obj = super(OwnObjMixin, self).get_object(queryset)
        return obj if self.validate(obj) else None


class DeleteOwnObjView(OwnObjMixin, DeleteView):
    """Delete object, checking that it belongs to current user."""


class UpdateOwnObjView(OwnObjMixin, UpdateView):
    """Update object, checking that it belongs to current user."""


class SearchEditFormset(SearchFormView):
    """Search form filtering a formset of items to be updated."""
    model         = None
    formset_class = None
    form_class    = None

    def get_form_class(self):
        if self.request.method == "GET": return self.form_class
        else: return self.formset_class

    def get_queryset(self, form=None):
        return self.model.objects.filter(self.get_query(form))

    def get_query(self, form):
        """This method should always be overridden, applying search from the `form`."""
        return Q()

    def form_valid(self, form):
        formset = None
        if self.request.method == "GET":
            formset = self.formset_class(queryset=self.get_queryset(form))
        else:
            form.save()
            messages.success(self.request, "%s(s) were updated successfully" % self.model.__name__.capitalize())
            formset = form
            form = self.form_class(self.request.GET)
        return self.render_to_response(self.get_context_data(form=form, formset=formset))

    def form_invalid(self, form):
        formset = form
        form = self.form_class(self.request.GET)
        return self.render_to_response(self.get_context_data(form=form, formset=formset))

    def get(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_bound:
            if form.is_valid(): return self.form_valid(form)
            else: return self.form_invalid(form)
        return self.render_to_response(self.get_context_data(form=form))
