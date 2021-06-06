from datetime import datetime
from uuid import UUID

import pytz
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import TemplateView

# Create your views here.
from stop_problem.froms import PlayerForm
from stop_problem.models import Player, Sequence, TimePeriod, SequenceAnswer, Answer


class MustHavePlayerIdTemplateView(TemplateView):

    def get(self, request, *args, **kwargs):
        if 'player_id' not in self.request.session:
            return redirect('player-registration')
        if not Player.objects.filter(id=self.request.session.get('player_id')).exists():
            return redirect('player-registration')
        kwargs['player_id'] = self.request.session['player_id']
        context = self.get_context_data(**kwargs)
        if 'player' not in context:
            context['player'] = get_object_or_404(Player, pk=self.request.session['player_id'])
        return self.render_to_response(context)


class PlayerRegistrationView(TemplateView):
    template_name = 'player_registration.html'

    def get(self, request, *args, **kwargs):
        if 'player_id' in self.request.session:
            player = Player.objects.filter(id=self.request.session['player_id'])
            if not player.exists():
                del self.request.session['player_id']
            else:
                player = player.first()
                if player.is_done:
                    return redirect('thanks-for-playing')
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        form = PlayerForm()
        return {'form': form, 'player_id': self.request.session.get('player_id', None)}

    def post(self, request, *args, **kwargs):
        form = PlayerForm(request.POST)
        if not form.is_valid():
            return render(request, 'player_registration.html', context={'form': form})
        player = form.save()
        request.session['player_id'] = player.id_as_string
        return redirect('start-game')


class StartGameView(MustHavePlayerIdTemplateView):
    template_name = 'start_game.html'

    def get_context_data(self, **kwargs):
        player_id = self.request.session.get('player_id', None)
        player = get_object_or_404(Player, id=player_id)
        return {'player': player}


@method_decorator(csrf_exempt, name='dispatch')
class GameSequenceView(MustHavePlayerIdTemplateView):
    template_name = 'game_sequence.html'

    def get_context_data(self, player_id: UUID, **kwargs):
        player = get_object_or_404(Player, id=player_id)
        sequence_query = Sequence.objects.filter(id=player.next_seq_id)
        if not sequence_query.exists():
            player.is_done = True
            player.save()
            return redirect('thanks-for-playing')
        sequence = sequence_query.first()
        context = {'sequence': sequence}
        return context

    def post(self, request, *args, **kwargs):
        data = request.POST
        time_stamps = [int(stamp) for stamp in data.getlist('time_stamps[]')]
        time_periods = []
        player = Player.objects.get(id=data.get('player_id'))
        sequence = Sequence.objects.get(id=data.get('seq_id'))
        chosen_index = data.get('chosen_index')
        is_accepted = True if data.get('is_accepted') == 'true' else False
        sequence_answer = SequenceAnswer.objects.create(player=player, sequence=sequence, chosen_index=chosen_index,
                                                        is_accepted=is_accepted)
        for i in range(len(time_stamps) - 1):
            start = datetime.fromtimestamp(time_stamps[i] / 1000, tz=pytz.UTC)
            end = datetime.fromtimestamp(time_stamps[i + 1] / 1000, tz=pytz.UTC)
            value = sequence.values.all()[i]
            time_period = TimePeriod.objects.create(start=start, end=end)
            time_period.save()
            answer = Answer.objects.create(value=value, time_period=time_period, sequence_answer=sequence_answer)
            # answer.save()
        return JsonResponse({'has_next': Sequence.objects.filter(id__gt=sequence.id).exists()})


class ThanksForPlayingView(MustHavePlayerIdTemplateView):
    template_name = 'thanks_for_playing.html'

