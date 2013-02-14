Bombquiz
========


This tutorial will demonstrate how to create a simple Quiz app in Django using mcbv (modular CBVs)
library. Giving correct answers allows you to disarm the bomb but giving a wrong answer removes
some amount of time and if the time runs out, the bomb will explode!

You can view or download the code here:

`Browse source files <https://github.com/akulakov/django/tree/master/dbe/>`_

`dbe.tar.gz <https://github.com/akulakov/django/tree/master/dbe.tar.gz>`_

A few custom functions and classes and the MCBV library are used in the tutorials, please look
through the `libraries page <libraries.html>`_ before continuing.

I will focus on the important parts of code in the listings below; I recommend opening the
source files in a separate window to see import lines and other details.


Models
------

I'll start by defining model classes for the player record, quesion and answer:

.. sourcecode:: python

    class Question(BaseModel):
        question = CharField(max_length=200, unique=True)
        answer   = CharField(max_length=60)
        order    = IntegerField(unique=True)

        def __unicode__(self):
            return "%d. %s - %s" % (self.order, self.question, self.answer)

        class Meta:
            ordering = ["order"]


    class PlayerRecord(BaseModel):
        name    = CharField(max_length=60)
        email   = EmailField(max_length=120)
        created = DateTimeField(auto_now_add=True)
        passed  = BooleanField(default=False)

        def __unicode__(self):
            return "%s - %s" % (self.name, self.email)

        class Meta:
            ordering        = ["created"]
            unique_together = [["name", "email"]]


    class Answer(BaseModel):
        answer        = CharField(max_length=60)
        player_record = ForeignKey(PlayerRecord, related_name="answers")
        question      = ForeignKey(Question, related_name="answers")
        correct       = BooleanField()

        def __unicode__(self):
            return "%s, %s" % (self.answer, self.correct)

        class Meta:
            ordering        = ["question__order"]
            unique_together = [["question", "player_record"]]

The order field specifies the sequence in which questions are asked; when the answer is
processed, the view logic will determine if it's the right answer and set the correct field.
The passed field is set if the user disarms the bomb.

Next I'll add add the views for creating a new player record, taking the quiz and showing a
simple statistics page.



NewPlayer View
--------------

.. sourcecode:: python

    from dbe.mcbv.edit import CreateView, FormView

    seconds = 30

    class NewPlayer(CreateView):
        """Create new player & add data to session."""
        form_model      = PlayerRecord
        modelform_class = NewPlayerForm
        success_url     = reverse_lazy("question")
        template_name   = "newplayer.html"

        def modelform_valid(self, modelform):
            resp = super(NewPlayer, self).modelform_valid(modelform)
            data = dict(player_record=self.modelform_object, question=1, left=seconds)
            self.request.session.update(data)
            return resp


We need to use `reverse_lazy()` call because the view is imported in `urls.py` file before the url
patterns are initialized (which would make regular `reverse()` call fail).

Once the record is created, I need to store a few variables in the session; to make things
simpler, I'm not creating a `User` record, which would require a username and a password.

The basic form only needs to exclude `passed` field:

.. sourcecode:: python

    class NewPlayerForm(f.ModelForm):
        class Meta:
            model   = PlayerRecord
            exclude = ["passed"]


QuestionView
------------

.. sourcecode:: python

    lose_question = 20

    class QuestionView(FormView):
        form_class    = QuestionForm
        template_name = "question.html"

        def get_form_kwargs(self):
            """Get current section (container), init the form based on questions in the section."""
            kwargs      = super(QuestionView, self).get_form_kwargs()
            session     = self.request.session
            self.player = session.get("player_record")
            self.qn     = session.get("question", 1)
            if not self.player: raise Http404

            self.questions = Question.obj.all()
            if not self.questions: raise Http404

            self.question = self.questions[self.qn-1]
            return dict(kwargs, question=self.question)

        def form_valid(self, form):
            """Create user answer records from form data."""
            session = self.request.session
            left    = session.get("left", seconds)
            answer  = form.cleaned_data.get("answer")
            correct = bool(answer == self.question.answer)

            # subtract time left and create the answer object
            if not correct:
                left -= lose_question
                session["left"] = left
            Answer.obj.create(question=self.question, player_record=self.player, correct=correct, answer=answer)

            # redirect to the next question or to 'done' page
            if self.qn >= self.questions.count() or left <= 0:
                self.player.update( passed=bool(left > 0) )
                return redir("bqdone")
            else:
                session["question"] = session.get("question", 1) + 1
                return redir("question")

        def add_context(self):
            session = self.request.session
            return dict(qnum=self.qn, total=self.questions.count(), left=session["left"])


In `get_form_kwargs()` I need to load the question and pass it on to the form (see the code below).

In `form_valid()` the time is subtracted from time left if the answer was wrong; `Answer` record is
created and the user goes on to the next question or to the `done` view.

Finally, in `add_context()` I create a few variables to be used in the template.

The form creates the answer field dynamically based on the passed question; the field specifies
standard Django `RadioSelect` field to be used instead of the dropdown:

.. sourcecode:: python

    choices = [(c,c) for c in "yes no pass".split()]

    class QuestionForm(f.Form):
        def __init__(self, *args, **kwargs):
            """Add the field for `question`."""
            question = kwargs.pop("question").question
            super(QuestionForm, self).__init__(*args, **kwargs)
            field = f.ChoiceField(choices=choices, widget=RadioSelect, help_text=question)
            self.fields["answer"] = field

(I'm saving the question as `help_text` argument because it's a convenient way to include it in
the field.)

To keep things simple for this tutorial, the answer choices are hard-coded to be yes / no /
pass, but it would be quite easy to load choices from the database instead.


Done View
---------

.. sourcecode:: python

    class Done(TemplateView):
        template_name = "bombquiz/done.html"


Stats View
----------

The simple stats view looks at the players who failed to disarm the bomb and calculates average
# of questions they were able to get through before setting it off:

.. sourcecode:: python

    from dbe.mcbv.base import TemplateView

    class Stats(TemplateView):
        template_name = "stats.html"

        def add_context(self):
            records   = PlayerRecord.obj.filter(passed=False)
            answer    = records.annotate(anum=Count("answers"))
            aggregate = answer.aggregate(avg=Avg("anum"))
            return dict(ans_failed=aggregate)


New Player Template
-------------------

.. sourcecode:: django

    <div class="main">

        <form action="" method="POST">{% csrf_token %}
            <fieldset class="module">

            {{ modelform.non_field_errors }}
            {% for fld in modelform %}
                <div class="form-row">
                    <label class="{% if fld.field.required %} required {% endif %}">
                        {{ fld.help_text }} {{ fld.name }}
                    </label>
                    {{ fld }} {{ fld.errors }}
                </div>
            {% endfor %}

            </fieldset>
            <div id="submit"><input id="submit-btn" type="submit" value="Continue"></div>
        </form>
    </div>

In the template, I need to display non-field errors (in this case, the error will be shown if
the model's `unique_together` constraint is not met.)

.. image:: _static/img/bqnp.gif
    :class: screenshot

Question Template
-----------------

.. sourcecode:: django

    <div class="main">

        {% if left %}
            <h2>BOMB</h2> 0:{{ left }} left <h2>BOMB</h2>
        {% endif %}

        <form action="" method="POST">{% csrf_token %}
            <fieldset class="module">

            {{ form.non_field_errors }}
            {% for fld in form %}
                <div class="form-row">
                    <label class="{% if fld.field.required %} required {% endif %}">
                        {{ fld.help_text }}
                    </label>
                    {{ fld }} {{ fld.errors }}
                </div>
            {% endfor %}

            </fieldset>
            <div id="submit"><input id="submit-btn" type="submit" value="Continue"></div>
        </form>

        {% if qnum %} <p>{{ qnum }} of {{ total }}</p> {% endif %}
    </div>

On the top of page, the Bomb and the amount of time left are shown; then a standard form and
finally the question number.

I've also included a javascript snippet that stops the user from going back in the browser to
change the previous answer -- you can view it in the source file.


.. image:: _static/img/bqq.gif
    :class: screenshot

Done Template
-------------

.. sourcecode:: django

    <div class="main">
        {% if view.request.session.left <= 0 %}
            <pre>
                [bomb explosion ASCII art here]
            </pre>
        {% else %}
            You've disabled the bomb and won the game!!
        {% endif %}
        <p><a href="{% url 'new_player' %}">back to main page</a></p>
    </div>


This template is used for both failed and successful quiz end.

Stats Template
--------------

.. sourcecode:: django

    <div class="main">
    <p>Average num of answers for failed players: {{ ans_failed.avg|floatformat:2 }}</p>
    </div>

The stats template uses `floatformat` filter to have a nice formatting of the average.
