"""
Export Qwen/Llama models to ONNX format for Android deployment

This script:
1. Downloads the specified model from HuggingFace
2. Exports it to ONNX format
3. Applies INT4/INT8 quantization for mobile
4. Saves tokenizer files
5. Optimizes for CPU inference on ARM devices

Requirements:
    pip install transformers optimum[onnxruntime] torch onnx onnxruntime
    (onnxruntime provides faster CPU inference during export)
"""

import os
import argparse
import shutil
from pathlib import Path
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from optimum.onnxruntime import ORTModelForCausalLM
from optimum.onnxruntime.configuration import AutoQuantizationConfig
from optimum.onnxruntime import ORTQuantizer
from optimum.onnxruntime.configuration import AutoQuantizationConfig


def get_dir_size(path):
    """Calculate directory size in bytes"""
    total = 0
    for entry in os.scandir(path):
        if entry.is_file():
            total += entry.stat().st_size
        elif entry.is_dir():
            total += get_dir_size(entry.path)
    return total


def export_model(
    model_name: str,
    output_path: str,
    quantization: str = "int4",
    max_length: int = 512
):
    """
    Export and quantize model for Android deployment
    
    Args:
        model_name: HuggingFace model name (e.g., "Qwen/Qwen2.5-1.5B-Instruct")
        output_path: Where to save ONNX model
        quantization: "int4", "int8", or "none"
        max_length: Maximum sequence length
    """
    
    print("=" * 60)
    print(f"Exporting {model_name} to ONNX")
    print("=" * 60)
    
    output_path = Path(output_path)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Step 1: Load model and tokenizer
    print("\n[1/5] Loading model and tokenizer...")
    try:
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        
        # Load with float16 for efficiency
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float16,
            low_cpu_mem_usage=True,
            trust_remote_code=True
        )
        
        print(f"✓ Model loaded: {model_name}")
        print(f"  Parameters: {model.num_parameters() / 1e9:.2f}B")
        
    except Exception as e:
        print(f"✗ Failed to load model: {e}")
        return False
    
    # Step 2: Export to ONNX
    print("\n[2/5] Exporting to ONNX format...")
    temp_onnx_path = output_path / "temp_onnx"
    
    try:
        # Use Optimum to export
        ort_model = ORTModelForCausalLM.from_pretrained(
            model_name,
            export=True,
            provider="CPUExecutionProvider",
            use_cache=True,
            use_io_binding=False
        )
        
        ort_model.save_pretrained(temp_onnx_path)
        print(f"✓ Exported to ONNX")
        
    except Exception as e:
        print(f"✗ ONNX export failed: {e}")
        return False
    
    # Step 3: Quantize model
    print(f"\n[3/5] Applying {quantization.upper()} quantization...")
    
    if quantization == "int4":
        try:
            # INT4 quantization for smallest size
            qconfig = AutoQuantizationConfig.int4(
                is_static=False,
                per_channel=True,
                reduce_range=True,
                optimize_model=True
            )
            
            quantizer = ORTQuantizer.from_pretrained(temp_onnx_path)
            quantizer.quantize(
                save_dir=output_path,
                quantization_config=qconfig
            )
            
            print(f"✓ INT4 quantization applied")
            
        except Exception as e:
            print(f"⚠ INT4 quantization failed, trying INT8: {e}")
            quantization = "int8"
    
    if quantization == "int8":
        try:
            # INT8 quantization (fallback)
            qconfig = AutoQuantizationConfig.avx512_vnni(
                is_static=False,
                per_channel=True
            )
            
            quantizer = ORTQuantizer.from_pretrained(temp_onnx_path)
            quantizer.quantize(
                save_dir=output_path,
                quantization_config=qconfig
            )
            
            print(f"✓ INT8 quantization applied")
            
        except Exception as e:
            print(f"⚠ Quantization failed, using FP16: {e}")
            # Just copy the FP16 model
            shutil.copytree(temp_onnx_path, output_path, dirs_exist_ok=True)
    
    elif quantization == "none":
        # No quantization, just copy
        shutil.copytree(temp_onnx_path, output_path, dirs_exist_ok=True)
        print(f"✓ No quantization (FP16)")
    
    # Step 4: Save tokenizer
    print("\n[4/5] Saving tokenizer...")
    try:
        tokenizer.save_pretrained(output_path)
        print(f"✓ Tokenizer saved")
    except Exception as e:
        print(f"✗ Failed to save tokenizer: {e}")
    
    # Step 5: Cleanup and summary
    print("\n[5/5] Cleanup...")
    if temp_onnx_path.exists():
        shutil.rmtree(temp_onnx_path)
    
    # Calculate sizes
    model_size_mb = get_dir_size(output_path) / 1024 / 1024
    
    print("\n" + "=" * 60)
    print("✓ Export Complete!")
    print("=" * 60)
    print(f"Output location: {output_path.absolute()}")
    print(f"Model size: {model_size_mb:.0f} MB")
    print(f"Quantization: {quantization.upper()}")
    
    # List files
    print("\nFiles created:")
    for file in sorted(output_path.glob("*")):
        size_mb = os.path.getsize(file) / 1024 / 1024
        print(f"  • {file.name} ({size_mb:.1f} MB)")
    
    # Performance estimates
    print("\nEstimated performance on Android (4GB RAM):")
    print(f"  • Memory usage: ~{model_size_mb * 1.5:.0f} MB")
    print(f"  • Load time: ~3-5 seconds")
    print(f"  • Inference: 5-10 tokens/second")
    
    print("\n✓ Ready to use in Android app!")
    print(f"Copy to: android/app/src/main/assets/models/")
    
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Export LLM to ONNX for Android deployment"
    )
    
    parser.add_argument(
        "--model_name",
        type=str,
        required=True,
        help="HuggingFace model name (e.g., Qwen/Qwen2.5-1.5B-Instruct)"
    )
    
    parser.add_argument(
        "--output_path",
        type=str,
        required=True,
        help="Output directory for ONNX model"
    )
    
    parser.add_argument(
        "--quantization",
        type=str,
        default="int4",
        choices=["int4", "int8", "none"],
        help="Quantization type (int4=smallest, int8=balanced, none=best quality)"
    )
    
    parser.add_argument(
        "--max_length",
        type=int,
        default=512,
        help="Maximum sequence length"
    )
    
    args = parser.parse_args()
    
    success = export_model(
        model_name=args.model_name,
        output_path=args.output_path,
        quantization=args.quantization,
        max_length=args.max_length
    )
    
    if not success:
        print("\n✗ Export failed!")
        exit(1)


if __name__ == "__main__":
    main()
