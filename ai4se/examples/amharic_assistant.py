"""
Amharic Voice Assistant - General Purpose

A complete offline voice assistant for Amharic speakers using pre-trained models:
- Speech-to-Text: OpenAI Whisper (supports Amharic)
- Language Model: Qwen2.5-1.5B-Instruct or Llama-3.2-1B (multilingual)
- Text-to-Speech: Piper TTS (Amharic voice)

Use cases:
- General conversation and questions
- Translation (Amharic ↔ English)
- Education and learning
- Information lookup
- Daily assistance

Requirements:
    pip install openai-whisper transformers torch piper-tts soundfile
"""

import whisper
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import os
from typing import Optional

class AmharicAssistant:
    """
    General-purpose Amharic voice assistant using pre-trained models.
    No fine-tuning required - works out of the box!
    """

    def __init__(
        self,
        stt_model_size: str = "small",
        llm_model_name: str = "Qwen/Qwen2.5-1.5B-Instruct",
        device: str = "auto"
    ):
        """
        Initialize the Amharic Assistant

        Args:
            stt_model_size: Whisper model size
                - 'tiny' (39M): Fastest, basic accuracy
                - 'base' (74M): Good balance
                - 'small' (244M): Recommended for Amharic
                - 'medium' (769M): Better accuracy
                - 'large' (1.5G): Best accuracy
            llm_model_name: Pre-trained model to use
                - "Qwen/Qwen2.5-1.5B-Instruct" (recommended)
                - "meta-llama/Llama-3.2-1B-Instruct"
                - "meta-llama/Llama-3.2-3B-Instruct"
            device: 'auto', 'cuda', or 'cpu'
        """
        self.device = self._setup_device(device)
        self._load_models(stt_model_size, llm_model_name)
        self.conversation_history = []

    def _setup_device(self, device: str) -> str:
        """Determine the best device to use"""
        if device == "auto":
            return "cuda" if torch.cuda.is_available() else "cpu"
        return device

    def _load_models(self, stt_size: str, llm_name: str):
        """Load all required models"""
        
        print(f"Loading models on {self.device}...")
        
        # 1. Speech-to-Text (Whisper)
        print(f"  • Loading Whisper-{stt_size} for Amharic STT...")
        self.stt_model = whisper.load_model(stt_size, device=self.device)
        
        # 2. Language Model (pre-trained, no fine-tuning)
        print(f"  • Loading {llm_name}...")
        self.tokenizer = AutoTokenizer.from_pretrained(llm_name)
        self.llm = AutoModelForCausalLM.from_pretrained(
            llm_name,
            torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
            device_map="auto" if self.device == "cuda" else None,
            low_cpu_mem_usage=True
        )
        
        if self.device == "cpu":
            self.llm = self.llm.to(self.device)
        
        print("✅ All models loaded successfully!")

    def transcribe_audio(self, audio_path: str, language: str = "am") -> str:
        """
        Convert speech to text
        
        Args:
            audio_path: Path to audio file (wav, mp3, etc.)
            language: Language code ('am' for Amharic, 'en' for English)
        
        Returns:
            Transcribed text
        """
        result = self.stt_model.transcribe(
            audio_path,
            language=language,
            task="transcribe"
        )
        return result["text"].strip()

    def chat(self, user_message: str, system_prompt: Optional[str] = None) -> str:
        """
        Have a conversation with the assistant
        
        Args:
            user_message: The user's message (in Amharic or English)
            system_prompt: Optional system instruction
        
        Returns:
            Assistant's response
        """
        # Add to conversation history
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })
        
        # Prepare messages
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.extend(self.conversation_history)
        
        # Generate response
        text = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )
        
        inputs = self.tokenizer([text], return_tensors="pt").to(self.device)
        
        with torch.no_grad():
            outputs = self.llm.generate(
                **inputs,
                max_new_tokens=512,
                temperature=0.7,
                top_p=0.9,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id
            )
        
        response = self.tokenizer.decode(
            outputs[0][inputs['input_ids'].shape[1]:],
            skip_special_tokens=True
        )
        
        # Add to history
        self.conversation_history.append({
            "role": "assistant",
            "content": response
        })
        
        return response

    def translate(self, text: str, from_lang: str, to_lang: str) -> str:
        """
        Translate text between languages
        
        Args:
            text: Text to translate
            from_lang: Source language (e.g., 'Amharic', 'English')
            to_lang: Target language
        
        Returns:
            Translated text
        """
        prompt = f"Translate from {from_lang} to {to_lang}: {text}"
        return self.chat(prompt)

    def voice_to_voice(self, audio_path: str, language: str = "am") -> str:
        """
        Complete voice pipeline: audio in → text response out
        
        Args:
            audio_path: Path to audio file
            language: Language code for STT
        
        Returns:
            Text response (can be converted to speech with TTS)
        """
        # 1. Speech to text
        user_text = self.transcribe_audio(audio_path, language)
        print(f"User said: {user_text}")
        
        # 2. Generate response
        response = self.chat(user_text)
        print(f"Assistant: {response}")
        
        return response

    def reset_conversation(self):
        """Clear conversation history"""
        self.conversation_history = []
        print("Conversation history cleared.")


def main():
    """Example usage"""
    
    print("=" * 60)
    print("Amharic Voice Assistant - General Purpose")
    print("=" * 60)
    
    # Initialize assistant
    assistant = AmharicAssistant(
        stt_model_size="small",  # Good balance of speed/accuracy
        llm_model_name="Qwen/Qwen2.5-1.5B-Instruct",
        device="auto"
    )
    
    print("\n" + "=" * 60)
    print("Examples")
    print("=" * 60)
    
    # Example 1: Text conversation
    print("\n1. General Conversation:")
    print("-" * 40)
    response = assistant.chat("ሰላም! እንዴት ነህ?")  # "Hello! How are you?"
    print(f"Response: {response}")
    
    # Example 2: Translation
    print("\n2. Translation:")
    print("-" * 40)
    assistant.reset_conversation()
    response = assistant.translate(
        "The weather is nice today",
        from_lang="English",
        to_lang="Amharic"
    )
    print(f"Translation: {response}")
    
    # Example 3: Question answering
    print("\n3. Question Answering:")
    print("-" * 40)
    assistant.reset_conversation()
    response = assistant.chat("What are the capital cities of Ethiopia?")
    print(f"Answer: {response}")
    
    # Example 4: Voice (if you have audio file)
    print("\n4. Voice Input:")
    print("-" * 40)
    audio_file = "test_audio.wav"
    if os.path.exists(audio_file):
        assistant.reset_conversation()
        response = assistant.voice_to_voice(audio_file, language="am")
    else:
        print(f"Skipped: {audio_file} not found")
    
    print("\n" + "=" * 60)
    print("Assistant ready! No training needed - works out of the box!")
    print("=" * 60)


if __name__ == "__main__":
    main()
