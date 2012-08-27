from django.forms import formsets
from django.contrib import messages
from django.db.models import Q

from detail import *
from edit import *
from dbe.shared.utils import *


class SearchFormViewMixin(BaseFormView):
    ignore_get_keys = ["page"]

    def get_form_kwargs(self):
        """ Returns the keyword arguments for instanciating the form. """
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


class UpdateView2(UpdateView):
    def get_success_url(self):
        return self.object.get_absolute_url()

    def get_context_data(self, **kwargs):
        c = super(UpdateView2, self).get_context_data(**kwargs)
        c.update(self.add_context())
        return c

    def add_context(self):
        return {}


class UserUpdateView(UpdateView2):
    def get_form_kwargs(self):
        d = super(UpdateView2, self).get_form_kwargs()
        d.update(dict(user=self.request.user))
        return d


class CreateView2(CreateView):
    def get_context_data(self, **kwargs):
        c = super(CreateView2, self).get_context_data(**kwargs)
        if hasattr(self, "add_context"):
            c.update(self.add_context())
        return c

    def get_form_kwargs(self):
        d = super(CreateView2, self).get_form_kwargs()
        d.update(dict(user=self.request.user))
        return d


class OwnObjMixin(SingleObjectMixin):
    """Access object, checking that it belongs to current user."""
    item_name        = None      # used in permissions error message
    owner_field      = "creator" # object's field to compare to current user to check permission

    def perm_error(self):
        return HttpResponse("You don't have permissions to access this %s." % self.item_name)

    def validate(self, obj):
        if getattr(obj, self.owner_field) == self.request.user:
            return True

    def get_object(self, queryset=None):
        obj = super(OwnObjMixin, self).get_object(queryset)
        if not self.validate(obj): return None
        return obj


class DeleteOwnObjView(OwnObjMixin, DeleteView):
    """Delete object, checking that it belongs to current user."""


class UpdateOwnObjView(OwnObjMixin, UpdateView2):
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


class CreateWithFormset(FormView):
    """ Create multiple objects using a formset.

        Passes user as an arg to each form init function.
    """
    model            = None
    form_class       = None
    extra            = 5

    def get_form(self, form_class=None):
        Formset = formsets.formset_factory(self.form_class, extra=self.extra)
        Formset.form = staticmethod(curry(self.form_class, user=self.request.user))
        return Formset(**self.get_form_kwargs())

    def post(self, request, *args, **kwargs):
        self.object = None
        formset = self.get_form()
        if formset.is_valid():
            return self.form_valid(formset)
        else:
            return self.form_invalid(formset)

    def form_valid(self, formset):
        for form in formset:
            if form.has_changed():
                form.save()
        return HttpResponseRedirect(reverse(self.success_url_name))

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))

    def get_context_data(self, **kwargs):
        context = super(CreateWithFormset, self).get_context_data(**kwargs)
        return updated( context, dict(formset=self.get_form()) )
