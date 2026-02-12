# AI4SE - Models Directory

This directory stores quantized models for offline inference.

## Directory Structure

```
models/
├── llama-3.2-3b-medical-q4.gguf     # Medical assistant (GGUF format)
├── llama-3.2-3b-medical-onnx/       # Medical assistant (ONNX format)
├── llama-3.2-3b-medical-webllm/     # Medical assistant (WebLLM format)
├── phi-3-mini-technical-q4.gguf     # Technical repair assistant
└── llama-3.2-vision-agriculture/    # Agriculture assistant
```

## Model Downloads

Models are **not included in the repository** due to their large size (1-3 GB each).

### Option 1: Download Pre-quantized Models (Recommended)

Coming soon - we'll host quantized models on Hugging Face or CDN.

### Option 2: Quantize Models Yourself

1. **Download base model**:
   ```bash
   huggingface-cli download meta-llama/Llama-3.2-3B-Instruct --local-dir ./base/llama-3.2-3b
   ```

2. **Quantize**:
   ```bash
   python ../training/quantize_model.py \
     --model ./base/llama-3.2-3b \
     --output ./llama-3.2-3b-q4.gguf \
     --format gguf \
     --quant-type Q4_K_M
   ```

### Option 3: Use WebLLM (Auto-download)

The demo application will automatically download models from MLC LLM's CDN on first load.

## Model Specifications

| Model | Size (FP16) | Size (Q4) | Parameters | Use Case |
|-------|-------------|-----------|------------|----------|
| Llama-3.2-1B | 2.5 GB | 0.6 GB | 1.2B | Low-end devices |
| Llama-3.2-3B | 6.4 GB | 1.9 GB | 3.2B | Medical assistant |
| Phi-3-mini | 7.8 GB | 2.3 GB | 3.8B | Technical repair |
| Llama-3.2-Vision | 15 GB | 4.5 GB | 11B | Agriculture (vision) |

## Testing Models

### Test GGUF Model (llama.cpp)

```bash
# Install llama.cpp first
git clone https://github.com/ggerganov/llama.cpp
cd llama.cpp && make

# Test inference
./main \
  -m ../models/llama-3.2-3b-medical-q4.gguf \
  -p "You are a medical assistant. A patient says: 'My child has fever.' Provide guidance." \
  --temp 0.7 \
  -n 512
```

### Test WebLLM Model (Browser)

1. Open `demo/index.html` in Chrome 113+
2. Select model from dropdown
3. Click "Load Model"
4. Start chatting!

## Storage Requirements

Plan for the following storage:

- **Development**: 10-20 GB (base models + quantized versions)
- **Production (mobile)**: 2-4 GB (one quantized model)
- **Production (server)**: 20-50 GB (multiple models + LoRA adapters)

## Cleaning Up

```bash
# Remove all models
rm -rf models/*

# Remove specific model
rm models/llama-3.2-3b-medical-q4.gguf
```

---

*Note: This directory is listed in `.gitignore` to prevent accidentally committing large model files.*
