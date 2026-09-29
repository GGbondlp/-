"""model.py — MLP surrogate model: thickness (4) -> spectrum (41)."""
import torch.nn as nn


class MLP(nn.Module):
    def __init__(self, in_dim=4, hidden=(128, 128, 64), out_dim=41):
        super().__init__()
        layers = []
        prev = in_dim
        for h in hidden:
            layers += [nn.Linear(prev, h), nn.ReLU()]
            prev = h
        layers += [nn.Linear(prev, out_dim)]
        self.net = nn.Sequential(*layers)

    def forward(self, x):
        return self.net(x)
