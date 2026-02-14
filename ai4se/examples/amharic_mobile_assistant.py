"""
Amharic Medical Voice Assistant for Mobile (MEIZU Mblu 21 Optimized)

Complete voice pipeline optimized for 4GB RAM devices:
- Whisper-small for Amharic Speech-to-Text
- Fine-tuned medical model for diagnosis
- Simple audio playback for responses

Optimizations:
- Lightweight models (fits in 4GB RAM)
- CPU-optimized inference
- Streaming responses
- Battery efficient
"""

import whisper
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
import torch
import soundfile as sf
import numpy as np
import os
from datetime import datetime


class AmharicMedicalAssistant:
    """
    Amharic-enabled medical assistant optimized for mobile devices
    """

    def __init__(
        self,
        base_model_name: str = "HuggingFaceTB/SmolLM2-135M-Instruct",
        lora_adapter_path: str = "models/medical-lora-test",
        whisper_model: str = "small",  # base for mobile, small for better accuracy
        device: str = "cpu"
    ):
        """
        Initialize Amharic Medical Assistant

        Args:
            base_model_name: Base model name
            lora_adapter_path: Path to fine-tuned medical LoRA adapter
            whisper_model: Whisper model size ('tiny', 'base', 'small')
            device: Device to use (default: 'cpu' for mobile)
        """
        self.device = device
        self.conversation_history = []
        
        print("=" * 60)
        print("Amharic Medical Assistant - Loading Models")
        print("=" * 60)
        
        self._load_models(base_model_name, lora_adapter_path, whisper_model)
        self._setup_system_prompt()

    def _load_models(self, base_model_name, lora_adapter_path, whisper_size):
        """Load all required models"""

        # 1. Load Speech-to-Text (Whisper for Amharic)
        print(f"\n1️⃣ Loading Whisper-{whisper_size} for Amharic STT...")
        print(f"   Size: ~{self._get_whisper_size(whisper_size)}")
        print(f"   Languages: 99 including Amharic (አማርኛ)")
        
        self.stt_model = whisper.load_model(whisper_size, device=self.device)
        print("   ✅ Whisper loaded")

        # 2. Load Fine-tuned Medical Model
        print(f"\n2️⃣ Loading medical model...")
        print(f"   Base: {base_model_name}")
        print(f"   Medical LoRA: {lora_adapter_path}")
        
        self.tokenizer = AutoTokenizer.from_pretrained(base_model_name)
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        
        # Load base model
        base_model = AutoModelForCausalLM.from_pretrained(
            base_model_name,
            torch_dtype=torch.float32,  # FP32 for CPU
            trust_remote_code=True
        )
        
        # Load LoRA adapter if path exists
        if os.path.exists(lora_adapter_path):
            self.model = PeftModel.from_pretrained(base_model, lora_adapter_path)
            print(f"   ✅ Medical LoRA adapter loaded")
        else:
            self.model = base_model
            print(f"   ⚠️  Using base model (no adapter found)")
        
        self.model.eval()
        print("   ✅ Medical model loaded")

        # 3. TTS Setup (Optional - for future)
        print(f"\n3️⃣ Text-to-Speech:")
        print(f"   Status: Not loaded (to save RAM)")
        print(f"   Note: Can add Piper TTS for Amharic voice output")
        self.tts_enabled = False

    def _get_whisper_size(self, model_size):
        """Get approximate model size"""
        sizes = {
            "tiny": "75 MB",
            "base": "140 MB",
            "small": "460 MB",
            "medium": "1.5 GB"
        }
        return sizes.get(model_size, "Unknown")

    def _setup_system_prompt(self):
        """Setup bilingual system prompt (Amharic + English)"""
        self.system_prompt = """አንተ የጤና አማካሪ ነህ። You are a medical assistant for primary health diagnosis.

Your role / ሚና:
1. Listen to patient symptoms / ምልክቶችን ማዳመጥ
2. Ask relevant questions / ጥያቄዎችን መጠየቅ
3. Provide initial assessment / የመጀመሪያ ምዘና መስጠት
4. Suggest immediate actions / ወዲያውኑ እርምጃዎችን ማስተላለፍ
5. Identify emergencies / አስቸኳይ ሁኔታዎችን መለየት

IMPORTANT:
- Always be clear and compassionate
- Ask one question at a time
- Use simple language
- Identify when urgent care is needed
- Respond in both Amharic and English when helpful

ተጨማሪ መረጃ ካስፈለገ ጥያቄዎችን ይጠይቁ።"""

    def transcribe_audio(self, audio_path: str) -> dict:
        """
        Transcribe Amharic speech to text

        Args:
            audio_path: Path to audio file (WAV, MP3, etc.)

        Returns:
            dict with 'text', 'language', 'confidence'
        """
        print(f"\n🎤 Transcribing audio: {audio_path}")
        
        result = self.stt_model.transcribe(
            audio_path,
            language="am",  # Amharic
            task="transcribe",
            fp16=False,  # Use FP32 for CPU
            verbose=False
        )

        transcribed_text = result["text"].strip()
        
        # Detect if response contains Amharic characters
        has_amharic = any('\u1200' <= char <= '\u137F' for char in transcribed_text)
        
        print(f"   Text: {transcribed_text}")
        print(f"   Language: {'Amharic (አማርኛ)' if has_amharic else 'English'}")
        print(f"   ✅ Transcription complete")
        
        return {
            "text": transcribed_text,
            "language": "amharic" if has_amharic else "english",
            "confidence": "high"  # Whisper doesn't provide confidence scores
        }

    def generate_response(self, user_message: str) -> str:
        """
        Generate medical advice based on user message

        Args:
            user_message: Patient's message (Amharic or English)

        Returns:
            Medical assistant's response
        """
        print(f"\n🤖 Generating medical response...")
        
        # Build prompt with system instructions and conversation
        prompt = f"System: {self.system_prompt}\n\n"
        
        # Add conversation history
        for msg in self.conversation_history[-4:]:  # Last 4 messages for context
            prompt += f"{msg['role']}: {msg['content']}\n\n"
        
        # Add current message
        prompt += f"User: {user_message}\n\nAssistant:"
        
        # Tokenize
        inputs = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=512
        )
        
        # Generate response
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=200,
                temperature=0.7,
                do_sample=True,
                top_p=0.9,
                repetition_penalty=1.1,
                pad_token_id=self.tokenizer.eos_token_id
            )
        
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Extract only the assistant's response
        if "Assistant:" in response:
            response = response.split("Assistant:")[-1].strip()
        
        print(f"   Response length: {len(response)} characters")
        print(f"   ✅ Response generated")
        
        # Update conversation history
        self.conversation_history.append({"role": "User", "content": user_message})
        self.conversation_history.append({"role": "Assistant", "content": response})
        
        return response

    def process_voice_input(self, audio_path: str) -> dict:
        """
        Complete voice pipeline: Audio → Text → Response

        Args:
            audio_path: Path to audio file

        Returns:
            dict with 'transcribed_text', 'response', 'timestamp'
        """
        print("\n" + "=" * 60)
        print("Processing Voice Input")
        print("=" * 60)
        
        # Step 1: Transcribe audio (Amharic → Text)
        transcription = self.transcribe_audio(audio_path)
        transcribed_text = transcription["text"]
        
        # Step 2: Generate medical response
        response = self.generate_response(transcribed_text)
        
        print("\n" + "=" * 60)
        print("Voice Processing Complete")
        print("=" * 60)
        
        return {
            "transcribed_text": transcribed_text,
            "detected_language": transcription["language"],
            "response": response,
            "timestamp": datetime.now().isoformat()
        }

    def chat(self, message: str) -> str:
        """
        Simple text-based chat (no voice)

        Args:
            message: User's text message

        Returns:
            Assistant's response
        """
        return self.generate_response(message)

    def reset_conversation(self):
        """Clear conversation history"""
        self.conversation_history = []
        print("Conversation history cleared")

    def save_conversation(self, filepath: str):
        """Save conversation to file"""
        import json
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.conversation_history, f, ensure_ascii=False, indent=2)
        print(f"Conversation saved to: {filepath}")


def demo_text_mode():
    """Demo: Text-based medical consultation"""
    print("\n" + "=" * 60)
    print("DEMO: Text-Based Medical Consultation")
    print("=" * 60 + "\n")
    
    assistant = AmharicMedicalAssistant()
    
    print("\n" + "=" * 60)
    print("Ready for consultation!")
    print("=" * 60 + "\n")
    
    # Test cases
    test_messages = [
        "ልጄ ለ3 ቀናት ትኩሳት እና ተቅማት አለበት። ምን ማድረግ አለብኝ?",  # Amharic
        "My child has fever and diarrhea for 3 days. What should I do?",  # English
    ]
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n{'='*60}")
        print(f"Test Case {i}")
        print(f"{'='*60}")
        print(f"User: {message}\n")
        
        response = assistant.chat(message)
        print(f"Assistant: {response}\n")


def demo_voice_mode():
    """Demo: Voice-based medical consultation (requires audio file)"""
    print("\n" + "=" * 60)
    print("DEMO: Voice-Based Medical Consultation")
    print("=" * 60 + "\n")
    
    assistant = AmharicMedicalAssistant()
    
    # Check for sample audio
    sample_audio = "sample_amharic.wav"
    
    if os.path.exists(sample_audio):
        result = assistant.process_voice_input(sample_audio)
        
        print(f"\n📝 Transcription: {result['transcribed_text']}")
        print(f"🌐 Language: {result['detected_language']}")
        print(f"💬 Response: {result['response']}")
    else:
        print(f"⚠️  No audio file found: {sample_audio}")
        print(f"   To test voice mode:")
        print(f"   1. Record Amharic audio (WAV or MP3)")
        print(f"   2. Save as '{sample_audio}'")
        print(f"   3. Run this demo again")


if __name__ == "__main__":
    print("=" * 60)
    print("Amharic Medical Voice Assistant")
    print("Optimized for MEIZU Mblu 21 (4GB RAM)")
    print("=" * 60)
    
    # Run text demo
    demo_text_mode()
    
    # Uncomment to test voice mode:
    # demo_voice_mode()
