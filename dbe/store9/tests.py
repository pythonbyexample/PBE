""" Tests for gen9 store app.. """

from django.test import TestCase
from django.test.client import Client
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse

from store.store9.models import *
from store.store9.views import *
from store.store9.changelist import randseq

class SimpleTest(TestCase):
    def setUp(self):
        # Site.objects.create(domain="test.org", name="test.org")
        self.u = User.objects.create_user("ak", "ak@abc.org", "pwd")
        self.items = []
        for x in range(3):
            i = Item(name='', sequence=randseq(), user=self.u)
            i.save()
            self.items.append(i)
        self.c = Client()
        self.c.login(username="ak", password="pwd")

    def test_add_to_cart(self):
        seqs = []
        for i in self.items:
            seqs.append('<td class="left">%s</td>' % i.sequence)
            add_item(self.u, i.pk)

        add_item(self.u, self.items[0].pk)
        add_item(self.u, self.items[0].pk)
        quantities = []
        # self.content_test(reverse("store9.views.cart"), [])

    def content_test(self, url, values):
        """Get content of url and test that each of items in `values` list is present."""
        r = self.c.get(url)
        self.assertEquals(r.status_code, 200)
        for v in values:
            self.assertTrue(v in r.content)
