package org.helpchildren.amharic.data

/**
 * Represents a single message in the conversation
 */
data class Message(
    val content: String,
    val role: MessageRole,
    val timestamp: Long = System.currentTimeMillis()
)

enum class MessageRole {
    USER,
    ASSISTANT,
    SYSTEM
}

/**
 * Model state
 */
sealed class ModelState {
    object NotLoaded : ModelState()
    object Loading : ModelState()
    object Ready : ModelState()
    data class Error(val message: String) : ModelState()
}

/**
 * UI state for the chat screen
 */
data class ChatUiState(
    val messages: List<Message> = emptyList(),
    val modelState: ModelState = ModelState.NotLoaded,
    val isGenerating: Boolean = false,
    val isListening: Boolean = false,
    val currentInput: String = ""
)
