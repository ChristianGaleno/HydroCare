import torch
import torch.nn as nn
from torchvision import models

def build_model(num_classes, dropout=0.2):
    net = models.resnet50(weights=None)
    in_features = net.fc.in_features
    net.fc = nn.Sequential(
        nn.Dropout(dropout),
        nn.Linear(in_features, num_classes),
    )
    return net

ckpt = torch.load("../model/best_resnet50.pt", map_location="cpu")
class_names = ckpt["classes"]

model = build_model(num_classes=len(class_names))
model.load_state_dict(ckpt["model_state"])
model.eval()