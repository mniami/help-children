# AI4SE - Amharic Language Support Guide

**Language**: አማርኛ (Amharic)
**Date**: February 12, 2026
**Version**: 1.0

---

## 📋 Overview

This guide provides comprehensive instructions for implementing Amharic language support in AI4SE, including:
- Text-to-Speech (TTS) - converting AI responses to Amharic speech
- Speech-to-Text (STT) - converting Amharic voice input to text
- Using pre-trained models from HuggingFace
- Fine-tuning for medical/technical domains

---

## 🎯 Key Question Answered

**Q: Czy to rozwiązanie korzysta z gotowych modeli językowych z np. HuggingFace czy wymaga wytrenowania modelu na bazie LLM?**

**A: TAK, używamy gotowych modeli z HuggingFace!**

Nasze rozwiązanie wykorzystuje:
1. **Pre-trained base models** (Llama-3.2, Phi-3) - gotowe z HuggingFace
2. **Fine-tuning z LoRA** - dostosowanie do medycyny (nie training od zera!)
3. **Pre-trained STT/TTS models** - gotowe modele dla języka amharskiego

**NIE WYMAGAMY** trenowania modelu od podstaw. Używamy istniejących modeli i je dostosowujemy (fine-tuning), co jest:
- **10-100x tańsze** niż training od zera
- **10-100x szybsze** (dni zamiast miesięcy)
- **Możliwe na pojedynczym GPU** (nie potrzeba cluster'a)

---

## 🗣️ Amharic Language Models

### Base Language Models for Amharic

#### Option 1: Multilingual LLMs (Recommended)

**Llama-3.2-3B-Instruct** (Meta AI)
- **HuggingFace**: `meta-llama/Llama-3.2-3B-Instruct`
- **Amharic Support**: Yes (128 languages including Amharic)
- **Size**: 6.4 GB (FP16), 1.9 GB (Q4)
- **License**: Llama 3.2 License (permissive for research/commercial)
- **Training Data**: Includes significant Amharic text

```python
from transformers import AutoModelForCausalLM, AutoTokenizer

model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-3.2-3B-Instruct",
    torch_dtype="auto",
    device_map="auto"
)

tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-3.2-3B-Instruct")

# Test Amharic
prompt = "ሰላም! እንዴት ነህ?" # "Hello! How are you?"
inputs = tokenizer(prompt, return_tensors="pt")
outputs = model.generate(**inputs, max_new_tokens=100)
response = tokenizer.decode(outputs[0], skip_special_tokens=True)
print(response)
```

**Phi-3-mini-4k-instruct** (Microsoft)
- **HuggingFace**: `microsoft/Phi-3-mini-4k-instruct`
- **Amharic Support**: Limited (better after fine-tuning)
- **Size**: 7.8 GB (FP16), 2.3 GB (Q4)
- **License**: MIT (fully open)

#### Option 2: Amharic-Specific Models

**afro-xlmr-large** (African Languages)
- **HuggingFace**: `Davlan/afro-xlmr-large`
- **Amharic Support**: Excellent (trained on African languages)
- **Size**: 1.7 GB
- **License**: MIT
- **Best for**: Classification, NER, sentiment analysis

**Note**: For medical dialogue, we recommend Llama-3.2-3B + fine-tuning on Amharic medical data.

---

## 🎤 Speech-to-Text (STT) for Amharic

### Option 1: Whisper Models (OpenAI) - Recommended

**Whisper** is the best open-source STT model with excellent Amharic support.

**Models Available**:

| Model | Size | WER (Amharic)* | Speed | Use Case |
|-------|------|----------------|-------|----------|
| whisper-tiny | 39M, 75 MB | ~15-20% | Very Fast | Mobile devices |
| whisper-base | 74M, 140 MB | ~12-15% | Fast | Low-end phones |
| whisper-small | 244M, 460 MB | ~8-10% | Medium | Mid-range phones |
| whisper-medium | 769M, 1.5 GB | ~5-7% | Slow | High-end devices |
| whisper-large-v3 | 1.5B, 3 GB | ~3-5% | Very Slow | Server/Desktop |

*WER = Word Error Rate (lower is better)

#### Implementation with Whisper (Offline)

**Installation**:
```bash
pip install openai-whisper
# OR for faster inference
pip install whisper-cpp-python
```

**Python Implementation**:
```python
import whisper

# Load model (downloads automatically from HuggingFace)
model = whisper.load_model("small")  # ~460 MB

# Transcribe Amharic audio
result = model.transcribe(
    "amharic_audio.mp3",
    language="am",  # Amharic language code
    task="transcribe"
)

print(result["text"])  # Transcribed Amharic text
```

**Browser Implementation (whisper.cpp + WebAssembly)**:
```javascript
// Using whisper.wasm for browser
import { WhisperModel } from '@whisper.cpp/webgpu';

const whisper = await WhisperModel.load('whisper-small-q5');

// Record audio from microphone
const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
const recorder = new MediaRecorder(stream);
const audioChunks = [];

recorder.ondataavailable = (event) => audioChunks.push(event.data);

recorder.onstop = async () => {
  const audioBlob = new Blob(audioChunks);
  const audioBuffer = await audioBlob.arrayBuffer();

  // Transcribe Amharic
  const result = await whisper.transcribe(audioBuffer, {
    language: 'am'
  });

  console.log('Amharic text:', result.text);
  // Send to LLM for processing...
};

// Start recording
recorder.start();

// Stop after 5 seconds (or on button click)
setTimeout(() => recorder.stop(), 5000);
```

**HuggingFace Models**:
- `openai/whisper-tiny` - 75 MB
- `openai/whisper-small` - 460 MB
- `openai/whisper-medium` - 1.5 GB
- `openai/whisper-large-v3` - 3 GB

### Option 2: MMS (Massively Multilingual Speech) - Meta AI

**Excellent for low-resource languages including Amharic**

**HuggingFace**: `facebook/mms-1b-all`
- **Languages**: 1,100+ languages including Amharic
- **Size**: 1.1 GB
- **License**: CC-BY-NC 4.0
- **Advantage**: Specifically trained on African languages

```python
from transformers import Wav2Vec2ForCTC, AutoProcessor
import torch
import torchaudio

# Load MMS model
processor = AutoProcessor.from_pretrained("facebook/mms-1b-all")
model = Wav2Vec2ForCTC.from_pretrained("facebook/mms-1b-all")

# Set target language to Amharic
processor.tokenizer.set_target_lang("amh")  # Amharic ISO code
model.load_adapter("amh")

# Load audio
audio_input, sample_rate = torchaudio.load("amharic_audio.wav")

# Resample to 16kHz if needed
if sample_rate != 16000:
    resampler = torchaudio.transforms.Resample(sample_rate, 16000)
    audio_input = resampler(audio_input)

# Process audio
inputs = processor(audio_input.squeeze(), sampling_rate=16000, return_tensors="pt")

# Transcribe
with torch.no_grad():
    outputs = model(**inputs).logits

# Decode
transcription = processor.decode(outputs[0].argmax(dim=-1))
print(f"Amharic transcription: {transcription}")
```

---

## 🔊 Text-to-Speech (TTS) for Amharic

### Option 1: Piper TTS (Recommended for Offline)

**Piper** is a fast, local TTS system with Amharic support.

**HuggingFace**: `rhasspy/piper-voices`
- **Size**: 10-50 MB per voice
- **Quality**: Natural-sounding
- **Speed**: Real-time on CPU
- **Offline**: Fully offline capable

**Available Amharic Voices**:
- `am_ET-mekonnen-medium` - Male voice, medium quality (25 MB)
- `am_ET-mekonnen-low` - Male voice, low quality (10 MB)

**Installation**:
```bash
# Install piper-tts
pip install piper-tts

# Download Amharic voice
wget https://github.com/rhasspy/piper/releases/download/v1.2.0/am_ET-mekonnen-medium.tar.gz
tar -xzf am_ET-mekonnen-medium.tar.gz
```

**Python Implementation**:
```python
from piper import PiperVoice
import wave

# Load Amharic voice
voice = PiperVoice.load("am_ET-mekonnen-medium/am_ET-mekonnen-medium.onnx")

# Generate speech
amharic_text = "ልጅዎን በተቻለ መጠን ብዙ ውሃ ይስጡ"  # "Give your child as much water as possible"

with wave.open("output.wav", "w") as wav_file:
    voice.synthesize(amharic_text, wav_file)

print("Audio saved to output.wav")
```

**Browser Implementation**:
```javascript
// Using piper-wasm for browser
import { PiperTTS } from 'piper-tts-web';

const tts = await PiperTTS.load('am_ET-mekonnen-medium');

// Synthesize Amharic text
const amharicText = "እንደምን አደርክ? ልጅዎ ምን ያህል ትኩሳት አለው?";
const audioBuffer = await tts.synthesize(amharicText);

// Play audio
const audio = new Audio();
audio.src = URL.createObjectURL(new Blob([audioBuffer], { type: 'audio/wav' }));
audio.play();
```

### Option 2: Coqui TTS (XTTS-v2)

**Multilingual TTS with voice cloning capability**

**HuggingFace**: `coqui/XTTS-v2`
- **Languages**: 16 languages (can synthesize Amharic with fine-tuning)
- **Size**: 1.8 GB
- **Quality**: Excellent (state-of-the-art)
- **Voice Cloning**: Can clone speaker's voice from 6+ seconds of audio

```python
from TTS.api import TTS

# Load XTTS-v2
tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")

# Generate Amharic speech
tts.tts_to_file(
    text="ልጅዎ ምግብ እየበላ ነው?",  # "Is your child eating?"
    file_path="output.wav",
    speaker_wav="reference_amharic_speaker.wav",  # Reference voice
    language="am"
)
```

### Option 3: MMS-TTS (Meta AI)

**TTS counterpart to MMS-ASR**

**HuggingFace**: `facebook/mms-tts-amh`
- **Size**: 300 MB
- **Quality**: Good
- **Speed**: Fast

```python
from transformers import VitsModel, AutoTokenizer
import torch
import scipy

# Load MMS-TTS for Amharic
model = VitsModel.from_pretrained("facebook/mms-tts-amh")
tokenizer = AutoTokenizer.from_pretrained("facebook/mms-tts-amh")

# Generate speech
text = "ልጅዎ በደንብ እንዲጠጣ ያድርጉ"  # "Make sure your child drinks well"
inputs = tokenizer(text, return_tensors="pt")

with torch.no_grad():
    output = model(**inputs).waveform

# Save audio
scipy.io.wavfile.write(
    "output.wav",
    rate=model.config.sampling_rate,
    data=output.squeeze().cpu().numpy()
)
```

---

## 🔄 Complete Amharic Voice Pipeline

### Architecture

```
User (Amharic Speech)
    ↓
[Speech-to-Text: Whisper/MMS]
    ↓
Amharic Text Input
    ↓
[LLM: Llama-3.2-3B Fine-tuned]
    ↓
Amharic Text Output
    ↓
[Text-to-Speech: Piper/MMS-TTS]
    ↓
AI Response (Amharic Speech)
```

### Full Implementation Example

```python
import whisper
from transformers import AutoModelForCausalLM, AutoTokenizer
from piper import PiperVoice
import wave
import torch

class AmharicHealthAssistant:
    def __init__(self):
        # Load STT (Whisper)
        print("Loading STT model...")
        self.stt_model = whisper.load_model("small")

        # Load LLM (Llama-3.2-3B fine-tuned)
        print("Loading LLM...")
        self.llm_model = AutoModelForCausalLM.from_pretrained(
            "meta-llama/Llama-3.2-3B-Instruct",
            torch_dtype=torch.float16,
            device_map="auto"
        )
        self.llm_tokenizer = AutoTokenizer.from_pretrained(
            "meta-llama/Llama-3.2-3B-Instruct"
        )

        # Load TTS (Piper)
        print("Loading TTS model...")
        self.tts_voice = PiperVoice.load(
            "models/am_ET-mekonnen-medium/am_ET-mekonnen-medium.onnx"
        )

        self.system_prompt = """አንተ የጤና አማካሪ ነህ። የታካሚውን ምልክቶች መረዳት እና መጀመሪያ ላይ ምክር መስጠት አለብህ።
You are a health advisor. You need to understand the patient's symptoms and provide initial advice."""

    def transcribe_audio(self, audio_path):
        """Convert Amharic speech to text"""
        print("Transcribing Amharic audio...")
        result = self.stt_model.transcribe(
            audio_path,
            language="am",
            task="transcribe"
        )
        return result["text"]

    def generate_response(self, amharic_text):
        """Generate AI response in Amharic"""
        print(f"Processing: {amharic_text}")

        # Format prompt
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": amharic_text}
        ]

        # Generate response
        prompt = self.llm_tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )

        inputs = self.llm_tokenizer(prompt, return_tensors="pt").to("cuda")

        outputs = self.llm_model.generate(
            **inputs,
            max_new_tokens=512,
            temperature=0.7,
            do_sample=True
        )

        response = self.llm_tokenizer.decode(
            outputs[0][inputs['input_ids'].shape[1]:],
            skip_special_tokens=True
        )

        return response

    def synthesize_speech(self, amharic_text, output_path="response.wav"):
        """Convert Amharic text to speech"""
        print("Generating Amharic speech...")

        with wave.open(output_path, "w") as wav_file:
            self.tts_voice.synthesize(amharic_text, wav_file)

        return output_path

    def process_voice_query(self, audio_input_path):
        """Full pipeline: Speech → Text → LLM → Text → Speech"""

        # Step 1: STT
        user_text = self.transcribe_audio(audio_input_path)
        print(f"User said: {user_text}")

        # Step 2: LLM
        ai_response = self.generate_response(user_text)
        print(f"AI response: {ai_response}")

        # Step 3: TTS
        output_audio = self.synthesize_speech(ai_response)
        print(f"Audio saved to: {output_audio}")

        return {
            "user_text": user_text,
            "ai_text": ai_response,
            "audio_path": output_audio
        }

# Usage
assistant = AmharicHealthAssistant()

# Process voice query
result = assistant.process_voice_query("patient_query_amharic.wav")

print("\n=== Results ===")
print(f"User: {result['user_text']}")
print(f"AI: {result['ai_text']}")
print(f"Audio: {result['audio_path']}")
```

---

## 🎓 Fine-Tuning for Amharic Medical Domain

### Dataset Preparation

**Format**: JSONL with Amharic translations

```json
{"messages": [
  {"role": "system", "content": "አንተ የጤና አማካሪ ነህ። You are a health advisor for primary diagnosis in rural areas."},
  {"role": "user", "content": "ልጄ ለሦስት ቀናት ትኩሳት እና ተቅማጥ አለው። ምን ማድረግ አለብኝ? My child has fever and diarrhea for 3 days. What should I do?"},
  {"role": "assistant", "content": "ስጋትህን ተረድቻለሁ። እባክህ የሚከተሉትን ጥያቄዎች መልስልኝ:\n\nI understand your concern. Please answer the following questions:\n\n1. ትኩሳቱ ምን ያህል ከፍተኛ ነው? How high is the fever?\n2. ልጅዎ ውሃ እየጠጣ ነው? Is the child drinking water?\n3. የውሃ እጥረት ምልክቶች አሉ? Are there signs of dehydration?\n   - ደረቅ አፍ dry mouth\n   - አይኖች ጥልቅ መሆን sunken eyes\n   - እንባ አለመኖር no tears\n\nተጨማሪ መረጃ: Additional information:\n\nይህ አጣዳፊ የሆድ ህመም ሊሆን ይችላል። This could be acute gastroenteritis.\n\n** ወዲያውኑ መወሰድ ያለባቸው እርምጃዎች IMMEDIATE ACTIONS:**\n\n1. ORS መስጠት Give ORS (Oral Rehydration Solution)\n   - የማዘጋጃ መንገድ Recipe: 1 ሊትር ንጹህ ውሃ + 6 የሻይ ማንኪያ ስኳር + 1/2 የሻይ ማንኪያ ጨው\n   - 1 liter clean water + 6 teaspoons sugar + 1/2 teaspoon salt\n\n2. በጡት ማጥባትን ይቀጥሉ Continue breastfeeding if infant\n\n3. የውሃ መጠን ይቆጣጠሩ Monitor hydration\n\n**⚠️ ወዲያውኑ የህክምና እርዳታ ይፈልጉ SEEK MEDICAL HELP IF:**\n- ልጁ መጠጣት አይችልም Child cannot drink\n- ትውከት እየጨመረ ነው Vomiting increases  \n- ትኩሳቱ >39°C ለ >48 ሰዓቶች Fever >39°C for >48 hours\n- በአንጀት ውስጥ ደም Blood in stool"}
]}
```

### Fine-Tuning Script for Amharic

```python
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    TrainingArguments,
    Trainer
)
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from datasets import load_dataset
import torch

# Load base model
model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-3.2-3B-Instruct",
    load_in_4bit=True,
    torch_dtype=torch.float16,
    device_map="auto"
)

tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-3.2-3B-Instruct")
tokenizer.pad_token = tokenizer.eos_token

# Prepare for training
model = prepare_model_for_kbit_training(model)

# Configure LoRA
lora_config = LoraConfig(
    r=16,
    lora_alpha=32,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM"
)

model = get_peft_model(model, lora_config)

# Load Amharic medical dataset
dataset = load_dataset('json', data_files='amharic_medical_training.jsonl')

# Training arguments
training_args = TrainingArguments(
    output_dir="./models/llama-3.2-3b-amharic-medical-lora",
    per_device_train_batch_size=4,
    gradient_accumulation_steps=4,
    num_train_epochs=3,
    learning_rate=2e-4,
    fp16=True,
    logging_steps=10,
    save_steps=100
)

# Train
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=dataset["train"]
)

trainer.train()

# Save LoRA adapter
model.save_pretrained("./models/llama-3.2-3b-amharic-medical-lora")
tokenizer.save_pretrained("./models/llama-3.2-3b-amharic-medical-lora")

print("✅ Amharic fine-tuning complete!")
```

---

## 📦 Model Sizes & Requirements

### Complete Amharic System

| Component | Model | Size | RAM Required |
|-----------|-------|------|--------------|
| STT | Whisper-small | 460 MB | 1 GB |
| LLM | Llama-3.2-3B Q4 + LoRA | 1.9 GB + 100 MB | 3 GB |
| TTS | Piper Amharic | 25 MB | 100 MB |
| **Total** | - | **~2.5 GB** | **~4 GB** |

### Storage Requirements

- **Development**: ~10 GB (base models + quantized versions)
- **Production Mobile**: ~3 GB (quantized models only)
- **Minimum Device**: 4 GB RAM, 5 GB storage

---

## 🚀 Deployment Options

### Option 1: Progressive Web App (Browser)

**Advantages**:
- No app store needed
- Instant updates
- Cross-platform

**Limitations**:
- STT/TTS may need server for conversion
- Or use WebAssembly versions (whisper.wasm, piper.wasm)

### Option 2: Native Android App

**Advantages**:
- Full offline capability
- Better performance
- Direct hardware access

**Implementation**:
```java
// Android with ONNX Runtime
import ai.onnxruntime.OrtSession;
import ai.onnxruntime.OrtEnvironment;

// Load models
OrtEnvironment env = OrtEnvironment.getEnvironment();
OrtSession sttSession = env.createSession("whisper-small.onnx");
OrtSession llmSession = env.createSession("llama-3.2-3b-q4.onnx");
OrtSession ttsSession = env.createSession("piper-amharic.onnx");

// Process pipeline...
```

### Option 3: Native iOS App

**Similar to Android using Core ML**

```swift
import CoreML

let sttModel = try WhisperSmall(configuration: MLModelConfiguration())
let llmModel = try Llama32_3B(configuration: MLModelConfiguration())
let ttsModel = try PiperAmharic(configuration: MLModelConfiguration())
```

---

## 🧪 Testing Amharic Implementation

### Test Phrases (Medical Domain)

```python
test_phrases = [
    "ልጄ ትኩሳት አለው",  # "My child has fever"
    "ራስ ምታት አለኝ",  # "I have a headache"
    "ሆድ ይቆርጠኛል",  # "I have stomach pain"
    "ልጄ ምግብ አይበላም",  # "My child is not eating"
    "ትንፋሽ ማግኘት አስቸጋሪ ነው",  # "Difficult to breathe"
]

for phrase in test_phrases:
    print(f"\nTesting: {phrase}")
    response = assistant.generate_response(phrase)
    print(f"Response: {response}")
```

### Evaluation Metrics

1. **STT Accuracy**: Word Error Rate (WER) < 10%
2. **LLM Quality**: Medical accuracy > 85%
3. **TTS Naturalness**: MOS (Mean Opinion Score) > 3.5/5
4. **End-to-End Latency**: < 5 seconds on mid-range phone

---

## 📚 Pre-trained Model Sources Summary

All models are available on HuggingFace - **NO training from scratch required!**

### Speech-to-Text
- `openai/whisper-small` - 460 MB, best overall
- `facebook/mms-1b-all` - 1.1 GB, excellent for African languages

### Text-to-Speech
- `rhasspy/piper-voices` (am_ET-mekonnen-medium) - 25 MB, best for offline
- `facebook/mms-tts-amh` - 300 MB, good quality
- `coqui/XTTS-v2` - 1.8 GB, highest quality with voice cloning

### Language Model
- `meta-llama/Llama-3.2-3B-Instruct` - 6.4 GB (1.9 GB quantized)
- Fine-tuned with LoRA on Amharic medical data (+ 100 MB adapter)

---

## 💰 Cost & Time Estimates

### Fine-Tuning Costs (One-Time)

| Task | Time | GPU Needed | Cost (Cloud) |
|------|------|------------|--------------|
| STT training | ❌ Not needed | - | $0 (pre-trained) |
| LLM fine-tuning | 4-8 hours | 1x A100 (40GB) | $15-30 |
| TTS training | ❌ Not needed | - | $0 (pre-trained) |
| **Total** | **<1 day** | - | **~$20-30** |

### Operational Costs

**$0/user** - Everything runs offline on device!

---

## 🎯 Next Steps

1. **Download Pre-trained Models**:
   ```bash
   # STT
   python -c "import whisper; whisper.load_model('small')"

   # LLM
   huggingface-cli download meta-llama/Llama-3.2-3B-Instruct

   # TTS
   wget https://github.com/rhasspy/piper/releases/download/v1.2.0/am_ET-mekonnen-medium.tar.gz
   ```

2. **Prepare Amharic Medical Dataset** (100-500 examples)

3. **Fine-tune LLM** (using provided script)

4. **Integrate All Components** (STT → LLM → TTS)

5. **Test on Target Devices** (Android/iOS)

6. **Deploy to Pilot** (20 CHWs in Hawassa, Ethiopia)

---

## 📞 Resources

- **Whisper Documentation**: https://github.com/openai/whisper
- **Piper TTS**: https://github.com/rhasspy/piper
- **MMS Models**: https://huggingface.co/facebook/mms-1b-all
- **Llama-3.2**: https://huggingface.co/meta-llama/Llama-3.2-3B-Instruct

---

**Summary**: Używamy gotowych modeli z HuggingFace + fine-tuning z LoRA. NIE trenujemy od zera!

*Last Updated: February 12, 2026*
