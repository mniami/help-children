package org.helpchildren.aiuniversity

import android.Manifest
import android.content.pm.PackageManager
import android.graphics.Color
import android.os.Bundle
import android.view.Gravity
import android.view.View
import android.widget.*
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import androidx.lifecycle.lifecycleScope
import kotlinx.coroutines.launch

/**
 * Single-Activity UI with three screens toggled by visibility:
 *   SETUP  → choose language, enter model path, load model
 *   TOPICS → icon grid, choose knowledge area
 *   VOICE  → big mic button, AI responds aloud
 */
class MainActivity : AppCompatActivity() {

    // ── Core components ───────────────────────────────────────────────────────
    private lateinit var aiEngine: AiEngine
    private lateinit var voiceManager: VoiceManager

    // ── Session state ─────────────────────────────────────────────────────────
    private var selectedLanguage = LANGUAGES[0]
    private var currentTopic: TopicConfig = TOPICS.last()
    private val conversationHistory = mutableListOf<Pair<String, String>>()
    private var userCount = 1
    private var lastAiResponse = ""

    private enum class MicState { IDLE, LISTENING, THINKING, SPEAKING }
    private enum class Screen { SETUP, TOPICS, VOICE }
    private var currentMicState = MicState.IDLE

    // ── Views ─────────────────────────────────────────────────────────────────
    private lateinit var screenSetup: View
    private lateinit var screenTopics: View
    private lateinit var screenVoice: View

    // Setup
    private lateinit var langGroup: LinearLayout
    private lateinit var modelPathInput: EditText
    private lateinit var startButton: Button
    private lateinit var progressBar: ProgressBar
    private lateinit var progressLabel: TextView

    // Topics
    private lateinit var userLabel: TextView
    private lateinit var topicsGrid: GridLayout

    // Voice
    private lateinit var topicBadge: TextView
    private lateinit var micButton: Button
    private lateinit var statusLabel: TextView
    private lateinit var hintLabel: TextView
    private lateinit var transcriptScroll: ScrollView
    private lateinit var transcriptContainer: LinearLayout

    // ── Lifecycle ─────────────────────────────────────────────────────────────

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        aiEngine = AiEngine(this)
        voiceManager = VoiceManager(this)

        bindViews()
        buildLanguageButtons()
        buildTopicGrid()
        showScreen(Screen.SETUP)
    }

    override fun onPause() {
        super.onPause()
        voiceManager.stopSpeaking()
        voiceManager.stopListening()
    }

    override fun onDestroy() {
        super.onDestroy()
        voiceManager.release()
        aiEngine.close()
    }

    // ── View binding ──────────────────────────────────────────────────────────

    private fun bindViews() {
        screenSetup   = findViewById(R.id.screenSetup)
        screenTopics  = findViewById(R.id.screenTopics)
        screenVoice   = findViewById(R.id.screenVoice)

        langGroup     = findViewById(R.id.langGroup)
        modelPathInput = findViewById(R.id.modelPathInput)
        modelPathInput.setText(AiEngine.DEFAULT_MODEL_PATH)
        startButton   = findViewById(R.id.startButton)
        progressBar   = findViewById(R.id.progressBar)
        progressLabel = findViewById(R.id.progressLabel)

        userLabel        = findViewById(R.id.userLabel)
        topicsGrid       = findViewById(R.id.topicsGrid)

        topicBadge          = findViewById(R.id.topicBadge)
        micButton           = findViewById(R.id.micButton)
        statusLabel         = findViewById(R.id.statusLabel)
        hintLabel           = findViewById(R.id.hintLabel)
        transcriptScroll    = findViewById(R.id.transcriptScroll)
        transcriptContainer = findViewById(R.id.transcriptContainer)

        startButton.setOnClickListener { loadModel() }
        micButton.setOnClickListener { toggleMic() }
        findViewById<Button>(R.id.btnNewUser).setOnClickListener { newUser() }
        findViewById<Button>(R.id.btnSettings).setOnClickListener { showScreen(Screen.SETUP) }
        findViewById<Button>(R.id.btnBack).setOnClickListener { showScreen(Screen.TOPICS) }
        findViewById<Button>(R.id.btnRepeat).setOnClickListener { repeatResponse() }
        findViewById<Button>(R.id.btnClear).setOnClickListener { clearConversation() }
        findViewById<Button>(R.id.btnTopics).setOnClickListener { showScreen(Screen.TOPICS) }
    }

    // ── Language selection ────────────────────────────────────────────────────

    private fun buildLanguageButtons() {
        langGroup.removeAllViews()
        LANGUAGES.forEachIndexed { index, lang ->
            val btn = Button(this).apply {
                text = lang.displayName
                textSize = 13f
                setTextColor(Color.WHITE)
                setPadding(28, 12, 28, 12)
                setOnClickListener { selectLanguage(lang, this) }
            }
            val lp = LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.WRAP_CONTENT,
                LinearLayout.LayoutParams.WRAP_CONTENT
            ).apply { setMargins(6, 4, 6, 4) }
            langGroup.addView(btn, lp)
            if (index == 0) highlightLangBtn(btn, selected = true)
        }
    }

    private fun selectLanguage(lang: LanguageOption, chosen: Button) {
        selectedLanguage = lang
        voiceManager.setLocale(lang.locale)
        for (i in 0 until langGroup.childCount) {
            highlightLangBtn(langGroup.getChildAt(i) as? Button ?: continue, selected = false)
        }
        highlightLangBtn(chosen, selected = true)
    }

    private fun highlightLangBtn(btn: Button, selected: Boolean) {
        btn.setBackgroundColor(if (selected) 0xFF4CAF50.toInt() else 0xFF333355.toInt())
    }

    // ── Topic grid ────────────────────────────────────────────────────────────

    private fun buildTopicGrid() {
        topicsGrid.removeAllViews()
        val cellSize = resources.displayMetrics.widthPixels / 2 - 24
        TOPICS.forEach { topic ->
            val btn = Button(this).apply {
                text = "${topic.emoji}\n${topic.displayName}"
                textSize = 15f
                setTextColor(Color.WHITE)
                gravity = Gravity.CENTER
                setBackgroundColor(Color.parseColor(topic.colorHex))
                setOnClickListener { startTopic(topic) }
            }
            val lp = GridLayout.LayoutParams().apply {
                width = cellSize
                height = cellSize
                setMargins(8, 8, 8, 8)
            }
            topicsGrid.addView(btn, lp)
        }
    }

    // ── Screen navigation ─────────────────────────────────────────────────────

    private fun showScreen(screen: Screen) {
        screenSetup.visibility  = if (screen == Screen.SETUP)   View.VISIBLE else View.GONE
        screenTopics.visibility = if (screen == Screen.TOPICS)  View.VISIBLE else View.GONE
        screenVoice.visibility  = if (screen == Screen.VOICE)   View.VISIBLE else View.GONE
    }

    // ── Model loading ─────────────────────────────────────────────────────────

    private fun loadModel() {
        val path = modelPathInput.text.toString().trim()
        if (path.isEmpty()) {
            progressLabel.text = "⚠️ Please enter the model file path."
            progressLabel.visibility = View.VISIBLE
            return
        }
        startButton.isEnabled = false
        progressBar.isIndeterminate = true
        progressBar.visibility = View.VISIBLE
        progressLabel.text = "Loading model from device storage…"
        progressLabel.visibility = View.VISIBLE

        lifecycleScope.launch {
            try {
                aiEngine.loadModel(path)
                progressLabel.text = "✅ Model ready!"
                progressBar.visibility = View.GONE
                showScreen(Screen.TOPICS)
                voiceManager.speak("Welcome to AI University. Tap a picture to choose your topic.")
            } catch (e: Exception) {
                progressLabel.text = "❌ ${e.message}"
                progressBar.visibility = View.GONE
                startButton.isEnabled = true
            }
        }
    }

    // ── Topic selection ───────────────────────────────────────────────────────

    private fun startTopic(topic: TopicConfig) {
        currentTopic = topic
        conversationHistory.clear()
        lastAiResponse = ""
        topicBadge.text = "${topic.emoji} ${topic.displayName}"
        clearTranscript()
        addMessage("system", topic.welcomeMessage)
        setMicState(MicState.IDLE)
        showScreen(Screen.VOICE)
        voiceManager.speak(topic.welcomeMessage)
    }

    private fun newUser() {
        userCount++
        userLabel.text = "👤 User $userCount"
        conversationHistory.clear()
        lastAiResponse = ""
        voiceManager.speak("New user. Hello User $userCount! Choose a topic.")
    }

    // ── Mic / voice interaction ───────────────────────────────────────────────

    private fun toggleMic() {
        when (currentMicState) {
            MicState.IDLE      -> startListening()
            MicState.LISTENING -> stopListeningEarly()
            else               -> { /* ignore taps while thinking/speaking */ }
        }
    }

    private fun startListening() {
        if (ContextCompat.checkSelfPermission(this, Manifest.permission.RECORD_AUDIO)
            != PackageManager.PERMISSION_GRANTED
        ) {
            ActivityCompat.requestPermissions(
                this, arrayOf(Manifest.permission.RECORD_AUDIO), RC_MIC
            )
            return
        }
        setMicState(MicState.LISTENING)
        voiceManager.startListening(
            onResult = { text -> handleUserSpeech(text) },
            onError  = { _ ->
                setMicState(MicState.IDLE)
                addMessage("system", "Could not hear clearly — please try again.")
            }
        )
    }

    private fun stopListeningEarly() {
        voiceManager.stopListening()
        setMicState(MicState.IDLE)
    }

    private fun handleUserSpeech(text: String) {
        setMicState(MicState.THINKING)
        addMessage("user", text)

        lifecycleScope.launch {
            try {
                val response = aiEngine.chat(
                    systemPrompt = currentTopic.systemPrompt,
                    history      = conversationHistory.toList(),
                    userMessage  = text,
                )
                lastAiResponse = response
                conversationHistory.add(Pair(text, response))
                addMessage("ai", response)
                setMicState(MicState.SPEAKING)
                voiceManager.speak(response) { setMicState(MicState.IDLE) }
            } catch (e: Exception) {
                addMessage("system", "⚠️ ${e.message}")
                setMicState(MicState.IDLE)
            }
        }
    }

    // ── Footer actions ────────────────────────────────────────────────────────

    private fun repeatResponse() {
        if (lastAiResponse.isBlank()) return
        setMicState(MicState.SPEAKING)
        voiceManager.speak(lastAiResponse) { setMicState(MicState.IDLE) }
    }

    private fun clearConversation() {
        conversationHistory.clear()
        lastAiResponse = ""
        clearTranscript()
        addMessage("system", "Conversation cleared. Tap the microphone to start again.")
        voiceManager.speak("Conversation cleared.")
    }

    // ── Mic state UI ──────────────────────────────────────────────────────────

    private fun setMicState(state: MicState) {
        currentMicState = state
        when (state) {
            MicState.IDLE -> {
                micButton.text = "🎤"
                micButton.setBackgroundColor(0xFF2E7D32.toInt())
                micButton.isEnabled = true
                statusLabel.text = "Tap to speak"
                hintLabel.text   = "Tap the microphone and ask your question"
            }
            MicState.LISTENING -> {
                micButton.text = "⏹"
                micButton.setBackgroundColor(0xFFB71C1C.toInt())
                micButton.isEnabled = true
                statusLabel.text = "Listening…"
                hintLabel.text   = "Speak now — tap again to stop"
            }
            MicState.THINKING -> {
                micButton.text = "⏳"
                micButton.setBackgroundColor(0xFFE65100.toInt())
                micButton.isEnabled = false
                statusLabel.text = "Thinking…"
                hintLabel.text   = "Please wait"
            }
            MicState.SPEAKING -> {
                micButton.text = "🔊"
                micButton.setBackgroundColor(0xFF1565C0.toInt())
                micButton.isEnabled = false
                statusLabel.text = "Speaking…"
                hintLabel.text   = "Tap Repeat to hear the answer again"
            }
        }
    }

    // ── Transcript ────────────────────────────────────────────────────────────

    private fun clearTranscript() = transcriptContainer.removeAllViews()

    private fun addMessage(role: String, text: String) {
        val tv = TextView(this).apply {
            this.text = when (role) {
                "user"  -> "🗣 $text"
                "ai"    -> "🤖 $text"
                else    -> text
            }
            textSize = 14f
            setTextColor(Color.WHITE)
            setPadding(20, 14, 20, 14)
            setBackgroundColor(
                when (role) {
                    "user"  -> 0x334285F4.toInt()
                    "ai"    -> 0x334CAF50.toInt()
                    else    -> 0x22FFFFFF.toInt()
                }
            )
        }
        val lp = LinearLayout.LayoutParams(
            LinearLayout.LayoutParams.MATCH_PARENT,
            LinearLayout.LayoutParams.WRAP_CONTENT
        ).apply { setMargins(0, 4, 0, 4) }
        transcriptContainer.addView(tv, lp)
        transcriptScroll.post { transcriptScroll.fullScroll(View.FOCUS_DOWN) }
    }

    // ── Permissions ───────────────────────────────────────────────────────────

    override fun onRequestPermissionsResult(
        requestCode: Int,
        permissions: Array<out String>,
        grantResults: IntArray,
    ) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults)
        if (requestCode == RC_MIC &&
            grantResults.firstOrNull() == PackageManager.PERMISSION_GRANTED
        ) {
            startListening()
        }
    }

    companion object {
        private const val RC_MIC = 101
    }
}
