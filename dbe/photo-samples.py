"""
Some code examples from Photo portfolio app I made for my own use.
"""

# in models.py

class PhotoManager(Manager):
    def get_or_none(self, **kwargs):
        try: return self.get(**kwargs)
        except self.model.DoesNotExist: return None

class Image(BasicModel):
    obj         = objects = PhotoManager()
    title       = CharField(max_length=60, blank=True, null=True)
    description = TextField(blank=True, null=True)
    image       = ImageField(upload_to="images/")
    thumbnail1  = ImageField(upload_to="images/", blank=True, null=True)
    thumbnail2  = ImageField(upload_to="images/", blank=True, null=True)

    width       = IntegerField(blank=True, null=True)
    height      = IntegerField(blank=True, null=True)
    hidden      = BooleanField()
    group       = ForeignKey(Group, related_name="images", blank=True)
    created     = DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created"]

    def __unicode__(self):
        return self.image.name

    @permalink
    def get_absolute_url(self):
        return ("image", (), dict(pk=self.pk))

    def save(self, *args, **kwargs):
        """Save image dimensions."""
        super(Image, self).save(*args, **kwargs)
        img = PImage.open(pjoin(MEDIA_ROOT, self.image.name))
        self.width, self.height = img.size
        self.save_thumbnail(img, 1, (128,128))
        self.save_thumbnail(img, 2, (64,64))
        super(Image, self).save(*args, **kwargs)

    def save_thumbnail(self, img, num, size):
        fn, ext = os.path.splitext(self.image.name)
        img.thumbnail(size, PImage.ANTIALIAS)
        thumb_fn = fn + "-thumb" + str(num) + ext
        tf = NamedTemporaryFile()
        img.save(tf.name, "JPEG")
        thumbnail = getattr(self, "thumbnail%s" % num)
        thumbnail.save(thumb_fn, File(open(tf.name)), save=False)
        tf.close()


# forms.py

class UserModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super(UserModelForm, self).__init__(*args, **kwargs)

class AKModelForm(UserModelForm):
    def __iter__(self):
        """Workaround for a bug in django1.4 modelformset factory."""
        for name in self.fields:
            if name!="id": yield self[name]

# views.py

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


class AddImages(CreateWithFormset):
    """Create new images."""
    model            = Image
    form_class       = AddImageForm
    item_name        = "image"
    template_name    = "add_images.html"
    extra            = 10

    def form_valid(self, formset):
        group = get_object_or_404(Group, pk=self.kwargs["pk"])
        for form in formset:
            if form.has_changed():
                img = form.save(commit=False)
                img.group = group
                img.save()
        return HttpResponseRedirect(reverse2("group", pk=group.pk))
