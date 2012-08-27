from base import *

class TemplateView2(TemplateView):
    def add_context(self, **kwargs):
        return {}

    def get_context_data(self, **kwargs):
        c = super(TemplateView2, self).get_context_data(**kwargs)
        c.update(self.add_context(**c))
        return c
