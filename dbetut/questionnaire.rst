Questionnaire
=============

This tutorial will show you how to create a Questionnaire App in Django using mcbv (modular
CBVs) library.

The basic idea of this App is that you can define multiple questionnaires, with each
questionnaire split into sections (each section will be shown on its own page), with multiple
questions per section. A question may be a multiple-choice with a dropdown menu or a simple
textbox entry.

You can view or download the code here:

`Browse source files <https://github.com/akulakov/django/tree/master/dbe/>`_

`dbe.tar.gz <https://github.com/akulakov/django/tree/master/dbe.tar.gz>`_

A few custom functions and classes and the MCBV library are used in the tutorials, please look
through the `libraries page <libraries.html>`_ before continuing.

I will focus on the important parts of code in the listings below; I recommend opening the
source files in a separate window to see import lines and other details.

Outline
-------

There are three models used to set up the questionnaire: `Question` defines a question, optional
choices, answer type, section and order; `Section` defines name, questionnaire and order;
`Questionnaire` has one field: name.

There are two additional models used to keep track of user's submissions: `Answer` contains
answer and a pointer to `Question;` `UserQuestionnaire` contains pointers to the `User` and to
`Questionnaire.`

`ViewQuestionnaire` is used to take the questionnaire; `Questionnaires` is the main listing view.

Results and statistics are provided by `UserQuests,` `UserQuest` and `QuestStats` views.

Questionnaire model
-------------------

.. sourcecode:: python

    link = "<a href='%s'>%s</a>"

    class Questionnaire(BaseModel):
        name = CharField(max_length=60, unique=True)

        def __unicode__(self):
            return self.name

        def get_absolute_url(self, section=1):
            return reverse2("questionnaire", self.pk, section)

        def section_links(self):
            section_url = "admin:questionnaire_section_change"
            lst         = [(c.pk, c.name) for c in self.sections.all()]
            lst         = [ (reverse2(section_url, pk), name) for pk, name in lst ]
            return ", ".join( [link % c for c in lst] )
        section_links.allow_tags = True

In `get_absolute_url()` I return specified section, not the entire questionnaire view as you'd
normally do. (In fact, there is no view of the entire questionnaire.)

Section & Question models
-------------------------

.. sourcecode:: python

    class Section(BaseModel):
        """Container for a few questions, shown on a single page."""
        name          = CharField(max_length=60, blank=True, null=True)
        questionnaire = ForeignKey(Questionnaire, related_name="sections", blank=True, null=True)
        order         = IntegerField()

        class Meta:
            ordering        = ["order"]
            unique_together = [["questionnaire", "order"]]

        def __unicode__(self):
            return "[%s] (%s) %s" % (self.questionnaire, self.order, self.name or '')

        def title(self):
            return "(%s) %s" % (self.order, self.name or '')

I need to make sure that I don't accidentally save a section with the same `order` number -- this
can be guarded against by setting the `unique_together` constraint.

.. sourcecode:: python

    class Question(BaseModel):
        question    = CharField(max_length=200)
        choices     = CharField(max_length=500, blank=True, null=True)
        answer_type = CharField(max_length=6, choices=(("str", "str"), ("int", "int")))
        section     = ForeignKey(Section, related_name="questions", blank=True, null=True)
        order       = IntegerField()

        class Meta:
            ordering        = ["order"]
            unique_together = [["section", "order"]]

        def __unicode__(self):
            return "%s: %s" % (self.section, self.question)

UserQuestionnaire and Answer models
-----------------------------------

.. sourcecode:: python

    class UserQuestionnaire(BaseModel):
        user          = ForeignKey(User, related_name="questionnaires", blank=True, null=True)
        questionnaire = ForeignKey(Questionnaire, related_name="user_questionnaires", blank=True, null=True)
        created       = DateTimeField(auto_now_add=True)

        def __unicode__(self):
            return "%s - %s" % (self.user, self.questionnaire)

        class Meta:
            ordering = ["user", "created"]

.. sourcecode:: python

    class Answer(BaseModel):
        answer             = CharField(max_length=200)
        question           = ForeignKey(Question, related_name="answers", blank=True, null=True)
        user_questionnaire = ForeignKey(UserQuestionnaire, related_name="answers", blank=True, null=True)

        def __unicode__(self):
            return "%s - %s" % (self.user_questionnaire, self.answer)

        class Meta:
            ordering = ["question__section__order", "question__order"]

Did you know that `ordering` can span relations?

Questionnaires, UserQuests and UserQuest Views
----------------------------------------------

.. sourcecode:: python

    class Questionnaires(ListView):
        list_model    = Questionnaire
        template_name = "questionnaires.html"

    class UserQuests(ListRelated):
        detail_model  = Questionnaire
        list_model    = UserQuestionnaire
        related_name  = "user_questionnaires"
        template_name = "user-quests.html"

    class UserQuest(DetailView):
        detail_model  = UserQuestionnaire
        template_name = "user-quest.html"

QuestStats View
---------------

.. sourcecode:: python

    class QuestStats(DetailView):
        detail_model  = Questionnaire
        template_name = "quest-stats.html"

        def stats(self):
            user_quests = UserQuestionnaire.obj.filter(questionnaire=self.detail_object)
            d           = DefaultOrderedDict
            #             quests    sections  questions answers:nums
            quests      = d( lambda:d( lambda:d( lambda:d(int) ) ) )

            for user_quest in user_quests:
                quest = user_quest.questionnaire.name

                # add each answer in user questionnaire to respective sections sub-dict, add to counter
                for answer in user_quest.answers.all():
                    question = answer.question
                    answer   = answer.answer
                    q        = question.question
                    section  = question.section.name

                    quests[quest][section][q][answer] += 1

            # sort to have most frequent answers first
            for quest in quests.values():
                for section in quest.values():
                    for name, question in section.items():
                        answers       = sorted(question.items(), key=itemgetter(1), reverse=True)
                        section[name] = OrderedDict(answers)

            return defdict_to_odict(quests)

The `stats()` method is a bit complicated since it's storing deeply nested data that needs to
be sorted. I'm using `utils.DefaultOrderedDict` to make it easy to create the nested dict;
unfortunately, Django templates can't iterate default dicts (Django tries to resolve `items()`
as a dictionary key first, which returns 0 for our default dict). To straighten this out, I use
`utils.defdict_to_odict()` to convert all nested dicts to ordered dicts.

ViewQuestionnaire
-----------------

.. sourcecode:: python

    class ViewQuestionnaire(ListRelated, FormView):
        detail_model  = Questionnaire
        list_model    = Section
        related_name  = "sections"
        form_class    = SectionForm
        template_name = "quest.html"

        def get_section(self):
            self.snum = int(self.kwargs.get("section", 1))
            return self.get_list_queryset()[self.snum-1]

        def get_form_kwargs(self):
            kwargs = super(ViewQuestionnaire, self).get_form_kwargs()
            return dict(kwargs, section=self.get_section())

        def form_valid(self, form):
            """Create user answer records using form data."""
            stotal  = self.get_list_queryset().count()
            quest   = self.get_detail_object()
            uquest  = UserQuestionnaire.obj.get_or_create(questionnaire=quest, user=self.user)[0]
            section = self.get_section()

            for order, value in form.cleaned_data.items():
                question = section.questions.get(order=int(order))
                answer   = Answer.obj.get_or_create(user_questionnaire=uquest, question=question)[0]
                answer.update(answer=value)

            # redirect to the next section or to 'done' page
            if self.snum >= stotal : return redir("done")
            else                   : return redir( quest.get_absolute_url(self.snum+1) )

In `get_form_kwargs()` I need to tell the form which section is to be used; in `form_valid()` the
logic is to update records based on user input and either go to the next section or to finish
the questionnaire.

SectionForm
-----------

.. sourcecode:: python

    class SectionForm(f.Form):
        def __init__(self, *args, **kwargs):
            """ Add a field for every question.
                Field may be CharField or ChoiceField; field name is question.order.
            """
            section = kwargs.pop("section")
            super(SectionForm, self).__init__(*args, **kwargs)

            for question in section.questions.all():
                choices = question.choices
                kw      = dict(help_text=question.question)

                if choices:
                    fld           = f.ChoiceField
                    choices       = [c.strip() for c in choices.split(',')]
                    kw["choices"] = [(c,c) for c in choices]
                else:
                    fld              = f.CharField
                    kw["max_length"] = 200

                self.fields[str(question.order)] = fld(**kw)

Question fields are created based on current section, using either ChoiceField (with a dropdown
menu) or a CharField.

Main Listing Template
---------------------

.. sourcecode:: django

    <div class="main">
        <table border="0" cellpadding="2" cellspacing="2">
            {% for quest in questionnaire_list %}
                <tr>
                    <td> {{ quest.name }} </td>
                    <td> <a href="{% url 'questionnaire' quest.pk %}">Take!</a> </td>
                    <td> <a href="{% url 'user_questionnaires' quest.pk %}">Results</a> </td>
                    <td> <a href="{% url 'quest_stats' quest.pk %}">Stats</a> </td>
                </tr>
            {% endfor %}
        </table>
    </div>

I've created a sample questionnaire called 'Mood':

.. image:: _static/img/q-list.gif
    :class: screenshot

UserQuests and UserQuest Templates
----------------------------------

.. sourcecode:: django

    <div class="main">
        <ul>
            {% for quest in userquestionnaire_list %}
                <li><a href="{% url 'user_questionnaire' quest.pk %}"
                            >{{ quest.user }} - {{ quest.questionnaire.name }}</a></li>
            {% endfor %}
        </ul>
    </div>

.. sourcecode:: django

    <div class="main">
        <table border="0" cellpadding="2" cellspacing="2">

        {% for answer in userquestionnaire.answers.all %}

            {% with answer.question.section.title as title %}
                {% ifchanged title %}
                    <tr><td colspan="2"><p class="title">{{ title }}</p></td></tr>
                {% endifchanged %}
            {% endwith %}

            <tr>
                <td>{{ answer.question.question }}</td>
                <td>{{ answer.answer }}</td>
            </tr>

        {% endfor %}

        </table>
    </div>

The following screenshot is the `UserQuest` view:

.. image:: _static/img/q-uquest.gif
    :class: screenshot

QuestStats Template
-------------------

.. sourcecode:: django

    <div class="main">

        {% for quest, sections in view.stats.items %}
            <h4>{{ quest }}</h4>
            <ul id="quest">
                {% for section, questions in sections.items %}
                    <h5>{{ section }}</h5>
                    <ul>

                        {% for question, answers in questions.items %}
                            <p>{{ question }}</p>
                            <ul>
                                {% for answer, num in answers.items %}
                                    <p>{{ answer }} - {{ num }}</p>
                                {% endfor %}
                            </ul>
                        {% endfor %}

                    </ul>
                {% endfor %}
            </ul>
        {% endfor %}

    </div>

Statistics are not very impressive because I only had the patience to take the questionnaire
with one user account:

.. image:: _static/img/q-stats.gif
    :class: screenshot

ViewQuestionnaire Template
--------------------------

.. sourcecode:: django

    <div class="main">
        <form action="" method="POST">{% csrf_token %}
            <fieldset class="module aligned">

            <!-- see note in SectionForm docstring -->
            {% for fld in form %}
                <div class="form-row">
                    <label class="{% if fld.field.required %} required {% endif %}">
                        {{ fld.label }}. {{ fld.help_text }}
                    </label>
                    {{ fld }} {{ fld.errors }}
                </div>
            {% endfor %}

            </fieldset>
            <div id="submit"><input id="submit-btn" type="submit" value="Continue"></div>
        </form>
    </div>

The screenshot is just for the first section:

.. image:: _static/img/q-quest.gif
    :class: screenshot

That's all!
