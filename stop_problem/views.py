from django.shortcuts import render

# Create your views here.
from stop_problem.froms import PlayerForm
from stop_problem.models import Sequence


def index(request):
    if request.method == 'GET':
        player_form = PlayerForm()
        return render(request, 'index.html', context={'form': player_form})
    if request.method == 'POST':
        form = PlayerForm(request.POST)
        if not form.is_valid():
            return render(request, 'index.html', context={'form': form})
        player = form.save()
        return render(request, 'start_game.html', context={'player': player})


def start_game(request):
    if request.method == 'GET':
        sequence = Sequence.objects.first()
        return render(request, 'start_game.html', context={'sequence': sequence})
