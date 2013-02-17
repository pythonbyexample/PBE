Libraries
=========


There are a few helper functions and one large class-based views library that will be used in
my tutorials that you need to be familiar with. This page summarizes everything you need to
know to get started with the tutorials (other than basic Django knowledge).

You can view or download the code here:

`Browse source files <https://github.com/akulakov/django/tree/master/dbe/>`_

`dbe.tar.gz <https://github.com/akulakov/django/tree/master/dbe.tar.gz>`_

The following functions and classes are located in shared/utils.py.

Helper functions
----------------

`reverse2(name, *args, **kwargs)` -- reverse URL name

`redir(to, *args, **kwargs)` -- redirect to a URL, wraps HTTPResponseRedirect, `to` may be a URL
or a name that will be automatically reversed using reverse2()

`getitem(iterable, index, default=None)` -- return item at iterable[index]

`first(iterable, default=None)` -- return first item of iterable or default if iterable is empty.


Forms and Models
----------------

`BaseModel` -- objects attribute is abbreviated to obj; update(**kwargs) method updates the
instance and saves it in one step

`UserForm,` `UserModelForm` -- accepts optional user keyword argument and saves it as form instance
attribute


Class-based Views
-----------------

If you are not familiar with Django class-based views, read the official Django docs first:

https://docs.djangoproject.com/en/1.5/topics/class-based-views/

My guide's tutorials will use a library of class-based views based on modified Django generic
views; the library is called `MCBV` (M stands for modular) and the main difference compared to
generic CBVs is that it's possible to mix and match multiple generic views easily (e.g.
`ListView` and `CreateView,` `DetailView` and `UpdateView,` etc.)

This is accomplished by having separate `get()` methods like `detail_get(),` `form_get(),`
`update_get(),` `list_get(),` etc; these methods return context dictionary instead of http response
and all contexts are combined in `TemplateResponseMixin.get()` -- therefore, you would normally
never override `get()` but instead each specific `get_*()` method as needed and you have to remember
to return context from these methods -- otherwise you will get an exception in `get().`

Another difference is that `MCBV` provides a `FormSetView` class in `edit` module.

All of the differences are summarized below but it's best to look at the code yourself -- the
link is at the top of this page.


MCBV Class attributes and methods
---------------------------------

Only the most important and useful attributes and methods are listed below -- these are the
ones you would normally want to override; look in the source files to get the full list.

`FormMixin` is unchanged from the standard Django `FormMixin`.


`ContextMixin`

    * add_context() -- return a dictionary to be injected into context -- this happens in
      get_context_data()

`View`

    * self.user is created together with self.request, self.args, self.kwargs
    * initsetup() runs inside dispatch() method and may be overridden to provide common setup
      before a specific request method is called

`SingleObjectMixin`

    * detail_model, detail_context_object_name, detail_pk_url_kwarg='dpk'
    * get_detail_object(), get_detail_queryset(), get_detail_context_data()

`FormSetMixin`

    * formset_model, formset_form_class, formset_class=BaseFormSet, extra=3
    * get_formset(), get_formset_kwargs(), formset_valid(), formset_invalid(), process_form()

`ModelFormMixin`

    * form_model, modelform_class, modelform_pk_url_kwarg="mfpk"
    * get_modelform(), get_modelform_kwargs(), modelform_valid(), modelform_invalid(),
      get_modelform_context_data()

`ProcessFormView`

    * form_get(), formset_get(), modelform_get()

`BaseCreateView`

    * create_get(), create_post()

`BaseUpdateView`

    * update_get(), update_post()

`CreateUpdateView(CreateView)`

    * Update object if modelform_pk_url_kwarg is in kwargs, otherwise create it.

`MultipleObjectMixin`

    * list_model, list_context_object_name
    * get_list_context_data()
    * when view is paginated, context["object_list"] contains the subset of objects for the
      current page instead of the full list

`BaseListView`

    * list_get()


There is also a number of combined views in `edit_custom` and `list_custom` modules; for example,
`ListRelated` provides a view of a detail object and a list of objects related to the first via
`ForeignKey.`
