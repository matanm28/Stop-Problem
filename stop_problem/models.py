import json
import uuid
from datetime import timedelta
from typing import Union, Tuple

from django.db import models
from django.db.models import QuerySet, Avg
from django.utils.translation import gettext_lazy as _


class Player(models.Model):
    class Gender(models.IntegerChoices):
        MALE = 1, _('Male')
        FEMALE = 2, _('Female')
        Other = 3, _('Other')
        RATHER_NOT_SAY = 4, _('Rather Not Say')

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    age = models.PositiveSmallIntegerField()
    gender = models.IntegerField(choices=Gender.choices, default=Gender.MALE)
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
        return self.current_seq.id + 1 if self.current_seq is not None else 0

    @property
    def total_score(self) -> int:
        total = 0
        for sequence_answer in self.sequence_answers.distinct().all():
            total += sequence_answer.chosen_value.value
        return total

    @property
    def sequence_and_choice(self) -> QuerySet:
        return self.sequence_answers.values_list('sequence', 'chosen_index').distinct()

    def __str__(self):
        return f'{self.id}'


class Sequence(models.Model):
    id = models.IntegerField(primary_key=True)

    class Meta:
        ordering = ['id']

    @property
    def optimal_instance(self) -> 'Value':
        return self.values.order_by('-value').first()

    @property
    def optimal_value(self) -> int:
        return self.optimal_instance.value

    @property
    def optimal_index(self) -> int:
        return self.optimal_instance.index

    @property
    def worst_instance(self) -> 'Value':
        return self.values.order_by('value').first()

    @property
    def worst_value(self) -> int:
        return self.worst_instance.value

    @property
    def worst_index(self) -> int:
        return self.worst_instance.index

    @property
    def median_instances(self) -> QuerySet['Value']:
        """Because Sequence.values.count() is even than we return two instances"""
        values_count = self.values.count()
        start = (values_count // 2)
        end = (values_count // 2) + 1
        if values_count % 2 == 0:
            start -= 1
        return self.values.order_by('value')[start:end]

    @property
    def median_value(self) -> float:
        return self.median_instances.aggregate(median_value=Avg('value'))['median_value']

    @property
    def median_indexes(self) -> Union[int, Tuple[int, int]]:
        qs = self.median_instances.values_list('index', flat=True)
        if qs.count() == 1:
            return qs[0]
        return tuple(qs)

    @property
    def average_value(self) -> float:
        return self.values.aggregate(average_value=Avg('value'))['average_value']

    @property
    def as_json(self) -> dict:
        from stop_problem.serializers import SequenceSerializer
        return json.loads(json.dumps(SequenceSerializer(self).data))

    def __str__(self):
        return f'Sequence #{self.id}: {", ".join([str(val) for val in self.values.values_list("value", flat=True)])}'


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

    @property
    def chosen_value(self) -> Value:
        return Value.objects.get(sequence=self.sequence, index=self.chosen_index)

    @property
    def chosen_value_other(self):
        return self.answers.last()

    class Meta:
        ordering = ['sequence']


class Answer(models.Model):
    value = models.ForeignKey(Value, on_delete=models.CASCADE, related_name='answers')
    time_period = models.ForeignKey(TimePeriod, on_delete=models.CASCADE, related_name='answers')
    sequence_answer = models.ForeignKey(SequenceAnswer, on_delete=models.CASCADE, related_name='answers')

    class Meta:
        ordering = ['time_period']
