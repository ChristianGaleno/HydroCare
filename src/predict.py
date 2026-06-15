import torch
import torchvision.transforms as transforms
from config import cfg
from PIL import Image
from model import model, class_names


eval_tf = transforms.Compose([
    transforms.Resize(int(cfg.IMAGE_SIZE * 1.14)),
    transforms.CenterCrop(cfg.IMAGE_SIZE),
    transforms.ToTensor(),
    transforms.Normalize(cfg.MEAN, cfg.STD),
])

def load_image(path):
    img = Image.open(path)
    img = img.convert("RGB")
    tensor = eval_tf(img)
    return tensor.unsqueeze(0)

def predict(model, input_data): 
    with torch.no_grad(): 
        output = model(input_data)
        probs = torch.softmax(output, dim=1)
        label = torch.argmax(probs, dim=1)
    return class_names[label]

if __name__ == "__main__":
    img = load_image("../test_grape leaf black rot_8.jpg")
    print(predict(model, img))
