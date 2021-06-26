import torch.optim as optim
from torch import nn


class Net(nn.Module):

    def __init__(self, num_of_predictions: int = 3):
        assert 1 <= num_of_predictions <= 5
        super(Net, self).__init__()
        self.whole_sequences = nn.Sequential(
            nn.Linear(561, 256),
            nn.ReLU(),
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Linear(128, num_of_predictions * 20),
            nn.ReLU(),
        )
        self.num_of_predictions = num_of_predictions
        self.answer_layers = [nn.Sequential(
            nn.Linear(20, 20), nn.ReLU(), nn.LogSoftmax(dim=1)
        ) for _ in range(num_of_predictions)]
        self.optimizer = optim.Adam(self.parameters(), lr=0.001)

    def forward(self, x):
        x = x.view(-1, 561)
        x = self.whole_sequences(x)
        answers = [self.answer_layers[k](x[:, k * 20:k * 20 + 20]) for k in range(self.num_of_predictions)]
        return answers
