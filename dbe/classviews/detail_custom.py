from ..cbv.detail import DetailView

class DetailView2(DetailView):
    def add_context(self, **kwargs):
        return {}

    def get_context_data(self, **kwargs):
        """Use get_queryset() if object_list not in kwargs."""
        if "object_list" not in kwargs:
            kwargs["object_list"] = self.get_queryset()
        kwargs.update(self.add_context(**kwargs))
        return super(DetailView2, self).get_context_data(**kwargs)
