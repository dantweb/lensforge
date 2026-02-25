#!/bin/bash
set -e

echo "=== LensForge Smoke Test ==="

echo "Building container..."
docker compose build

echo "Starting container..."
docker compose up -d
echo "Waiting for startup (model loading)..."
sleep 15

echo "Testing /health..."
curl -sf http://localhost:8000/health | python3 -m json.tool

echo ""
echo "Testing /analyze with sample image..."
IMG_B64=$(python3 -c "
import base64
from io import BytesIO
from PIL import Image, ImageDraw
img = Image.new('RGB', (224, 224), color=(180, 130, 100))
draw = ImageDraw.Draw(img)
for i in range(0, 224, 8):
    draw.line([(i, 0), (i, 224)], fill='black', width=2)
buf = BytesIO()
img.save(buf, format='JPEG')
print(base64.b64encode(buf.getvalue()).decode())
")

curl -sf -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d "{\"image_base64\": \"$IMG_B64\"}" | python3 -m json.tool

echo ""
echo "Cleaning up..."
docker compose down

echo "=== Smoke test passed! ==="
