package org.helpchildren.aiuniversity

import android.content.Context
import com.google.mediapipe.tasks.genai.llminference.LlmInference
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock
import kotlinx.coroutines.withContext

/**
 * Wraps the MediaPipe LLM Inference API for fully offline, on-device chat.
 *
 * The model file must already exist on the device's local storage — no network
 * access is used at any point.
 *
 * Thread-safety: a [Mutex] ensures only one inference runs at a time, which is
 * required because [LlmInference] is not reentrant.
 */
class AiEngine(private val context: Context) {

    private var llm: LlmInference? = null
    private val mutex = Mutex()

    val isLoaded: Boolean get() = llm != null

    // ── Model lifecycle ───────────────────────────────────────────────────────

    /**
     * Load the model from [modelPath] on the device's local storage.
     * Runs on the IO dispatcher; safe to call from any coroutine.
     *
     * @throws IllegalArgumentException if the file does not exist or is invalid.
     */
    suspend fun loadModel(modelPath: String) = withContext(Dispatchers.IO) {
        mutex.withLock {
            llm?.close()
            val options = LlmInference.LlmInferenceOptions.builder()
                .setModelPath(modelPath)
                .setMaxTokens(MAX_RESPONSE_TOKENS)
                .setTopK(40)
                .setTemperature(0.7f)
                .setRandomSeed(0)
                .build()
            llm = LlmInference.createFromOptions(context, options)
        }
    }

    /** Release model memory. Safe to call more than once. */
    fun close() {
        llm?.close()
        llm = null
    }

    // ── Inference ─────────────────────────────────────────────────────────────

    /**
     * Generate a response to [userMessage] given [systemPrompt] and [history].
     *
     * @param systemPrompt  Topic-specific instruction for the model.
     * @param history       Alternating (user, assistant) pairs from this session.
     * @param userMessage   The user's latest spoken input.
     * @return              The model's response, trimmed.
     * @throws IllegalStateException if [loadModel] has not been called.
     */
    suspend fun chat(
        systemPrompt: String,
        history: List<Pair<String, String>>,
        userMessage: String,
    ): String = withContext(Dispatchers.IO) {
        mutex.withLock {
            val engine = llm ?: error("Model not loaded. Call loadModel() first.")
            val prompt = buildGemmaPrompt(systemPrompt, history, userMessage)
            engine.generateResponse(prompt).trim()
        }
    }

    // ── Prompt formatting ─────────────────────────────────────────────────────

    /**
     * Builds a prompt in Gemma's chat format:
     *
     * ```
     * <start_of_turn>system
     * {systemPrompt}<end_of_turn>
     * <start_of_turn>user
     * {userMessage}<end_of_turn>
     * <start_of_turn>model
     * ```
     */
    private fun buildGemmaPrompt(
        systemPrompt: String,
        history: List<Pair<String, String>>,
        userMessage: String,
    ) = buildString {
        append("<start_of_turn>system\n")
        append(systemPrompt)
        append("<end_of_turn>\n")
        for ((user, assistant) in history) {
            append("<start_of_turn>user\n$user<end_of_turn>\n")
            append("<start_of_turn>model\n$assistant<end_of_turn>\n")
        }
        append("<start_of_turn>user\n$userMessage<end_of_turn>\n")
        append("<start_of_turn>model\n")
    }

    companion object {
        /** Maximum tokens to generate per response (keeps answers concise). */
        private const val MAX_RESPONSE_TOKENS = 300

        /**
         * Default path where a volunteer should place the model file.
         * Accessible via `adb push model.task /sdcard/Download/ai-university/model.task`.
         * On Android 13+ use the app's internal storage path instead:
         * `context.filesDir.absolutePath + "/model.task"`
         */
        const val DEFAULT_MODEL_PATH = "/sdcard/Download/ai-university/model.task"
    }
}
