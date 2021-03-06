from typing import Dict, Iterable

import numpy as np
from django.db.models import F
from numpy import ndarray

from stop_problem.models import Player, Sequence


def as_gender_one_hot(gender: int):
    gender_values = Player.Gender.values
    one_hot = np.zeros(len(gender_values))
    one_hot[gender - 1] = 1
    return one_hot


sequences_dict = {
    seq.pk: {
        'values': list(seq.values.values_list('value', flat=True)),
        'optimal_value': seq.optimal_value,
        'optimal_index': seq.optimal_index,
        'worst_value': seq.worst_value,
        'worst_index': seq.worst_index,
        'median_value': seq.median_value,
        'median_indices': seq.median_indices,
    }
    for seq in Sequence.objects.all()
}


def make_sequence_to_flat_list(sequence_data: Dict):
    flat_list = []
    for value in sequence_data.values():
        if isinstance(value, Iterable):
            flat_list.extend(value)
        else:
            flat_list.append(value)
    return flat_list


sequences_flat_lists = [make_sequence_to_flat_list(seq_data) for seq_data in sequences_dict.values()]
sequences_np_arr = np.array(sequences_flat_lists)


def get_inputs_from_player(player: Player) -> ndarray:
    """
    returns a numpy array representing the data for a single player with shape (11,51).
    data representation as follows:
    [0]: Player meta-info:
        [0] - age
        [1-4] - gender as one-hot encoded vector
        [4-50] - padding with -1 as null value
    [1-10]:
        [0-26]: Sequence related data:
            [0-19] - sequence values
            [20] - sequence optimal value
            [21] - sequence optimal index
            [22] - sequence worst value
            [23] - sequence worst index
            [24] - sequence median value
            [25-26] - sequence median indices
        [27-50]: Player answer data:
            [27]: chosen value
            [28]: chosen index
            [29]: total time in seconds
            [30-50]: time spent decoding weather to pick a value or pass (padded with -1 after 30 + <chosen index>)
    """
    meta_info_vec = [player.age, *as_gender_one_hot(player.gender)]
    answers = []
    for answer in player.sequence_answers.all():
        chosen_value = answer.chosen_value
        answer_values_list = [chosen_value.value, chosen_value.index, int(answer.is_accepted),
                              answer.total_time_period.total_seconds()]
        time_deltas = answer.answers.values_list(F('time_period__end') - F('time_period__start'), flat=True)
        padding = [-1 for _ in range(time_deltas.count(), answer.sequence.values.count())]
        answer_values_list.extend([td.total_seconds() for td in time_deltas] + padding)
        answers.append(answer_values_list)
    answer_length = len(answers[0])
    assert all(answer_length == len(answer) for answer in answers)
    sequence_length = sequences_np_arr.shape[1]
    padding_for_meta = [-1 for _ in range(len(meta_info_vec), answer_length + sequence_length)]
    data_matrix = [meta_info_vec + padding_for_meta]
    for sequence, answer in zip(sequences_flat_lists, answers):
        data_matrix.append(sequence + answer)
    return np.array(data_matrix)


def get_data_for_10_players():
    i = 0
    players_dict = {}
    for player in Player.objects.filter(is_done=True):
        i += 1
        if i == 10:
            return players_dict
        players_dict[player.id] = get_inputs_from_player(player)
    return players_dict


def get_data_for_all_players():
    return {str(player.id): get_inputs_from_player(player) for player in Player.objects.filter(is_done=True)}


def main():
    a = get_data_for_all_players()

    print(a)


if __name__ == '__main__':
    main()
