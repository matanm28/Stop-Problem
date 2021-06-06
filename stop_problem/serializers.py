from rest_framework import serializers

from stop_problem.models import Value, Sequence, Player


class ValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Value
        fields = ['value', 'index']


class SequenceSerializer(serializers.ModelSerializer):
    values = ValueSerializer(many=True)

    class Meta:
        model = Sequence
        fields = ['id', 'values']
