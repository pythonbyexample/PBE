from django.contrib.auth.models import User
from django.db import models
from django.core import urlresolvers
from django.utils.translation import get_language, ugettext, ugettext_lazy as _
# from l10n.models import Country
import datetime

from utils import slugify

# subset of Satchmo's model, plus Gen9-specific fields

# TBD: University discount ... but may be able to simplify vs. Satchmo discount (e.g. apply to entire order)
# TBD: add tags, presumably via a generic Django app


class Contact(models.Model):
    """
    A customer, supplier or any individual that a store owner might interact
    with.
    """
    # why does Satchmo repeat fields from the 'auth' user???
    title = models.CharField(_("Title"), max_length=30, blank=True, null=True)
#    first_name = models.CharField(_("First name"), max_length=30, )
#    last_name = models.CharField(_("Last name"), max_length=30, )
    user = models.ForeignKey(User, blank=True, null=True, unique=True)
#    role = models.ForeignKey(ContactRole, verbose_name=_("Role"), null=True)
#    organization = models.ForeignKey(Organization, verbose_name=_("Organization"), blank=True, null=True)
#    email = models.EmailField(_("Email"), blank=True, max_length=75)
    notes = models.TextField(_("Notes"), max_length=500, blank=True)
    # Contact.create_date and Product.date_added are consistent with Satchmo, though not each other
    create_date = models.DateField(_("Creation date"))
    
    # Satchmo handles via a ForeignKey
    organization_name = models.CharField(_("Organization name"), max_length=50, blank=True, null=True)

    first_name = user.first_name
    last_name = user.last_name
    email = user.email
    
    def _get_full_name(self):
        """Return the person's full name."""
        return u'%s %s' % (self.first_name, self.last_name)
    full_name = property(_get_full_name)

    def _shipping_address(self):
        """Return the default shipping address or None."""
        try:
            return self.addressbook_set.get(is_default_shipping=True)
        except AddressBook.DoesNotExist:
            return None
    shipping_address = property(_shipping_address)

    def _billing_address(self):
        """Return the default billing address or None."""
        try:
            return self.addressbook_set.get(is_default_billing=True)
        except AddressBook.DoesNotExist:
            return None
    billing_address = property(_billing_address)

    def _primary_phone(self):
        """Return the default phone number or None."""
        try:
            return self.phonenumber_set.get(primary=True)
        except PhoneNumber.DoesNotExist:
            return None
    primary_phone = property(_primary_phone)

    def __unicode__(self):
        return self.full_name

    def save(self, **kwargs):
        """Ensure we have a create_date before saving the first time."""
        if not self.pk:
            self.create_date = datetime.date.today()
        # Validate contact to user sync
        #if self.user:
            #dirty = False
            #user = self.user
            #if user.email != self.email:
                #user.email = self.email
                #dirty = True

            #if user.first_name != self.first_name:
                #user.first_name = self.first_name
                #dirty = True

            #if user.last_name != self.last_name:
                #user.last_name = self.last_name
                #dirty = True

            #if dirty:
                #self.user = user
                #self.user.save()

        super(Contact, self).save(**kwargs)

    class Meta:
        verbose_name = _("Contact")
        verbose_name_plural = _("Contacts")


# class PhoneNumber(models.Model):
#     """
#     Phone number associated with a contact.
#     """
#     contact = models.ForeignKey(Contact)
#     type = models.CharField(_("Description"), choices=PHONE_CHOICES,
#         max_length=20, blank=True)
#     phone = models.CharField(_("Phone Number"), blank=True, max_length=30,
#         )
#     primary = models.BooleanField(_("Primary"), default=False)
# 
#     def __unicode__(self):
#         return u'%s - %s' % (self.type, self.phone)
# 
#     def save(self, **kwargs):
#         """
#         If this number is the default, then make sure that it is the only
#         primary phone number. If there is no existing default, then make
#         this number the default.
#         """
#         existing_number = self.contact.primary_phone
#         if existing_number:
#             if self.primary:
#                 existing_number.primary = False
#                 super(PhoneNumber, existing_number).save()
#         else:
#             self.primary = True
#         super(PhoneNumber, self).save(**kwargs)
# 
#     class Meta:
#         ordering = ['-primary']
#         verbose_name = _("Phone Number")
#         verbose_name_plural = _("Phone Numbers")


class AddressBook(models.Model):
    """
    Address information associated with a contact.
    """
    contact = models.ForeignKey(Contact, related_name='%(app_label)s_%(class)s_related')
    description = models.CharField(_("Description"), max_length=20, blank=True,
        help_text=_('Description of address - Home, Office, Warehouse, etc.',))
    addressee = models.CharField(_("Addressee"), max_length=80)
    street1 = models.CharField(_("Street1"), max_length=80)
    street2 = models.CharField(_("Street2"), max_length=80, blank=True)
    state = models.CharField(_("State"), max_length=50, blank=True)
    city = models.CharField(_("City"), max_length=50)
    postal_code = models.CharField(_("Zip Code"), max_length=30)
    # country = models.ForeignKey(Country, verbose_name=_("Country"))
    is_default_shipping = models.BooleanField(_("Default Shipping Address"),
        default=False)
    is_default_billing = models.BooleanField(_("Default Billing Address"),
        default=False)
    
    # not in Satchmo
    country_name = models.CharField(_("Country Name"), max_length=80)

    def __unicode__(self):
       return u'%s - %s' % (self.contact.full_name, self.description)

    def save(self, **kwargs):
        """
        If this address is the default billing or shipping address, then
        remove the old address's default status. If there is no existing
        default, then make this address the default.
        """
        existing_billing = self.contact.billing_address
        if existing_billing:
            if self.is_default_billing:
                existing_billing.is_default_billing = False
                super(AddressBook, existing_billing).save()
        else:
            self.is_default_billing = True

        existing_shipping = self.contact.shipping_address
        if existing_shipping:
            if self.is_default_shipping:
                existing_shipping.is_default_shipping = False
                super(AddressBook, existing_shipping).save()
        else:
            self.is_default_shipping = True

        super(AddressBook, self).save(**kwargs)

    class Meta:
        verbose_name = _("Address Book")
        verbose_name_plural = _("Address Books")


class Product(models.Model):
    """
    Root class for all Products
    """
    # CONSIDER: might need "unique together" ('slug', 'owner')
    
    # name is NOT required for customer-defined products
    name = models.CharField(_("Name"), max_length=255, null=True, blank=True, help_text=_("Max length: 255 characters."))
    slug = models.SlugField(_("Slug"), blank=True, help_text=_("Product ID (SEGUID; a hash of the sequence), e.g. for URLs ('slug' is a newspaper / Django term)"))
# ignore the short_description for now
    short_description = models.TextField(_("Short description"), max_length=200, default='', blank=True, help_text=_("Max length: 200 characters."))
    description = models.TextField(_("Long description"), default='', blank=True, help_text=_("No maximum length."))
    
    # Contact.create_date and Product.date_added are consistent with Satchmo, though not each other
    date_added = models.DateField(_("Date added"), null=True, blank=True)
    active = models.BooleanField(_("Active"), default=True, help_text=_("Set inactive rather than deleting."))
    ordering = models.IntegerField(_("Ordering"), default=0, help_text=_("Sort order: override alphabetical order."))
    length = models.DecimalField(_("Length"), max_digits=6, decimal_places=0, null=True, blank=True)
    
    # not in Satchmo
    variation_of = models.ManyToManyField('self', blank=True, null=True, verbose_name=_('Variation Of'), related_name='%(app_label)s_%(class)s_related')
    sequence = models.TextField(_("Sequence"), default='', blank=True, help_text=_("Maximum 1K (not yet enforced)."))
    contact = models.ForeignKey(Contact, verbose_name=_('Contact'), null=True, blank=True, related_name='%(app_label)s_%(class)s_related', 
        help_text=_("Customer who created this product; may be blank for public parts."))
    # related_name for owner must be different since it's a second ForeignKey into Contact
    owner = models.ForeignKey(Contact, verbose_name=_('Owner'), null=True, blank=True, related_name='owns', 
        help_text=_("Gen9 will create this link if customer is NOT the owner."))
    royalty_rate = models.DecimalField(_("Royalty Rate"), max_digits = 2, decimal_places=2, null=True, blank=True)

    def translated_attributes(self, language_code=None):
        if not language_code:
            language_code = get_language()
        q = self.productattribute_set.filter(languagecode__exact = language_code)
        if q.count() == 0:
            q = self.productattribute_set.filter(Q(languagecode__isnull = True) | Q(languagecode__exact = ""))
        return q

    def translated_description(self, language_code=None):
        return lookup_translation(self, 'description', language_code)

    def translated_name(self, language_code=None):
        return lookup_translation(self, 'name', language_code)

    def translated_short_description(self, language_code=None):
        return lookup_translation(self, 'short_description', language_code)

    def __unicode__(self):
        # customer-defined products may NOT have a name
        if self.name:
            return self.name
        else:
            return self.slug

    def get_absolute_url(self):
        return urlresolvers.reverse('store9_product', kwargs={'product_slug': self.slug})

    class Meta:
        ordering = ('ordering', 'name', '-date_added')
        verbose_name = _("Product")
        verbose_name_plural = _("Products")

    def save(self, **kwargs):
        if not self.pk:
            # the product is new
            self.date_added = datetime.date.today()

        if not self.slug:
            # TBD: replace with SEGUID from BioPython
            if self.name:
                # this is risky since I'm not verifying that name is unique
                self.slug = slugify(self.name, instance=self)
            else:
                # replace non-word chars to follow the default slug rules checked by admin UI
                self.slug = datetime.datetime.now().isoformat().replace('.', '-').replace(':', '-')
        
        self.length = len(self.sequence.replace(' ', ''))

        super(Product, self).save(**kwargs)