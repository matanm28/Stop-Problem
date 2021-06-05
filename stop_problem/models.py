import uuid
from datetime import timedelta

from django.db import models
from django.utils.translation import gettext_lazy as _


# Create your models here.

class Player(models.Model):
    class Gender(models.IntegerChoices):
        MALE = 1, _('Male')
        FEMALE = 2, _('Female')
        Other = 3, _('Other')
        RATHER_NOT_SAY = 4, _('Rather Not Say')

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    age = models.PositiveSmallIntegerField()
    gender = models.IntegerField(choices=Gender.choices, default=Gender.RATHER_NOT_SAY)


class Sequence(models.Model):
    id = models.IntegerField(primary_key=True)

    class Meta:
        ordering = ['id']

    @property
    def optimal_instance(self) -> 'Value':
        return self.values.filter(value=models.Max('values__value')).first()

    @property
    def optimal_value(self) -> int:
        return self.optimal_instance.value

    @property
    def optimal_index(self) -> int:
        return self.optimal_instance.index


class Value(models.Model):
    value = models.IntegerField()
    index = models.IntegerField()
    sequence = models.ForeignKey(Sequence, on_delete=models.CASCADE, related_name='values')

    class Meta:
        ordering = ('index',)
        unique_together = ['index', 'sequence']


class TimePeriod(models.Model):
    start = models.DateTimeField()
    end = models.DateTimeField()

    @property
    def total_time(self) -> timedelta:
        return self.end - self.start

    @property
    def total_seconds(self) -> float:
        return self.total_time.total_seconds()

    class Meta:
        ordering = ('start', 'end')


class SequenceAnswer(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='sequence_answers')
    sequence = models.ForeignKey(Sequence, on_delete=models.CASCADE, related_name='sequence_answers')

    @property
    def total_time_period(self) -> timedelta:
        time_periods = TimePeriod.objects.filter(answers__sequence_answer=self).order_by('start', 'end')
        return time_periods.last().end - time_periods.first().start


class Answer(models.Model):
    value = models.ForeignKey(Value, on_delete=models.CASCADE, related_name='answers')
    time_period = models.ForeignKey(TimePeriod, on_delete=models.CASCADE, related_name='answers')
    is_accepted = models.BooleanField()
    sequence_answer = models.ForeignKey(SequenceAnswer, on_delete=models.CASCADE, related_name='answers')
