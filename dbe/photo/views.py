from django.core.exceptions import PermissionDenied
from django.db.models import Q

from dbe.photo.models import *
from dbe.photo.forms import *
from settings import MEDIA_URL

from dbe.classviews.list_custom import *
from dbe.classviews.detail_custom import *
from dbe.classviews.base import View


class PermissionMixin(View):
    def dispatch(self, request, *args, **kwargs):
        model = getattr(self, "main_model", self.model)
        obj = get_object_or_404(model, pk=kwargs.get("pk"))
        if not request.user.is_authenticated() and not obj.public:
            raise PermissionDenied      # needs to be raised before self.post() is processed
        return super(PermissionMixin, self).dispatch(request, *args, **kwargs)


class Main(AKListView):
    model               = Album
    context_object_name = "albums"
    paginate_by         = 10
    template_name       = "photo/list.html"

    def get_queryset(self):
        qs = super(Main, self).get_queryset()
        if not self.request.user.is_authenticated():
            qs = qs.filter(public=True)
        return qs


class AlbumView(PermissionMixin, DetailListFormsetView):
    """List of images in an album, optionally with a formset to update image data."""
    main_model          = Album
    list_model          = Image
    related_name        = "images"
    context_object_name = "album"
    form_class          = ImageForm
    paginate_by         = 25
    template_name       = "album.html"

    def do_init(self):
        self.show = self.kwargs.get("show", "thumbnails")
        if self.show == "edit" and not self.request.user.is_authenticated():
            self.show = "thumbnails"

    def form_valid(self, form):
        super(AlbumView, self).form_valid(form)
        url = reverse2("album", pk=self.main_object.pk, show=self.show)
        return redir("%s?%s" % (url, self.request.GET.urlencode()))

    def add_context(self, **kwargs):
        return dict(show=self.show)


class ImageView(PermissionMixin, UpdateView2):
    model               = Image
    form_class          = ImageForm
    context_object_name = "image"
    template_name       = "image.html"

    def get_context_data(self, **kwargs):
        c = super(ImageView, self).get_context_data(**kwargs)
        edit = self.request.GET.get("edit", False)
        if not self.request.user.is_authenticated():
            edit = False
        return updated(c, dict(edit=edit))


class SearchView(ListFilterView):
    model               = Image
    form_class          = SearchForm
    context_object_name = "images"
    paginate_by         = 25
    template_name       = "search.html"

    def form_valid(self, form):
        """ Perform search and sorting and save results to `self.object_list`.

            Note: The search is very slow for users who are not logged in, for better performance,
            `public` field should be added to Image model.
        """
        data = Container(**form.cleaned_data)

        # create all search queries
        if data.title:
            self.q &= Q(title__icontains=data.title)
        for field in "rating width height".split():
            self.range_query(data, field)
        if data.albums:
            self.q &= Q(albums__in=data.albums)     # inclusive filter
        for tag in data.get("tags"):
            self.q &= Q(tags=tag)                   # tests if tag is contained in `tags`

        # apply filter and ordering
        self.object_list = self.model.obj.filter(self.q).order_by( data.sort_dir+data.sort_by )

        if not self.request.user.is_authenticated():
            self.object_list = [i for i in self.object_list if i.public]
        return super(SearchView, self).form_valid(form)

    def range_query(self, data, field):
        value = data.get(field, None)
        if value:
            q0 = {field+"__gte": value[0]}
            q1 = {field+"__lte": value[1]}
            if value[0]: self.q &= Q(**q0)
            if value[1]: self.q &= Q(**q1)


def photo_context(request):
    return dict(user=request.user, media_url=MEDIA_URL)
