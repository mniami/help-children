package org.helpchildren.aiuniversity

import android.content.Context
import android.content.Intent
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.speech.RecognitionListener
import android.speech.RecognizerIntent
import android.speech.SpeechRecognizer
import android.speech.tts.TextToSpeech
import android.speech.tts.UtteranceProgressListener
import java.util.Locale

/**
 * Manages Android's built-in Speech-to-Text and Text-to-Speech — both work
 * fully offline once the device's offline voice packs are installed.
 *
 * STT:  Android SpeechRecognizer (requires offline pack from device Settings)
 * TTS:  Android TextToSpeech    (English built-in; other languages need voice data)
 */
class VoiceManager(private val context: Context) : TextToSpeech.OnInitListener {

    private val mainHandler = Handler(Looper.getMainLooper())
    private val tts: TextToSpeech = TextToSpeech(context, this)
    private var stt: SpeechRecognizer? = null
    private var ttsReady = false
    private var currentLocale = Locale.ENGLISH

    // ── TextToSpeech init ─────────────────────────────────────────────────────

    override fun onInit(status: Int) {
        if (status == TextToSpeech.SUCCESS) {
            tts.language = currentLocale
            ttsReady = true
        }
    }

    // ── Language ──────────────────────────────────────────────────────────────

    fun setLocale(locale: Locale) {
        currentLocale = locale
        if (ttsReady) tts.language = locale
    }

    // ── TTS ───────────────────────────────────────────────────────────────────

    /**
     * Speak [text] aloud. [onDone] is called on the main thread when speech ends.
     * Any speech currently playing is interrupted.
     */
    fun speak(text: String, onDone: (() -> Unit)? = null) {
        if (!ttsReady) {
            onDone?.invoke()
            return
        }
        tts.setOnUtteranceProgressListener(object : UtteranceProgressListener() {
            override fun onStart(utteranceId: String?) {}
            override fun onDone(utteranceId: String?) {
                mainHandler.post { onDone?.invoke() }
            }
            @Deprecated("Deprecated in Java")
            override fun onError(utteranceId: String?) {
                mainHandler.post { onDone?.invoke() }
            }
        })
        tts.speak(text, TextToSpeech.QUEUE_FLUSH, null, "utt_${System.currentTimeMillis()}")
    }

    fun stopSpeaking() = tts.stop()

    // ── STT ───────────────────────────────────────────────────────────────────

    /**
     * Start listening for voice input.
     *
     * @param onResult Called on the main thread with the recognised text.
     * @param onError  Called on the main thread with an error code on failure.
     *                 Error -1 means recognition returned an empty result.
     */
    fun startListening(onResult: (String) -> Unit, onError: (Int) -> Unit) {
        stt?.destroy()
        stt = SpeechRecognizer.createSpeechRecognizer(context).apply {
            setRecognitionListener(object : RecognitionListener {
                override fun onReadyForSpeech(params: Bundle?) {}
                override fun onBeginningOfSpeech() {}
                override fun onRmsChanged(rmsdB: Float) {}
                override fun onBufferReceived(buffer: ByteArray?) {}
                override fun onEndOfSpeech() {}
                override fun onPartialResults(partialResults: Bundle?) {}
                override fun onEvent(eventType: Int, params: Bundle?) {}

                override fun onResults(results: Bundle?) {
                    val text = results
                        ?.getStringArrayList(SpeechRecognizer.RESULTS_RECOGNITION)
                        ?.firstOrNull()
                        .orEmpty()
                    if (text.isNotBlank()) onResult(text) else onError(-1)
                }

                override fun onError(error: Int) = onError(error)
            })

            startListening(Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH).apply {
                putExtra(
                    RecognizerIntent.EXTRA_LANGUAGE_MODEL,
                    RecognizerIntent.LANGUAGE_MODEL_FREE_FORM
                )
                putExtra(RecognizerIntent.EXTRA_LANGUAGE, currentLocale.toLanguageTag())
                putExtra(RecognizerIntent.EXTRA_MAX_RESULTS, 1)
            })
        }
    }

    fun stopListening() {
        stt?.stopListening()
        stt?.destroy()
        stt = null
    }

    // ── Lifecycle ─────────────────────────────────────────────────────────────

    fun release() {
        stopListening()
        tts.stop()
        tts.shutdown()
    }
}
