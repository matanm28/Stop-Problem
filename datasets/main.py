import json
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

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
            [29]: is accepted
            [30]: total time in seconds
            [31-50]: time spent decoding weather to pick a value or pass (padded with -1 after 31 + <chosen index>)
    """


def load_json_file(path):
    with open(path) as f:
        data = json.load(f)
    return pd.DataFrame.from_dict(data)


df = load_json_file('site_data_1st_iteration.json')

# plot 1:
accept_per_sequence = []
# each sequence:
for i in range(1, 11):
    count = 0
    sequence_result = df.iloc[i]
    # each user
    for user in sequence_result:
        if user[29] == 1.0:
            count += 1
    accept_per_sequence.append(count)
y = np.array(accept_per_sequence)
x = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
plt.bar(x, y)
plt.xticks(np.arange(min(x), max(x) + 1, 1.0))
plt.xlabel('sequences')
plt.ylabel("number of accepts")
plt.title("number of accepts per sequence")
plt.show()

# plot 2:
arr = [0, 0, 0, 0]
# each sequence:
for i in range(1, 10):
    sequence_result = df.iloc[i]
    # each user
    for user in sequence_result:
        sequence_optimal_value = user[20]
        chosen_value = user[27]
        success_rate = (chosen_value / sequence_optimal_value) * 100
        if success_rate > 100:
            success_rate = 100
        if success_rate % 25 == 0:
            arr[int(success_rate // 25) - 1] += 1
        else:
            arr[int(success_rate // 25)] += 1
y = np.array(arr)
pie_labels = ["0% - 25%", "25% - 50%", "50% - 75%", "75% - 100%"]
plt.pie(y, labels=pie_labels, startangle=0)
plt.title("users success")
plt.show()

# plot 3:
hits_per_sequence = []
# each sequence:
for i in range(1, 11):
    count = 0
    sequence_result = df.iloc[i]
    # each user
    for user in sequence_result:
        if user[20] == user[27]:
            count += 1
    hits_per_sequence.append(count)
y = np.array(hits_per_sequence)
x = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
plt.bar(x, y, color='purple')
plt.xticks(np.arange(min(x), max(x) + 1, 1.0))
plt.xlabel('sequences')
plt.ylabel("number of hits (out of 153)")
plt.title("number of hits per sequence")
plt.show()

# plot 4:
# plotting a line plot after changing it's width and height
plt.rcParams["figure.figsize"] = (15, 10)
arr = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
# each sequence:
for i in range(1, 10):
    sequence_result = df.iloc[i]
    # each user
    for user in sequence_result:
        total_time = user[30]
        if total_time > 15:
            arr[15] += 1
        else:
            arr[int(total_time)] += 1
y = np.array(arr)
x = ["0-1", "1-2", "2-3", "3-4", "4-5", "5-6", "6-7", "7-8", "8-9", "9-10", "10-11", "11-12", "12-13",
     "13-14", "14-15", "15+"]
plt.figure(figsize=(12,5))
plt.bar(x, y, width=0.5, color="#4CAF50")
plt.xlabel("total time in seconds")
plt.ylabel('amount of users')
plt.title("amount of users per total time")
plt.show()

