package org.helpchildren.amharic.ui

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import org.helpchildren.amharic.data.ChatUiState
import org.helpchildren.amharic.data.Message
import org.helpchildren.amharic.data.MessageRole
import org.helpchildren.amharic.data.ModelState
import org.helpchildren.amharic.ml.ModelInference
import org.helpchildren.amharic.voice.VoiceResult
import org.helpchildren.amharic.voice.VoiceService

class ChatViewModel(application: Application) : AndroidViewModel(application) {
    
    private val modelInference = ModelInference(application)
    private val voiceService = VoiceService(application)
    
    private val _uiState = MutableStateFlow(ChatUiState())
    val uiState: StateFlow<ChatUiState> = _uiState.asStateFlow()
    
    private val systemPrompt = """You are a helpful AI assistant for Amharic speakers. 
        |You can understand and respond in both Amharic (አማርኛ) and English.
        |Be helpful, friendly, and culturally respectful.
        |You are running completely offline on the user's device.""".trimMargin()
    
    init {
        // Initialize TTS
        voiceService.initializeTts { success ->
            if (success) {
                addSystemMessage("Voice output enabled ✓")
            }
        }
        
        // Add welcome message
        addSystemMessage("ሰላም! Welcome! I'm your offline AI assistant.")
    }
    
    /**
     * Initialize the AI model
     */
    fun initializeModel() {
        viewModelScope.launch {
            _uiState.update { it.copy(modelState = ModelState.Loading) }
            
            val success = modelInference.initialize()
            
            _uiState.update {
                it.copy(
                    modelState = if (success) {
                        ModelState.Ready
                    } else {
                        ModelState.Error("Failed to load model")
                    }
                )
            }
            
            if (success) {
                addSystemMessage("AI model loaded successfully! You can start chatting.")
            }
        }
    }
    
    /**
     * Send a text message
     */
    fun sendMessage(text: String) {
        if (text.isBlank()) return
        
        val userMessage = Message(
            content = text,
            role = MessageRole.USER
        )
        
        _uiState.update {
            it.copy(
                messages = it.messages + userMessage,
                currentInput = "",
                isGenerating = true
            )
        }
        
        // Generate response
        viewModelScope.launch {
            try {
                val response = modelInference.generate(
                    prompt = text,
                    systemPrompt = systemPrompt
                )
                
                val assistantMessage = Message(
                    content = response,
                    role = MessageRole.ASSISTANT
                )
                
                _uiState.update {
                    it.copy(
                        messages = it.messages + assistantMessage,
                        isGenerating = false
                    )
                }
                
            } catch (e: Exception) {
                val errorMessage = Message(
                    content = "Sorry, I encountered an error: ${e.message}",
                    role = MessageRole.ASSISTANT
                )
                
                _uiState.update {
                    it.copy(
                        messages = it.messages + errorMessage,
                        isGenerating = false
                    )
                }
            }
        }
    }
    
    /**
     * Start voice input
     */
    fun startVoiceInput(language: String = "am") {
        _uiState.update { it.copy(isListening = true) }
        
        viewModelScope.launch {
            voiceService.startListening(language).collect { result ->
                when (result) {
                    is VoiceResult.Success -> {
                        _uiState.update { it.copy(isListening = false) }
                        sendMessage(result.text)
                    }
                    is VoiceResult.Error -> {
                        _uiState.update { it.copy(isListening = false) }
                        addSystemMessage("Voice error: ${result.message}")
                    }
                    is VoiceResult.Listening -> {
                        // Already in listening state
                    }
                    is VoiceResult.Ready -> {
                        // Ready to listen
                    }
                }
            }
        }
    }
    
    /**
     * Stop voice input
     */
    fun stopVoiceInput() {
        voiceService.stopListening()
        _uiState.update { it.copy(isListening = false) }
    }
    
    /**
     * Speak a message using TTS
     */
    fun speakMessage(text: String, language: String = "am") {
        voiceService.speak(text, language)
    }
    
    /**
     * Update current input text
     */
    fun updateInput(text: String) {
        _uiState.update { it.copy(currentInput = text) }
    }
    
    /**
     * Clear conversation
     */
    fun clearConversation() {
        _uiState.update {
            it.copy(messages = emptyList())
        }
        addSystemMessage("Conversation cleared")
    }
    
    /**
     * Add a system message
     */
    private fun addSystemMessage(text: String) {
        val systemMessage = Message(
            content = text,
            role = MessageRole.SYSTEM
        )
        
        _uiState.update {
            it.copy(messages = it.messages + systemMessage)
        }
    }
    
    override fun onCleared() {
        super.onCleared()
        modelInference.release()
        voiceService.release()
    }
}
