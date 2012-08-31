
Django Tutorial: A Simple Forum - Part III
------------------------------------------

It's good to have a forum of your own, post new topics, reply to oneself, start flamewars. All of
that is great, but what if.. you would like other users to be able to participate, as well? That
will be our last task in this tutorial: user registration.

User Registration
=================


There is already an existing package for Django that handles user registration --- all we have to
do is set it up for our needs. If you are on Ubuntu / Debian, you can install it by running
`apt-get install django-registration`.

Here is the outline of what we'll need to do to set things up for this package: we'll need to add
it to `settings.py`, we'll add `register`, `login` and `logout` links to our own `fbase.html`
template, add one `urlconf` line to the base `urls.py` module of our site and finally we'll
add a new directory with registration templates.

Here are the changes you'll need to do:

`settings.py`:

.. sourcecode:: python

    INSTALLED_APPS = (
        # ...
        'dbe.forum',
        'registration',
    )

`urls.py` (note: this is the base `urlconf` file located under `dbe/`, **not** under `dbe/forum/`):

.. sourcecode:: python

    (r'^accounts/', include('registration.urls')),

New links in `fbase.html`:

.. sourcecode:: django


    {% if not user.is_authenticated %}<a href="/accounts/login/?next=/forum/">login</a> | <a
        href="/accounts/register/">register</a>{% endif %}

    {% if user.is_authenticated %}<a href="/accounts/logout/?next=/forum/">logout</a>
        {% endif %}

Files under `templates/registration/`:


`activate.html`:

.. sourcecode:: django

    <html>
        <head>
            <title>Activation</title>
        </head>
        <body>
            <h2>Your account is now active!</h2>
            <a href="/accounts/login/?next=/forum/">Login</a>
        </body>
    </html>

`activation_complete.html`:

.. sourcecode:: django

    <html>
        <head>
            <title>Activation complete</title>
        </head>
        <body>
            <h4>Activation complete! Your account is now active.</h4>
        </body>
    </html>

`activation_email.txt`:

.. sourcecode:: text

    Your activation key: {{ activation_key }}

    Please use this link to activate your account:

    http://localhost:8000/accounts/activate/{{ activation_key }}/

    After activation you can login to the site:

    http://localhost:8000/accounts/login/

`activation_email_subject.txt`:

.. sourcecode:: text

    Activate your account

`login.html`:

.. sourcecode:: django

    {% extends "admin/base_site.html" %}
    {% load i18n %}

    {% block extrastyle %}{% load adminmedia %}{{ block.super }}
        <link rel="stylesheet" type="text/css" href="{% admin_media_prefix %}css/login.css" />
    {% endblock %}

    {% block bodyclass %}login{% endblock %}

    {% block content_title %}{% endblock %}

    {% block breadcrumbs %}{% endblock %}

    {% block content %}
    {% if error_message %}
    <p class="errornote">{{ error_message }}</p>
    {% endif %}
    <div id="content-main">
        <form action="{{ app_path }}" method="post" id="login-form">{% csrf_token %}
      <div class="form-row">
        <label for="id_username">{% trans 'Username:' %}</label>
            <input type="text" name="username" id="id_username" />
      </div>
      <div class="form-row">
        <label for="id_password">{% trans 'Password:' %}</label>
            <input type="password" name="password" id="id_password" />
        <input type="hidden" name="this_is_the_login_form" value="1" />
      </div>
      <div class="submit-row">
        <label>&nbsp;</label><input type="submit" value="{% trans 'Log in' %}" />
      </div>
    </form>

    <script type="text/javascript">
    document.getElementById('id_username').focus()
    </script>
    </div>
    {% endblock %}

`registration_complete.html`:

.. sourcecode:: django

    <html>
        <head>
            <title>Registration Complete</title>
        </head>
        <body>
            <h2>Registration Complete!</h2>
        </body>
    </html>

`registration_form.html`:

.. sourcecode:: django

    <html>
        <head>
            <title>Register</title>
        </head>
        <body>
            <h2>Register</h2>
            <form action="/accounts/register/" method="POST">{% csrf_token %}
                <table>
                {{ form.as_table }}
                </table>
            <p>
                <input type="submit" value="Submit" />
            </p>
            </form>
        </body>
    </html>

Screenshots of registration form and confirmation email:

.. image:: _static/f7.png

.. sourcecode:: django

.. image:: _static/f8.png

One last thing we should do is automatic creation of a `UserProfile` whenever a new user is
created. If `User` was a regular type of class defined in our `models.py`, you would already know
how to override `save()` method to create a profile along with user. There's just one little
problem.. `User` is a part of Admin --- how can we change what it does when saving itself?! One
way to do this would be to make a custom version of the Admin but there's an easier way using
Django `signals`. The idea is very simple: every time a certain model is saved, a `post_save`
signal is sent and associated function will be run:

.. sourcecode:: python

    from django.db.models.signals import post_save

    def create_user_profile(sender, **kwargs):
        """When creating a new user, make a profile for him or her."""
        u = kwargs["instance"]
        if not UserProfile.objects.filter(user=u):
            UserProfile(user=u).save()

    post_save.connect(create_user_profile, sender=User)

(This code should go into `models.py`). We have to check if `UserProfile` already exists because
this function will run every time changes to `User` are saved.

Automated Testing
=================

Automated testing can be tremendously useful with anything beyond the most basic web app. The
following code shows how to test basic functionality of the Forum app using Django's test client.
This code should live in `tests.py` under `dbe/forum/`:

.. sourcecode:: python

    from django.test import TestCase
    from django.test.client import Client
    from django.contrib.auth.models import User
    from django.contrib.sites.models import Site

    from dbe.forum.models import *

    class SimpleTest(TestCase):
        def setUp(self):
            f = Forum.objects.create(title="forum")
            u = User.objects.create_user("ak", "ak@abc.org", "pwd")
            Site.objects.create(domain="test.org", name="test.org")
            t = Thread.objects.create(title="thread", creator=u, forum=f)
            p = Post.objects.create(title="post", body="body", creator=u, thread=t)

        def content_test(self, url, values):
            """Get content of url and test that each of items in `values` list is present."""
            r = self.c.get(url)
            self.assertEquals(r.status_code, 200)
            for v in values:
                self.assertTrue(v in r.content)

        def test(self):
            self.c = Client()
            self.c.login(username="ak", password="pwd")

            self.content_test("/forum/", ['<a href="/forum/forum/1/">forum</a>'])
            self.content_test("/forum/forum/1/", ['<a href="/forum/thread/1/">thread</a>', "ak - post"])

            self.content_test("/forum/thread/1/", ['<div class="ttitle">thread</div>',
                   '<span class="title">post</span>', 'body <br />', 'by ak |'])

            r = self.c.post("/forum/new_thread/1/", {"subject": "thread2", "body": "body2"})
            r = self.c.post("/forum/reply/2/", {"subject": "post2", "body": "body3"})
            self.content_test("/forum/thread/2/", ['<div class="ttitle">thread2</div>',
                   '<span class="title">post2</span>', 'body2 <br />', 'body3 <br />'])

To run it, do: `manage.py test forum`. Django test
framework creates a separate, blank set of database tables for testing --- when the test is run,
it's up to you to create all records beforehand, including user accounts.

Instead of using standard `create()` method to create a user, we have to use special
`create_user()` method because the password is stored in hashed form; `create_user()` takes care
of that automatically.

The `test()` function creates a client object that logs in and accesses views similarly to how a
user's browser would use the App (technically, it works in a rather different way but we're not
concerned with that here). You can use client object to make `GET` and `POST` requests and check
if you get proper response status codes and contents.

Client object `post()` method accepts the url and a dictionary that will go into `request.POST` dictionary.
In the code sample above, `r.contents` will have full HTML code of the page as sent to the
browser, letting us test for presence of links, elements, data, etc.

This is a very basic example of testing, there's much more to it! --- make sure you take a quick
look through Django Documentation's `Chapter on Testing <http://docs.djangoproject.com/en/dev/topics/testing/>`_.

Forum Search
============

Adding an efficient full-text search is specific to the database you're using, although for small
and light traffic forums you might get away with using `.filter(body__icontains=myquery)` ---
simple SQL search.  Another option is to use a Google search box restricted to your domain:

.. sourcecode:: django

    <form method="get" action="http://www.google.com/search">
        <input type="text"   name="q" size="31" maxlength="255" value="" />
        <input type="submit" value="Google Search" />
        <input type="radio"  name="sitesearch" value="" /> The Web
        <input type="radio"  name="sitesearch" value="mydomain.com" checked /> My Site<br />
    </form>

That's all for `A Simple Forum` tutorial. Hope you enjoyed it!



`Download Full Sources <forumsrc.tar.gz>`_

The Moss photo was created by: `KirinX <http://en.wikipedia.org/wiki/User:KirinX>`_


