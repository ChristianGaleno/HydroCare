"""HydroCare web app — FastAPI backend.

Loads the trained ResNet-50 checkpoint once at startup and serves:
  * GET  /              -> the botanical web UI (static frontend)
  * GET  /api/health    -> liveness + model info
  * GET  /api/crops     -> list of supported crops & conditions
  * POST /api/predict   -> classify an uploaded leaf image
"""

import io
from pathlib import Path

import torch
import torch.nn as nn
import torchvision.transforms as transforms
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from PIL import Image, UnidentifiedImageError

from disease_info import parse_label

# --- paths -----------------------------------------------------------------
ROOT = Path(__file__).resolve().parent.parent
CKPT_PATH = ROOT / "model" / "best_resnet50.pt"
STATIC_DIR = Path(__file__).resolve().parent / "static"

# --- inference config (mirrors src/config.py) ------------------------------
IMAGE_SIZE = 224
MEAN = [0.485, 0.456, 0.406]
STD = [0.229, 0.224, 0.225]
TOP_K = 3

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def build_model(num_classes: int, dropout: float = 0.2) -> nn.Module:
    from torchvision import models

    net = models.resnet50(weights=None)
    in_features = net.fc.in_features
    net.fc = nn.Sequential(
        nn.Dropout(dropout),
        nn.Linear(in_features, num_classes),
    )
    return net


# --- load model once -------------------------------------------------------
if not CKPT_PATH.exists():
    raise FileNotFoundError(f"Model checkpoint not found at {CKPT_PATH}")

_ckpt = torch.load(CKPT_PATH, map_location="cpu")
CLASS_NAMES = _ckpt["classes"]
MODEL = build_model(num_classes=len(CLASS_NAMES))
MODEL.load_state_dict(_ckpt["model_state"])
MODEL.to(DEVICE)
MODEL.eval()

EVAL_TF = transforms.Compose([
    transforms.Resize(int(IMAGE_SIZE * 1.14)),
    transforms.CenterCrop(IMAGE_SIZE),
    transforms.ToTensor(),
    transforms.Normalize(MEAN, STD),
])

# Pre-parse every label once for the /api/crops endpoint.
PARSED = [parse_label(name) for name in CLASS_NAMES]

app = FastAPI(title="HydroCare", description="Plant disease classifier", version="1.0.0")


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "device": str(DEVICE),
        "num_classes": len(CLASS_NAMES),
    }


@app.get("/api/crops")
def crops():
    """Grouped crop -> conditions, for the 'supported plants' UI section."""
    grouped: dict[str, list[str]] = {}
    for p in PARSED:
        grouped.setdefault(p["crop"], [])
        if p["condition"] not in grouped[p["crop"]]:
            grouped[p["crop"]].append(p["condition"])
    out = [
        {"crop": crop, "conditions": sorted(conds)}
        for crop, conds in sorted(grouped.items())
    ]
    return {"count": len(out), "total_classes": len(CLASS_NAMES), "crops": out}


@app.post("/api/predict")
async def predict(file: UploadFile = File(...)):
    raw = await file.read()
    if not raw:
        raise HTTPException(status_code=400, detail="Empty file uploaded.")

    try:
        img = Image.open(io.BytesIO(raw)).convert("RGB")
    except (UnidentifiedImageError, OSError):
        raise HTTPException(status_code=400, detail="Could not read that image. Please upload a valid JPG or PNG.")

    tensor = EVAL_TF(img).unsqueeze(0).to(DEVICE)

    with torch.no_grad():
        logits = MODEL(tensor)
        probs = torch.softmax(logits, dim=1)[0]

    k = min(TOP_K, probs.numel())
    top_probs, top_idx = torch.topk(probs, k)

    predictions = []
    for prob, idx in zip(top_probs.tolist(), top_idx.tolist()):
        info = PARSED[idx]
        predictions.append({
            "crop": info["crop"],
            "condition": info["condition"],
            "display": info["display"],
            "kind": info["kind"],
            "confidence": round(prob * 100, 2),
        })

    best = PARSED[top_idx[0].item()]
    return {
        "best": {
            "crop": best["crop"],
            "condition": best["condition"],
            "display": best["display"],
            "kind": best["kind"],
            "summary": best["summary"],
            "tips": best["tips"],
            "confidence": round(top_probs[0].item() * 100, 2),
        },
        "predictions": predictions,
    }


# --- static frontend (mounted last so /api/* wins) -------------------------
@app.get("/")
def index():
    return FileResponse(STATIC_DIR / "index.html")


app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")
