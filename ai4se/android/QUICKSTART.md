# Amharic Assistant Android - Quick Start

## ⚡ 5-Minute Setup

### Step 1: Install Dependencies

```bash
# Install Python dependencies for model export
# onnxruntime provides faster CPU inference during export
pip install transformers optimum[onnxruntime] torch onnx onnxruntime
```

### Step 2: Export Model to ONNX

```bash
cd /home/dszczepek/help-children/ai4se

# Export Qwen 1.5B to ONNX (INT4 quantized, ~800 MB)
python scripts/export_to_onnx.py \
  --model_name "Qwen/Qwen2.5-1.5B-Instruct" \
  --output_path "android/app/src/main/assets/models" \
  --quantization int4

# This will take 5-10 minutes on first run
# Downloads model, exports to ONNX, and quantizes
```

**Alternative: Use smaller model for testing**
```bash
# Llama 1B (faster export, smaller size)
python scripts/export_to_onnx.py \
  --model_name "meta-llama/Llama-3.2-1B-Instruct" \
  --output_path "android/app/src/main/assets/models" \
  --quantization int4
```

### Step 3: Build APK

```bash
cd android

# Build debug APK (for testing)
./gradlew assembleDebug

# APK location: app/build/outputs/apk/debug/app-debug.apk
```

### Step 4: Install on Device

```bash
# Via ADB
adb install app/build/outputs/apk/debug/app-debug.apk

# Or transfer APK to phone and install manually
```

### Step 5: Grant Permissions

When app first launches:
1. Grant microphone permission (for voice input)
2. Wait 3-5 seconds for model to load
3. Start chatting!

## 🎯 Usage Examples

**Text Chat:**
- Type "ሰላም! እንዴት ነህ?" (Hello! How are you?)
- Type "What is the capital of Ethiopia?"

**Voice Chat:**
- Tap microphone icon
- Speak in Amharic or English
- Tap speak icon on response to hear it

**Translation:**
- "Translate 'Good morning' to Amharic"
- "ይህን ወደ እንግሊዝኛ ተርጐም" (Translate this to English)

## 🐛 Troubleshooting

**Model export fails:**
```bash
# Install missing dependencies
pip install --upgrade transformers optimum onnxruntime torch

# Try with smaller model first
python scripts/export_to_onnx.py \
  --model_name "TinyLlama/TinyLlama-1.1B-Chat-v1.0" \
  --output_path "android/app/src/main/assets/models" \
  --quantization int8
```

**Build fails:**
```bash
# Clean and rebuild
cd android
./gradlew clean
./gradlew assembleDebug
```

**App crashes on launch:**
- Check logcat: `adb logcat | grep AmharicAssistant`
- Ensure model files are in `app/src/main/assets/models/`
- Verify device has 4GB+ RAM

**Voice not working:**
- Grant microphone permission in Settings
- Check if Android TTS is installed
- Test with English first

## 📊 Expected Results

**On MEIZU Mblu 21 (4GB RAM):**
- Cold start: ~2 seconds ✅
- Model load: ~3 seconds ✅
- First response: 4-8 seconds ✅
- Subsequent responses: 3-6 seconds ✅
- Memory usage: 1.8-2.2 GB ✅

**Much better than WebLLM!** 🎉

## 📱 Distribution

**For testing:**
- Share APK file directly
- Install with "Unknown sources" enabled

**For production:**
- Sign with release keystore
- Upload to Play Store or F-Droid
- Or distribute via website

## 🎉 You're Done!

The app now runs completely offline with:
- ✅ Amharic voice input (Android STT)
- ✅ AI responses (ONNX Runtime)
- ✅ Amharic voice output (Android TTS)
- ✅ No internet required!
- ✅ Full privacy (everything on-device)

## 📖 Next Steps

- Read [android/README.md](README.md) for detailed docs
- Customize UI in `MainActivity.kt`
- Add more features in `ChatViewModel.kt`
- Optimize model in `ModelInference.kt`

---

Questions? Check the README or open an issue!
