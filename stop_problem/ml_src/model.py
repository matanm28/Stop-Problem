import numpy as np
import torch
from torch import nn
import torch.nn.functional as F
import torch.optim as optim


class Net(nn.Module):

    def __init__(self):
        super(Net, self).__init__()
        self.fc1 = nn.Linear(561, 256)
        self.fc2 = nn.Linear(256, 128)
        self.fc3 = nn.Linear(128, 60)
        self.fc4 = nn.Linear(60, 20)


        self.optimizer = optim.Adam(self.parameters(), lr=0.001)
        self.drop = nn.Dropout(0.25)

    def forward(self, x):
        x = x.view(-1, 561)
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = F.relu(self.fc3(x))
        x = self.fc4(x)
        return F.log_softmax(x, -1)