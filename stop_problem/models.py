import json
import uuid
from datetime import timedelta

from django.db import models
from django.utils.translation import gettext_lazy as _


class Player(models.Model):
    class Gender(models.IntegerChoices):
        MALE = 1, _('Male')
        FEMALE = 2, _('Female')
        Other = 3, _('Other')
        RATHER_NOT_SAY = 4, _('Rather Not Say')

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    age = models.PositiveSmallIntegerField()
    gender = models.IntegerField(choices=Gender.choices, default=Gender.RATHER_NOT_SAY)
    is_done = models.BooleanField(default=False, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def id_as_string(self):
        return f'{self.id}'

    @property
    def as_json(self) -> dict:
        return json.dumps({'id': self.id_as_string, 'is_done': self.is_done})

    @property
    def current_seq(self) -> 'Sequence':
        return Sequence.objects.filter(sequence_answers__player=self).order_by('-id').first()

    @property
    def next_seq_id(self) -> int:
        return self.current_seq.id + 1 if self.current_seq is not None else 1


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

    @property
    def as_json(self) -> dict:
        from stop_problem.serializers import SequenceSerializer
        return json.loads(json.dumps(SequenceSerializer(self).data))


class Value(models.Model):
    value = models.IntegerField()
    index = models.IntegerField()
    sequence = models.ForeignKey(Sequence, on_delete=models.CASCADE, related_name='values')

    class Meta:
        ordering = ('index',)
        unique_together = ['index', 'sequence']

    def __str__(self) -> str:
        return f'{self.value}'


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

    def __str__(self) -> str:
        date_format = '%d.%m.%y'
        time_format = '%H:%M:%S'
        if self.start.date() == self.end.date():
            return f'{self.start.strftime(f"{date_format} {time_format}")} - {self.end.strftime(time_format)}'
        else:
            joined_format = f'{date_format}: {time_format}'
            return f'{self.start.strftime(joined_format)} - {self.end.strftime(joined_format)}'


class SequenceAnswer(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='sequence_answers')
    sequence = models.ForeignKey(Sequence, on_delete=models.CASCADE, related_name='sequence_answers')
    chosen_index = models.PositiveSmallIntegerField()
    is_accepted = models.BooleanField()

    @property
    def total_time_period(self) -> timedelta:
        time_periods = TimePeriod.objects.filter(answers__sequence_answer=self).order_by('start', 'end')
        return time_periods.last().end - time_periods.first().start


class Answer(models.Model):
    value = models.ForeignKey(Value, on_delete=models.CASCADE, related_name='answers')
    time_period = models.ForeignKey(TimePeriod, on_delete=models.CASCADE, related_name='answers')
    sequence_answer = models.ForeignKey(SequenceAnswer, on_delete=models.CASCADE, related_name='answers')
