from string import ascii_letters, digits, join
from random import choice
import datetime

from django.contrib.auth.models import User
from django.db import models, IntegrityError
from django.db.models import *
from django.core import urlresolvers
from django.utils.translation import get_language, ugettext, ugettext_lazy as _
# from l10n.models import Country

from utils import slugify

from dbe.shared.utils import BaseModel, first, reverse2

# TBD: University discount ... but may be able to simplify vs. Satchmo discount (e.g. apply to
# entire order)
# TBD: add tags, presumably via a generic Django app


class GenIDMixin(object):
    def save(self, **kwargs):
        if not self.pk:
            for x in xrange(99999):
                try:
                    setattr(self, self.id_field, make_id(digits, self.id_len))
                    super(GenIDMixin, self).save(**kwargs)
                    return
                except IntegrityError:
                    continue
        super(GenIDMixin, self).save(**kwargs)


class AddressBook(BaseModel):
    """Address information associated with a contact."""
    contact             = ForeignKey("Contact", related_name="addressbook")
    description         = CharField(_("Description"), max_length=20, blank=True)
    addressee           = CharField(_("Addressee"), max_length=80, blank=True)
    street1             = CharField(_("Street"), max_length=80)
    street2             = CharField(_("Street"), max_length=80, blank=True)
    state               = CharField(_("State"), max_length=50, blank=True)
    city                = CharField(_("City"), max_length=50)
    postal_code         = CharField(_("Zip Code"), max_length=30)
    is_default_shipping = BooleanField(_("Default Shipping Address"), default=False)
    is_default_billing  = BooleanField(_("Default Billing Address"), default=False)
    country_name        = CharField(_("Country Name"), max_length=80, blank=True)

    def __unicode__(self):
       return u"%s - %s" % (self.contact.full_name, self.description)

    def save(self, **kwargs):
        """ If this address is the default billing or shipping address, then remove the old
            address's default status. If there is no existing default, then make this address the
            default.
        """
        existing_billing = self.contact.billing_address()
        if existing_billing:
            if self.is_default_billing:
                existing_billing.is_default_billing = False
                super(AddressBook, existing_billing).save()
        else:
            self.is_default_billing = True

        existing_shipping = self.contact.shipping_address()
        if existing_shipping:
            if self.is_default_shipping:
                existing_shipping.is_default_shipping = False
                super(AddressBook, existing_shipping).save()
        else:
            self.is_default_shipping = True

        super(AddressBook, self).save(**kwargs)

    class Meta:
        verbose_name = verbose_name_plural = _("Address Book")


class Contact(BaseModel):
    """A customer, supplier or any individual that a store owner might interact with."""
    title             = CharField(_("Title"), max_length=30, blank=True, null=True)
    first_name        = CharField(_("First Name"), max_length=30, null=True)
    last_name         = CharField(_("Last Name"), max_length=30, null=True)
    user              = ForeignKey(User, blank=True, null=True, unique=True)
    notes             = TextField(_("Notes"), max_length=500, blank=True)
    create_date       = DateField(_("Creation date"), auto_now_add=True)
    phone             = CharField(_("Phone"), max_length=15, blank=True, null=True)
    email             = CharField(_("Email"), max_length=30, null=True)
    organization_name = CharField(_("Organization name"), max_length=50, blank=True, null=True)

    def have_addresses(self):
        """Have shipping and billing addresses for checkout."""
        return self.billing_address() and self.shipping_address()

    def billing_address(self):
        return first(self.addressbook.filter(is_default_billing=True))

    def shipping_address(self):
        return first(self.addressbook.filter(is_default_shipping=True))

    def _get_full_name(self):
        """Return the person's full name."""
        return u"%s %s" % (self.first_name, self.last_name)
    full_name = property(_get_full_name)

    def __unicode__(self):
        return unicode(self.user) if self.user else self.full_name

    def save(self, *args, **kwargs):
        if not self.pk:
            self.email      = self.user.email
            self.first_name = self.user.first_name
            self.last_name  = self.user.last_name
        elif self.user:
            self.user.email      = self.email
            self.user.first_name = self.first_name
            self.user.last_name  = self.last_name
            self.user.save()
        super(Contact, self).save(*args, **kwargs)

    class Meta:
        verbose_name = _("Contact")
        verbose_name_plural = _("Contacts")


class Product(BaseModel):
    """ Root class for all Products. """
    short_description = TextField(_("Short description"), max_length=200, default='', blank=True)
    description       = TextField(_("Long description"), default='', blank=True, help_text=_("No maximum length."))
    date_added        = DateField(_("Date added"), null=True, blank=True, auto_now_add=True)
    length            = DecimalField(_("Length"), max_digits=6, decimal_places=0, null=True, blank=True)

    sequence          = TextField(_("Sequence"), default='', blank=True)
    contact           = ForeignKey(Contact, verbose_name=_("Contact"), null=True, blank=True, related_name="contacts")

    owner             = ForeignKey(Contact, verbose_name=_("Owner"), null=True, blank=True, related_name="owns")
    royalty_rate      = DecimalField(_("Royalty Rate"), max_digits = 2, decimal_places=2, null=True, blank=True)
    notes             = TextField(_("Notes"), max_length=500, blank=True)

    class Meta:
        ordering            = ["-date_added"]
        verbose_name        = _("Product")
        verbose_name_plural = _("Products")

    def translated_description(self, language_code=None):
        return lookup_translation(self, "description", language_code)

    def translated_short_description(self, language_code=None):
        return lookup_translation(self, "short_description", language_code)

    def __unicode__(self):
        s = self.sequence
        if len(s) <= 20 : return s + u" (len: %d)" % self.length
        else            : return s[:20] + u" ... (len: %d)" % self.length

    def get_absolute_url(self):
        return reverse2("store9_product")

    def save(self, **kwargs):
        self.sequence = self.sequence.replace(' ', '')
        self.length   = len(self.sequence)
        super(Product, self).save(**kwargs)


class Item(GenIDMixin, BaseModel):
    """Customer's item."""
    name         = CharField(_("Name"), max_length=255, null=True, blank=True, help_text=_("Max length: 255 characters."))
    date_added   = DateField(_("Date added"), null=True, blank=True, auto_now_add=True)
    active       = BooleanField(_("Active"), default=True, help_text=_("Set inactive rather than deleting."))
    sort_order   = IntegerField(_("Sort Order"), default=0, help_text=_("Sort order: override alphabetical order."))
    variation_of = ManyToManyField("self", blank=True, null=True, verbose_name=_("Variation Of"))

    sequence     = TextField(_("Sequence"), default='', blank=True, help_text=_("Maximum 1K (not yet enforced)."))
    notes        = TextField(_("Notes"), max_length=500, blank=True)
    product      = ForeignKey(Product, verbose_name=_("Product"), blank=True, null=True)
    item_id      = TextField(max_length=12, blank=True, primary_key=True)
    user         = ForeignKey(User, blank=True, null=True)

    id_field     = "item_id"
    id_len       = 12


    class Meta:
        ordering            = ("sort_order", "name", "-date_added")
        verbose_name        = _("Item")
        verbose_name_plural = _("Items")

    # next 5 methods are needed for sorting of listing adapted from Admin
    def _length(self):
        return self.product.length
    _length.admin_order_field = "product__length"

    def _description(self):
        return self.product.description
    _description.admin_order_field = "product__description"

    def _contact(self):
        return self.product.contact or ''
    _contact.admin_order_field = "product__contact"

    def _owner(self):
        return self.product.owner or ''
    _owner.admin_order_field = "product__owner"

    def _royalty_rate(self):
        return self.product.royalty_rate or ''
    _royalty_rate.admin_order_field = "product__royalty_rate"

    def __unicode__(self):
        # customer-defined products may NOT have a name
        if self.name:
            t = self.name
        else:
            s = self.sequence
            t = s if len(s)<=20 else (s[:20] + u" ...")
        return t

    def save(self, **kwargs):
        if not self.pk:
            seq = self.sequence.replace(' ', '')
            self.product, created = Product.objects.get_or_create(sequence=seq)
        super(Item, self).save(**kwargs)


class CartItem(GenIDMixin, BaseModel):
    """Each Item instance in the customer's shopping cart."""
    date_added = DateTimeField(auto_now_add=True)
    quantity   = IntegerField(default=1)
    item       = ForeignKey(Item)
    cart_iid   = TextField(max_length=12, primary_key=True)

    id_field   = "cart_iid"
    id_len     = 12

    class Meta:
        ordering = ["date_added"]

    def __unicode__(self):
        if self.item.name:
            t = self.item.name
        else:
            s = self.item.sequence
            t = s if len(s)<=20 else s[:20] + " ..."
        return u"Cart Item: " + t

    def total(self) : return self.quantity * 2
    def name(self)  : return self.item.name
    def price(self) : return 1

    def get_absolute_url(self):
        return self.product.get_absolute_url()

    def augment_quantity(self, quantity):
        """Called when adding an Item instance already in the shopping cart."""
        self.quantity = self.quantity + int(quantity)
        self.save()


class Order(GenIDMixin, BaseModel):
    created   = DateTimeField(auto_now_add=True)
    user      = ForeignKey(User, blank=True, null=True)
    items     = TextField(_("Items"), max_length=20000, blank=True)
    notes     = TextField(_("Notes"), max_length=500, blank=True)
    shipped   = BooleanField(_("Shipped"), default=False)
    po_num    = CharField(max_length=30, blank=True, null=True)
    order_num = CharField(max_length=8, primary_key=True)

    id_field  = "order_num"
    id_len    = 8

    def __unicode__(self):
        return u"Order: %s, %s, %s" % (self.user, self.created, self.order_num)


def make_id(chars, length):
    return join([x for x in [choice(chars) for y in range(length)]], '')
