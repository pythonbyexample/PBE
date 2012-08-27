#!/usr/bin/env python2.7

from __future__ import print_function, unicode_literals, division
import sys
import warnings
sys.path = [
            # "/usr/local/lib/python2.6/dist-packages/",
            # "/media/Main/Home/Projects/dprojects/django1.3/",
            "/home/ak/gen9/django1.3/",
            "/media/Main/Home/Projects/dprojects/",
            "/home/ak/.vim/python/",
           ] + sys.path

from django.core.management import execute_manager
try:
    import settings # Assumed to be in the same directory.
except ImportError:
    import sys
    sys.stderr.write("Error: Can't find the file 'settings.py' in the directory containing %r. It appears you've customized things.\nYou'll have to run django-admin.py, passing it your settings module.\n(If the file settings.py does indeed exist, it's causing an ImportError somehow.)\n" % __file__)
    sys.exit(1)

try: from reminders import *
except ImportError: pass

if __name__ == "__main__":
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        execute_manager(settings)
