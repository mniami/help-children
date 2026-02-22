package org.helpchildren.amharic.ml

import android.content.Context
import android.util.Log
import ai.onnxruntime.OnnxTensor
import ai.onnxruntime.OrtEnvironment
import ai.onnxruntime.OrtSession
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import java.io.File
import java.nio.LongBuffer

/**
 * ONNX Runtime-based inference engine for Qwen/Llama models
 * Optimized for mobile devices with INT4 quantization
 */
class ModelInference(private val context: Context) {
    
    private var ortEnvironment: OrtEnvironment? = null
    private var session: OrtSession? = null
    private var tokenizer: SimpleTokenizer? = null
    
    private val maxSequenceLength = 512
    private val maxNewTokens = 256
    
    companion object {
        private const val TAG = "ModelInference"
        private const val MODEL_NAME = "qwen-1.5b-instruct-q4.onnx"
        private const val VOCAB_FILE = "tokenizer.json"
    }
    
    /**
     * Initialize the model (call this on app startup or when model is downloaded)
     */
    suspend fun initialize(): Boolean = withContext(Dispatchers.IO) {
        try {
            Log.d(TAG, "Initializing ONNX Runtime...")
            
            // Check if model file exists
            val modelFile = File(context.filesDir, "models/$MODEL_NAME")
            if (!modelFile.exists()) {
                Log.e(TAG, "Model file not found: ${modelFile.absolutePath}")
                return@withContext false
            }
            
            // Initialize ONNX Runtime environment
            ortEnvironment = OrtEnvironment.getEnvironment()
            
            // Create session options for mobile optimization
            val sessionOptions = OrtSession.SessionOptions().apply {
                // Use all available CPU cores
                setIntraOpNumThreads(Runtime.getRuntime().availableProcessors())
                setInterOpNumThreads(Runtime.getRuntime().availableProcessors())
                
                // Memory optimization for mobile
                setOptimizationLevel(OrtSession.SessionOptions.OptLevel.ALL_OPT)
            }
            
            // Load model
            session = ortEnvironment?.createSession(
                modelFile.absolutePath,
                sessionOptions
            )
            
            // Load tokenizer
            val vocabFile = File(context.filesDir, "models/$VOCAB_FILE")
            if (vocabFile.exists()) {
                tokenizer = SimpleTokenizer(vocabFile)
            } else {
                Log.w(TAG, "Tokenizer file not found, using fallback")
                tokenizer = SimpleTokenizer.createFallback()
            }
            
            Log.d(TAG, "Model initialized successfully")
            true
            
        } catch (e: Exception) {
            Log.e(TAG, "Failed to initialize model", e)
            false
        }
    }
    
    /**
     * Generate response for a given prompt
     */
    suspend fun generate(
        prompt: String,
        systemPrompt: String? = null,
        onTokenGenerated: ((String) -> Unit)? = null
    ): String = withContext(Dispatchers.IO) {
        
        if (session == null || tokenizer == null) {
            throw IllegalStateException("Model not initialized")
        }
        
        try {
            // Format prompt with system message if provided
            val fullPrompt = buildPrompt(prompt, systemPrompt)
            
            // Tokenize input
            val inputIds = tokenizer!!.encode(fullPrompt)
            
            // Prepare input tensor
            val inputTensor = createInputTensor(inputIds)
            
            // Run inference
            val outputs = session!!.run(mapOf("input_ids" to inputTensor))
            
            // Decode output tokens
            val outputTensor = outputs[0].value as Array<*>
            val outputIds = (outputTensor[0] as LongArray).toList()
            
            val generatedText = tokenizer!!.decode(outputIds)
            
            // Clean up
            inputTensor.close()
            outputs.close()
            
            generatedText
            
        } catch (e: Exception) {
            Log.e(TAG, "Generation failed", e)
            "Sorry, I encountered an error processing your request."
        }
    }
    
    private fun buildPrompt(userMessage: String, systemPrompt: String?): String {
        // Qwen2.5 chat template
        val system = systemPrompt ?: "You are a helpful AI assistant for Amharic speakers."
        return """<|im_start|>system
$system<|im_end|>
<|im_start|>user
$userMessage<|im_end|>
<|im_start|>assistant
"""
    }
    
    private fun createInputTensor(tokens: List<Long>): OnnxTensor {
        val env = ortEnvironment ?: throw IllegalStateException("ORT environment not initialized")
        
        // Pad or truncate to max sequence length
        val paddedTokens = tokens.take(maxSequenceLength).toLongArray()
        val buffer = LongBuffer.wrap(paddedTokens)
        
        return OnnxTensor.createTensor(
            env,
            buffer,
            longArrayOf(1, paddedTokens.size.toLong())
        )
    }
    
    /**
     * Clean up resources
     */
    fun release() {
        session?.close()
        session = null
        ortEnvironment = null
    }
}

/**
 * Simple tokenizer (for demo purposes - in production, use HuggingFace tokenizers library)
 */
class SimpleTokenizer(vocabFile: File? = null) {
    
    private val vocab: Map<String, Long> = loadVocab(vocabFile)
    private val reverseVocab: Map<Long, String> = vocab.entries.associate { it.value to it.key }
    
    fun encode(text: String): List<Long> {
        // Simple whitespace tokenization (replace with proper BPE in production)
        return text.split(" ").mapNotNull { token ->
            vocab[token] ?: vocab["<unk>"]
        }
    }
    
    fun decode(tokens: List<Long>): String {
        return tokens.mapNotNull { reverseVocab[it] }
            .joinToString(" ")
            .replace(" ##", "") // Handle subword tokens
    }
    
    private fun loadVocab(file: File?): Map<String, Long> {
        // In production, parse tokenizer.json from HuggingFace
        // For now, return a minimal vocab
        return mapOf(
            "<unk>" to 0L,
            "<s>" to 1L,
            "</s>" to 2L,
            "<|im_start|>" to 3L,
            "<|im_end|>" to 4L
        )
    }
    
    companion object {
        fun createFallback() = SimpleTokenizer(null)
    }
}
