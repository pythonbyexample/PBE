# encoding:utf-8
from django import forms as f
from django.forms import widgets
from django.utils.safestring import mark_safe

from dbe.photo.models import Tag
from dbe.shared.utils import *


class RangeWidget(widgets.MultiWidget):
    """ A Widget with value and range inputs. """
    is_required = False
    min_max     = False

    def __init__(self, attrs=None):
        w = (widgets.TextInput(attrs=attrs), widgets.TextInput(attrs=attrs))
        super(RangeWidget, self).__init__(w, attrs)

    def render(self, name, value, attrs=None):
        # value is a list of values, each corresponding to a widget in self.widgets
        if not isinstance(value, list):
            value = self.decompress(value)
        output = []
        final_attrs = self.build_attrs(attrs)
        id_ = final_attrs.get('id', None)
        pm = u'-' if self.min_max else u'±'
        for i, widget in enumerate(self.widgets):
            try:
                widget_value = value[i]
            except IndexError:
                widget_value = None
            if id_:
                final_attrs = dict(final_attrs, id='%s_%s' % (id_, i))
            output.append(widget.render(name + '_%s' % i, widget_value, final_attrs))
            if i == 0:
                output.append(u'<span class="plus-minus">%s</span>' % pm)
        return mark_safe(self.format_output(output))

    def decompress(self, value):
        return value or (None, None)

class MinMaxRangeWidget(RangeWidget):
    """Similar to RangeWidget but range is provided directly, i.e. val1 to val2."""
    min_max = True


class SelectCSVField(f.ModelChoiceField):
    """Select related objects by unique name via Text Input."""

    def prepare_value(self, value):
        """ Note: normally value will be a list of pk's but when form is invalid, it will be a string
            with CSVs.
        """
        if isinstance(value, unicode):
            return value
        return cjoin(Tag.obj.get(pk=pk).tag for pk in value)

    def to_python(self, value):
        value = [v.strip() for v in value.split(',')]
        value = [Tag.obj.get_or_create(tag=v) for v in value]
        return [v[0].pk for v in value]

class TagParseField(f.CharField):
    """Parse tags from CSV string."""
    def prepare_value(self, value):
        return value

    def to_python(self, value):
        value = [v.strip() for v in value.split(',')]
        value = [Tag.obj.get_or_none(tag=v) for v in value if v]
        return [v.pk for v in value if v]


class MinMaxRangeField(f.MultiValueField):
    """Similar to RangeField but range is provided directly, i.e. val1 to val2."""
    widget         = MinMaxRangeWidget
    to_python_func = float_or_none
    field_class    = f.FloatField

    def __init__(self, *args, **kwargs):
        fields = self.field_class(), self.field_class()
        super(MinMaxRangeField, self).__init__(fields, *args, **kwargs )
        self.required = False

    def to_python(self, value):
        return [self.to_python_func(v) for v in value]

    def compress(self, lst):
        return (lst[0], lst[1]) if lst else (None, None)

class MinMaxRangeIntField(MinMaxRangeField):
    to_python_func = int_or_none
    field_class    = f.IntegerField
