""" Forms and validation code for user registration. """

from django import forms as f
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User

from dbe.cregistration.models import RegistrationProfile

from dbe.shared.utils import ContainerFormMixin


class RegistrationForm(f.Form):
    """ Form for registering a new user account.
        Validates that the requested username is not already in use.
    """
    username  = f.RegexField(regex=r'^\w+$', max_length=30, label=_(u'username'))
    email     = f.EmailField(widget=f.TextInput(attrs=dict(maxlength=75)), label=_(u'email address'))
    password1 = f.CharField(widget=f.PasswordInput(render_value=False), label=_(u'password'))
    password2 = f.CharField(widget=f.PasswordInput(render_value=False), label=_(u'password (again)'))

    error_css_class    = "error"
    required_css_class = "required"

    def clean_username(self):
        """ Validate that the username is alphanumeric and is not already in use. """
        username = self.cleaned_data['username']
        try:
            user = User.objects.get(username__iexact=username)
        except User.DoesNotExist:
            return username
        raise f.ValidationError(_(u'This username is already taken. Please choose another.'))

    def clean(self):
        """ Verify that the values entered into the two password fields match. """
        super(RegistrationForm, self).clean()
        data   = self.cleaned_data
        p1, p2 = data.get("password1"), data.get("password2")
        if p1 and p1 != p2:
            raise f.ValidationError(_(u'You must type the same password each time'))
        return data

    def save(self, profile_callback=None):
        """ Create the new ``User`` and ``RegistrationProfile``, and returns the ``User``. """
        data = self.cleaned_data
        args = data.get("username"), data.get("password1"), data.get("email")
        return RegistrationProfile.obj.create_inactive_user(*args, profile_callback=profile_callback)


class RegistrationFormTermsOfService(RegistrationForm):
    err   = {'required': u"You must agree to the terms to register"}
    label = _(u'I have read and agree to the Terms of Service')
    tos   = f.BooleanField(label=label, error_messages=err)


class RegistrationFormUniqueEmail(RegistrationForm):
    """ Subclass of ``RegistrationForm`` which enforces uniqueness of email addresses. """
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email__iexact=email):
            raise f.ValidationError(_(u"This email address is already in use. Please supply a different email address."))
        return email


class RegistrationFormNoFreeEmail(RegistrationForm):
    bad_domains = ['aim.com', 'aol.com', 'email.com', 'gmail.com',
                   'googlemail.com', 'hotmail.com', 'hushmail.com',
                   'msn.com', 'mail.ru', 'mailinator.com', 'live.com']

    def clean_email(self):
        errmsg = u'Registration using free email addresses is prohibited. Please supply a different email address.'
        email  = self.cleaned_data.get("email")
        if email.split('@')[1] in self.bad_domains:
            raise f.ValidationError(_(errmsg))
        return email
