package org.helpchildren.amharic

import android.Manifest
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.result.contract.ActivityResultContracts
import androidx.activity.viewModels
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.lazy.rememberLazyListState
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import org.helpchildren.amharic.data.Message
import org.helpchildren.amharic.data.MessageRole
import org.helpchildren.amharic.data.ModelState
import org.helpchildren.amharic.ui.ChatViewModel
import org.helpchildren.amharic.ui.theme.AmharicAssistantTheme

class MainActivity : ComponentActivity() {
    
    private val viewModel: ChatViewModel by viewModels()
    
    private val micPermissionLauncher = registerForActivityResult(
        ActivityResultContracts.RequestPermission()
    ) { isGranted ->
        if (isGranted) {
            viewModel.startVoiceInput()
        }
    }
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        // Initialize model on startup
        viewModel.initializeModel()
        
        setContent {
            AmharicAssistantTheme {
                ChatScreen(
                    viewModel = viewModel,
                    onRequestMicPermission = {
                        micPermissionLauncher.launch(Manifest.permission.RECORD_AUDIO)
                    }
                )
            }
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ChatScreen(
    viewModel: ChatViewModel,
    onRequestMicPermission: () -> Unit
) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()
    val listState = rememberLazyListState()
    
    // Auto-scroll to bottom when new messages arrive
    LaunchedEffect(uiState.messages.size) {
        if (uiState.messages.isNotEmpty()) {
            listState.animateScrollToItem(uiState.messages.size - 1)
        }
    }
    
    Scaffold(
        topBar = {
            TopAppBar(
                title = { 
                    Column {
                        Text("Amharic Assistant")
                        Text(
                            text = when (uiState.modelState) {
                                is ModelState.Ready -> "✓ Ready (Offline)"
                                is ModelState.Loading -> "⏳ Loading..."
                                is ModelState.Error -> "⚠ Error"
                                is ModelState.NotLoaded -> "Not loaded"
                            },
                            style = MaterialTheme.typography.bodySmall
                        )
                    }
                },
                actions = {
                    IconButton(onClick = { viewModel.clearConversation() }) {
                        Icon(Icons.Default.Delete, "Clear chat")
                    }
                }
            )
        }
    ) { paddingValues ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues)
        ) {
            // Messages list
            LazyColumn(
                state = listState,
                modifier = Modifier
                    .weight(1f)
                    .fillMaxWidth(),
                contentPadding = PaddingValues(16.dp),
                verticalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                items(uiState.messages) { message ->
                    MessageBubble(message, onSpeak = { text ->
                        viewModel.speakMessage(text)
                    })
                }
                
                if (uiState.isGenerating) {
                    item {
                        CircularProgressIndicator(
                            modifier = Modifier
                                .size(24.dp)
                                .padding(8.dp)
                        )
                    }
                }
            }
            
            // Example prompts (show when no messages)
            if (uiState.messages.isEmpty() && uiState.modelState is ModelState.Ready) {
                ExamplePrompts(
                    onExampleClick = { viewModel.sendMessage(it) }
                )
            }
            
            // Input area
            Surface(
                shadowElevation = 8.dp,
                tonalElevation = 3.dp
            ) {
                InputArea(
                    text = uiState.currentInput,
                    onTextChange = { viewModel.updateInput(it) },
                    onSend = { viewModel.sendMessage(uiState.currentInput) },
                    onVoiceClick = { onRequestMicPermission() },
                    isListening = uiState.isListening,
                    enabled = uiState.modelState is ModelState.Ready && !uiState.isGenerating
                )
            }
        }
    }
}

@Composable
fun MessageBubble(
    message: Message,
    onSpeak: (String) -> Unit
) {
    val alignment = when (message.role) {
        MessageRole.USER -> Alignment.End
        MessageRole.ASSISTANT -> Alignment.Start
        MessageRole.SYSTEM -> Alignment.CenterHorizontally
    }
    
    val backgroundColor = when (message.role) {
        MessageRole.USER -> MaterialTheme.colorScheme.primaryContainer
        MessageRole.ASSISTANT -> MaterialTheme.colorScheme.secondaryContainer
        MessageRole.SYSTEM -> MaterialTheme.colorScheme.tertiaryContainer
    }
    
    Box(
        modifier = Modifier.fillMaxWidth(),
        contentAlignment = alignment
    ) {
        Card(
            colors = CardDefaults.cardColors(containerColor = backgroundColor),
            modifier = Modifier.widthIn(max = 300.dp)
        ) {
            Row(
                modifier = Modifier.padding(12.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = message.content,
                    modifier = Modifier.weight(1f),
                    style = MaterialTheme.typography.bodyMedium
                )
                
                if (message.role == MessageRole.ASSISTANT) {
                    IconButton(
                        onClick = { onSpeak(message.content) },
                        modifier = Modifier.size(32.dp)
                    ) {
                        Icon(
                            Icons.Default.VolumeUp,
                            contentDescription = "Speak",
                            modifier = Modifier.size(18.dp)
                        )
                    }
                }
            }
        }
    }
}

@Composable
fun ExamplePrompts(
    onExampleClick: (String) -> Unit
) {
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .padding(16.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.spacedBy(8.dp)
    ) {
        Text(
            "💡 Try these examples:",
            style = MaterialTheme.typography.titleSmall,
            color = MaterialTheme.colorScheme.primary
        )
        
        val examples = listOf(
            "ሰላም! እንዴት ነህ?",
            "Translate 'Good morning' to Amharic",
            "What is the capital of Ethiopia?",
            "Tell me about Ethiopian coffee"
        )
        
        examples.forEach { example ->
            AssistChip(
                onClick = { onExampleClick(example) },
                label = { Text(example, style = MaterialTheme.typography.bodySmall) }
            )
        }
    }
}

@Composable
fun InputArea(
    text: String,
    onTextChange: (String) -> Unit,
    onSend: () -> Unit,
    onVoiceClick: () -> Unit,
    isListening: Boolean,
    enabled: Boolean
) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(16.dp),
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.spacedBy(8.dp)
    ) {
        OutlinedTextField(
            value = text,
            onValueChange = onTextChange,
            modifier = Modifier.weight(1f),
            placeholder = { Text("Type your message…") },
            enabled = enabled,
            maxLines = 4
        )
        
        IconButton(
            onClick = onVoiceClick,
            enabled = enabled
        ) {
            Icon(
                if (isListening) Icons.Default.MicOff else Icons.Default.Mic,
                contentDescription = "Voice input",
                tint = if (isListening) MaterialTheme.colorScheme.error 
                       else MaterialTheme.colorScheme.primary
            )
        }
        
        IconButton(
            onClick = onSend,
            enabled = enabled && text.isNotBlank()
        ) {
            Icon(
                Icons.Default.Send,
                contentDescription = "Send"
            )
        }
    }
}
