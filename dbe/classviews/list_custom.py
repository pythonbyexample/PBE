from django.db.models import Q
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404
from django.forms.models import modelformset_factory
from django.core.urlresolvers import reverse

from list import *
from edit_custom import *


class AKListView(ListView):
    """Modified ListView; added insertion of `object_list` into context if it's not there."""
    object_list = None

    def add_context(self, **kwargs):
        return {}

    def get_context_data(self, **kwargs):
        """Use get_queryset() if object_list not in kwargs."""
        if "object_list" not in kwargs:
            kwargs["object_list"] = self.get_queryset()
        kwargs.update(self.add_context(**kwargs))
        return super(AKListView, self).get_context_data(**kwargs)


class ListFilterView(AKListView, SearchFormViewMixin):
    """ List Filter - filter list with a search form.

        as_view      : dispatch -> get or post
        get          : get_form OR get_queryset -> get_context_data -> render_to_response
        post         : get_form -> get_form_kwargs -> form_valid or form_invalid
        form_valid   : get_success_url
        form_invalid : get_context_data -> render_to_response

        as_view, dispatch      : base.View
        render_to_response     : TemplateResponseMixin

        get                    : BaseListView
        post                   : ProcessFormView
        get_form, form_invalid : FormMixin
        get_form_kwargs        : SearchFormViewMixin

        form_valid, get_success_url, get_queryset, get_context_data
    """
    context_object_name = None
    success_url_name    = None
    q                   = Q()

    def get(self, request):
        self.object_list = self.model.obj.all()
        form             = self.get_form()
        return self.form_valid(form) if form.is_valid() else self.form_invalid(form)

    def get_success_url(self):
        return reverse(self.success_url_name) if self.success_url_name else None

    def get_queryset(self):
        return self.model.objects.filter(self.q)

    def form_valid(self, form):
        u = self.get_success_url()
        if u: return HttpResponseRedirect(u)
        return self.render_to_response(self.get_context_data(form=form))

    def get_context_data(self, **kwargs):
        # search query to be added to page links
        get = self.request.GET.copy()
        get.pop("page", None)
        kwargs.update({"object_list"            : self.object_list,
                       "extra_vars"             : '&'+get.urlencode(),
                       self.context_object_name : self.object_list,
                       })
        c = super(ListFilterView, self).get_context_data(**kwargs)
        c.update( dict(form=self.get_form()) )
        return c


class DetailListCreateView(ListView, BaseCreateView):
    """View with details of an object, listing of related objects and a form."""
    main_model          = None      # model of object to display
    list_model          = None      # related objects to list
    form_class          = None
    main_object         = None      # instance of main object
    related_name        = None      # attribute name linking main object to related objects
    context_object_name = None
    template_name       = None
    paginate_by         = 20
    success_url         = '#'

    def get_queryset(self):
        self.object = self.list_model()
        mainobj = self.get_mainobj()
        return getattr(mainobj, self.related_name).all()

    def get_mainobj(self):
        if not self.main_object:
            self.main_object = get_object_or_404(self.main_model, pk=self.kwargs.get("pk"))
        return self.main_object

    def get_context_data(self, **kwargs):
        c = ListView.get_context_data(self, **kwargs)
        c.update({ "form": self.get_form(),
                   self.context_object_name: self.get_mainobj()
                })
        return c


class ListRelated(ListView):
    """ Listing of an object and related items.
        first 4 attributes: e.g. Image Album "album" "images"
    """
    model               = None      # items to be listed
    related_model       = None      # related item
    foreign_key_field   = None      # FK field: model->related_model
    context_object_name = None      # list of `model` items
    template_name       = None
    paginate_by         = 20

    def get_queryset(self):
        lookup = {self.foreign_key_field: self.kwargs["pk"]}
        return self.model.objects.filter(**lookup)

    def get_context_data(self, **kwargs):
        c = super(ListRelated, self).get_context_data(**kwargs)
        pk = self.kwargs["pk"]
        c.update({
                  "pk": pk,
                  self.foreign_key_field: self.related_model.objects.get(pk=pk)
                  })
        return c


class DetailListFormsetView(MultipleObjectMixin, FormView):
    """ List of items related to main item, viewed as a paginated formset.

        Note: `list_model` needs to have ordering specified for it to be able to paginate.
    """
    main_model          = None
    list_model          = None
    related_name        = None
    context_object_name = None
    form_class          = None
    paginate_by         = None
    template_name       = None
    main_object         = None  # should be left as None in subclass

    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        return self.render_to_response(self.get_context_data(form=self.get_form()))

    def post(self, *args, **kwargs):
        self.object_list = self.get_queryset()
        return super(DetailListFormsetView, self).post(*args, **kwargs)

    def get_queryset(self):
        mainobj = self.get_mainobj()
        return getattr(mainobj, self.related_name).all()

    def get_form(self, form_class=None):
        Formset   = modelformset_factory(self.list_model, form=self.form_class, extra=0)
        queryset  = self.object_list
        page_size = self.get_paginate_by(queryset)
        if page_size:
            queryset = self.paginate_queryset(queryset, page_size)[2]

        args = [self.request.POST] if self.request.method=="POST" else []
        return Formset(*args, queryset=queryset)

    def form_valid(self, form):
        form.save()
        form    = self.form_class(self.request.GET)
        msg     = "%s(s) were updated successfully"
        messages.success(self.request, msg % self.list_model.__name__.capitalize())
        return HttpResponseRedirect('#')

    def form_invalid(self, form):
        form = self.form_class(self.request.GET)
        return self.render_to_response(self.get_context_data(form=form))

    def get_context_data(self, **kwargs):
        kwargs["object_list"] = self.object_list
        c = super(DetailListFormsetView, self).get_context_data(**kwargs)
        c.update({"formset"                : self.get_form(),
                  self.context_object_name : self.get_mainobj(),
                  self.related_name        : c["object_list"],
                })
        return c

    def get_mainobj(self):
        if not self.main_object:
            self.main_object = get_object_or_404(self.main_model, pk=self.kwargs.get("pk"))
        return self.main_object
