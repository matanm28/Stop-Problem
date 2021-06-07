from stop_problem.models import Sequence, Value


def init_sequences():
    import json
    with open('conf/data.json', 'r') as f:
        data = json.load(f)

    sequences = {int(key): item for key, item in data['Sequences'].items()}
    for seq_id in sequences:
        sequence = Sequence.objects.create(id=seq_id)
        for index, value in enumerate(sequences[seq_id]):
            value = Value.objects.create(index=index, value=value, sequence=sequence)
            value.save()


if __name__ == '__main__':
    init_sequences()
