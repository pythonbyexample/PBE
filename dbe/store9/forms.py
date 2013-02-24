# forms.py for store9, Aug 2010 by Scott S. Lawton

from django import forms
from django.utils.html import escape

from dbe.store9.models import Contact, Product, Item
from dbe.store9.models import *

from dbe.shared.utils import FormsetModelForm


def add_required_label_tag(original_function):
    """Adds the 'required' CSS class and an asterisks to required field labels."""
    def required_label_tag(self, contents=None, attrs=None):
        contents = contents or escape(self.label)
        if self.field.required:
            #  if not self.label.endswith(" *"):
            #    self.label += " *"
            #    contents += " *"
            attrs = {'class': 'required'}
        return original_function(self, contents, attrs)
    return required_label_tag

def decorate_bound_field():
    from django.forms.forms import BoundField
    BoundField.label_tag = add_required_label_tag(BoundField.label_tag)


class ContactForm(forms.ModelForm):
    required_css_class = "required"     # does not work (on ModelForm?)!
    class Meta:
        model   = Contact
        exclude = ["user"]

class ItemForm(forms.ModelForm):
    class Meta:
        model   = Item
        exclude = ("sequence", "date_added", "item_id", "product", "user")

class CartItemForm(forms.ModelForm):
    class Meta:
        model   = CartItem
        exclude = "date_added item cart_iid".split()
        widgets = dict(quantity=forms.TextInput(attrs=dict(size=2)))

    def __init__(self, *args, **kwargs):
        super(CartItemForm, self).__init__(*args, **kwargs)
        # del self.fields["cart_item_id"]

    def X__iter__(self):
        print "self.exclude", self.exclude
        for name in self.fields:
            if name != "cart_iid": yield self[name]

    def __iter__(self):
        """Workaround for a bug in modelformset factory."""
        for name in self.fields:
            if name!="cart_iid": yield self[name]


class AddressForm(FormsetModelForm):
    class Meta:
        model   = AddressBook
        exclude = ("contact",)


class ConfirmForm(forms.Form):
    pass

class ItemSequencesForm(forms.Form):
    textarea = forms.Textarea(attrs={"cols": 80, "rows": 30})
    records  = forms.CharField(widget=textarea)

decorate_bound_field()
