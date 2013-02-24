# views.py for store9, Aug 2010 by Scott S. Lawton

import re
import locale
from string import join

from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, render_to_response
from django.views.generic.simple import direct_to_template    # for csrf
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.context_processors import csrf
from django.core.mail import send_mail
from django.template import RequestContext
from django.forms.models import modelformset_factory
from django.core.urlresolvers import reverse
from django.utils.http import urlencode
from django.core.urlresolvers import reverse_lazy

from dbe.store9.models import Product, Item, CartItem, Order, Contact, AddressBook
from dbe.store9.forms import *
from dbe.store9.email import *
# from dbe.store9.changelist import changelist_view

from dbe.shared.utils import *

from dbe.mcbv.base import TemplateView, View
from dbe.mcbv.edit import UpdateView, ModelFormSetView, FormView
from dbe.mcbv.list import ListView


def cart_processor(request):
    return {"num_citems": CartItem.obj.filter(item__user=request.user).count()}


def add_item(user, item_id):
    """Add item to cart."""
    item = Item.obj.get(item_id=item_id, user=user)
    citem, created = CartItem.obj.get_or_create(item=item)
    if not created:
        citem.update(quantity=citem.quantity+1)
    return citem


class IndexView(TemplateView):
    template_name = "store9/index.html"


class AddToCartView(View):
    def get(self, request, *args, **kwargs):
        add_item(self.user, self.kwargs.get("dpk"))
        return redir("items")


class AddressBookView(ModelFormSetView):
    formset_model      = AddressBook
    formset_form_class = AddressForm
    can_delete         = True
    extra              = 1
    success_url        = reverse_lazy("sprofile")
    template_name      = "addresses.html"

    def get_formset_queryset(self):
        return AddressBook.obj.filter(contact__user=self.user)

    def process_form(self, form):
        form.instance.update( contact=Contact.obj.get(user=self.user) )


class CheckoutView(ListView, FormView):
    list_model    = CartItem
    form_class    = ConfirmForm
    template_name = "checkout.html"
    confirmtpl    = "Gen9 Order #%s Confirmation"
    receivedtpl   = "Order #%s received"

    def get_list_queryset(self):
        return CartItem.obj.filter(item__user=self.user)

    def add_context(self):
        total = sum(i.total() for i in self.get_list_queryset())
        return dict(total=total)

    def form_valid(self, form):
        user        = self.user
        p           = request.POST
        citems_text = join(["%s, %d" % (i, i.quantity) for i in citems], '\n')
        notes       = p.get("notes")
        po_num      = p.get("po_num", '')
        order       = Order.obj.create(items=citems_text, user=user, notes=notes, po_num=po_num)
        order_num   = order.order_num
        self.object_list.delete()

        c_body  = cust_order_tpl % (order_num, po_num, user, order.created, citems_text, notes, total)
        g9_body = gen9_order_tpl % (order_num, po_num, user, order.created, citems_text, notes, total, order_num)
        send_mail(self.confirmtpl % order_num, c_body, from_address, [user.email], fail_silently=False)
        send_mail(self.receivedtpl % order_num, g9_body, from_address, [copy_order_to], fail_silently=False)

        return redir(reverse("your_order") + '?' + urlencode(dict(order_num=order_num, po_num=po_num)))


class YourOrderView(TemplateView):
    template_name = "your-order.html"

    def add_context(self):
        return self.request.GET


class CartView(ListView, ModelFormSetView):
    list_model         = CartItem
    formset_model      = CartItem
    formset_form_class = CartItemForm
    can_delete         = True
    template_name      = "cart.html"

    def get_formset_queryset(self):
        return CartItem.obj.filter(item__user=self.user)

    get_list_queryset = get_formset_queryset

    def add_context(self):
        total          = sum(i.total() for i in self.get_formset_queryset())
        contact        = first(Contact.obj.filter(user=self.user))
        have_addresses = contact.have_addresses() if contact else False

        return dict(total=total, have_addresses=have_addresses)

    def process_form(self, form):
        if form.instance.quantity < 1 : form.instance.delete()
        else                          : form.instance.save()

    def form_valid(self, form):
        user        = self.user
        p           = request.POST
        citems_text = join(["%s, %d" % (i, i.quantity) for i in citems], '\n')
        notes       = p.get("notes")
        po_num      = p.get("po_num", '')
        order       = Order.obj.create(items=citems_text, user=user, notes=notes, po_num=po_num)
        order_num   = order.order_num

        self.object_list.delete()

        c_body  = cust_order_tpl % (order_num, po_num, user, order.created, citems_text, notes, total)
        g9_body = gen9_order_tpl % (order_num, po_num, user, order.created, citems_text, notes, total, order_num)

        send_mail(self.confirmtpl % order_num, c_body, from_address, [user.email], fail_silently=False)
        send_mail(self.receivedtpl % order_num, g9_body, from_address, [copy_order_to], fail_silently=False)

        return redir(reverse("your_order") + '?' + urlencode(dict(order_num=order_num, po_num=po_num)))


class ProfileView(UpdateView):
    form_model          = Contact
    modelform_class     = ContactForm
    modelform_valid_msg = "Profile Updated"
    success_url         = '#'
    template_name       = "view-profile.html"

    def get_modelform_object(self):
        return Contact.obj.get_or_create(user=self.user)[0]


class ItemsView(ListView):
    list_model    = Item
    template_name = "items.haml"


class ItemView(UpdateView):
    form_model      = Item
    modelform_class = ItemForm
    success_url     = '#'
    template_name   = "item.html"

    def get_modelform_object(self):
        return Item.obj.get(user=self.user, pk=self.kwargs.get("mfpk"))

    def edit(self):
        return self.request.GET.get("edit")


class AddItemsView(FormView):
    form_class    = ItemSequencesForm
    template_name = "many-new-items.html"

    def process_record(self, record, nth):
        """Process each line and create item or report an error."""
        sequence = None
        name     = ''
        nth += 1

        try:
            if '\t' in record  : values = record.split('\t')
            elif ',' in record : values = record.split(',', 2)
            else               : values = [record]

            values      = [v.strip() for v in values]
            description = getitem(values, 2, '')

            if len(values) > 1    : name, sequence = values[:2]
            elif len(values) == 1 : sequence = values[0]

            if not (4 > len(values) > 0):
                self.create_errors.append("ERROR - wrong # of fields in sequence %i: %i: %s" % (nth, len(values), values))

        except Exception, e:
            self.create_errors.append("ERROR in sequence %i: %s -- %s" % (nth, values, e))

        if not re.search(r"^[ACGT ]+$", sequence):
            self.create_errors.append(
                "ERROR in sequence %i: %s -- should only contain ACGT and space" % (nth, sequence))

        try:
            self.duplicates.append(Item.obj.get(sequence=sequence, user=self.user))
        except Item.DoesNotExist:
            try:
                item = Item.obj.create(name=name, sequence=sequence, user=self.user, notes=description)
                add_item(self.user, item.pk)  # to cart
            except Exception, e:
                self.create_errors.append("ERROR in sequence %i: %s -- %s" % (nth, name, e))

    def form_valid(self, form):
        self.duplicates, self.create_errors = [], []
        records = re.split(r"[\n\r]+", form.cleaned_data["records"].strip())

        for nth, record in enumerate(records):
            process_record(record, nth)
        return redir("items")
