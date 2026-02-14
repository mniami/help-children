# AI4SE Setup and Training Summary

**Date:** February 13, 2026  
**Status:** ✅ Successfully Completed

## Overview

This document summarizes the setup, build, and fine-tuning process for the AI4SE (AI for Social Empowerment) project.

---

## 1. Environment Setup ✅

### Python Environment
- **Version:** Python 3.12.3
- **Type:** Virtual environment (venv)
- **Location:** `/home/dszczepek/help-children/.venv`

### Dependencies Installed

**Python packages:**
- `transformers` (5.1.0) - Hugging Face Transformers library
- `torch` (2.10.0) - PyTorch with CUDA 12.9 support
- `peft` (0.18.1) - Parameter-Efficient Fine-Tuning
- `accelerate` (1.12.0) - Training acceleration
- `bitsandbytes` (0.49.1) - Quantization support
- `datasets` (4.5.0) - Dataset loading and processing
- `openai-whisper` - Speech-to-Text for Amharic
- `piper-tts` - Text-to-Speech for Amharic
- And many more supporting libraries

**Node.js packages:**
- `serve` - Local development server
- `@mlc-ai/web-llm` - WebLLM framework
- `eslint`, `prettier` - Code quality tools

---

## 2. Hardware Configuration ⚠️

### CPU-Only Environment
- **CUDA Available:** No
- **GPU Devices:** 0
- **Training Mode:** CPU-only (slower but functional)

**Note:** For production training, GPU is highly recommended:
- Training time: ~10-100x faster with GPU
- Larger models: Can train 3B-7B parameter models efficiently
- Better convergence: More stable training with larger batch sizes

---

## 3. Demo Server 🌐

### Web Demo Running
- **Server:** Serve (npx)
- **Port:** 8000
- **Local URL:** http://localhost:8000
- **Network URL:** http://172.21.126.15:8000

### Demo Features
- Browser-based health assistant
- WebLLM integration (downloads ~2GB on first load)
- Offline-first architecture
- WebGPU acceleration (if supported)

**Access:** Open browser to http://localhost:8000 to test the demo

---

## 4. Model Fine-Tuning ✅

### Training Configuration

**Base Model:** `HuggingFaceTB/SmolLM2-135M-Instruct`
- Size: 135 million parameters
- Format: SmolLM2 architecture
- License: Apache 2.0

**LoRA Configuration:**
- Rank: 8
- Alpha: 16
- Target modules: q_proj, k_proj, v_proj, o_proj
- Dropout: 0.05
- Trainable parameters: 921,600 (0.68% of total)

**Training Parameters:**
- Epochs: 1
- Batch size: 1
- Gradient accumulation: 2 steps
- Learning rate: 2e-4
- Max sequence length: 256 tokens
- Optimizer: AdamW
- Precision: FP32 (CPU-compatible)

### Training Results

**Dataset:** 
- Training samples: 2
- Validation samples: 1
- Format: Medical Q&A conversations

**Metrics:**
- Training loss: 2.255
- Validation loss: 2.266
- Training time: 5.99 seconds
- Training speed: 0.334 samples/second

**Output:**
- LoRA adapter saved to: `models/medical-lora-test/`
- Includes: adapter weights, config, tokenizer

---

## 5. Testing Results 🧪

### Model Inference Test

Created test script: `training/test_model.py`

**Test Cases:**
1. ✅ Child with fever and diarrhea
2. ✅ Chest pain and breathing difficulty

**Observations:**
- Model loads successfully
- Generates responses (though not yet medical-grade)
- Fine-tuning pipeline works end-to-end

**Note:** Model quality is limited due to:
- Small training dataset (2 examples)
- Only 1 epoch of training
- CPU-only training (slower convergence)

For production-quality results, need:
- 500+ training examples
- 3-5 epochs
- GPU training for better convergence

---

## 6. Files Created 📁

### New Files

1. **`training/train_medical_lora_cpu.py`**
   - CPU-optimized training script
   - Removed 4-bit quantization (GPU-only feature)
   - Uses FP32 for CPU compatibility

2. **`training/test_model.py`**
   - Model inference testing script
   - Loads fine-tuned LoRA adapter
   - Tests medical Q&A scenarios

3. **`datasets/medical_training_clean.jsonl`**
   - Cleaned training dataset
   - Removed comment lines
   - Valid JSONL format

4. **`models/medical-lora-test/`**
   - Fine-tuned LoRA adapter
   - Configuration files
   - Tokenizer files

---

## 7. How to Use 🚀

### Run the Web Demo

```bash
cd /home/dszczepek/help-children/ai4se/demo
npx serve -l 8000
```

Visit: http://localhost:8000

### Train a New Model

```bash
cd /home/dszczepek/help-children/ai4se

# Activate Python environment
source /home/dszczepek/help-children/.venv/bin/activate

# Run training (CPU)
python training/train_medical_lora_cpu.py \
  --base_model "HuggingFaceTB/SmolLM2-135M-Instruct" \
  --dataset_path "datasets/medical_training_clean.jsonl" \
  --output_dir "models/medical-lora-new" \
  --num_train_epochs 3 \
  --per_device_train_batch_size 1 \
  --gradient_accumulation_steps 2 \
  --learning_rate 2e-4 \
  --max_seq_length 256 \
  --logging_steps 5 \
  --save_steps 50 \
  --lora_rank 8 \
  --lora_alpha 16 \
  --fp16 False \
  --report_to none
```

### Test Fine-Tuned Model

```bash
cd /home/dszczepek/help-children/ai4se

# Edit test_model.py to point to your model
python training/test_model.py
```

---

## 8. Next Steps 🎯

### Immediate Improvements

1. **Expand Dataset:**
   - Add 100+ medical Q&A examples
   - Cover diverse symptoms and conditions
   - Include emergency scenarios

2. **Improve Training:**
   - Train for 3-5 epochs
   - Use larger base model (1B-3B parameters)
   - Obtain GPU access for faster training

3. **Model Evaluation:**
   - Create evaluation metrics
   - Test on held-out medical cases
   - Get feedback from healthcare professionals

### Production Deployment

1. **Quantization:**
   - Convert to GGUF format (for llama.cpp)
   - Convert to WebLLM format (for browser)
   - Optimize for mobile devices

2. **Integration:**
   - Add voice input/output (Whisper + Piper)
   - Create mobile app (Android/iOS)
   - Offline-first PWA deployment

3. **Field Testing:**
   - Deploy to 20 Community Health Workers
   - Collect usage data and feedback
   - Iterate based on real-world needs

---

## 9. Resources 📚

### Documentation
- [AI4SE README](../README.md)
- [Implementation Guide](../docs/IMPLEMENTATION_GUIDE.md)
- [Amharic Language Support](../docs/AMHARIC_LANGUAGE_SUPPORT.md)

### Models
- Base: [SmolLM2-135M-Instruct](https://huggingface.co/HuggingFaceTB/SmolLM2-135M-Instruct)
- Alternative: [Llama-3.2-1B](https://huggingface.co/meta-llama/Llama-3.2-1B-Instruct)
- Alternative: [Phi-3-mini](https://huggingface.co/microsoft/Phi-3-mini-4k-instruct)

### Tools
- [Hugging Face Transformers](https://huggingface.co/docs/transformers)
- [PEFT Library](https://github.com/huggingface/peft)
- [WebLLM](https://webllm.mlc.ai/)

---

## 10. Troubleshooting 🔧

### Common Issues

**Issue:** CUDA not available  
**Solution:** Use CPU training script (`train_medical_lora_cpu.py`)

**Issue:** JSON parse error  
**Solution:** Remove comments from JSONL file with `grep -v "^#"`

**Issue:** Out of memory  
**Solution:** Reduce batch size, sequence length, or use smaller model

**Issue:** Slow training  
**Solution:** Use GPU, reduce epochs, or use smaller dataset for testing

---

## 11. Project Status 📊

### Completed ✅
- [x] Environment setup
- [x] Dependency installation
- [x] Demo server running
- [x] Training pipeline functional
- [x] Model fine-tuning complete
- [x] Basic testing implemented

### In Progress 🔄
- [ ] Expanding training dataset
- [ ] Multi-epoch training
- [ ] Model quantization for deployment
- [ ] Voice interface integration

### Planned 📅
- [ ] GPU training setup
- [ ] Production model training
- [ ] Mobile app development
- [ ] Field deployment in Ethiopia

---

## 12. Contact & Support 💬

**Project:** AI4SE - AI for Social Empowerment  
**Repository:** https://github.com/mniami/help-children  
**Purpose:** Local-first AI for resource-constrained environments  

**Maintainer:** Help Children Initiative  
**Focus:** Healthcare, Agriculture, Technical Skills  
**Impact:** Serving communities without internet access  

---

**Last Updated:** February 13, 2026  
**Version:** 0.1.0-alpha  

---

*"AI should empower everyone, not just those with internet and credit cards."*
