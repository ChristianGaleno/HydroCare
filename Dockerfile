# HydroCare — Hugging Face Spaces (Docker SDK)
# Serves the FastAPI app + ResNet-50 checkpoint on port 7860.
FROM python:3.11-slim

WORKDIR /app

# CPU-only PyTorch keeps the image small and the free CPU Space happy.
RUN pip install --no-cache-dir \
    torch==2.2.2 torchvision==0.17.2 \
    --index-url https://download.pytorch.org/whl/cpu

# Runtime deps for the web app (training-only libs are intentionally omitted).
RUN pip install --no-cache-dir \
    "fastapi>=0.110.0" \
    "uvicorn[standard]>=0.27.0" \
    "python-multipart>=0.0.9" \
    "Pillow>=10.0.0" \
    "numpy>=1.24.0"

COPY . .

# Hugging Face Spaces expects the app on 7860.
EXPOSE 7860
CMD ["uvicorn", "server:app", "--app-dir", "webapp", "--host", "0.0.0.0", "--port", "7860"]
