import torch
import torch.nn as nn
import torch.nn.functional as F
import math

class SimpleEEGConvNet(nn.Module):
    def __init__(self, input_channels=8, input_length=125, num_classes=2):
        super(SimpleEEGConvNet, self).__init__()
        self.conv1 = nn.Conv1d(input_channels, 32, kernel_size=5, padding=2)
        self.bn1 = nn.BatchNorm1d(32)
        self.pool1 = nn.MaxPool1d(2)

        self.conv2 = nn.Conv1d(32, 64, kernel_size=5, padding=2)
        self.bn2 = nn.BatchNorm1d(64)
        self.pool2 = nn.MaxPool1d(2)

        self.flatten = nn.Flatten()
        self.fc1 = nn.Linear((input_length // 4) * 64, 64)
        self.fc2 = nn.Linear(64, num_classes)

    def forward(self, x):  # x: (B, T, C)
        x = x.permute(0, 2, 1)  # -> (B, C, T)
        x = self.pool1(F.relu(self.bn1(self.conv1(x))))
        x = self.pool2(F.relu(self.bn2(self.conv2(x))))
        x = self.flatten(x)
        x = F.relu(self.fc1(x))
        return self.fc2(x)

# ---- Custom scaled_tanh activation ----
def scaled_tanh(x):
    return 1.7159 * torch.tanh((2.0 / 3.0) * x)


# ---- Cecotti-style initializer ----
def cecotti_normal_init(tensor):
    if tensor.dim() == 1:
        fan_in = tensor.size(0)
    elif tensor.dim() == 2:
        fan_in = tensor.size(0)
    else:
        receptive_field_size = tensor[0][0].numel()
        fan_in = tensor.size(1) * receptive_field_size
    std = 1.0 / fan_in
    with torch.no_grad():
        return tensor.normal_(mean=0.0, std=std)


# ---- CNN1 Model ----
class CNN1(nn.Module):
    def __init__(self, Chans=6, Samples=206):
        super(CNN1, self).__init__()

        self.conv1 = nn.Conv1d(in_channels=Chans, out_channels=10, kernel_size=1, padding='same')
        self.conv2 = nn.Conv1d(in_channels=10, out_channels=50, kernel_size=13, padding='same')

        self.flatten = nn.Flatten()
        self.dense1 = nn.Linear(50 * Samples, 100)
        self.dense2 = nn.Linear(100, 2)  # 2 classes

        self.init_weights()

    def init_weights(self):
        cecotti_normal_init(self.conv1.weight)
        cecotti_normal_init(self.conv2.weight)
        nn.init.zeros_(self.conv1.bias)
        nn.init.zeros_(self.conv2.bias)

    def forward(self, x):  # x: (batch, time, chans)
        x = x.permute(0, 2, 1)  # → (batch, chans, time)
        x = scaled_tanh(self.conv1(x))
        x = scaled_tanh(self.conv2(x))
        x = self.flatten(x)
        x = torch.sigmoid(self.dense1(x))
        x = torch.sigmoid(self.dense2(x))
        return x


# ---- SepConv1D Model ----
class SepConv1D(nn.Module):
    def __init__(self, Chans=6, Samples=206, Filters=32):
        super(SepConv1D, self).__init__()
        self.pad = nn.ConstantPad1d((4, 4), 0)  # pad only in time dim
        self.depthwise = nn.Conv1d(in_channels=Chans, out_channels=Chans,
                                   kernel_size=16, stride=8, groups=Chans, bias=True)
        self.pointwise = nn.Conv1d(in_channels=Chans, out_channels=Filters,
                                   kernel_size=1, bias=True)

        # Compute output shape to flatten
        self.output_len = (Samples + 8 - 16) // 8 + 1  # after stride and padding
        self.flatten = nn.Flatten()
        self.classifier = nn.Linear(Filters * self.output_len, 1)

    def forward(self, x):  # x: (batch, time, chans)
        x = x.permute(0, 2, 1)  # → (batch, chans, time)
        x = self.pad(x)
        x = self.depthwise(x)
        x = self.pointwise(x)
        x = torch.tanh(x)
        x = self.flatten(x)
        x = torch.sigmoid(self.classifier(x))
        return x