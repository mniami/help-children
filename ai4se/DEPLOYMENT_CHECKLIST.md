# Android App Build & Deployment Checklist

Use this checklist to ensure successful build and deployment of the Amharic Assistant Android app.

## 📋 Pre-Build Checklist

### Development Environment
- [ ] Android Studio Hedgehog (2023.1.1) or newer installed
- [ ] JDK 17 or higher installed
- [ ] Android SDK 34 installed
- [ ] Android NDK installed (for ARM support)
- [ ] Python 3.9+ with required packages
- [ ] Git repository cloned

### Dependencies
```bash
# Python dependencies
- [ ] pip install transformers
- [ ] pip install optimum[onnxruntime]
- [ ] pip install torch
- [ ] pip install onnx
```

### Model Preparation
- [ ] Decided on model: Qwen 1.5B (recommended) or Llama 1B
- [ ] Run export script successfully
- [ ] Verify model files in `android/app/src/main/assets/models/`
- [ ] Model size confirmed (~800 MB for INT4)
- [ ] Tokenizer files present

### Project Setup
- [ ] Open `android/` folder in Android Studio
- [ ] Gradle sync completed without errors
- [ ] No dependency conflicts
- [ ] NDK configured for ARM targets
- [ ] Build variants configured (debug/release)

## 🔨 Build Checklist

### Debug Build (Testing)
```bash
cd android
./gradlew assembleDebug
```

- [ ] Build completes without errors
- [ ] APK generated at `app/build/outputs/apk/debug/app-debug.apk`
- [ ] APK size reasonable (~900 MB with model)
- [ ] Manifest permissions correct

### Release Build (Production)
```bash
# First time: Generate keystore
keytool -genkey -v -keystore release.keystore \
  -alias amharic-assistant -keyalg RSA -keysize 2048 -validity 10000

# Build
./gradlew assembleRelease
```

- [ ] Keystore generated and backed up securely
- [ ] `app/build.gradle.kts` configured with signing config
- [ ] Build completes without errors
- [ ] APK generated at `app/build/outputs/apk/release/app-release.apk`
- [ ] ProGuard rules applied correctly
- [ ] Code obfuscated (check mapping file)

## 🧪 Testing Checklist

### Pre-Installation Tests
- [ ] APK integrity verified (not corrupted)
- [ ] APK size checked (~900 MB with model)
- [ ] Version code/name correct

### Installation Tests
```bash
adb install app/build/outputs/apk/debug/app-debug.apk
```

- [ ] Installs successfully on test device
- [ ] App icon appears in launcher
- [ ] App name displays correctly
- [ ] No installation errors

### Functional Tests

#### App Launch
- [ ] App launches without crashes
- [ ] Splash screen (if any) works
- [ ] Main screen loads
- [ ] Model loading starts automatically
- [ ] Loading progress shown

#### Permissions
- [ ] Microphone permission requested
- [ ] Permission dialog clear and informative
- [ ] App handles permission denial gracefully
- [ ] Permission can be re-requested

#### Model Loading
- [ ] Model loads successfully
- [ ] Loading time acceptable (~3-5 seconds)
- [ ] Error handling if model missing
- [ ] Status indicator updates correctly

#### Text Chat
- [ ] Can type in text field
- [ ] Send button enables/disables correctly
- [ ] Message appears in chat
- [ ] Response generated successfully
- [ ] Response latency acceptable (4-8 seconds first time)
- [ ] Subsequent responses faster
- [ ] Chat scrolls to latest message
- [ ] Can copy message text

#### Voice Input
- [ ] Mic button visible and accessible
- [ ] Clicking mic requests permission (first time)
- [ ] Voice recording starts
- [ ] Audio indicator shown
- [ ] Speech recognized correctly (Amharic)
- [ ] Speech recognized correctly (English)
- [ ] Transcribed text shown
- [ ] Response generated
- [ ] Can cancel recording

#### Voice Output
- [ ] Speaker icon on assistant messages
- [ ] TTS speaks message when clicked
- [ ] Amharic pronunciation acceptable
- [ ] English pronunciation good
- [ ] Can stop playback
- [ ] Multiple messages can be played

#### UI/UX
- [ ] Layout looks good on small screens (5")
- [ ] Layout looks good on large screens (6.5"+)
- [ ] Text readable (good contrast)
- [ ] Amharic text renders correctly
- [ ] Scrolling smooth
- [ ] No UI lag during generation
- [ ] Material Design 3 theme consistent
- [ ] Dark mode works (if supported)

#### Example Prompts
- [ ] "ሰላም! እንዴት ነህ?" works correctly
- [ ] "Translate 'Good morning' to Amharic" works
- [ ] "What is the capital of Ethiopia?" works
- [ ] "Tell me about Ethiopian coffee" works

#### Edge Cases
- [ ] Empty input handled gracefully
- [ ] Very long input (>1000 chars) handled
- [ ] Rapid multiple messages handled
- [ ] App backgrounding/resuming works
- [ ] Screen rotation works
- [ ] Low memory warning handled

### Performance Tests

#### Memory
- [ ] Memory usage < 2.5 GB during operation
- [ ] No memory leaks (test long sessions)
- [ ] App doesn't crash on low memory

#### Battery
```bash
# Monitor battery usage
adb shell dumpsys batterystats --reset
# Use app for 1 hour
adb shell dumpsys batterystats
```
- [ ] Battery drain < 15% per hour
- [ ] No battery drain when idle
- [ ] Properly releases resources

#### Storage
- [ ] Total storage < 1.5 GB
- [ ] Model files in correct location
- [ ] Cache manageable
- [ ] Can clear cache if needed

#### Offline Tests
- [ ] Enable airplane mode
- [ ] App still works
- [ ] All features functional
- [ ] No network errors shown

### Device Compatibility

Test on multiple devices:

**Budget Phone (Target Device)**
- [ ] MEIZU Mblu 21 or similar
- [ ] 4 GB RAM
- [ ] Android 7-9
- [ ] ARM64 processor

**Mid-Range Phone**
- [ ] 6-8 GB RAM
- [ ] Android 10-12
- [ ] Better performance verified

**Older Device**
- [ ] 3 GB RAM (if possible)
- [ ] Android 7
- [ ] Graceful degradation

## 📦 Packaging Checklist

### APK Preparation
- [ ] Final version number set
- [ ] App name final
- [ ] Icon final (all densities)
- [ ] Splash screen final
- [ ] Model bundled or download configured
- [ ] Permissions list finalized
- [ ] ProGuard optimizations applied

### Documentation
- [ ] User guide created (if needed)
- [ ] Privacy policy included
- [ ] Terms of service (if needed)
- [ ] Attribution for model/libraries
- [ ] License information clear

### Security
- [ ] Release keystore backed up securely
- [ ] Keystore password recorded safely
- [ ] No hardcoded secrets in code
- [ ] ProGuard mapping file saved
- [ ] APK signed correctly

## 🚀 Deployment Checklist

### Pre-Deployment
- [ ] All tests passed
- [ ] Performance acceptable
- [ ] Security review done
- [ ] Legal review (if needed)
- [ ] User documentation ready

### Distribution Method Selected

#### Option 1: Direct APK Distribution
- [ ] APK uploaded to hosting (website, cloud)
- [ ] Download link created
- [ ] Installation instructions provided
- [ ] SHA256 checksum published
- [ ] Version tracking set up

#### Option 2: Play Store
- [ ] Developer account created
- [ ] App listing prepared (title, description, screenshots)
- [ ] Privacy policy URL
- [ ] Content rating completed
- [ ] App bundle generated (`./gradlew bundleRelease`)
- [ ] Uploaded to Play Console
- [ ] Internal testing track created
- [ ] Alpha/Beta testing done

#### Option 3: F-Droid
- [ ] App meets F-Droid requirements
- [ ] Source code public
- [ ] Build reproducible
- [ ] Metadata created
- [ ] Submitted to F-Droid

### Post-Deployment
- [ ] Download link tested
- [ ] Installation tested by external user
- [ ] Feedback mechanism set up
- [ ] Update plan documented
- [ ] Crash reporting configured (optional)
- [ ] Analytics configured (if desired, privacy-conscious)

## 📊 Launch Checklist

### Pre-Launch
- [ ] Announcement prepared
- [ ] User guide available
- [ ] Support channel ready (email, forum, etc.)
- [ ] Social media posts ready
- [ ] Community informed

### Launch Day
- [ ] APK available for download
- [ ] Download link shared
- [ ] Announcement published
- [ ] Monitor for issues
- [ ] Ready to provide support

### Post-Launch (First Week)
- [ ] Monitor crash reports
- [ ] Collect user feedback
- [ ] Track download numbers
- [ ] Respond to user questions
- [ ] Fix critical bugs quickly
- [ ] Plan first update

## 🐛 Troubleshooting Reference

### Build Issues
```
Issue: Gradle sync failed
Solution: Check Android Studio Gradle version, update if needed

Issue: NDK not found
Solution: Install NDK via SDK Manager

Issue: Out of memory during build
Solution: Increase Gradle memory: org.gradle.jvmargs=-Xmx4g
```

### Runtime Issues
```
Issue: Model not found
Solution: Verify model in assets/ or implement download

Issue: Out of memory crash
Solution: Use INT4 quant, reduce context length

Issue: TTS not working
Solution: Check if language pack installed, test with English
```

### Device-Specific Issues
```
Issue: Slow on old devices
Solution: Reduce model size, use INT8, optimize batch size

Issue: App crashes on launch
Solution: Check logs, verify device meets requirements
```

## ✅ Final Sign-Off

Before releasing to users, confirm:

- [ ] All critical tests passed
- [ ] Performance acceptable on target devices
- [ ] User documentation complete
- [ ] Support plan in place
- [ ] Legal/privacy requirements met
- [ ] Deployment method ready
- [ ] Team ready for launch

**Ready to launch!** 🚀

---

**For questions or issues, see:**
- [android/README.md](android/README.md) - Technical details
- [android/QUICKSTART.md](android/QUICKSTART.md) - Quick setup
- [ANDROID_IMPLEMENTATION.md](ANDROID_IMPLEMENTATION.md) - Architecture overview
