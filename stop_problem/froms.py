from django import forms

from stop_problem.models import Player


class PlayerForm(forms.ModelForm):
    class Meta:
        model = Player
        fields = ['age', 'gender']
