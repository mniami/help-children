package org.helpchildren.amharic.voice

import android.content.Context
import android.content.Intent
import android.os.Bundle
import android.speech.RecognitionListener
import android.speech.RecognizerIntent
import android.speech.SpeechRecognizer
import android.speech.tts.TextToSpeech
import android.util.Log
import kotlinx.coroutines.channels.awaitClose
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.callbackFlow
import java.util.Locale

/**
 * Voice service for Speech-to-Text and Text-to-Speech
 * Uses Android's native APIs for optimal performance
 */
class VoiceService(private val context: Context) {
    
    private var speechRecognizer: SpeechRecognizer? = null
    private var textToSpeech: TextToSpeech? = null
    private var isTtsInitialized = false
    
    companion object {
        private const val TAG = "VoiceService"
        
        // Amharic locale
        val AMHARIC_LOCALE = Locale("am", "ET")
    }
    
    /**
     * Initialize Text-to-Speech
     */
    fun initializeTts(onInitialized: (Boolean) -> Unit) {
        textToSpeech = TextToSpeech(context) { status ->
            if (status == TextToSpeech.SUCCESS) {
                // Try to set Amharic locale
                val result = textToSpeech?.setLanguage(AMHARIC_LOCALE)
                isTtsInitialized = result != TextToSpeech.LANG_MISSING_DATA &&
                                  result != TextToSpeech.LANG_NOT_SUPPORTED
                
                if (!isTtsInitialized) {
                    Log.w(TAG, "Amharic TTS not available, falling back to English")
                    textToSpeech?.setLanguage(Locale.US)
                    isTtsInitialized = true
                }
                
                onInitialized(isTtsInitialized)
            } else {
                Log.e(TAG, "TTS initialization failed")
                onInitialized(false)
            }
        }
    }
    
    /**
     * Speak text using TTS
     */
    fun speak(text: String, language: String = "am") {
        if (!isTtsInitialized) {
            Log.w(TAG, "TTS not initialized")
            return
        }
        
        // Set language
        val locale = if (language == "am") AMHARIC_LOCALE else Locale.US
        textToSpeech?.setLanguage(locale)
        
        // Speak
        textToSpeech?.speak(text, TextToSpeech.QUEUE_FLUSH, null, "utteranceId")
    }
    
    /**
     * Start listening for speech input
     * Returns a Flow that emits recognized text
     */
    fun startListening(language: String = "am"): Flow<VoiceResult> = callbackFlow {
        
        if (!SpeechRecognizer.isRecognitionAvailable(context)) {
            trySend(VoiceResult.Error("Speech recognition not available"))
            close()
            return@callbackFlow
        }
        
        // Create speech recognizer
        speechRecognizer = SpeechRecognizer.createSpeechRecognizer(context)
        
        // Set up recognition listener
        speechRecognizer?.setRecognitionListener(object : RecognitionListener {
            override fun onReadyForSpeech(params: Bundle?) {
                trySend(VoiceResult.Ready)
            }
            
            override fun onBeginningOfSpeech() {
                trySend(VoiceResult.Listening)
            }
            
            override fun onRmsChanged(rmsdB: Float) {
                // Can be used to show audio level
            }
            
            override fun onBufferReceived(buffer: ByteArray?) {}
            
            override fun onEndOfSpeech() {}
            
            override fun onError(error: Int) {
                val errorMsg = when (error) {
                    SpeechRecognizer.ERROR_AUDIO -> "Audio recording error"
                    SpeechRecognizer.ERROR_CLIENT -> "Client error"
                    SpeechRecognizer.ERROR_INSUFFICIENT_PERMISSIONS -> "Insufficient permissions"
                    SpeechRecognizer.ERROR_NETWORK -> "Network error"
                    SpeechRecognizer.ERROR_NETWORK_TIMEOUT -> "Network timeout"
                    SpeechRecognizer.ERROR_NO_MATCH -> "No match found"
                    SpeechRecognizer.ERROR_RECOGNIZER_BUSY -> "Recognizer busy"
                    SpeechRecognizer.ERROR_SERVER -> "Server error"
                    SpeechRecognizer.ERROR_SPEECH_TIMEOUT -> "No speech input"
                    else -> "Unknown error"
                }
                trySend(VoiceResult.Error(errorMsg))
                close()
            }
            
            override fun onResults(results: Bundle?) {
                val matches = results?.getStringArrayList(SpeechRecognizer.RESULTS_RECOGNITION)
                if (!matches.isNullOrEmpty()) {
                    trySend(VoiceResult.Success(matches[0]))
                } else {
                    trySend(VoiceResult.Error("No results"))
                }
                close()
            }
            
            override fun onPartialResults(partialResults: Bundle?) {
                // Can be used for real-time transcription
            }
            
            override fun onEvent(eventType: Int, params: Bundle?) {}
        })
        
        // Create recognition intent
        val intent = Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH).apply {
            putExtra(
                RecognizerIntent.EXTRA_LANGUAGE_MODEL,
                RecognizerIntent.LANGUAGE_MODEL_FREE_FORM
            )
            
            // Set language (Amharic or English)
            val locale = if (language == "am") "am-ET" else "en-US"
            putExtra(RecognizerIntent.EXTRA_LANGUAGE, locale)
            putExtra(RecognizerIntent.EXTRA_LANGUAGE_PREFERENCE, locale)
            
            putExtra(RecognizerIntent.EXTRA_PARTIAL_RESULTS, true)
            putExtra(RecognizerIntent.EXTRA_MAX_RESULTS, 1)
        }
        
        // Start listening
        try {
            speechRecognizer?.startListening(intent)
        } catch (e: Exception) {
            Log.e(TAG, "Failed to start listening", e)
            trySend(VoiceResult.Error(e.message ?: "Unknown error"))
            close()
        }
        
        awaitClose {
            speechRecognizer?.destroy()
            speechRecognizer = null
        }
    }
    
    /**
     * Stop listening
     */
    fun stopListening() {
        speechRecognizer?.stopListening()
    }
    
    /**
     * Stop TTS
     */
    fun stopSpeaking() {
        textToSpeech?.stop()
    }
    
    /**
     * Check if TTS is speaking
     */
    fun isSpeaking(): Boolean {
        return textToSpeech?.isSpeaking ?: false
    }
    
    /**
     * Release resources
     */
    fun release() {
        speechRecognizer?.destroy()
        speechRecognizer = null
        
        textToSpeech?.stop()
        textToSpeech?.shutdown()
        textToSpeech = null
    }
}

/**
 * Voice recognition result
 */
sealed class VoiceResult {
    object Ready : VoiceResult()
    object Listening : VoiceResult()
    data class Success(val text: String) : VoiceResult()
    data class Error(val message: String) : VoiceResult()
}
