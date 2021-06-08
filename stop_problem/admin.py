from typing import Union

from django.contrib import admin

from stop_problem.models import Player, Sequence, SequenceAnswer


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ['id', 'age', 'gender', 'created_at', 'is_done', 'current_seq', 'total_score']
    sortable_by = ['age', 'gender', 'created_at', 'is_done']
    list_filter = ['gender', 'is_done']
    ordering = ['created_at', 'gender', 'age', 'is_done']

    @admin.display(description='Current Sequence', empty_value='Done')
    def current_seq(self, obj: Player) -> Union[int, str]:
        if obj.current_seq is None:
            return "Didn't Start"
        return obj.current_seq.id if not obj.is_done else ''

    @admin.display(description='Score')
    def total_score(self, obj: Player):
        return obj.total_score


@admin.register(Sequence)
class SequenceAdmin(admin.ModelAdmin):
    list_display = ['id', 'optimal_value', 'optimal_index', 'worst_value', 'worst_index', 'median_value', 'median_indexes',
                    'average_value']
    ordering = ['id']

    @admin.display(description='Optimal Value')
    def optimal_value(self, obj: Sequence):
        return obj.optimal_value

    @admin.display(description='Optimal Index')
    def optimal_index(self, obj: Sequence):
        return obj.optimal_index

    @admin.display(description='Worst Value')
    def worst_value(self, obj: Sequence):
        return obj.worst_value

    @admin.display(description='Worst Index')
    def worst_index(self, obj: Sequence):
        return obj.worst_index

    @admin.display(description='Median Value')
    def median_value(self, obj: Sequence):
        return obj.median_value

    @admin.display(description='Median Index')
    def median_value(self, obj: Sequence):
        return obj.median_indexes

    @admin.display(description='Average Value')
    def average_value(self, obj: Sequence):
        return obj.average_value


@admin.register(SequenceAnswer)
class SequenceAnswerAdmin(admin.ModelAdmin):
    list_display = ['player', 'sequence_id', 'chosen_index', 'is_accepted']
    sortable_by = ['player', 'sequence']
    list_filter = ['sequence__id', 'is_accepted']
    ordering = ['sequence', 'player']

    @admin.display(description='Sequence Id')
    def sequence_id(self, obj: SequenceAnswer) -> int:
        return obj.sequence.id
