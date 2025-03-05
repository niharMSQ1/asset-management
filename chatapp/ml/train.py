import numpy as np
import json
import random
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from .ntk_utils import bag_of_words, tokenize, stem
from .model import NeuralNet

# Load intents
with open('chatapp/ml/intents.json', 'r') as f:
    intents = json.load(f)

all_words = []
tags = []
xy = []

# Process intents
for intent in intents['intents']:
    tag = intent['tag']
    tags.append(tag)
    for pattern in intent['patterns']:
        w = tokenize(pattern)
        all_words.extend(w)
        xy.append((w, tag))

# Stemming and sorting words
ignore_words = ['?', '.', '!']
all_words = sorted(set(stem(w) for w in all_words if w not in ignore_words))
tags = sorted(set(tags))

# Training data
X_train = []
y_train = []
for (pattern_sentence, tag) in xy:
    bag = bag_of_words(pattern_sentence, all_words)
    X_train.append(bag)
    y_train.append(tags.index(tag))

X_train = np.array(X_train)
y_train = np.array(y_train)

# Hyperparameters
num_epochs = 6000
batch_size = 128
learning_rate = 0.0005
input_size = len(X_train[0])
hidden_size = 128
output_size = len(tags)

# Dataset
class ChatDataset(Dataset):
    def __init__(self):
        self.n_samples = len(X_train)
        self.x_data = X_train
        self.y_data = y_train

    def __getitem__(self, index):
        return self.x_data[index], self.y_data[index]

    def __len__(self):
        return self.n_samples

dataset = ChatDataset()
train_loader = DataLoader(dataset=dataset, batch_size=batch_size, shuffle=True, num_workers=0)

# Model, loss, and optimizer
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model = NeuralNet(input_size, hidden_size, output_size).to(device)

criterion = nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)

# Training loop
for epoch in range(num_epochs):
    for words, labels in train_loader:
        words = words.to(device)
        labels = labels.to(dtype=torch.long).to(device)
        
        outputs = model(words)
        loss = criterion(outputs, labels)
        
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        
    if (epoch+1) % 100 == 0:
        print (f'Epoch [{epoch+1}/{num_epochs}], Loss: {loss.item():.4f}')

# Save model
data = {
    "model_state": model.state_dict(),
    "input_size": input_size,
    "hidden_size": hidden_size,
    "output_size": output_size,
    "all_words": all_words,
    "tags": tags
}

FILE = "chatapp/ml/data.pth"
torch.save(data, FILE)
print(f'Training complete. Model saved to {FILE}')
