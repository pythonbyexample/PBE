
Django Tutorial: A Simple Forum - Part II
-----------------------------------------

Profile Picture
===============

Forums would look a little boring without ubiquitous profile pics. We already know how to add
images using Admin interface from the last tutorial, but doing the same from regular views
involves a bit more work.

To get us started, let's set out the naming scheme we'll use: url, function and template will all
be called `profile` and both url and function for saving the image will be called `save_profile`;
model class will be `UserProfile`. We have to add a link to `fbase.html`:

.. sourcecode:: django

    {% if user.is_authenticated %}
        <a href="{% url forum.views.profile user.pk %}">Edit profile</a> {% endif %}

Here's our `UserProfile` class:

.. sourcecode:: python

    class UserProfile(models.Model):
        avatar = models.ImageField("Profile Pic", upload_to="images/", blank=True, null=True)
        posts = models.IntegerField(default=0)
        user = models.ForeignKey(User, unique=True)

        def __unicode__(self):
            return unicode(self.user)

Don't forget to run `manage.py syncdb` to save the table!

We already used a ModelForm in MyBlog tutorial --- that part should be familiar to you. In
`profile()`, we're sending the image URL to the template if it already exists:

.. sourcecode:: python

    from PIL import Image as PImage
    from os.path import join as pjoin

    class ProfileForm(ModelForm):
        class Meta:
            model = UserProfile
            exclude = ["posts", "user"]

    @login_required
    def profile(request, pk):
        """Edit user profile."""
        profile = UserProfile.objects.get(user=pk)
        img = None

        if request.method == "POST":
            pf = ProfileForm(request.POST, request.FILES, instance=profile)
            if pf.is_valid():
                pf.save()
                # resize and save image under same filename
                imfn = pjoin(MEDIA_ROOT, profile.avatar.name)
                im = PImage.open(imfn)
                im.thumbnail((160,160), PImage.ANTIALIAS)
                im.save(imfn, "JPEG")
        else:
            pf = ProfileForm(instance=profile)

        if profile.avatar:
            img = "/media/" + profile.avatar.name
        return render_to_response("forum/profile.html", add_csrf(request, pf=pf, img=img))


`profile.html:`

.. sourcecode:: django

    <div id="rtitle">Edit Profile</div><br />

    <p>
    <form enctype="multipart/form-data" action="{% url forum.views.save_profile user.pk %}" method="POST">
        {% csrf_token %}
        {% if img %} <p><img border="0" alt="Profile Pic" src="{{ img }}" /></p> {% endif %}

        Profile Pic: {{ pf.avatar }}
        <input type="submit" value="Submit" id="submit" />
    </form>
    </p>

It's *very* important that the form tag should include the `enctype` property as shown. It's
particularly important to remember because there won't be any error if you omit it --- the file
simply won't be saved (guess if I forgot it while writing this tutorial!).

I haven't talked in depth about django forms yet and I won't now, but I'd like to point out that
Django gives you the choice between rendering the full form (except for the form opening, form
closing and submit tags) and formatting each field separately. To have Django show the full form,
I would just put `{{ pf }}` right before the submit tag. In this case, that would work almost as
well as it does now except that there would be no space between semicolon and the image input
field. Since we only have the single form field to show, it's very easy to add the Label and the
field manually.

It's also very important not to forget to add the `request.FILES` argument because Django won't
warn you or show any error. To keep things simple I'm assuming we'll be dealing with JPEG images
although in a real forum you'd want to also handle PNG and GIF files.

As always, we have to add the `urlconf` line:

.. sourcecode:: python

    (r"^profile/(\d+)/$", "profile"),


That what we have so far, with this wonderful picture of Moss I got off Wikipedia uploaded and
resized:

.. image:: _static/f5.png

Showing Profile Data in Posts
=============================

Of course, this is a bit useless if the profile pic doesn't show up in actual posts in a thread.
Usually forums will also add a bit of additional information like the number of posts and date
joined under the profile pic.

I could do this from the template but I think it's clearer and easier when this code is in
`models.py`:

.. sourcecode:: python

    class Post:
        # ...
        def profile_data(self):
            p = self.creator.userprofile_set.all()[0]
            return p.posts, p.avatar

In `thread.html`, we'll add this block of code:

.. sourcecode:: django

    <div class="ppic">
        {% with post.profile_data as pdata %}
            {% if pdata.1 %}
                <img src="{{ media_root }}{{ pdata.1 }}" /> <br />
            {% endif %}
        {{ post.creator }}<br />
        Posts: {{ pdata.0 }}<br />
        Joined: {{ post.creator.date_joined|date:"M d Y" }}
        {% endwith %}
    </div>

I'm using `with` tag to make code a little shorter and `date` filter to only show the date joined,
because `date_joined` stores both date and time.

We also have to make sure we increment the `posts` counter every time a user replies or creates a
thread:

.. sourcecode:: python

    def increment_post_counter(request):
        profile = request.user.userprofile_set.all()[0]
        profile.posts += 1
        profile.save()

    def new_thread(request, pk):
        """Start a new thread."""
        p = request.POST
        if p["subject"] and p["body"]:
            forum = Forum.objects.get(pk=pk)
            thread = Thread.objects.create(forum=forum, title=p["subject"], creator=request.user)
            Post.objects.create(thread=thread, title=p["subject"], body=p["body"], creator=request.user)
            increment_post_counter(request)
        return HttpResponseRedirect(reverse("dbe.forum.views.forum", args=[pk]))

The same call to `increment_post_counter()` should be added to `reply()` view as well.

Here's what we have now:

.. image:: _static/f6.png

`Continue to part III <forum3.html>`_
