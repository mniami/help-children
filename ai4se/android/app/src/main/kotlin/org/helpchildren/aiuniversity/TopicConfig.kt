package org.helpchildren.aiuniversity

import java.util.Locale

/** Configuration for one knowledge topic (system prompt + display metadata). */
data class TopicConfig(
    val id: String,
    val displayName: String,
    val emoji: String,
    /** Background color as an ARGB hex string, e.g. "#C62828". */
    val colorHex: String,
    val systemPrompt: String,
    val welcomeMessage: String,
)

val TOPICS = listOf(
    TopicConfig(
        id = "health",
        displayName = "Health",
        emoji = "🏥",
        colorHex = "#C62828",
        systemPrompt = """
            You are a village health advisor. You provide general health information and
            first aid guidance only — you are NOT a doctor and cannot diagnose or prescribe.
            Always remind users that serious symptoms require a real medical professional.
            Use simple, kind language and keep answers short.
        """.trimIndent(),
        welcomeMessage = "Hello! Tell me about your health concern.",
    ),
    TopicConfig(
        id = "education",
        displayName = "Education",
        emoji = "📖",
        colorHex = "#1565C0",
        systemPrompt = """
            You are a friendly teacher. Help people learn to read, count, and understand
            the world around them. Use very simple explanations and real-life examples.
            Encourage and motivate the learner. Keep answers short.
        """.trimIndent(),
        welcomeMessage = "Hello! What would you like to learn today?",
    ),
    TopicConfig(
        id = "farming",
        displayName = "Farming",
        emoji = "🌾",
        colorHex = "#2E7D32",
        systemPrompt = """
            You are an experienced farmer and agricultural advisor. Help with crop growing,
            soil health, pest control, weather patterns, and livestock care. Give practical
            advice using local methods and materials. Keep answers short.
        """.trimIndent(),
        welcomeMessage = "Hello! How can I help with your farm?",
    ),
    TopicConfig(
        id = "rights",
        displayName = "Rights & Law",
        emoji = "⚖️",
        colorHex = "#4A148C",
        systemPrompt = """
            You are a community rights advisor. Explain basic human rights and legal
            processes in very simple terms. Help people understand their rights and
            how to protect themselves and their families. Keep answers short.
        """.trimIndent(),
        welcomeMessage = "Hello! Ask me about your rights.",
    ),
    TopicConfig(
        id = "emergency",
        displayName = "Emergency",
        emoji = "🆘",
        colorHex = "#E65100",
        systemPrompt = """
            You are an emergency response guide. Provide clear, step-by-step instructions
            for life-threatening situations: injuries, fire, floods, dangerous animals.
            Be calm, direct, and concise. Prioritise the most urgent action first.
        """.trimIndent(),
        welcomeMessage = "Hello! Describe the emergency and I will help immediately.",
    ),
    TopicConfig(
        id = "general",
        displayName = "Anything",
        emoji = "💬",
        colorHex = "#37474F",
        systemPrompt = """
            You are a helpful, knowledgeable friend — like a portable university.
            Answer any question with patience, clarity, and respect.
            Use the simplest possible language and helpful examples. Keep answers short.
        """.trimIndent(),
        welcomeMessage = "Hello! Ask me anything — I am here to help.",
    ),
)

/** A spoken language the user can select. */
data class LanguageOption(val displayName: String, val locale: Locale)

val LANGUAGES = listOf(
    LanguageOption("🇬🇧 English", Locale.ENGLISH),
    LanguageOption("🇪🇹 Amharic", Locale("am", "ET")),
    LanguageOption("🇰🇪 Swahili", Locale("sw", "KE")),
    LanguageOption("🇫🇷 Français", Locale.FRANCE),
    LanguageOption("🇸🇦 Arabic", Locale("ar", "SA")),
)
