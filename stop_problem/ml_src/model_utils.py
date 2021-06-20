import torch
import torch.nn.functional as F
from torch import no_grad
import time

from stop_problem.ml_src.model import Net
import numpy as np
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

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
    return  accuracy

def predict(model_net, test_loader):
    model_net.eval()
    i = 0
    for batch_idx, (data, label) in enumerate(test_loader):
        data = data.to(device)
        output = model_net(data)
        prediction = output.cpu().data.max(1, keepdim=True)[1].max()
        i += 1
    return prediction