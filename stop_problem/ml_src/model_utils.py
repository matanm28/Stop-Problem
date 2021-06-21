import json

import torch
import torch.nn.functional as F
from torch import no_grad
from torch.utils.data import Dataset

from stop_problem.ml_src.data_preperation import get_data_for_all_players, get_data_for_10_players
from ..ml_src.model import Net
import time

import numpy as np

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
VALUE_INDEX = 28


def train(model, train_loader):
    i = 0
    model.train()
    for batch, (xs, ys) in enumerate(train_loader):
        i += 1
        model.optimizer.zero_grad()
        output = model(xs)
        loss = F.nll_loss(output, ys)
        loss.backward()
        model.optimizer.step()


def validation(model, valid_loader):
    sum_loss = 0
    sum_c = 0
    i = 0
    model.eval()
    with no_grad():
        for data in valid_loader:
            i += 1
            xs, ys = data
            output = model(xs.float())
            loss = F.nll_loss(output, ys.long(), size_average=False).item()
            sum_loss += loss
            pred = output.max(1, keepdim=True)[1]
            sum_c += pred.eq(ys.view_as(pred)).sum()
    accuracy = sum_c / i
    avr_loss = sum_loss / i
    print("acc [{0}], avg loss [{1}]".format(accuracy, avr_loss))
    return accuracy


def predict(model_net, test_loader):
    model_net.eval()
    i = 0
    for batch_idx, (data, label) in enumerate(test_loader):
        data = data.to(device)
        output = model_net(data)
        prediction = output.cpu().data.max(1, keepdim=True)[1].max()
        i += 1
    return prediction


def padding_to_k(*argv):
    list_to_pad = argv[0]
    k = argv[1]
    the_padding = [-1] * k
    for i in range(len(list_to_pad)):
        list_to_pad[i].extend(the_padding)
    return list_to_pad


class TrainingStopProblemDataset(Dataset):
    def __init__(self, list_seq):
        self.samplesx = []
        self.samplesy = []
        for x, y in list_seq:
            self.samplesx.append(np.array(x, dtype=np.float32))
            vector = torch.tensor([y])
            self.samplesy.append(vector)

        self.samplesx = torch.tensor(self.samplesx)

    def __len__(self):
        return len(self.samplesx)

    def __getitem__(self, idx):
        return self.samplesx[idx], self.samplesy[idx]


# class TestStopProblemDataset(Dataset):
#     def __init__(self, list_seq):
#         self.samplesx = list_seq
#
#     def __len__(self):
#         return len(self.samplesx)
#
#     def __getitem__(self, idx):
#         return np.array(self.samplesx[idx])


def main():
    print("k")

    with open('stop_problem\ml_src\data.json', 'r') as fp:
        users = json.load(fp)
    model = Net()
    train_list = []
    list_place_to_key = {}
    i = 0
    for u_key in users.keys():
        list_place_to_key[i] = u_key
        x = users[u_key][:8]
        seq_only = [k[:26] for k in users[u_key][8:11]]
        y = int(users[u_key][10][VALUE_INDEX])
        padding_to_k(seq_only, 51 - 26)
        x.extend(seq_only)
        train_list.append((x, y))
    train_set = TrainingStopProblemDataset(np.array(train_list))

    train(model, train_set)

    print("k")
