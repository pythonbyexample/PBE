"""Based on django-registration 0.7"""

import random
import re
import sha

from datetime import datetime, timedelta

from django.conf import settings
from django.db import models
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.contrib.sites.models import Site


SHA1_RE = re.compile('^[a-f0-9]{40}$')


class RegistrationManager(models.Manager):
    subject_tpl = "Registration Confirmation for %s"

    def activate_user(self, activation_key):
        """
        To prevent reactivation of an account which has been deactivated by site administrators,
        the activation key is reset to the string ``ALREADY_ACTIVATED`` after successful
        activation.
        """
        if SHA1_RE.search(activation_key):
            try:
                profile = self.get(activation_key=activation_key)
            except self.model.DoesNotExist:
                return False
            if not profile.activation_key_expired():
                user = profile.user
                user.is_active = True
                user.save()
                profile.activation_key = self.model.ACTIVATED
                profile.save()
                return user
        return False

    def create_inactive_user(self, username, password, email, send_email=True, profile_callback=None):
        """ Note: Use `profile_callback` function to create a custom user profile. """
        print "in create_inactive_user()"
        new_user = User.objects.create_user(username, email, password)
        new_user.is_active = False
        new_user.save()

        registration_profile = self.create_profile(new_user)
        if profile_callback: profile_callback(user=new_user)

        if send_email:
            from django.core.mail import send_mail
            current_site = Site.objects.get_current()
            subject = self.subject_tpl % current_site

            c = {'activation_key'  : registration_profile.activation_key,
                 'expiration_days' : settings.ACCOUNT_ACTIVATION_DAYS,
                 'site'            : current_site }
            message = render_to_string('activation_email.txt', c)

            print "subject", subject
            print "message", message
            print "settings.DEFAULT_FROM_EMAIL", settings.DEFAULT_FROM_EMAIL
            print "new_user.email", new_user.email
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [new_user.email])
        return new_user

    def create_profile(self, user):
        """
        The activation key for the ``RegistrationProfile`` will be a SHA1 hash, generated from a
        combination of the ``User``'s username and a random salt.
        """
        salt = sha.new( str(random.random()) ).hexdigest()[:5]
        activation_key = sha.new(salt+user.username).hexdigest()
        return self.create(user=user, activation_key=activation_key)

    def delete_expired_users(self):
        """
        Remove expired instances of ``RegistrationProfile`` and their associated ``User``s.
        runs on: ``manage.py cleanupregistration``.

        If you have a troublesome ``User`` and wish to disable their account while keeping it in
        the database, simply delete the associated ``RegistrationProfile``; an inactive ``User``
        which does not have an associated ``RegistrationProfile`` will not be deleted.
        """
        for profile in self.all():
            if profile.activation_key_expired():
                if not profile.user.is_active:
                    profile.user.delete()


class RegistrationProfile(models.Model):
    objects        = obj = RegistrationManager()
    user           = models.ForeignKey(User, unique=True, verbose_name=_('user'),
                                       related_name="creg_profile")
    activation_key = models.CharField(_('activation key'), max_length=40)
    ACTIVATED      = u"ALREADY_ACTIVATED"

    class Meta:
        verbose_name = _('registration profile')
        verbose_name_plural = _('registration profiles')

    def __unicode__(self):
        return u"Registration information for %s" % self.user

    def activation_key_expired(self):
        expiration_date = timedelta(days=settings.ACCOUNT_ACTIVATION_DAYS)
        return self.activation_key == self.ACTIVATED or \
               (self.user.date_joined + expiration_date <= datetime.now())
    activation_key_expired.boolean = True
