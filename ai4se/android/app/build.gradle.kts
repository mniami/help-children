plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
}

android {
    namespace = "org.helpchildren.aiuniversity"
    compileSdk = 35

    defaultConfig {
        applicationId = "org.helpchildren.aiuniversity"
        minSdk = 26   // Android 8.0 — good ML support; most phones able to run a 2B model are 8+
        targetSdk = 35
        versionCode = 1
        versionName = "1.0"
    }

    buildTypes {
        release {
            isMinifyEnabled = false
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
        }
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }

    kotlinOptions {
        jvmTarget = "17"
    }
}

dependencies {
    // ── On-device AI ────────────────────────────────────────────────────────
    // MediaPipe LLM Inference runs Gemma 2B/3B natively on the device GPU/NPU.
    // The model file (.task) must already be on device storage — no internet needed.
    //
    // Alternative: replace this with llama.cpp JNI bindings for Llama 3.2 support.
    // See README.md → "Llama 3.2 alternative" for instructions.
    implementation("com.google.mediapipe:tasks-genai:0.10.14")

    // ── Android core ────────────────────────────────────────────────────────
    implementation("androidx.core:core-ktx:1.12.0")
    implementation("androidx.appcompat:appcompat:1.6.1")
    implementation("com.google.android.material:material:1.11.0")

    // ── Coroutines (for non-blocking model inference) ────────────────────────
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.7.3")
}
