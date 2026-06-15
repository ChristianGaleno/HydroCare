---
title: HydroCare
emoji: 🌿
colorFrom: green
colorTo: green
sdk: docker
app_port: 7860
pinned: false
license: mit
---

# 🌿 HydroCare — Plant Disease Classifier

> 🔗 **Live demo:** https://huggingface.co/spaces/ChristianGaleno/hydrocare

A deep-learning pipeline that identifies **89 plant disease & health conditions** across **24 crop species** using a fine-tuned **ResNet-50** model.

## Highlights

- 89-class classification covering healthy states + disease conditions across 24 crops
- Two-stage training: frozen backbone → partial fine-tune
- Ready-to-use inference script

---

## Project Structure

```
HydroCare/
├── model/
│   └── best_resnet50.pt          # Trained weights + class list
├── notebooks/
│   └── HydroCare_ResNet50_Kaggle.ipynb   # Full training notebook
├── src/
│   ├── config.py                 # Hyperparameters & paths
│   ├── model.py                  # Model builder + checkpoint loader
│   └── predict.py                # Single-image inference
├── webapp/                       # 🌿 Web app (UI + API)
│   ├── server.py                 # FastAPI backend (loads model, /api/predict)
│   ├── disease_info.py           # Label → friendly name + care tips
│   └── static/
│       ├── index.html            # Botanical-themed UI
│       ├── styles.css            # Fresh green design system
│       └── app.js                # Upload / camera / result rendering
├── run_webapp.sh                 # One-command launcher
├── test/                         # Sample test images (by class)
├── classes.json                  # Class index → label mapping
├── confusion_matrix.png          # Validation confusion matrix
├── curves.png                    # Training / validation curves
└── requirements.txt
```

---

## Getting Started

### Prerequisites

- Python 3.10+
- (Optional) CUDA-capable GPU — see [PyTorch install guide](https://pytorch.org/get-started/locally/)

### Installation

```bash
# Clone the repo
git clone <repo-url> && cd HydroCare

# Create a virtual environment
python -m venv .venv && source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Quick Inference

```bash
cd src
python predict.py
```

By default `predict.py` classifies `../test_grape leaf black rot_8.jpg`. To classify your own image, change the path in `load_image()` or import the helpers:

```python
from src.predict import load_image, predict
from src.model import model

img = load_image("path/to/leaf_photo.jpg")
print(predict(model, img))   # e.g. "Grape__black_rot"
```

---

## 🌿 Web App (UI/UX)

A full web interface lets you upload or snap a leaf photo and get a diagnosis,
confidence score, and care tips — powered by the same ResNet-50 checkpoint.

### Run it

```bash
pip install -r requirements.txt      # adds fastapi, uvicorn, python-multipart
./run_webapp.sh                      # → http://127.0.0.1:8000
```

Or manually:

```bash
python -m uvicorn server:app --app-dir webapp --port 8000
```

Then open **http://127.0.0.1:8000** in your browser.

### Features

- **Upload or camera capture** with drag-and-drop and image preview
- **Live diagnosis**: crop, condition, and a color-coded confidence ring
- **Care tips** tailored to the detected condition (disease / pest / healthy)
- **Top-3 possibilities** with animated probability bars
- **Supported-plants explorer** auto-built from the model's class list

### API

| Method | Endpoint        | Description                                   |
|--------|-----------------|-----------------------------------------------|
| GET    | `/`             | The web UI                                    |
| GET    | `/api/health`   | Liveness + device + class count               |
| GET    | `/api/crops`    | Crops grouped with their recognizable conditions |
| POST   | `/api/predict`  | Multipart image upload → top-3 predictions + care info |

```bash
curl -F "file=@test_grape leaf black rot_8.jpg" http://127.0.0.1:8000/api/predict
```

---

## Training Details

| Parameter | Value |
|-----------|-------|
| Architecture | ResNet-50 (ImageNet pretrained) |
| Input size | 224 × 224 px |
| Batch size | 512 |
| Optimizer | AdamW (head LR 1e-3 → fine-tune LR 1e-4) |
| Label smoothing | 0.1 |
| Weight decay | 1e-4 |
| Freeze epochs | 4 (head only) |
| Total epochs | 20 (early stopping patience: 6) |
| Val / Test split | 15 % / 15 % |

Training was done on Kaggle (GPU P100). See [`notebooks/HydroCare_ResNet50_Kaggle.ipynb`](notebooks/HydroCare_ResNet50_Kaggle.ipynb) for the full pipeline.

---

## Trained Classes

The model outputs **89 logits**. Labels follow the format `Crop__condition`, where `healthy` means no disease was detected.

### Classes by Crop

| Crop | Conditions | Count |
|------|------------|-------|
| **Apple** | black rot · healthy · rust · scab | 4 |
| **Cassava** | bacterial blight · brown streak disease · green mottle · healthy · mosaic disease | 5 |
| **Cherry** | healthy · powdery mildew | 2 |
| **Chili** | healthy · leaf curl · leaf spot · whitefly · yellowish | 5 |
| **Coffee** | cercospora leaf spot · healthy · red spider mite · rust | 4 |
| **Corn** | common rust · gray leaf spot · healthy · northern leaf blight | 4 |
| **Cucumber** | diseased · healthy | 2 |
| **Guava** | diseased · healthy | 2 |
| **Grape** | black measles · black rot · healthy · leaf blight (isariopsis leaf spot) | 4 |
| **Jamun** | diseased · healthy | 2 |
| **Lemon** | diseased · healthy | 2 |
| **Mango** | diseased · healthy | 2 |
| **Peach** | bacterial spot · healthy | 2 |
| **Pepper, bell** | bacterial spot · healthy | 2 |
| **Pomegranate** | diseased · healthy | 2 |
| **Potato** | early blight · healthy · late blight | 3 |
| **Rice** | brown spot · healthy · hispa · leaf blast · neck blast | 5 |
| **Soybean** | bacterial blight · caterpillar · diabrotica speciosa · downy mildew · healthy · mosaic virus · powdery mildew · rust · southern blight | 9 |
| **Strawberry** | leaf scorch · healthy | 2 |
| **Sugarcane** | bacterial blight · healthy · red rot · red stripe · rust | 5 |
| **Tea** | algal leaf · anthracnose · bird eye spot · brown blight · healthy · red leaf spot | 6 |
| **Tomato** | bacterial spot · early blight · healthy · late blight · leaf mold · mosaic virus · septoria leaf spot · spider mites (two spotted spider mite) · target spot · yellow leaf curl virus | 10 |
| **Wheat** | brown rust · healthy · septoria · yellow rust | 4 |

### Full Label List (model output order)

| Index | Label |
|-------|-------|
| 0 | Apple__black_rot |
| 1 | Apple__healthy |
| 2 | Apple__rust |
| 3 | Apple__scab |
| 4 | Cassava__bacterial_blight |
| 5 | Cassava__brown_streak_disease |
| 6 | Cassava__green_mottle |
| 7 | Cassava__healthy |
| 8 | Cassava__mosaic_disease |
| 9 | Cherry__healthy |
| 10 | Cherry__powdery_mildew |
| 11 | Chili__healthy |
| 12 | Chili__leaf curl |
| 13 | Chili__leaf spot |
| 14 | Chili__whitefly |
| 15 | Chili__yellowish |
| 16 | Coffee__cercospora_leaf_spot |
| 17 | Coffee__healthy |
| 18 | Coffee__red_spider_mite |
| 19 | Coffee__rust |
| 20 | Corn__common_rust |
| 21 | Corn__gray_leaf_spot |
| 22 | Corn__healthy |
| 23 | Corn__northern_leaf_blight |
| 24 | Cucumber__diseased |
| 25 | Cucumber__healthy |
| 26 | Gauva__diseased |
| 27 | Gauva__healthy |
| 28 | Grape__black_measles |
| 29 | Grape__black_rot |
| 30 | Grape__healthy |
| 31 | Grape__leaf_blight_(isariopsis_leaf_spot) |
| 32 | Jamun__diseased |
| 33 | Jamun__healthy |
| 34 | Lemon__diseased |
| 35 | Lemon__healthy |
| 36 | Mango__diseased |
| 37 | Mango__healthy |
| 38 | Peach__bacterial_spot |
| 39 | Peach__healthy |
| 40 | Pepper_bell__bacterial_spot |
| 41 | Pepper_bell__healthy |
| 42 | Pomegranate__diseased |
| 43 | Pomegranate__healthy |
| 44 | Potato__early_blight |
| 45 | Potato__healthy |
| 46 | Potato__late_blight |
| 47 | Rice__brown_spot |
| 48 | Rice__healthy |
| 49 | Rice__hispa |
| 50 | Rice__leaf_blast |
| 51 | Rice__neck_blast |
| 52 | Soybean__bacterial_blight |
| 53 | Soybean__caterpillar |
| 54 | Soybean__diabrotica_speciosa |
| 55 | Soybean__downy_mildew |
| 56 | Soybean__healthy |
| 57 | Soybean__mosaic_virus |
| 58 | Soybean__powdery_mildew |
| 59 | Soybean__rust |
| 60 | Soybean__southern_blight |
| 61 | Strawberry___leaf_scorch |
| 62 | Strawberry__healthy |
| 63 | Sugarcane__bacterial_blight |
| 64 | Sugarcane__healthy |
| 65 | Sugarcane__red_rot |
| 66 | Sugarcane__red_stripe |
| 67 | Sugarcane__rust |
| 68 | Tea__algal_leaf |
| 69 | Tea__anthracnose |
| 70 | Tea__bird_eye_spot |
| 71 | Tea__brown_blight |
| 72 | Tea__healthy |
| 73 | Tea__red_leaf_spot |
| 74 | Tomato__bacterial_spot |
| 75 | Tomato__early_blight |
| 76 | Tomato__healthy |
| 77 | Tomato__late_blight |
| 78 | Tomato__leaf_mold |
| 79 | Tomato__mosaic_virus |
| 80 | Tomato__septoria_leaf_spot |
| 81 | Tomato__spider_mites_(two_spotted_spider_mite) |
| 82 | Tomato__target_spot |
| 83 | Tomato__yellow_leaf_curl_virus |
| 84 | Wheat__brown_rust |
| 85 | Wheat__healthy |
| 86 | Wheat__septoria |
| 87 | Wheat__yellow_rust |

---

## License

This project is for educational and research purposes.
