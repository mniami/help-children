# AI University — Native Android App

Fully offline voice assistant compiled and installed as a native Android APK.  
No browser, no internet connection, no API key — ever.

## Why Native Instead of WebLLM?

| | WebLLM (browser) | This app (native) |
|---|---|---|
| First-use download | Via browser cache — needs internet | Model transferred via USB / SD card |
| Subsequent uses | Instant (cached) | Instant (on device) |
| Internet required | For first load | Never |
| Distribution | Share a URL | Install APK once |
| Performance | WebGPU (limited) | Native ARM64 / GPU delegate |

For users with no reliable internet access, WebLLM's one-time download is a blocker.
A sideloaded APK with the model already on the device solves that completely.

---

## Architecture

```
User speaks
    │
    ▼
Android SpeechRecognizer  ← built-in, works offline (requires offline voice pack)
    │
    ▼
MediaPipe LLM Inference   ← Gemma 2B/3B running natively via GPU/NPU delegate
    │
    ▼
Android TextToSpeech      ← built-in, works offline
    │
    ▼
User hears the answer
```

---

## Requirements

- Android 8.0 (API 26) or higher
- 4 GB RAM minimum (6 GB recommended for 3B model)
- ~2 GB free storage for the AI model
- No internet after initial device setup

---

## One-Time Device Setup

### Step 1 — Get the model file

Download **Gemma 2B Instruct** in MediaPipe `.task` format from Kaggle:

```
https://www.kaggle.com/models/google/gemma/frameworks/tfLite/variations/gemma-2b-it-gpu-int8
```

> **Llama 3.2 alternative:** Replace `AiEngine.kt` with a JNI wrapper around
> [llama.cpp](https://github.com/ggerganov/llama.cpp) compiled for Android NDK (ARM64).
> Llama 3.2 has stronger Amharic/Swahili support than Gemma 2B.
> See `docs/LLAMA_CPP_ANDROID.md` for instructions.

### Step 2 — Transfer the model to the device (USB)

```bash
adb push gemma-2b-it-gpu-int8.task /sdcard/Download/ai-university/model.task
```

Or use a file manager app once connected to a computer via USB.

> **Android 11+ note:** If `/sdcard/Download/` is not accessible, copy the model into the
> app's private storage instead:
> ```bash
> adb push gemma-2b-it-gpu-int8.task \
>   /data/data/org.helpchildren.aiuniversity/files/model.task
> ```
> Then enter `/data/data/org.helpchildren.aiuniversity/files/model.task` in the app.

### Step 3 — Install the APK

```bash
# Build
cd ai4se/android
./gradlew assembleRelease

# Install
adb install app/build/outputs/apk/release/app-release.apk
```

Or share the APK file directly and install via USB / Bluetooth / local Wi-Fi.

### Step 4 — Enable offline speech

On the device:  
**Settings → Language & Input → Voice Input → Download offline speech recognition**  
Select the language(s) you need.

For Text-to-Speech voices:  
**Settings → Language & Input → Text-to-Speech → Install voice data**

---

## Project Structure

```
android/
├── settings.gradle.kts
├── build.gradle.kts
└── app/
    ├── build.gradle.kts
    └── src/main/
        ├── AndroidManifest.xml
        └── kotlin/org/helpchildren/aiuniversity/
            ├── MainActivity.kt      # UI + screen navigation
            ├── AiEngine.kt          # MediaPipe LLM wrapper (offline inference)
            ├── VoiceManager.kt      # Android STT + TTS (offline)
            └── TopicConfig.kt       # Topics, system prompts, languages
```

---

## User Flow

```
App opens
    │
    ├─ Screen 1: SETUP
    │   Select language → enter model path → tap Start
    │   (model loads from local storage in ~5–10 s)
    │
    ├─ Screen 2: TOPICS
    │   Icon grid: Health 🏥 / Education 📖 / Farming 🌾
    │              Rights ⚖️ / Emergency 🆘 / Anything 💬
    │   (tappable without reading)
    │
    └─ Screen 3: VOICE
        Tap 🎤 → speak → AI responds aloud
        "New User" clears conversation for the next person
```

---

## Deploying to Multiple Phones

A volunteer can:
1. Transfer the model file to each phone once via USB
2. Install the APK via USB or Bluetooth
3. Done — each phone works fully offline from that point on

No accounts, no subscriptions, no internet required.
