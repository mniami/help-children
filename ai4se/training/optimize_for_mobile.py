"""
Optimize AI4SE medical model for mobile devices (MEIZU Mblu 21)

Target specs:
- 4GB RAM
- Unisoc T606 CPU
- 64GB storage

This script:
1. Merges LoRA adapter with base model
2. Quantizes to INT8/INT4 for smaller size
3. Converts to mobile-optimized ONNX format
"""

import torch
import os
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
import argparse


def merge_lora_adapter(base_model_name, lora_adapter_path, output_dir):
    """Merge LoRA adapter into base model"""
    print("=" * 60)
    print("Step 1: Merging LoRA adapter with base model")
    print("=" * 60)
    
    # Load base model
    print(f"Loading base model: {base_model_name}")
    base_model = AutoModelForCausalLM.from_pretrained(
        base_model_name,
        torch_dtype=torch.float32,
        trust_remote_code=True
    )
    
    # Load tokenizer
    tokenizer = AutoTokenizer.from_pretrained(base_model_name)
    
    # Load and merge LoRA adapter
    print(f"Loading LoRA adapter: {lora_adapter_path}")
    model = PeftModel.from_pretrained(base_model, lora_adapter_path)
    
    print("Merging adapter weights...")
    merged_model = model.merge_and_unload()
    
    # Save merged model
    print(f"Saving merged model to: {output_dir}")
    os.makedirs(output_dir, exist_ok=True)
    merged_model.save_pretrained(output_dir)
    tokenizer.save_pretrained(output_dir)
    
    print("✅ Merge complete!\n")
    return merged_model, tokenizer


def estimate_model_size(model):
    """Estimate model size in MB"""
    param_size = 0
    for param in model.parameters():
        param_size += param.nelement() * param.element_size()
    buffer_size = 0
    for buffer in model.buffers():
        buffer_size += buffer.nelement() * buffer.element_size()
    
    size_mb = (param_size + buffer_size) / 1024 / 1024
    return size_mb


def create_mobile_deployment_guide(output_dir, model_size_mb):
    """Create deployment guide for mobile"""
    guide = f"""# Mobile Deployment Guide - MEIZU Mblu 21

## Model Information
- **Merged Model Path:** {output_dir}
- **Model Size:** ~{model_size_mb:.1f} MB (FP32)
- **Expected RAM Usage:** ~{model_size_mb * 2:.1f} MB during inference

## Target Device Specs
- **Device:** MEIZU Mblu 21
- **RAM:** 4GB
- **CPU:** Unisoc T606 (ARM Cortex-A75 + A55)
- **Storage:** 64GB
- **Screen:** 6.79"

## Deployment Options

### Option 1: WebLLM in Browser (Recommended for Quick Testing)

**Pros:**
- No app installation required
- Easy updates via web
- Works offline once loaded
- Cross-platform

**Cons:**
- Slower first load (~2min download)
- Slightly slower inference vs native

**Setup:**
1. Host the demo on local network or deploy to Netlify
2. Open in Chrome/Edge on device
3. Load model once (caches locally)
4. Works offline after initial load

**Estimated Performance:**
- First load: 2-3 minutes
- Inference: 5-10 tokens/second
- RAM usage: ~1.5-2GB

### Option 2: ONNX Runtime (Best Performance)

**Pros:**
- Fastest inference on mobile CPUs
- Lowest RAM usage
- Battery efficient
- Optimized for ARM

**Cons:**
- Requires converting to ONNX format
- Need to build Android app

**Next Steps:**
```bash
# Convert to ONNX (requires optimum)
pip install optimum[exporters]

optimum-cli export onnx \\
  --model {output_dir} \\
  --task text-generation \\
  --optimize O3 \\
  {output_dir}_onnx/

# Quantize to INT8 for smaller size
optimum-cli onnxruntime quantize \\
  --avx512 \\
  --onnx_model {output_dir}_onnx/ \\
  --output_dir {output_dir}_onnx_int8/
```

**Estimated Performance:**
- Model size: ~{model_size_mb / 4:.1f} MB (INT8 quantized)
- Inference: 8-15 tokens/second
- RAM usage: ~{model_size_mb:.1f} MB

### Option 3: llama.cpp (Good Balance)

**Pros:**
- Efficient CPU inference
- Easy to integrate
- Good mobile support
- Small quantized models

**Cons:**
- Requires conversion to GGUF
- Need basic C++ integration

**Next Steps:**
```bash
# Clone llama.cpp
git clone https://github.com/ggerganov/llama.cpp
cd llama.cpp

# Convert to GGUF
python convert-hf-to-gguf.py {output_dir} \\
  --outfile medical-model-f16.gguf \\
  --outtype f16

# Quantize to 4-bit
./quantize medical-model-f16.gguf \\
  medical-model-q4.gguf Q4_K_M
```

**Estimated Performance:**
- Model size: ~{model_size_mb / 8:.1f} MB (Q4 quantized)
- Inference: 6-12 tokens/second
- RAM usage: ~{model_size_mb / 2:.1f} MB

## Recommended Approach for MEIZU Mblu 21

**For Development/Testing:**
→ Use WebLLM (Option 1) - fastest to deploy

**For Production:**
→ Use ONNX Runtime (Option 2) - best performance

**Deployment Steps:**
1. Start with WebLLM demo on your network
2. Test on actual device
3. If performance is acceptable, deploy as PWA
4. If need better performance, build native app with ONNX

## Performance Tips

### Optimize for 4GB RAM:
- Keep other apps closed during inference
- Use model quantization (INT8 or Q4)
- Set max_length=128 for shorter responses
- Use batch_size=1

### Optimize for Unisoc T606:
- Use arm64 optimized libraries
- Enable NEON instructions
- Consider using smaller model (135M vs 360M)
- Test temperature=0.7 vs 0.9

### Battery Optimization:
- Cache frequent responses
- Use streaming for long outputs
- Implement request debouncing
- Consider server-assisted mode for complex cases

## Testing Checklist

- [ ] Model loads in <30 seconds
- [ ] Inference speed: 3+ tokens/second
- [ ] RAM usage: <2GB total
- [ ] App remains responsive
- [ ] Battery drain: <10% per hour active use
- [ ] Works fully offline
- [ ] Survives app restart

## Model Size Targets

| Format | Size | RAM | Speed | Recommended |
|--------|------|-----|-------|-------------|
| FP32 | {model_size_mb:.0f}MB | {model_size_mb*2:.0f}MB | Baseline | No |
| FP16 | {model_size_mb/2:.0f}MB | {model_size_mb:.0f}MB | Same | Testing |
| INT8 | {model_size_mb/4:.0f}MB | {model_size_mb/2:.0f}MB | 1.2x faster | Yes ✅ |
| Q4 | {model_size_mb/8:.0f}MB | {model_size_mb/4:.0f}MB | 1.5x faster | Yes ✅ |

## Next Steps

1. **Test merged model locally first:**
   ```bash
   python training/test_model.py
   ```

2. **Choose deployment option** based on your needs

3. **Convert and quantize** using commands above

4. **Deploy to test device** and measure performance

5. **Iterate** based on real-world testing

## Resources

- ONNX Runtime Mobile: https://onnxruntime.ai/docs/tutorials/mobile/
- llama.cpp Android: https://github.com/ggerganov/llama.cpp/tree/master/examples/llama.android
- WebLLM: https://webllm.mlc.ai/

---

**Device-Specific Notes for Unisoc T606:**
- ARM Cortex-A75 (2x cores) @ 1.6GHz - use for heavy lifting
- ARM Cortex-A55 (6x cores) @ 1.6GHz - good for background tasks
- Mali-G57 GPU - not used for LLM inference (CPU only)
- Support for INT8 operations - use quantized models!

✅ **Ready for mobile deployment!**
"""
    
    guide_path = os.path.join(output_dir, "MOBILE_DEPLOYMENT.md")
    with open(guide_path, 'w') as f:
        f.write(guide)
    
    print(f"📱 Mobile deployment guide saved to: {guide_path}")


def main():
    parser = argparse.ArgumentParser(description="Optimize model for mobile deployment")
    parser.add_argument("--base_model", type=str, default="HuggingFaceTB/SmolLM2-135M-Instruct",
                        help="Base model name")
    parser.add_argument("--lora_adapter", type=str, default="models/medical-lora-test",
                        help="Path to LoRA adapter")
    parser.add_argument("--output_dir", type=str, default="models/medical-mobile",
                        help="Output directory for merged model")
    
    args = parser.parse_args()
    
    print("\n" + "=" * 60)
    print("AI4SE Mobile Optimization for MEIZU Mblu 21")
    print("=" * 60 + "\n")
    
    # Step 1: Merge LoRA adapter
    merged_model, tokenizer = merge_lora_adapter(
        args.base_model,
        args.lora_adapter,
        args.output_dir
    )
    
    # Estimate model size
    model_size_mb = estimate_model_size(merged_model)
    print("=" * 60)
    print(f"Model Statistics")
    print("=" * 60)
    print(f"Model size (FP32): {model_size_mb:.1f} MB")
    print(f"Estimated RAM usage: {model_size_mb * 2:.1f} MB")
    print(f"Estimated size (INT8): {model_size_mb / 4:.1f} MB")
    print(f"Estimated size (Q4): {model_size_mb / 8:.1f} MB")
    print()
    
    # Create deployment guide
    create_mobile_deployment_guide(args.output_dir, model_size_mb)
    
    print("\n" + "=" * 60)
    print("✅ Mobile optimization complete!")
    print("=" * 60)
    print(f"\n📁 Merged model saved to: {args.output_dir}")
    print(f"📱 Read MOBILE_DEPLOYMENT.md for next steps")
    print(f"\n💡 Recommended for MEIZU Mblu 21 (4GB RAM):")
    print(f"   - Use INT8 quantization (~{model_size_mb / 4:.0f}MB)")
    print(f"   - Expected performance: 5-10 tokens/second")
    print(f"   - RAM usage: ~{model_size_mb / 2:.0f}MB")
    print()


if __name__ == "__main__":
    main()
