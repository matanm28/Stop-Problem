import numpy as np
import torch
from torch import nn
import torch.nn.functional as F
import torch.optim as optim


class Net(nn.Module):

    def __init__(self):
        super(Net, self).__init__()
        # self.pool = nn.MaxPool2d(2, 2)
        # self.conv1 = nn.Conv2d(1, 4, kernel_size= 3)

        self.fc1 = nn.Linear(561, 256)
        self.fc2 = nn.Linear(256, 128)
        self.fc3 = nn.Linear(128, 60)
        self.fc4 = nn.Linear(60, 20)
        self.fc5 = nn.Linear(60, 20)
        self.fc6 = nn.Linear(60, 20)

        self.optimizer = optim.Adam(self.parameters(), lr=0.001)
        self.drop = nn.Dropout(0.25)

    def forward(self, x):
        x = x.view(-1, 561)
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = self.fc3(x)
        x1,x2,x3 = self.fc4(x), self.fc5(x), self.fc6(x)
        output = [F.log_softmax(x1, -1), F.log_softmax(x2, -1), F.log_softmax(x3, -1)]
        #output = torch.FloatTensor(np.array(output))
        b = torch.Tensor(3, 1, 20)
        output = torch.cat(output, out= b)
        return output