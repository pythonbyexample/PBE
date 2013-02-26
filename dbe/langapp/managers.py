import operator

from django.db.models import *
from fate.custom import utils
from fate.custom.batch_select import batch_select

class BaseManager(manager.Manager):
    def get_or_none(self, **kwargs):
        try: return self.get(**kwargs)
        except self.model.DoesNotExist: return None


class CardManager(BaseManager):

    def get_count_qs(self, category, secondary=False, teacher=False, classroom=False, student=False):

        from fate.game.models import Student, Card
        # get the subset of students we're interested in
        students = Student.objects.get_filtered_qs(teacher=teacher, classroom=classroom, student=student)\
            .values_list('id',flat=True)

        count = len(students)

        # build base values_list
        values_list = [category+'__name']
        if secondary:
            values_list.append(secondary+'__name')

        base = Card.objects.distinct().values_list(*values_list).annotate(count=Count('id', distinct=True))

        # need to exclude period = None
        if category == 'period' or secondary == 'period':
            base = base.exclude(period__isnull=True)

        values_list.append('score__game__student__id')

        # filter by students, re-add values_list, and re-annotate count(id)
        qs = base.filter(score__game__student__id__in = students)\
            .values_list(*values_list).annotate(count=Count('id', distinct=True))


        # turn tup lists into sets of nested dictionaries { category_values: { sec_values: % mastery } }
        ref = utils.tup_to_dict(base)
        data = utils.parse_card_counts(qs, count)

        if secondary:
            return utils.calc_nested_averages(data, ref)
        else:
            return utils.calc_averages(data, ref)


class BadgeManager(batch_select.BatchManager):

    def unlock_badges(self, student):
        from fate.game.models import StudentBadge
        unearned_cards = Card.objects.exclude(score__game__student = student).values_list('id',flat=True).distinct()
        earned_badges  = Badge.objects.exclude(cards__id__in = unearned_cards)

        for badge in earned_badges:
            StudentBadge.objects.get_or_create(student_id=student, badge=badge)


    def get_aggregate_badges(self, teacher=False, classroom=False, student=False):
        from fate.game.models import Game
        base = self.values_list('studentbadge__date').annotate(count = Count('id')).order_by('studentbadge__date')

        try:
            # filter on teacher or classroom or student
            if teacher:
                qs = base.filter(studentbadge__student__classroom__teacher = teacher)
                new_list = [ (Game.objects.values_list('date',flat=True).filter(student__classroom__teacher = teacher).order_by('date')[0], 0) ]
            elif classroom:
                qs = base.filter(studentbadge__student__classroom = classroom)
                new_list = [ (Game.objects.values_list('date',flat=True).filter(student__classroom = classroom).order_by('date')[0], 0) ]
            elif student:
                qs = base.filter(studentbadge__student= student)
                new_list = [ (Game.objects.values_list('date',flat=True).filter(student = student).order_by('date')[0], 0) ]

        except:
            return []

        total = 0
        for tup in qs:
            total += tup[1]
            new_list.append( (tup[0], total) )

        return new_list


class StudentManager(BaseManager):

    def get_filtered_qs(self, teacher=None, classroom=None, student=None):
        '''Return a Student queryset filtered by teacher, classroom, or student.'''
        qs = self
        if classroom:
            qs = qs.filter(classroom = classroom)
        elif teacher:
            qs = qs.filter(classroom__teacher = teacher)
        elif student:
            qs = qs.filter(id = student)
        return qs


    def get_sorted_students(self, field=None, object_id=None, sort="DESC", secondary=None, teacher=None, classroom=None, student=None):
        from fate.game.models import Card
        card_total = False
        base = self.get_filtered_qs(teacher=teacher, classroom=classroom).annotate(field_value=Count('id'))

        # what are we looking for?
        if field == "points":
            # qs = base.annotate( field_value = Sum('game__score__card__points') )
            qs = base.annotate( field_value = Sum('lastanswer__answer__card__points') )
        elif field == "badges":
            qs = base.annotate( field_value = Count('studentbadge') )

        elif field in ["theme", "region", "period"]:
            card_total = Card.objects.filter(**{field:object_id}).count()
            # qs = base.filter(**{ "game__score__card__" + field : object_id }).annotate(
                                        # field_value = Count('game__score__card__id', distinct=True) )
            qs = base.filter(**{ "lastanswer__answer__card__" + field : object_id }).annotate(
                                 field_value = Count('lastanswer__answer__card__id', distinct=True) )

        qs = qs.exclude(field_value__isnull = True)

        result_dict = dict([(s.id, s) for s in qs])

        for s in qs:
            if not s.field_value:
                s.field_value = 0
            if card_total:
                s.field_value = 100 * ( s.field_value * 1.0 / card_total * 1.0 )

        tup_list = []
        for s in base:
            if s.id in result_dict:
                s = result_dict[s.id]
            else:
                s.field_value = 0
            tup_list.append( (s, s.field_value) )

        sorted_list = sorted(tup_list, key=operator.itemgetter(1))
        if sort == 'DESC':
            sorted_list.reverse()

        return [ t[0] for t in sorted_list ]


    def get_average_mastery(self, field=None, object_id=None, teacher=None, classroom=None, student=None):
        students = self.get_sorted_students(field=field, object_id=object_id, teacher=teacher, classroom=classroom, student=student)
        total    = 0
        count    = len(students)

        for s in students:
            total += s.field_value

        return (total * 1.0) / count


class CareerManager(BaseManager):

    def unlock_careers(self, student):
        from fate.game.models import StudentCareer
        career_ids = student.studentcareer_set.values_list('id',flat=True)
        earned_careers = self.filter(badges__studentbadge__student = student).distinct().annotate(
                                                    count=Count('badges__studentbadge', distinct=True))

        for c in earned_careers:
            if c.count >= c.badge_count and c.id not in career_ids:
                StudentCareer.objects.get_or_create(student=student, career=c)
