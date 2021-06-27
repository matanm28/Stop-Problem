import json
import uuid

LINE_LENGTH = 50
SEQ_LENGTH = 20


def padding_by_k(vector: list, k: int) -> list:
    padd = [-1.] * k
    vector.extend(padd)
    return vector

def build_seq_vector(seq_dict:dict) ->dict:
    vector = []
    for s in seq_dict["seq"]:
        vector.append(float(s))
    vector.extend([float(seq_dict["optimal_value"]), float(seq_dict["optimal_index"]), float(seq_dict["worst_value"]), float(seq_dict["worst_index"]), float(seq_dict["median_value_1"]),
                   float(seq_dict["median_index_1"]), float(seq_dict["median_index_2"])])
    return vector

def create_sequence_dict(sequences: list) -> list:
    parse_sequence_list = []
    for seq in sequences:
        seq = sequences[seq]
        parse_seq = {}
        parse_seq["seq"] = seq
        sort_seq = seq.copy()
        sort_seq.sort()
        parse_seq["worst_value"] = sort_seq[0]
        parse_seq["worst_index"] = seq.index(sort_seq[0])
        parse_seq["optimal_value"] = sort_seq[len(seq) - 1]
        parse_seq["optimal_index"] = seq.index(sort_seq[len(seq) - 1])
        median_index_1 = int(len(seq) / 2)
        median_index_2 = int(len(seq) / 2) - 1
        parse_seq["median_value_1"] = sort_seq[median_index_1]
        parse_seq["median_value_2"] = sort_seq[median_index_2]
        parse_seq["median_index_1"] = seq.index(sort_seq[median_index_1])
        parse_seq["median_index_2"] = seq.index(sort_seq[median_index_2])
        parse_seq["vector"] = build_seq_vector(parse_seq)
        parse_sequence_list.append(parse_seq)
    return parse_sequence_list


def uniform_time(chosen_index, total_time):
    time_per_index = total_time / chosen_index
    time_list = [float(time_per_index)] * chosen_index
    time_list = padding_by_k(time_list, SEQ_LENGTH - chosen_index)
    return time_list


if __name__ == '__main__':
    with open('datasets/experiment_data_raw.json', 'r') as f:
        data = json.load(f)

    seq_list = create_sequence_dict(data["Sequences"])
    experiment = data["Experiment"]["records"]
    parse_data = {}
    for single_exp in experiment:
        single_answer, metadata_row = [], []
        metadata_row = padding_by_k(metadata_row, LINE_LENGTH)
        single_answer.append(metadata_row)
        for i, single_seq in enumerate(seq_list):
            answer = []
            answer.extend(single_seq["vector"])
            chosen_index = single_exp[f"Stopping position Round {i+1}"] - 1
            chosen_value = single_seq["seq"][int(chosen_index)]
            total_time = single_exp["Time taken (minues)"]
            answer.extend([float(chosen_value), float(chosen_index), float(total_time)])
            answer.extend(uniform_time(int(chosen_index) + 1, total_time))
            single_answer.append(answer)
        myuuid = uuid.uuid4()
        parse_data[str(myuuid)] = single_answer
    with open('datasets/experiment_data.json', 'w') as f:
        json.dump(parse_data, f)
    print("done")