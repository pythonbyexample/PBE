#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Imports {{{
import os, sys
import warnings
import inspect
from os.path import dirname, abspath, join as pjoin
sys.path = ["/usr/local/lib/python2.6/dist-packages/",
            "/usr/lib/python2.6/",
            pjoin(dirname(__file__), ".."),
            pjoin(dirname(__file__), "../.."),
           ] + sys.path
os.environ["DJANGO_SETTINGS_MODULE"] = "settings"

import re
from cStringIO import StringIO
from datetime import datetime, date
from copy import copy

from BeautifulSoup import BeautifulSoup

with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    import django
    from django.test import TestCase
    from django.test.client import Client
    from django.contrib.auth.models import User
    from django.contrib.sites.models import Site
    from django.core.urlresolvers import reverse

    from parse9.models import *
    from parse9.views import *
    from parse9.views import Container

username, pwd = "tests.py", "alkj 3s34senm-+()L;AKJSF D6374635%#@*LO IUN"
# }}}

class R: "Fake request."


class Test(TestCase):
    def setUp(self):
        # Site.objects.create(domain="test.org", name="test.org")
        self.lst = []
        self.u = User.objects.create_user(username, "ak@abc.org", pwd)
        self.r = R()
        self.r.user = self.u
        self.c = Client()
        self.c.login(username=username, password=pwd)
        self.proj = Project.objects.create(name="project1")
        self.const = Construct.objects.create(sequence="aaaaaa", name="const1")
        self.const.projects = [self.proj]
        self.const.save()
        pa = Parse.objects.create(name="parse1", project=self.proj)
        h = Half.objects.create(sequence="aaa")
        o = Oligo.objects.create(sequence="aaa", half1=h, oligo_number=1, parse=pa, construct=self.const,
                                 is_sense=True)


    def str2dict(self, s, sep1="\s\s+", sep2=','):
        """'foo  bar, baz  booz' => dict(foo='bar', baz='booz')"""
        return dict([[y.strip() for y in re.split(sep1, x.strip())] for x in s.split(sep2)])

    def get_content(self, url):
        """Get content of url."""
        ok, c = get_content(self.c, url)
        self.assertTrue(ok)
        return c

    def test_all_urls(self):
        self.status()
        urls_test(self.c, test_case=self)

    def test_melting_temp(self):
        """Test melting temp form."""
        self.status()
        url = reverse("parse9.views.melting_temp_rc", args=["tm"])

        data = Container(exact_rc30="aaa", dna_conc='2', salt_conc='5', mg_conc='9', column='')
        out1 = self.melt_temp_results(url, data)[-1]

        data.dna_conc, data.salt_conc, data.mg_conc = '1', '25', '10'
        out2 = self.melt_temp_results(url, data)[-1]

        data.exact_rc30, data.two_sequences = '', "aaa\n\nttt"
        out3 = self.melt_temp_results(url, data)[-1]

        data.exact_rc30, data.two_sequences = "aaa\nttt\nccc", ''
        out4 = self.melt_temp_results(url, data)[-3:]

        data.exact_rc30, data.column = "test\tttt\ttest", '2'
        out5 = self.melt_temp_results(url, data)[-1]

        # using .endswith() because AK local system does not have utils2
        self.assertTrue(out1.endswith("at Tm 2.0e-09;5;9 for aaa; GC 0%"))
        self.assertTrue(out2.endswith("at Tm 1.0e-09;25;10 for aaa; GC 0%"))
        self.assertTrue(out3.endswith("at Tm 1.0e-09;25;10 for aaa vs. ttt"))
        self.assertTrue(out4[0].endswith("at Tm 1.0e-09;25;10 for aaa; GC 0%"))
        self.assertTrue(out4[1].endswith("at Tm 1.0e-09;25;10 for ttt; GC 0%"))
        self.assertTrue(out4[2].endswith("at Tm 1.0e-09;25;10 for ccc; GC 100%"))
        self.assertTrue(out5.endswith("at Tm 1.0e-09;25;10 for ttt; GC 0%"))

    def test_calc_rc(self):
        """Test calculate RC form."""
        self.status()
        url = reverse("parse9.views.melting_temp_rc", args=["rc"])
        res = self.melt_temp_results

        data = Container(exact_rc30="aaa", column='')
        out1 = res(url, data)[-1]
        data.exact_rc30, data.two_sequences = '', "aaa\n\nttt"
        out3 = res(url, data)[-1]
        data.exact_rc30, data.two_sequences = "aaa\nttt\nccc", ''
        out4 = res(url, data)[-3:]
        data.exact_rc30, data.column = "test\tttt\ttest", '2'
        out5 = res(url, data)[-1]

        # using .endswith() because AK local system does not have utils2
        self.assertTrue(out1 == "C: ttt RC: ttt for aaa; GC 0%")
        self.assertTrue(out3 == "C: ttt, aaa; RC: ttt, aaa for aaa vs. ttt")
        self.assertTrue(out4[0] == "C: ttt RC: ttt for aaa; GC 0%")
        self.assertTrue(out4[1] == "C: aaa RC: aaa for ttt; GC 0%")
        self.assertTrue(out4[2] == "C: ggg RC: ggg for ccc; GC 100%")
        self.assertTrue(out5 == "C: aaa RC: aaa for ttt; GC 0%")

    def melt_temp_results(self, url, data):
        r = self.c.post(url, data)
        soup = BeautifulSoup(r.content)
        x = soup.find("textarea", id="id_results").string
        return x.split('\n')

    def status(self):
        print "running: %s()\n" % inspect.stack()[1][3]

    def test_create_project(self):
        """Test create project form."""
        self.status()
        url = reverse("parse9.views.create_project")
        cname, cseq = "c1", "ACGTACGTACGTACGTACGTACGTACGTACGTACGTACGTACGTACGTACGTACGTACGTACGT"
        seq = ">%s\t%s" % (cname, cseq)
        r = self.c.post(url, dict(name="proj", sequences=seq, constructs=[self.const.pk]))
        self.assertTrue(r.status_code == 302)

        p = Project.objects.get(name="proj")
        c = Construct.objects.get(name=cname, sequence=cseq)
        self.assertTrue(set(p.constructs.all()) == set([c, self.const]))

    def test_parse_project(self):
        """Test parse project form."""
        self.status()
        url = reverse("parse9.views.parse_project")
        p = Project.objects.create(name="proj")
        data = dict(project=p.pk, name="parse2", tm_target=1, tm_method="length", tag='x',
                    description='x', s_padding='x', is_padded=True)
        r = self.c.post(url, data)
        self.assertTrue(r.status_code == 302)
        self.assertTrue(Parse.objects.filter(**data))

    def test_create_oligos(self):
        """Test create oligos (add parse result) form."""
        self.status()

        url = reverse("parse9.views.create_oligos")
        # o1 = "1S ATACCTGGGAATCAATC"
        # o3 = "1A GCAACGGACGACCCC-GATTGATTCCCAGGTATAAAA"
        o2 = "3S TCAGCAGTCAACCGGAA-GTACGGACGATCGC"
        o4 = "3A GCGATCGTCCGTAC-TTCCGGTTGACTGCTGA"

        # post the form
        pa1 = Parse.objects.get(name="parse1").pk
        data = Container(oligos=join([o2,o4], '\n'), construct_name="const2", parse_name="parse2",
                         tm_target=1, tm_method="length", tag='x', description='x', is_padded=True,
                         s_padding='x', unpadded_parse=pa1)
        r = self.c.post(url, data)
        self.assertTrue("The following oligos were added to the database" in r.content)

        # check that oligos, parse and construct were created
        for o in (o2, o4):
            self.assertTrue(Oligo.objects.filter(sequence=o.split()[1]))

        kwargs = copy(data)
        del kwargs.oligos, kwargs.construct_name, kwargs.parse_name
        kwargs.name = "parse2"
        self.assertTrue(Parse.objects.filter(**kwargs))
        self.assertTrue(Construct.objects.filter(name="const2"))

        # post with a different const name
        data.construct_name = "const3"
        r = self.c.post(url, data)
        self.assertTrue("Save construct under old name: 'const2'?" in r.content)
        self.assertTrue("confirm saving under old name below or change the sequence" in r.content)

        # confirm save under old const name
        data.rename_construct = True
        data.parse_name="parse3"

        r = self.c.post(url, data)
        self.assertTrue("These oligos are already in the database" in r.content)
        # print 'DEBUG 4: here'

        # repost with same const name but different sequence
        o2 += 'C'
        o4 = "3A G" + o4.split()[1]
        data.oligos = join([o2,o4], '\n')
        data.construct_name = "const2"
        r = self.c.post(url, data)
        self.assertTrue(("Construct with this name (and a different sequence) already in DB, pick a "
                         "different name") in r.content)

    def errdebug(self, content):
        find = "error different rename_construct".split()
        lines = content.split('\n')
        for l in lines:
            for pat in find:
                if pat in l: print l

    def check_search(self, stype, pk, data):
        url = reverse("parse9.views.search", args=[stype])
        r = self.c.post(url, data)
        self.assertTrue(r.status_code == 200)
        if "Found 1 match" not in r.content:
            soup = BeautifulSoup(r.content)
            print soup.find('i')
        self.assertTrue("Found 1 match" in r.content)
        self.assertTrue(reverse("parse9.views.detail", args=[stype, pk]) in r.content)

    def loop_items(self, stype, attributes, initial=None):
        """ Assign attribute to each item and confirm that search finds that single item.

            Note: not all searches rely on item assignment, in some cases the search is performed
            on a different model field vs. form field, or on a related record. (e.g. parse name
            form field searches name_target).
        """
        for ind, attrs in enumerate(attributes):
            attr, value = attrs[:2]
            formval = value if len(attrs)==2 else attrs[2]
            setattr(self.lst[ind], attr, value)
            self.lst[ind].save()

            data = {} if not initial else copy(initial)
            data[attr] = formval
            self.check_search(stype, self.lst[ind].pk, data)

    def test_search_halves(self):
        """Test search halves form."""
        self.status()
        for x in range(1, 10):
            self.lst.append(Half.objects.create(sequence='a'*x))
        attributes = [
                         ("sequence"      , 'c'),
                         ("name"          , 'x'),
                         ("tm_unafold"    , 1),
                         ("gc_content"    , 50),
                         ("tag"           , 'x'),
                         ("description"   , 'x'),
                         ("creator"       , self.u),
                         ("creation_date" , date(2011, 3, 1)),
                         ("length"        , 9)
                     ]
        self.loop_items("half", attributes)


    def test_search_oligos(self):
        """Test search oligos form."""
        self.status()
        for x in range(1, 12):
            self.lst.append(Oligo.objects.create(sequence='a'*x, is_sense=True, oligo_number=x))
        attributes = [
                         ("sequence"      , 'c'),
                         ("name"          , 'x'),
                         ("oligo_number"  , 3),
                         ("oligo_id"      , "4S"),
                         ("is_sense"      , ''),
                         ("s_offset"      , 1),
                         ("tag"           , 'x'),
                         ("description"   , 'x'),
                         ("creator"       , self.u),
                         ("creation_date" , date(2011, 3, 1)),
                         ("length"        , 11)
                     ]
        self.loop_items("oligo", attributes, dict(is_sense="all"))

    def create_proj_const(self, pname, sequence, cname):
        """Create project and construct; return project."""
        p = Project.objects.create(name=pname)
        c = Construct.objects.create(sequence=sequence, name=cname)
        c.projects.add(p)
        return p

    def test_search_parses(self):
        """Test search parses form."""
        self.status()
        for x in range(1, 13):
            self.lst.append(Parse.objects.create(name=str(x), is_padded=False))

        self.lst[9].project  = self.create_proj_const("proj2", "ccc", "const2")
        self.lst[10].project = self.create_proj_const("proj3", "ttt", "const3")
        attributes = [
                         ("name"               , "(id %d)" % self.lst[0].pk),
                         ("tm_target"          , 2),
                         ("tm_method"          , "length"),
                         ("tag"                , 'x'),
                         ("description"        , 'x'),
                         ("creator"            , self.u),
                         ("creation_date"      , date(2011, 3, 1)),
                         ("is_padded"          , True, '1'),
                         ("s_padding"          , 'x'),
                         ("construct_name"     , "const2"),
                         ("construct_sequence" , "ttt"),
                     ]
        self.loop_items("parse", attributes, dict(is_padded="all"))

    def test_search_constructs(self):
        """Test search constructs form."""
        self.status()
        for x in range(1, 13):
            self.lst.append(Construct.objects.create(name=str(x), sequence='c'*x))
        attributes = [
                         ("sequence"      , "ggg"),
                         ("name"          , "const4"),
                         ("creator"       , self.u),
                         ("tag"           , 'x'),
                         ("description"   , 'x'),
                         ("prefix"        , 'x'),
                         ("suffix"        , 'x'),
                         ("prefix_note"   , 'x'),
                         ("suffix_note"   , 'x'),
                         ("creation_date" , date(2011, 3, 1)),
                         ("length"        , 11)
                     ]
        self.loop_items("construct", attributes)

    def test_search_projects(self):
        """Test search projects form."""
        self.status()
        for x in range(1, 7):
            self.lst.append(Project.objects.create(name=str(x)))
        c = Construct.objects.create(sequence="ggg", name="const5")
        c.projects.add(self.lst[5])
        attributes = [
                         ("name"          , "proj4"),
                         ("creator"       , self.u),
                         ("description"   , 'x'),
                         ("tag"           , 'x'),
                         ("creation_date" , date(2011, 3, 1)),
                         ("sequence"      , "ggg"),
                     ]
        self.loop_items("project", attributes)

def get_content(client, url, status_code=200):
    r = client.get(url)
    if (r.status_code==status_code) : return True, r.content, 0, 0
    else                            : return False, r.status_code, r.content, r


def add_align_stats(durls, constructs):
    """Go through `constructs` and, if a const is parsed, add alignment/stats/report urls to `durls`."""
    for obj in constructs:
        for proj in obj.projects.all():
            parses = proj.parses.all()
            if parses:
                p = parses[0]
                for v in "alignment stats parsed_construct".split():
                    durls.append(reverse("parse9.views."+v, args=["parse", p.pk, "construct", obj.pk]))
                    if v != "parsed_construct":
                        durls.append(reverse("parse9.views."+v, args=["parse", p.pk]))
                return

def urls_test(client, test_case=None):
    """ Test all urls return proper status code.

        `test_case`=None when run from command line, otherwise TestCase instance.
    """
    command_line = not test_case

    urls = "create_oligos create_project parse_project".split()
    urls = [reverse("parse9.views." + u) for u in urls]

    for arg in "tm rc".split():
        urls.append(reverse("parse9.views.melting_temp_rc", args=[arg]))

    itypes = "project parse construct oligo half".split()
    surls = [reverse("parse9.views.search", args=[u]) for u in itypes]

    durls = []
    for itype in itypes:
        cls = globals()[itype.capitalize()]
        lst = cls.objects.all()
        if lst:
            obj = lst[0]
            durls.append(reverse("parse9.views.detail", args=[itype, obj.pk]))
            if itype == "construct":
                add_align_stats(durls, lst)

    urls = [(u, 200) for u in urls + surls + durls + "/ /tools/".split()]

    for url, code in urls:
        ok, error_code, cont, r = get_content(client, url, code)
        if command_line:
            print "url: %-40s" % url,    # comma to append the status below
            if ok:
                print "[ OK ]"
            else:
                print "[ %s ERROR ]" % error_code
                print r, cont
                print
        else:
            if not ok: print url
            test_case.assertTrue(ok)

def main():
    """urls test"""
    if not User.objects.filter(username=username):
        User.objects.create_user(username, "test@test.com", pwd)
    c = Client()
    print "Logging in as:", username, pwd
    if not c.login(username=username, password=pwd):
        print "Error: could not login using l=%s, p=%s, existing.." % (username, pwd)
    else:
        urls_test(c)

if __name__ == '__main__':
    main()
