"""
Model Quantization Script for AI4SE

This script converts and quantizes models for deployment on resource-constrained devices.
Supports multiple quantization formats and frameworks.

Requirements:
    pip install torch transformers optimum onnx onnxruntime

    # For llama.cpp conversion
    git clone https://github.com/ggerganov/llama.cpp
    cd llama.cpp && make
"""

import os
import argparse
import subprocess
from pathlib import Path


def quantize_to_gguf(model_path, output_path, quant_type="Q4_K_M"):
    """
    Quantize model to GGUF format using llama.cpp

    Args:
        model_path: Path to Hugging Face model
        output_path: Output path for quantized model
        quant_type: Quantization type (Q4_K_M, Q4_K_S, Q5_K_M, Q6_K, Q2_K)
    """
    print(f"Quantizing to GGUF format ({quant_type})...")

    # Temporary FP16 GGUF path
    fp16_path = output_path.replace('.gguf', '-fp16.gguf')

    # Step 1: Convert to FP16 GGUF
    print("Step 1: Converting to FP16 GGUF...")
    subprocess.run([
        'python', 'llama.cpp/convert-hf-to-gguf.py',
        model_path,
        '--outfile', fp16_path,
        '--outtype', 'f16'
    ], check=True)

    # Step 2: Quantize
    print(f"Step 2: Quantizing to {quant_type}...")
    subprocess.run([
        'llama.cpp/quantize',
        fp16_path,
        output_path,
        quant_type
    ], check=True)

    # Clean up FP16 file
    if os.path.exists(fp16_path):
        os.remove(fp16_path)
        print(f"Cleaned up temporary file: {fp16_path}")

    file_size_gb = os.path.getsize(output_path) / (1024**3)
    print(f"✅ Quantization complete! File size: {file_size_gb:.2f} GB")
    print(f"Saved to: {output_path}")


def quantize_to_onnx(model_path, output_path, quant_bits=4):
    """
    Quantize model to ONNX format

    Args:
        model_path: Path to Hugging Face model
        output_path: Output directory for ONNX model
        quant_bits: Quantization bits (4 or 8)
    """
    print(f"Quantizing to ONNX INT{quant_bits}...")

    from optimum.onnxruntime import ORTModelForCausalLM
    from optimum.onnxruntime.configuration import AutoQuantizationConfig
    from transformers import AutoTokenizer

    # Step 1: Export to ONNX
    print("Step 1: Exporting to ONNX...")
    model = ORTModelForCausalLM.from_pretrained(
        model_path,
        export=True
    )

    # Step 2: Quantize
    print(f"Step 2: Quantizing to INT{quant_bits}...")
    if quant_bits == 4:
        qconfig = AutoQuantizationConfig.arm64(is_static=False, per_channel=False)
    else:  # 8-bit
        qconfig = AutoQuantizationConfig.avx512_vnni(is_static=False, per_channel=True)

    model.quantize(
        save_directory=output_path,
        quantization_config=qconfig
    )

    # Save tokenizer
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    tokenizer.save_pretrained(output_path)

    print(f"✅ ONNX quantization complete!")
    print(f"Saved to: {output_path}")


def quantize_to_webllm(model_path, output_path, quant_type="q4f16_1"):
    """
    Quantize model for WebLLM (WebGPU)

    Args:
        model_path: Path to Hugging Face model
        output_path: Output directory for WebLLM model
        quant_type: Quantization type (q4f16_1, q4f32_1, q0f16, q0f32)
    """
    print(f"Quantizing for WebLLM ({quant_type})...")

    # Compile model for WebGPU
    subprocess.run([
        'mlc_llm', 'compile',
        model_path,
        '--quantization', quant_type,
        '--target', 'webgpu',
        '-o', output_path
    ], check=True)

    # Generate config
    subprocess.run([
        'mlc_llm', 'gen_config',
        model_path,
        '--quantization', quant_type,
        '--conv-template', 'llama-3',
        '-o', output_path
    ], check=True)

    print(f"✅ WebLLM compilation complete!")
    print(f"Saved to: {output_path}")


def benchmark_model(model_path, model_type="gguf"):
    """
    Benchmark quantized model performance

    Args:
        model_path: Path to quantized model
        model_type: Type of model (gguf, onnx, webllm)
    """
    print(f"Benchmarking model: {model_path}")

    if model_type == "gguf":
        # Benchmark with llama.cpp
        subprocess.run([
            'llama.cpp/main',
            '-m', model_path,
            '-p', 'You are a medical assistant. A patient says: "My child has fever." Provide guidance.',
            '-n', '100',
            '--temp', '0.7'
        ], check=True)

    elif model_type == "onnx":
        print("ONNX benchmarking not implemented in this script.")
        print("Use onnxruntime Python API for benchmarking.")

    elif model_type == "webllm":
        print("WebLLM benchmarking requires browser environment.")
        print("Open demo/index.html to test.")


def main():
    parser = argparse.ArgumentParser(
        description="Quantize models for AI4SE deployment"
    )

    parser.add_argument(
        '--model',
        type=str,
        required=True,
        help='Path to Hugging Face model or model ID'
    )

    parser.add_argument(
        '--output',
        type=str,
        required=True,
        help='Output path for quantized model'
    )

    parser.add_argument(
        '--format',
        type=str,
        choices=['gguf', 'onnx', 'webllm', 'all'],
        default='gguf',
        help='Output format (default: gguf)'
    )

    parser.add_argument(
        '--quant-type',
        type=str,
        default='Q4_K_M',
        help='Quantization type (for GGUF: Q4_K_M, Q4_K_S, Q5_K_M, Q6_K, Q2_K; for ONNX: 4 or 8)'
    )

    parser.add_argument(
        '--benchmark',
        action='store_true',
        help='Run benchmark after quantization'
    )

    args = parser.parse_args()

    # Create output directory
    os.makedirs(os.path.dirname(args.output) if os.path.dirname(args.output) else '.', exist_ok=True)

    # Quantize based on format
    if args.format == 'gguf' or args.format == 'all':
        gguf_output = args.output if args.output.endswith('.gguf') else f"{args.output}.gguf"
        quantize_to_gguf(args.model, gguf_output, args.quant_type)

        if args.benchmark:
            benchmark_model(gguf_output, 'gguf')

    if args.format == 'onnx' or args.format == 'all':
        onnx_output = args.output.replace('.gguf', '-onnx') if args.output.endswith('.gguf') else f"{args.output}-onnx"
        quant_bits = int(args.quant_type) if args.quant_type in ['4', '8'] else 4
        quantize_to_onnx(args.model, onnx_output, quant_bits)

        if args.benchmark:
            benchmark_model(onnx_output, 'onnx')

    if args.format == 'webllm' or args.format == 'all':
        webllm_output = args.output.replace('.gguf', '-webllm') if args.output.endswith('.gguf') else f"{args.output}-webllm"
        webllm_quant = 'q4f16_1' if args.quant_type.startswith('Q4') else 'q0f16'
        quantize_to_webllm(args.model, webllm_output, webllm_quant)

        if args.benchmark:
            benchmark_model(webllm_output, 'webllm')

    print("\n" + "="*80)
    print("📊 Quantization Summary")
    print("="*80)
    print(f"Model: {args.model}")
    print(f"Format: {args.format}")
    print(f"Output: {args.output}")
    print("\nNext steps:")
    print("1. Test the quantized model")
    print("2. Compare quality vs original model")
    print("3. Deploy to target devices")
    print("="*80)


if __name__ == "__main__":
    main()


"""
Usage Examples:

# Quantize to GGUF (Q4, recommended)
python quantize_model.py \
  --model meta-llama/Llama-3.2-3B-Instruct \
  --output models/llama-3.2-3b-q4.gguf \
  --format gguf \
  --quant-type Q4_K_M \
  --benchmark

# Quantize to ONNX (INT4)
python quantize_model.py \
  --model meta-llama/Llama-3.2-3B-Instruct \
  --output models/llama-3.2-3b-onnx \
  --format onnx \
  --quant-type 4

# Quantize for WebLLM
python quantize_model.py \
  --model meta-llama/Llama-3.2-3B-Instruct \
  --output models/llama-3.2-3b-webllm \
  --format webllm \
  --quant-type q4f16_1

# Quantize to all formats
python quantize_model.py \
  --model meta-llama/Llama-3.2-3B-Instruct \
  --output models/llama-3.2-3b \
  --format all \
  --benchmark
"""
