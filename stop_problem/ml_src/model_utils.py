import json
import os.path
import random
import warnings
from typing import Optional, List

import numpy as np
import torch
from numpy import ndarray
from torch import no_grad, Tensor, nn
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms

from ..ml_src.model import Net

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
CHOSEN_VALUE_INDEX = 27
CHOSEN_INDEX_INDEX = 28


def train(model, train_set, epochs=30):
    model.train()
    criterion = nn.NLLLoss()
    loss_list = []
    accuracy_list = []
    train_loader = DataLoader(train_set, batch_size=8, shuffle=True)
    for epoch in range(epochs):
        running_loss = 0.0
        total = 0
        correct = 0
        for batch_idx, (inputs, labels) in enumerate(train_loader):
            model.optimizer.zero_grad()
            yhats_list = model(inputs)
            losses = []
            for yhat, y_true in zip(yhats_list, labels.transpose(0, 1)):
                losses.append(criterion(yhat, y_true))
                predictions = torch.argmax(yhat.data, dim=1)
                correct += (predictions == y_true).sum().item()
            total += labels.size().numel()
            loss = sum(losses)
            loss.backward()
            model.optimizer.step()
            running_loss += loss.item()
        accuracy_list.append(round(100 * correct / total, 2))
        loss_list.append(round(running_loss / total, 2))
        print(f'Epoch: {epoch + 1} loss: {loss_list[-1]} accuracy: {accuracy_list[-1]}%')
    return accuracy_list[-1], loss_list[-1]


def test(model, validation_data):
    data_loader = DataLoader(validation_data, batch_size=3, shuffle=False)
    correct = 0
    loss = 0
    total = 0
    criterion = nn.NLLLoss()
    model.eval()
    with no_grad():
        for inputs, batch_ys in data_loader:
            yhats_tuple = model(inputs)
            for yhat, y_true in zip(yhats_tuple, batch_ys.transpose(0, 1)):
                loss += criterion(yhat, y_true).sum().item()
                predictions = torch.argmax(yhat.data, 1)
                correct += (predictions == y_true).sum().item()
            total += batch_ys.size().numel()
    accuracy = round(100 * correct / total, 2)
    avg_loss = round(loss / total, 2)
    print(f'accuracy: {accuracy}%')
    print(f'avg loss: {avg_loss}')
    return accuracy, avg_loss


def predict(model, data, k=3):
    data_loader = DataLoader(data, batch_size=len(data))
    model.eval()
    predictions = []
    for inputs, label in data_loader:
        yhat_tuple = model(inputs)
        for yhat in yhat_tuple:
            top_k_predictions = torch.topk(yhat, k)
            predictions.append(top_k_predictions.indices[:, 0])
    return predictions, top_k_predictions.indices


def padding_to_k(*argv):
    list_to_pad = argv[0]
    k = argv[1]
    the_padding = [-1] * k
    for i in range(len(list_to_pad)):
        list_to_pad[i].extend(the_padding)
    return list_to_pad


def create_one_hot(train_y: ndarray, vector_size: Optional[int] = None, min_label: int = 0):
    if vector_size is None:
        min_label, max_label = train_y.min(), train_y.max()
        vector_size = max_label - min_label + 1
    one_hot_y = np.zeros((train_y.shape[0], vector_size))
    one_hot_y[np.arange(train_y.shape[0]), train_y - min_label] = 1
    return one_hot_y


class TrainingStopProblemDataset(Dataset):
    def __init__(self, list_seq):
        x_data = []
        y_data = []
        self.y_samples = []
        for x, y in list_seq:
            x_data.append(np.array(x, dtype=np.float32))
            y_data.append(y)
        self.x_samples = torch.tensor(x_data)
        self.y_samples = torch.tensor(y_data)
        self.transforms = transforms.Compose([StdNormalizer(self.x_samples)])

    def __len__(self):
        return len(self.x_samples)

    def __getitem__(self, idx):
        return self.transforms(self.x_samples[idx]), self.y_samples[idx]


class StdNormalizer:
    def __init__(self, data_set: ndarray) -> None:
        self.mean = data_set.mean(axis=0)
        self.std_dev = data_set.std(axis=0)

    def __call__(self, data: Tensor) -> Tensor:
        x = (data - self.mean) / self.std_dev
        x[torch.isnan(x)] = 0
        return x


class MinMaxNormalizer:
    def __init__(self, data_set: Tensor, normalized_max=1, normalized_min: int = 0) -> None:
        self.min = data_set.min(axis=0)
        self.max = data_set.max(axis=0)
        self.normalized_min = normalized_min
        self.normalized_max = normalized_max

    def __call__(self, data: ndarray):
        factor = (self.normalized_max - self.normalized_min)
        x = ((data - self.min) / (self.max - self.min)) * factor + self.normalized_min
        return x


def train_test_and_save_model():
    warnings.filterwarnings("ignore", category=np.VisibleDeprecationWarning)
    # x = get_data_for_all_players()
    #full_data_path = os.path.join(os.path.curdir, 'datasets', 'site_data.json')
    full_data_path = os.path.join(os.path.curdir, 'datasets', 'experiment_data.json')
    lines_to_predict = 3
    model = Net(lines_to_predict)
    organized_data = parse_data_from_json(full_data_path, lines_to_predict)
    train_size = (len(organized_data) // 5) * 4
    train_set = TrainingStopProblemDataset(np.array(organized_data[0:train_size]))
    validation_set = TrainingStopProblemDataset(np.array(organized_data[train_size:len(organized_data)]))
    train_accuracy, train_loss = train(model, train_set)
    test_accuracy, test_loss = test(model, validation_set)
    if test_accuracy >= 35:
        model_path = os.path.join('saved_models', f'model_{train_accuracy}-{test_accuracy}.pt')
        torch.save(model, model_path)


def parse_data_from_json(json_path: str, lines_to_delete=3) -> List:
    users = None
    with open(json_path, 'r') as fp:
        users = json.load(fp)
    if users is None:
        exit(-1)
    organized_data = []
    for user in users.values():
        meta = user[0]
        x = user[1:]
        random.shuffle(x)
        x.insert(0, meta)
        y = []
        for i in range(len(x) - lines_to_delete, len(x)):
            y.append(int(x[i][CHOSEN_INDEX_INDEX]))
            for j in range(CHOSEN_VALUE_INDEX, len(x[i])):
                x[i][j] = -1
        organized_data.append((x, y))
    return organized_data
