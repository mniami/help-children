# Keep ONNX Runtime classes
-keep class ai.onnxruntime.** { *; }
-dontwarn ai.onnxruntime.**

# Keep model inference classes
-keep class org.helpchildren.amharic.ml.** { *; }
-keep class org.helpchildren.amharic.voice.** { *; }

# Keep data classes
-keep class org.helpchildren.amharic.data.** { *; }

# Keep Compose
-keep class androidx.compose.** { *; }
-dontwarn androidx.compose.**

# Kotlin coroutines
-keepclassmembernames class kotlinx.** {
    volatile <fields>;
}

# Keep native methods
-keepclasseswithmembernames class * {
    native <methods>;
}
