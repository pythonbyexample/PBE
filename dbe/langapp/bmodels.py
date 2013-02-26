import operator
from django.db.models import *

from django.contrib.auth.models import User, UserManager

from fate.custom.batch_select import batch_select
from fate.game.managers import *

test_types    = [(x,x) for x in ("Short answer", "MC", "Argument")]
test_features = [(x,x) for x in ("Map", "Quotation", "Cartoon", "Chart")]


# Tag is a base class for Region, Period, and Theme
class Tag(Model):
    obj  = objects = BaseManager()
    name = CharField(max_length=30, unique=True)

    def __unicode__(self):
        return self.name

    class Meta:
        abstract = True

class Region(Tag):
    abbr = CharField(max_length=30, unique=True)

class Period(Tag):
    pass

class Theme(Tag):
    pass


class Card(Model):
    obj           = objects = CardManager()
    region_number = IntegerField()
    region        = ForeignKey(Region)
    period        = ForeignKey(Period, null=True)
    theme         = ForeignKey(Theme)
    points        = IntegerField(default=1)
    question      = CharField(max_length=500)
    answers       = TextField()
    right_answer  = IntegerField()

    def __unicode__(self):
        return u"%s: %d, %s" % (self.region, self.region_number, self.theme)

    def answer_list(self):
        return self.answers.strip().split("\n\n")

    class Meta:
        unique_together = (("region", "region_number"))


class ResourceFile(Model):
    obj         = objects = BaseManager()
    region      = ForeignKey(Region, blank=True, null=True)
    period      = ForeignKey(Period, blank=True, null=True)
    theme       = ForeignKey(Theme, blank=True, null=True)
    file        = FileField(upload_to="resources/", max_length=80)
    description = TextField()

    def __unicode__(self):
        return u"%s, %s, %s, file: %s" % (self.region, self.period, self.theme, self.file.name)


class Badge(Model):
    obj     = objects = BadgeManager()
    name    = CharField(max_length=100, unique=True)
    cards   = ManyToManyField(Card)
    themes  = ManyToManyField(Theme, blank=True, null=True)
    regions = ManyToManyField(Region, blank=True, null=True)
    periods = ManyToManyField(Period, blank=True, null=True)

    def __unicode__(self):
        return self.name


class Classroom(Model):
    obj     = objects = BaseManager()
    name    = CharField(max_length=100, blank=True)
    teacher = ForeignKey(User)
    # teacher = ManyToManyField(Teacher, through="TeacherAssignment")

    def __unicode__(self):
        return "%s: %s" % (self.teacher, self.name)

    def get_students(self):
        return Student.objects.filter(classroom = self)

    def get_total_score(self):
        answers = LastAnswer.objects.filter(answer__test__student__classroom = self)
        return sum( answers.values_list('answer__card__points', flat=True) )

    def calc_games_played(self):
        return Game.objects.filter(student__classroom = self).filter(won = True).distinct().count()

    def get_badge_total(self):
        return Badge.objects.filter(studentbadge__student__classroom=self).distinct().count()

    def get_points_data(self):
        # return Score.objects.values_list('game__date').annotate(pts = Sum('card__points')).filter(game__student__classroom = self).order_by('game__date')
        answers = LastAnswer.objects.values_list('answer__test__taken')
        return answers.annotate(pts = Sum('answer__card__points')).filter(
                                    answer__test__student__classroom = self).order_by('answer__test__taken')

    def get_recent_careers(self):
        return StudentCareer.objects.filter(student__classroom=self).distinct().order_by('-date').select_related('student','career')[:10]

    def get_best_qs(self, category):
        qs = Card.objects.get_count_qs(classroom=self.id, category=category)
        sorted_x = sorted(qs.iteritems(), key=operator.itemgetter(1), reverse=True)
        per = "%.1f" % sorted_x[0][1]
        return sorted_x[0][0] + " (" + per + "%)"

    def get_worst_qs(self, category):
        qs = Card.objects.get_count_qs(classroom=self.id, category=category)
        sorted_x = sorted(qs.iteritems(), key=operator.itemgetter(1))
        if not sorted_x: return '0'
        per = "%.1f" % sorted_x[0][1]
        return sorted_x[0][0] + " (" + per + "%)"


    # still haven't figured out the best way to call these from a template. custom templatetags I suppose.
    def get_best_theme(self):
        return self.get_best_qs(category='theme')

    def get_worst_theme(self):
        return self.get_worst_qs(category='theme')

    def get_best_period(self):
        return self.get_best_qs(category='period')

    def get_worst_period(self):
        return self.get_worst_qs(category='period')

    def get_best_region(self):
        return self.get_best_qs(category='region')

    def get_worst_region(self):
        return self.get_worst_qs(category='region')


class Student(Model):
    obj        = objects    = StudentManager()
    first_name = CharField(max_length=100)
    last_name  = CharField(max_length=100)
    classroom  = ForeignKey(Classroom)
    user       = ForeignKey(User, blank=True, null=True)
    # classroom = ManyToManyField(Classroom, through="StudentSchedule")

    def __unicode__(self):
        return "%s %s" % (self.first_name, self.last_name)

    def get_total_mastery(self):
        """UNUSED?"""
        cards = Card.objects.filter(score__game__student = self)
        # cards = Card.objects.filter(answer__last_answer__student = self)
        earned = cards.values_list('id',flat=True).distinct().count()
        return 100 * ( earned * 1.0 / Card.objects.count() )

    def get_total_points(self):
        """UNUSED?"""
        return sum( list( Score.objects.filter(game__student = self).values_list('card__points', flat=True) ) )

    def get_badges(self):
        badges = Badge.objects.filter(studentbadge__student=self).distinct().batch_select('themes','regions','periods')

        for b in badges:
            b.tooltip, extra = "", []
            # group if all present
            if len(b.themes_all) == 5:
                b.themes_all = []
                extra.append('All Themes')
            if len(b.regions_all) == 4:
                b.regions_all = []
                extra.append(' All Regions')
            if len(b.periods_all) == 5:
                b.periods_all = []
                extra.append('All Periods')
            tags = b.themes_all + b.periods_all + b.regions_all
            b.tooltip = ", ".join([ t.name for t in tags ])
            if extra:
                b.tooltip += ', ' + ", ".join(extra)

        return badges

    def get_badge_total(self):
        return Badge.objects.filter(studentbadge__student=self).distinct().count()

    def get_careers(self):
        return Career.objects.filter(studentcareer__student=self).distinct()

    def get_career_total(self):
        return self.get_careers().count()

    def get_points_data(self):
        """UNUSED?"""
        qs = Score.objects.values_list('game__date').annotate(pts = Sum('card__points')).filter(game__student = self).order_by('game__date')

        new_list = []
        total = 0
        for tup in qs:
            total += tup[1]
            new_list.append( (tup[0], total) )

        return new_list

    class Meta:
        unique_together = (("first_name", "last_name", "classroom"))


class StudentBadge(Model):
    obj     = objects = BaseManager()
    student = ForeignKey(Student)
    badge   = ForeignKey(Badge)
    date    = DateField(auto_now_add=True)


class Career(Model):
    obj         = objects     = CareerManager()
    name        = CharField(max_length=100, unique=True)
    badges      = ManyToManyField(Badge)
    badge_count = IntegerField(default=1)

    def __unicode__(self):
        return self.name


class StudentCareer(Model):
    obj     = objects = BaseManager()
    student = ForeignKey(Student)
    career  = ForeignKey(Career)
    date    = DateField(auto_now_add=True)


class Game(Model):
    obj     = objects = BaseManager()
    student = ForeignKey(Student)
    career  = ForeignKey(Career, blank=True, null=True)
    region  = ForeignKey(Region, blank=True, null=True)
    date    = DateField(auto_now_add=True)
    won     = BooleanField()

    # def __unicode__(self):
        # return u''


class Score(Model):
    obj   = objects = BaseManager()
    game  = ForeignKey(Game)
    card  = ForeignKey(Card)
    notes = CharField(max_length=200, blank=True)

    class Meta:
        unique_together = ( ("game", "card") )


class TestPreset(Model):
    obj       = objects = BaseManager()
    region    = ForeignKey(Region, blank=True, null=True)
    period    = ForeignKey(Period, blank=True, null=True)
    theme     = ForeignKey(Theme, blank=True, null=True)

    def __unicode__(self):
        return u"%s, %s, %s" % (self.region, self.period, self.theme)


class TestSetup(Model):
    obj         = objects = BaseManager()
    classroom   = ForeignKey(Classroom)
    test_preset = ForeignKey(TestPreset, help_text="You can choose a test preset OR the options below", blank=True, null=True)
    match_all   = BooleanField(help_text="Include questions that match all selected categories", blank=True)
    region      = ManyToManyField(Region, blank=True, null=True)
    period      = ManyToManyField(Period, blank=True, null=True)
    theme       = ManyToManyField(Theme, blank=True, null=True)
    type        = CharField(max_length=20, blank=True, null=True, choices=test_types)
    feature     = CharField(max_length=20, blank=True, null=True, choices=test_features)

    def __unicode__(self):
        return u"%s: %s, %s, %s" % (self.classroom, self.region, self.period, self.theme)


class Test(Model):
    obj     = objects = BaseManager()
    student = ForeignKey(Student)
    taken   = DateTimeField(auto_now_add=True)
    score   = IntegerField(default=0, blank=True)
    done    = BooleanField(default=False)

    def calculate_score(self):
        answers = self.answers.all()
        correct = len([a for a in answers if a.correct])
        self.score = int(round( float(correct) / answers.count() * 100 ) )
        return self.score

    def cards(self):
        return set(a.card for a in self.answers.all())

    def __unicode__(self):
        return u"%s, %s%s" % (self.student, self.score, ", done" if self.done else '')


class Answer(Model):
    # student = ForeignKey(Student, related_name="answers")
    obj     = objects = BaseManager()
    card    = ForeignKey(Card)
    test    = ForeignKey(Test, related_name="answers")
    answer  = CharField(max_length=200, blank=True, null=True)
    correct = IntegerField(help_text="0:unset, 1:correct, 2:incorrect", default=0)

    def __unicode__(self):
        return u"%s, %s" % (self.test.student, self.correct)


class LastAnswer(Model):
    obj     = objects = BaseManager()
    answer  = ForeignKey(Answer)
    # note: can't use related_name because of annotations in get_sorted_students()
    student = ForeignKey(Student)


#class StudentSchedule(Model):
#    student = ForeignKey(Student)
#    classroom = ForeignKey(Classroom)
#    start_date = DateField()
#    stop_date = DateField()

#class TeacherAssignment(Model):
#    teacher = ForeignKey(User)
#    classroom = ForeignKey(Classroom)
#    start_date = DateField()
#    stop_date = DateField()
