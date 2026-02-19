# AI4SE Implementation Guide

## Technical Implementation for Local-First AI

This guide provides detailed steps to implement Local-First AI models for social empowerment in resource-constrained environments.

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Architecture Overview](#architecture-overview)
3. [Model Selection & Preparation](#model-selection--preparation)
4. [Quantization & Optimization](#quantization--optimization)
5. [Deployment Options](#deployment-options)
6. [Testing & Validation](#testing--validation)
7. [Performance Optimization](#performance-optimization)
8. [Troubleshooting](#troubleshooting)

---

## Quick Start

### Prerequisites

- **Development Machine**:
  - 16+ GB RAM
  - NVIDIA GPU with 8+ GB VRAM (for training/quantization)
  - Ubuntu 20.04+ or macOS

- **Target Devices**:
  - Android 8+ with 3+ GB RAM
  - iOS 12+ with 3+ GB RAM
  - Modern browser with WebGPU support

### 5-Minute Demo

```bash
# Clone the repository
git clone https://github.com/mniami/help-children.git
cd help-children/ai4se

# Serve the demo locally
npx serve demo

# Open browser to http://localhost:3000
# Click "Load Model" and wait for download (~2 GB)
# Start chatting with the AI!
```

---

## Architecture Overview

### System Layers

```
┌─────────────────────────────────────────────────────┐
│                User Interface Layer                 │
│  - Progressive Web App (PWA)                        │
│  - Voice Input/Output (optional)                    │
│  - Photo Capture & Display                          │
└───────────────────┬─────────────────────────────────┘
                    │
┌───────────────────▼─────────────────────────────────┐
│              Application Logic Layer                │
│  - Conversation Management                          │
│  - Context Handling                                 │
│  - Response Formatting                              │
└───────────────────┬─────────────────────────────────┘
                    │
┌───────────────────▼─────────────────────────────────┐
│              Inference Engine Layer                 │
│  - WebLLM (Browser: WebGPU acceleration)            │
│  - ONNX Runtime (Native: DirectML/CoreML)           │
│  - llama.cpp (CLI/Server)                           │
└───────────────────┬─────────────────────────────────┘
                    │
┌───────────────────▼─────────────────────────────────┐
│                 Model Layer                         │
│  - Quantized LLM (1-3 GB)                           │
│  - LoRA Adapters (50-200 MB)                        │
│  - Tokenizer & Config                               │
└─────────────────────────────────────────────────────┘
```

### Data Flow

```
User Input → Tokenization → Model Inference → Detokenization → UI Display
     ↑                                                              ↓
     └──────────────── Conversation History ────────────────────────┘
```

---

## Model Selection & Preparation

### Step 1: Choose Base Model

**Criteria**:
- Parameter count: 1-8B (fits in mobile RAM)
- License: Permissive (Apache 2.0, MIT)
- Multi-lingual support (if needed)
- Performance on target tasks

**Recommended Models**:

| Model | Size | Parameters | License | Best For |
|-------|------|-----------|---------|----------|
| Llama-3.2-1B | 0.6 GB (Q4) | 1.2B | Llama 3.2 License | Low-end devices |
| Llama-3.2-3B | 1.9 GB (Q4) | 3.2B | Llama 3.2 License | General use |
| Phi-3-mini | 2.3 GB (Q4) | 3.8B | MIT | Instruction following |
| Phi-3-medium | 4.5 GB (Q4) | 7B | MIT | High accuracy |
| Gemma-2-2B | 1.2 GB (Q4) | 2B | Gemma License | Efficient |

### Step 2: Download Base Model

```bash
# Using Hugging Face CLI
pip install huggingface-hub

# Login (if model requires authentication)
huggingface-cli login

# Download model
huggingface-cli download \
  meta-llama/Llama-3.2-3B-Instruct \
  --local-dir ./models/llama-3.2-3b-instruct
```

### Step 3: Evaluate Base Model

```python
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

# Load model
model_name = "meta-llama/Llama-3.2-3B-Instruct"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype=torch.float16,
    device_map="auto"
)

# Test prompt
prompt = """You are a medical assistant. A patient says:
"My child has fever and diarrhea for 3 days."

Provide initial assessment and guidance."""

inputs = tokenizer(prompt, return_tensors="pt").to("cuda")
outputs = model.generate(
    **inputs,
    max_new_tokens=512,
    temperature=0.7,
    do_sample=True
)

response = tokenizer.decode(outputs[0], skip_special_tokens=True)
print(response)
```

---

## Quantization & Optimization

### Option A: Using llama.cpp (Recommended)

**Advantages**:
- Excellent performance on CPU
- Easy to use
- Supports many quantization formats
- Cross-platform (Windows, macOS, Linux, Android, iOS)

**Installation**:
```bash
# Clone llama.cpp
git clone https://github.com/ggerganov/llama.cpp.git
cd llama.cpp

# Build (with GPU support if available)
make LLAMA_CUDA=1  # NVIDIA GPU
# OR
make LLAMA_METAL=1  # Apple Silicon
# OR
make  # CPU only

# Install Python bindings
pip install llama-cpp-python
```

**Convert Model**:
```bash
# 1. Convert Hugging Face model to GGUF format
python convert-hf-to-gguf.py \
  ./models/llama-3.2-3b-instruct \
  --outfile ./models/llama-3.2-3b-instruct-f16.gguf \
  --outtype f16

# 2. Quantize to 4-bit (Q4_K_M is recommended)
./quantize \
  ./models/llama-3.2-3b-instruct-f16.gguf \
  ./models/llama-3.2-3b-instruct-q4.gguf \
  Q4_K_M

# Result: ~1.9 GB file
```

**Quantization Formats**:

| Format | Size Reduction | Quality | Speed | Use Case |
|--------|---------------|---------|-------|----------|
| Q4_K_M | 75% | Excellent | Fast | Recommended |
| Q4_K_S | 77% | Very Good | Faster | Low memory |
| Q5_K_M | 68% | Excellent | Medium | High quality |
| Q6_K | 50% | Best | Slower | Maximum quality |
| Q2_K | 87% | Good | Fastest | Minimal memory |

**Test Quantized Model**:
```bash
# Interactive mode
./main \
  -m ./models/llama-3.2-3b-instruct-q4.gguf \
  -p "You are a medical assistant. A patient says: 'My child has fever.' Provide guidance." \
  --temp 0.7 \
  --repeat-penalty 1.1 \
  -n 512
```

### Option B: Using WebLLM (Browser Deployment)

**Installation**:
```bash
# Install MLC LLM
pip install mlc-llm mlc-ai-nightly

# Install WebLLM package
npm install @mlc-ai/web-llm
```

**Convert Model**:
```bash
# 1. Clone WebLLM config repo
git clone https://github.com/mlc-ai/mlc-llm.git
cd mlc-llm

# 2. Compile model for WebGPU
mlc_llm compile \
  ./models/llama-3.2-3b-instruct \
  --quantization q4f16_1 \
  --target webgpu \
  -o ./dist/llama-3.2-3b-q4-webgpu

# 3. Generate model config
mlc_llm gen_config \
  ./models/llama-3.2-3b-instruct \
  --quantization q4f16_1 \
  --conv-template llama-3 \
  -o ./dist/llama-3.2-3b-q4-webgpu/

# Result: WebGPU-optimized model (~1.9 GB)
```

**Host Model Files**:
```bash
# Option 1: Local development
npx serve dist/llama-3.2-3b-q4-webgpu

# Option 2: Deploy to CDN
# Upload to: Cloudflare R2, AWS S3, or GitHub Pages
```

### Option C: Using ONNX Runtime (Native Apps)

**Installation**:
```bash
pip install onnx onnxruntime-gpu optimum
```

**Convert & Quantize**:
```python
from optimum.onnxruntime import ORTModelForCausalLM
from optimum.onnxruntime.configuration import AutoQuantizationConfig
from transformers import AutoTokenizer

model_name = "meta-llama/Llama-3.2-3B-Instruct"

# 1. Export to ONNX
model = ORTModelForCausalLM.from_pretrained(
    model_name,
    export=True,
    provider="CUDAExecutionProvider"
)

# 2. Quantize to INT4
qconfig = AutoQuantizationConfig.arm64(is_static=False, per_channel=False)
model.quantize(
    save_directory="./models/llama-3.2-3b-instruct-onnx-q4",
    quantization_config=qconfig
)

# Save tokenizer
tokenizer = AutoTokenizer.from_pretrained(model_name)
tokenizer.save_pretrained("./models/llama-3.2-3b-instruct-onnx-q4")

print("✅ Model exported and quantized!")
```

---

## Fine-Tuning for Domain Specialization

### Prepare Dataset

**Format** (JSONL):
```json
{"messages": [
  {"role": "system", "content": "You are a medical assistant for primary health diagnosis in rural areas."},
  {"role": "user", "content": "My child has fever and diarrhea for 3 days. What should I do?"},
  {"role": "assistant", "content": "I understand your concern. Let me ask a few questions to assess the situation:\n\n1. How high is the fever? (approximate temperature)\n2. Is your child drinking water or breastfeeding?\n3. Are there signs of dehydration (dry mouth, no tears, sunken eyes)?\n\nBased on the symptoms you described, this could be acute gastroenteritis. Here are immediate steps:\n\n**IMMEDIATE ACTIONS:**\n1. Give Oral Rehydration Solution (ORS)\n   Recipe: 1 liter clean water + 6 teaspoons sugar + 1/2 teaspoon salt\n2. Continue breastfeeding if infant\n3. Offer small amounts of water frequently\n4. Monitor for dehydration signs\n\n**SEEK MEDICAL HELP IF:**\n- Child cannot drink\n- Vomiting increases\n- Fever above 39°C for more than 48 hours\n- Blood in stool\n- No urination for 8+ hours\n\nThe nearest health clinic is typically located at the center of your community. If symptoms worsen, seek immediate medical attention."}
]}
```

**Dataset Size**:
- Minimum: 100 examples per domain
- Recommended: 500-1,000 examples
- Optimal: 5,000+ examples

**Example Dataset Creation Script**:
```python
import json

medical_examples = [
    {
        "messages": [
            {"role": "system", "content": "You are a medical assistant for primary health diagnosis in rural areas."},
            {"role": "user", "content": "My child has fever and diarrhea for 3 days. What should I do?"},
            {"role": "assistant", "content": "I understand your concern. Let me assess the situation...[detailed response]"}
        ]
    },
    # Add more examples...
]

with open('medical_training_data.jsonl', 'w') as f:
    for example in medical_examples:
        f.write(json.dumps(example) + '\n')
```

### Fine-Tune with LoRA

**Installation**:
```bash
pip install peft transformers accelerate bitsandbytes
```

**Training Script**:
```python
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling
)
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from datasets import load_dataset
import torch

# 1. Load base model in 4-bit
model_name = "meta-llama/Llama-3.2-3B-Instruct"

model = AutoModelForCausalLM.from_pretrained(
    model_name,
    load_in_4bit=True,
    torch_dtype=torch.float16,
    device_map="auto"
)

tokenizer = AutoTokenizer.from_pretrained(model_name)
tokenizer.pad_token = tokenizer.eos_token

# 2. Prepare model for training
model = prepare_model_for_kbit_training(model)

# 3. Configure LoRA
lora_config = LoraConfig(
    r=16,  # Rank
    lora_alpha=32,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM"
)

model = get_peft_model(model, lora_config)
model.print_trainable_parameters()  # Should be ~1-2% of total

# 4. Load training data
dataset = load_dataset('json', data_files='medical_training_data.jsonl')

def tokenize_function(examples):
    return tokenizer(examples['text'], truncation=True, max_length=512)

tokenized_dataset = dataset.map(tokenize_function, batched=True)

# 5. Training arguments
training_args = TrainingArguments(
    output_dir="./models/llama-3.2-3b-medical-lora",
    per_device_train_batch_size=4,
    gradient_accumulation_steps=4,
    num_train_epochs=3,
    learning_rate=2e-4,
    fp16=True,
    logging_steps=10,
    save_steps=100,
    save_total_limit=3,
    optim="paged_adamw_8bit"
)

# 6. Train
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset["train"],
    data_collator=DataCollatorForLanguageModeling(tokenizer, mlm=False)
)

trainer.train()

# 7. Save LoRA adapter (only ~50-200 MB!)
model.save_pretrained("./models/llama-3.2-3b-medical-lora")
tokenizer.save_pretrained("./models/llama-3.2-3b-medical-lora")

print("✅ Fine-tuning complete!")
```

**Merge LoRA with Base Model**:
```python
from peft import PeftModel

# Load base model
base_model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype=torch.float16,
    device_map="auto"
)

# Load and merge LoRA
model = PeftModel.from_pretrained(base_model, "./models/llama-3.2-3b-medical-lora")
model = model.merge_and_unload()

# Save merged model
model.save_pretrained("./models/llama-3.2-3b-medical-merged")
tokenizer.save_pretrained("./models/llama-3.2-3b-medical-merged")

print("✅ LoRA merged with base model!")
```

---

## Deployment Options

### Option 1: Progressive Web App (PWA)

**Advantages**:
- No app store approval needed
- Instant updates
- Cross-platform (Android, iOS, Desktop)
- Offline-first architecture

**Implementation**:

1. **Create manifest.json**:
```json
{
  "name": "AI4SE Health Assistant",
  "short_name": "AI4SE",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#ffffff",
  "theme_color": "#2E7D32",
  "icons": [
    {
      "src": "/icons/icon-192.png",
      "sizes": "192x192",
      "type": "image/png"
    },
    {
      "src": "/icons/icon-512.png",
      "sizes": "512x512",
      "type": "image/png"
    }
  ],
  "description": "Offline AI-powered health assistant",
  "categories": ["health", "medical", "education"],
  "orientation": "portrait"
}
```

2. **Create service-worker.js**:
```javascript
const CACHE_NAME = 'ai4se-v1';
const STATIC_ASSETS = [
  '/',
  '/index.html',
  '/styles.css',
  '/app.js',
  '/manifest.json'
];

// Install event - cache static assets
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(STATIC_ASSETS))
  );
});

// Fetch event - serve from cache, fallback to network
self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request)
      .then(response => {
        if (response) {
          return response;  // Cache hit
        }
        return fetch(event.request)  // Cache miss
          .then(response => {
            // Cache successful responses
            if (response.ok) {
              const clone = response.clone();
              caches.open(CACHE_NAME)
                .then(cache => cache.put(event.request, clone));
            }
            return response;
          });
      })
  );
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames
          .filter(name => name !== CACHE_NAME)
          .map(name => caches.delete(name))
      );
    })
  );
});
```

3. **Register service worker in index.html**:
```html
<script>
  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('/service-worker.js')
      .then(reg => console.log('Service Worker registered', reg))
      .catch(err => console.log('Service Worker registration failed', err));
  }
</script>
```

4. **Deploy**:
```bash
# Option A: GitHub Pages (Free)
git add .
git commit -m "Deploy PWA"
git push origin main
# Enable GitHub Pages in repository settings

# Option B: Netlify (Free)
npm install -g netlify-cli
netlify deploy --prod

# Option C: Vercel (Free)
npm install -g vercel
vercel --prod
```

### Option 2: Native Android App

**Using React Native**:

1. **Initialize project**:
```bash
npx react-native init AI4SEHealth
cd AI4SEHealth
```

2. **Install dependencies**:
```bash
npm install @react-native-community/async-storage
npm install react-native-fs
```

3. **Integrate ONNX Runtime**:
```bash
# Add to android/app/build.gradle
dependencies {
    implementation 'com.microsoft.onnxruntime:onnxruntime-android:1.16.0'
}
```

4. **Load model**:
```javascript
import RNFS from 'react-native-fs';
import { InferenceSession } from 'onnxruntime-react-native';

async function loadModel() {
  // Copy model from assets to app directory
  const modelPath = `${RNFS.DocumentDirectoryPath}/model.onnx`;

  // Download or copy from assets
  await RNFS.downloadFile({
    fromUrl: 'https://cdn.ai4se.org/models/llama-3.2-3b-medical-q4.onnx',
    toFile: modelPath
  }).promise;

  // Create inference session
  const session = await InferenceSession.create(modelPath);

  return session;
}
```

### Option 3: Native iOS App

**Using Swift + ONNX Runtime**:

1. **Add ONNX Runtime to Podfile**:
```ruby
pod 'onnxruntime-mobile-objc', '~> 1.16.0'
```

2. **Load and run model**:
```swift
import onnxruntime_mobile_objc

class AIModel {
    var session: ORTSession?

    func loadModel() throws {
        guard let modelPath = Bundle.main.path(forResource: "model", ofType: "onnx") else {
            throw NSError(domain: "Model not found", code: -1)
        }

        let env = try ORTEnv(loggingLevel: .warning)
        let options = try ORTSessionOptions()
        session = try ORTSession(env: env, modelPath: modelPath, sessionOptions: options)
    }

    func runInference(input: String) throws -> String {
        // Tokenize input
        let tokens = tokenize(input)

        // Create input tensor
        let inputData = ORTValue(tensorData: NSMutableData(bytes: tokens, length: tokens.count * MemoryLayout<Int64>.size))

        // Run inference
        let outputs = try session!.run(withInputs: ["input_ids": inputData], outputNames: ["output"], runOptions: nil)

        // Decode output
        let result = decode(outputs["output"]!)
        return result
    }
}
```

---

## Testing & Validation

### Performance Benchmarks

**Test Script** (llama.cpp):
```bash
#!/bin/bash

MODEL="./models/llama-3.2-3b-instruct-q4.gguf"

echo "=== Performance Benchmark ==="
echo ""

# Test 1: Speed (tokens/second)
echo "Test 1: Generation Speed"
time ./main -m $MODEL \
  -p "You are a medical assistant." \
  -n 100 \
  --temp 0.7 \
  2>&1 | grep "eval time"

# Test 2: Memory usage
echo ""
echo "Test 2: Memory Usage"
/usr/bin/time -v ./main -m $MODEL \
  -p "Test prompt" \
  -n 50 \
  2>&1 | grep "Maximum resident set size"

# Test 3: Latency (first token)
echo ""
echo "Test 3: First Token Latency"
./main -m $MODEL \
  -p "Test" \
  -n 1 \
  --log-disable \
  2>&1 | grep "prompt eval time"
```

**Expected Performance**:

| Device | Model | Speed (tok/s) | Memory | First Token |
|--------|-------|---------------|--------|-------------|
| iPhone 14 Pro | Llama-3.2-3B Q4 | 15-20 | 2.5 GB | 500ms |
| Samsung A54 | Llama-3.2-3B Q4 | 8-12 | 2.5 GB | 800ms |
| MacBook M2 | Llama-3.2-3B Q4 | 40-50 | 2.5 GB | 200ms |
| Desktop RTX 3060 | Llama-3.2-3B Q4 | 80-100 | 3.0 GB | 100ms |

### Quality Evaluation

**Medical Domain Test Set**:
```python
test_cases = [
    {
        "input": "My child has fever and diarrhea for 3 days",
        "expected_keywords": ["dehydration", "ORS", "medical", "symptoms"],
        "expected_actions": ["questions", "immediate_actions", "warning_signs"]
    },
    {
        "input": "I have chest pain and shortness of breath",
        "expected_keywords": ["emergency", "urgent", "hospital", "heart"],
        "expected_severity": "high"
    },
    # Add more test cases...
]

def evaluate_response(model, test_case):
    response = model.generate(test_case["input"])

    # Check for expected keywords
    keyword_score = sum(
        kw.lower() in response.lower()
        for kw in test_case["expected_keywords"]
    ) / len(test_case["expected_keywords"])

    # Check for appropriate severity
    contains_emergency = any(
        word in response.lower()
        for word in ["emergency", "urgent", "immediately", "911"]
    )

    print(f"Input: {test_case['input']}")
    print(f"Keyword Score: {keyword_score:.2%}")
    print(f"Emergency Detection: {contains_emergency}")
    print(f"Response: {response[:200]}...")
    print("-" * 80)

# Run evaluation
for test in test_cases:
    evaluate_response(model, test)
```

---

## Performance Optimization

### 1. Model Sharding (Large Models)

Split model across multiple files for faster loading:

```python
# Split large model into chunks
def shard_model(model_path, shard_size_mb=500):
    import os

    file_size = os.path.getsize(model_path)
    shard_size = shard_size_mb * 1024 * 1024
    num_shards = (file_size + shard_size - 1) // shard_size

    with open(model_path, 'rb') as f:
        for i in range(num_shards):
            shard_data = f.read(shard_size)
            shard_path = f"{model_path}.shard{i:02d}"
            with open(shard_path, 'wb') as shard_file:
                shard_file.write(shard_data)
            print(f"Created {shard_path}")

# Load sharded model
def load_sharded_model(base_path):
    import glob

    shards = sorted(glob.glob(f"{base_path}.shard*"))

    with open(base_path, 'wb') as output:
        for shard in shards:
            with open(shard, 'rb') as f:
                output.write(f.read())

    return load_model(base_path)
```

### 2. KV-Cache Optimization

Reduce memory usage for longer conversations:

```python
# llama.cpp command
./main -m model.gguf \
  --ctx-size 2048 \    # Context window
  --n-gpu-layers 32 \  # Offload to GPU
  --mlock \            # Lock model in RAM
  --no-mmap \          # Don't use memory mapping
  --keep 512           # Keep only recent tokens in cache
```

### 3. Batch Processing

Process multiple requests efficiently:

```python
# ONNX Runtime batch inference
import onnxruntime as ort

session = ort.InferenceSession("model.onnx")

# Batch of inputs
inputs = [
    "Patient 1 symptoms...",
    "Patient 2 symptoms...",
    "Patient 3 symptoms..."
]

# Tokenize batch
tokenized = tokenizer(inputs, padding=True, truncation=True, return_tensors="np")

# Run batch inference
outputs = session.run(
    None,
    {
        "input_ids": tokenized["input_ids"],
        "attention_mask": tokenized["attention_mask"]
    }
)

# Decode batch
responses = tokenizer.batch_decode(outputs[0], skip_special_tokens=True)
```

---

## Troubleshooting

### Issue: Model fails to load in browser

**Symptoms**: "Failed to compile shader" or "WebGPU not supported"

**Solutions**:
1. Check browser version (Chrome 113+, Edge 113+)
2. Enable WebGPU flags:
   - Navigate to `chrome://flags`
   - Enable "Unsafe WebGPU"
   - Restart browser
3. Check GPU compatibility:
   ```javascript
   if (!navigator.gpu) {
     alert('WebGPU not supported. Please use Chrome 113+ or Edge 113+');
   }
   ```

### Issue: Out of memory on mobile device

**Symptoms**: App crashes during model loading

**Solutions**:
1. Use smaller model (Llama-3.2-1B instead of 3B)
2. Use more aggressive quantization (Q2 instead of Q4)
3. Clear browser cache before loading
4. Close other apps to free RAM

```javascript
// Check available memory
if (navigator.deviceMemory) {
  console.log(`Device RAM: ${navigator.deviceMemory} GB`);
  if (navigator.deviceMemory < 4) {
    // Use lighter model
    selectedModel = "Llama-3.2-1B-Instruct-q2";
  }
}
```

### Issue: Slow inference speed

**Symptoms**: <5 tokens/second on decent hardware

**Solutions**:
1. Enable GPU acceleration:
   ```bash
   # llama.cpp with CUDA
   ./main -m model.gguf --n-gpu-layers 99
   ```

2. Reduce context size:
   ```bash
   ./main -m model.gguf --ctx-size 512  # Instead of 2048
   ```

3. Use flash attention (if supported):
   ```python
   from transformers import AutoModelForCausalLM

   model = AutoModelForCausalLM.from_pretrained(
       model_name,
       attn_implementation="flash_attention_2"
   )
   ```

### Issue: Poor response quality

**Symptoms**: Irrelevant or nonsensical responses

**Solutions**:
1. Check prompt format:
   ```python
   # Llama-3 format
   prompt = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>

   {system_prompt}<|eot_id|><|start_header_id|>user<|end_header_id|>

   {user_message}<|eot_id|><|start_header_id|>assistant<|end_header_id|>
   """
   ```

2. Adjust generation parameters:
   ```python
   outputs = model.generate(
       inputs,
       max_new_tokens=512,
       temperature=0.7,        # Lower = more deterministic
       top_p=0.9,              # Nucleus sampling
       top_k=50,               # Top-k sampling
       repetition_penalty=1.1  # Avoid repetition
   )
   ```

3. Fine-tune on domain-specific data (see Fine-Tuning section)

---

## Next Steps

1. **Try the demo**: Open `ai4se/demo/index.html` in browser
2. **Customize system prompt**: Edit for your specific use case
3. **Prepare training data**: Create domain-specific datasets
4. **Fine-tune model**: Follow LoRA training guide
5. **Deploy to production**: Choose deployment option (PWA/Native)
6. **Gather feedback**: Iterate based on user testing

---

## Additional Resources

- **WebLLM Documentation**: https://mlc.ai/web-llm/
- **llama.cpp GitHub**: https://github.com/ggerganov/llama.cpp
- **ONNX Runtime**: https://onnxruntime.ai/
- **Hugging Face Transformers**: https://huggingface.co/docs/transformers
- **PEFT (LoRA)**: https://huggingface.co/docs/peft

---

**Questions or Issues?**

Open an issue on GitHub: https://github.com/mniami/help-children/issues

Join our community: [Discord link - to be created]

---

*Last Updated: February 12, 2026*
