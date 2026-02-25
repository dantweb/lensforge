# Dermatology Context Cluster

Skin lesion screening extension for LensForge. Classifies dermatoscopic images using the HAM10000 dataset categories.

## Pipeline

### NN1: Quality Check — BrisqueChecker

**What it does**: Detects blurry/low-quality images using OpenCV Laplacian variance. Rejects images below the sharpness threshold.

**Model**: OpenCV built-in (no download, no API key).

**Config**:
```env
QUALITY_CLASS=custom.extensions.dermatology.brisque_checker.BrisqueChecker
QUALITY_BLUR_THRESHOLD=100
```

**No API key required.**

### NN1: Safety Filter — FalconsaiNsfwDetector

**What it does**: Filters NSFW/inappropriate content before medical analysis. Uses a ViT model fine-tuned for NSFW detection.

**Model**: [Falconsai/nsfw_image_detection](https://huggingface.co/Falconsai/nsfw_image_detection)
- License: Apache 2.0
- Size: ~350 MB (auto-downloaded on first use, cached)
- Runs on CPU

**Config**:
```env
NSFW_CLASS=custom.extensions.dermatology.falconsai_nsfw.FalconsaiNsfwDetector
NSFW_THRESHOLD=0.7
```

**No API key required.** Model is public on HuggingFace.

### NN2: Domain Classifier — VitSkinClassifier

**What it does**: Classifies skin lesions into 7 HAM10000 categories with risk levels and urgency recommendations.

**Model**: [Anwarkh1/Skin_Cancer-Image_Classification](https://huggingface.co/Anwarkh1/Skin_Cancer-Image_Classification)
- License: Apache 2.0
- Size: ~350 MB (auto-downloaded on first use, cached)
- Architecture: ViT (Vision Transformer) fine-tuned on HAM10000
- Runs on CPU

**Config**:
```env
CLASSIFIER_CLASS=custom.extensions.dermatology.vit_skin.VitSkinClassifier
CLASSIFIER_MODEL_NAME=Anwarkh1/Skin_Cancer-Image_Classification
DEVICE=cpu
```

**No API key required.** Model is public on HuggingFace.

**Classification categories**:

| Label | Condition | Risk Level | Urgency |
|-------|-----------|-----------|---------|
| mel | Melanoma | HIGH | Consult dermatologist within days |
| bcc | Basal cell carcinoma | HIGH | Consult dermatologist within days |
| akiec | Actinic keratoses | MODERATE | Consult dermatologist within weeks |
| df | Dermatofibroma | LOW | Monitor, no immediate urgency |
| nv | Melanocytic nevi (moles) | LOW | Monitor, no immediate urgency |
| bkl | Benign keratosis | LOW | Monitor, no immediate urgency |
| vasc | Vascular lesions | LOW | Monitor, no immediate urgency |

## API Keys

### This extension: none required

All three models (BRISQUE, Falconsai, Anwarkh1) are free and public. No HuggingFace token needed.

### Optional: HuggingFace token (for gated models)

If you swap the classifier to a gated model (e.g. Google MedGemma), you need a HuggingFace token:

1. Create account at https://huggingface.co/join
2. Go to https://huggingface.co/settings/tokens
3. Create a new token with `read` scope
4. Add to `custom/.env`:
   ```env
   HF_TOKEN=hf_xxxxxxxxxxxxxxxxxxxx
   ```
5. Accept the model's license on its HuggingFace page

### Optional: GPU deployment

For production with GPU acceleration:

| Provider | Setup | Cost |
|----------|-------|------|
| Local CUDA | Set `DEVICE=cuda` in `custom/.env` | Your GPU |
| Modal | `pip install modal && modal token new` | $30/mo free tier |
| RunPod | Sign up at https://runpod.io | Pay-per-use |

## Connecting to LensForge

### 1. Configure

Copy the example config and adjust if needed:

```bash
cp custom/.env.example custom/.env
```

Default `custom/.env` for dermatology:

```env
DEVICE=cpu
QUALITY_CLASS=custom.extensions.dermatology.brisque_checker.BrisqueChecker
QUALITY_BLUR_THRESHOLD=100
NSFW_CLASS=custom.extensions.dermatology.falconsai_nsfw.FalconsaiNsfwDetector
NSFW_THRESHOLD=0.7
CLASSIFIER_CLASS=custom.extensions.dermatology.vit_skin.VitSkinClassifier
CLASSIFIER_MODEL_NAME=Anwarkh1/Skin_Cancer-Image_Classification
MAX_IMAGE_SIZE=1024
HOST=0.0.0.0
PORT=8000
```

### 2. Build and run

```bash
make build
make run
```

Service starts at `http://localhost:8000`.

### 3. Send an image

```bash
# Base64 encoded image
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"image_base64": "<base64-string>"}'

# Or image URL
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"image_url": "https://example.com/lesion.jpg"}'
```

### 4. Response

```json
{
  "status": "success",
  "lesion_detected": true,
  "main_description": "Top prediction: nv (87.0%)",
  "predictions": [
    {"label": "nv", "probability": 0.87, "risk_level": "low"},
    {"label": "mel", "probability": 0.08, "risk_level": "high"}
  ],
  "urgency": "Monitor, no immediate urgency",
  "disclaimer": "This is NOT a medical diagnosis. See a qualified specialist. AI output only.",
  "inference_time_ms": 342,
  "model_versions": {
    "nn1_quality": "brisque-laplacian-1.0",
    "nn1_safety": "falconsai-nsfw-vit-1.0",
    "nn2": "vit-skin-Skin_Cancer-Image_Classification"
  }
}
```

### 5. Batch analysis

```bash
curl -X POST http://localhost:8000/batch-analyze \
  -H "Content-Type: application/json" \
  -d '{"images": [{"image_base64": "..."}, {"image_url": "..."}]}'
```

Max 50 images per batch request.

## Testing

```bash
make test-unit        # Unit tests (mocked, fast)
make test-integration # Integration tests (downloads real models, ~30s)
make pre-commit       # Lint + unit tests
```
