"""
Amharic Health Assistant - Complete Voice Pipeline

This script demonstrates the full Amharic voice pipeline:
- Speech-to-Text (Whisper)
- Language Model Processing (Llama-3.2-3B)
- Text-to-Speech (Piper)

Requirements:
    pip install openai-whisper transformers torch piper-tts soundfile
"""

import whisper
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import wave
import os
from typing import Dict

class AmharicHealthAssistant:
    """
    Complete Amharic voice-enabled health assistant using:
    - Whisper for STT
    - Llama-3.2-3B for dialogue
    - Piper for TTS
    """

    def __init__(
        self,
        stt_model_size: str = "small",
        llm_model_name: str = "meta-llama/Llama-3.2-3B-Instruct",
        tts_model_path: str = None,
        device: str = "auto"
    ):
        """
        Initialize the Amharic Health Assistant

        Args:
            stt_model_size: Whisper model size ('tiny', 'base', 'small', 'medium', 'large')
            llm_model_name: HuggingFace model name or path
            tts_model_path: Path to Piper TTS model (ONNX)
            device: Device to use ('auto', 'cuda', 'cpu')
        """
        self.device = device
        self._load_models(stt_model_size, llm_model_name, tts_model_path)

    def _load_models(self, stt_size, llm_name, tts_path):
        """Load all required models"""

        # 1. Load Speech-to-Text (Whisper)
        print(f"Loading STT model (Whisper-{stt_size})...")
        self.stt_model = whisper.load_model(stt_size)
        print("✓ STT model loaded")

        # 2. Load Language Model
        print(f"Loading LLM ({llm_name})...")
        self.llm_tokenizer = AutoTokenizer.from_pretrained(llm_name)
        self.llm_model = AutoModelForCausalLM.from_pretrained(
            llm_name,
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            device_map=self.device,
            low_cpu_mem_usage=True
        )
        print("✓ LLM model loaded")

        # 3. Load Text-to-Speech (Piper)
        print("Loading TTS model (Piper Amharic)...")
        if tts_path and os.path.exists(tts_path):
            try:
                from piper import PiperVoice
                self.tts_voice = PiperVoice.load(tts_path)
                print("✓ TTS model loaded")
            except ImportError:
                print("⚠ Piper not installed. Install with: pip install piper-tts")
                self.tts_voice = None
        else:
            print("⚠ TTS model not found. Download from:")
            print("  https://github.com/rhasspy/piper/releases/download/v1.2.0/am_ET-mekonnen-medium.tar.gz")
            self.tts_voice = None

        # System prompt for medical assistant
        self.system_prompt = """አንተ የጤና አማካሪ ነህ። የታካሚውን ምልክቶች መረዳት እና መጀመሪያ ላይ ምክር መስጠት አለብህ።

You are a health advisor for primary health diagnosis in rural areas. You need to:
1. Ask relevant questions about symptoms
2. Provide initial assessment
3. Suggest immediate actions
4. Identify when professional medical care is urgently needed

Respond in both Amharic and English for clarity."""

    def transcribe_audio(self, audio_path: str, language: str = "am") -> str:
        """
        Convert Amharic speech to text using Whisper

        Args:
            audio_path: Path to audio file
            language: Language code (default: 'am' for Amharic)

        Returns:
            Transcribed text
        """
        print(f"Transcribing audio from: {audio_path}")

        result = self.stt_model.transcribe(
            audio_path,
            language=language,
            task="transcribe",
            fp16=False  # Set to True if using CUDA
        )

        transcribed_text = result["text"].strip()
        print(f"Transcribed: {transcribed_text}")

        return transcribed_text

    def generate_response(self, user_message: str, conversation_history: list = None) -> str:
        """
        Generate AI response using LLM

        Args:
            user_message: User's message (in Amharic or English)
            conversation_history: Previous conversation messages

        Returns:
            AI response text
        """
        # Build conversation
        messages = [{"role": "system", "content": self.system_prompt}]

        if conversation_history:
            messages.extend(conversation_history)

        messages.append({"role": "user", "content": user_message})

        # Format prompt
        prompt = self.llm_tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )

        # Tokenize
        inputs = self.llm_tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=2048
        ).to(self.llm_model.device)

        # Generate response
        print("Generating response...")
        with torch.no_grad():
            outputs = self.llm_model.generate(
                **inputs,
                max_new_tokens=512,
                temperature=0.7,
                do_sample=True,
                top_p=0.9,
                repetition_penalty=1.1
            )

        # Decode response
        response = self.llm_tokenizer.decode(
            outputs[0][inputs['input_ids'].shape[1]:],
            skip_special_tokens=True
        ).strip()

        print(f"Response: {response[:100]}...")
        return response

    def synthesize_speech(self, text: str, output_path: str = "response.wav") -> str:
        """
        Convert text to Amharic speech using Piper

        Args:
            text: Text to synthesize
            output_path: Path to save audio file

        Returns:
            Path to generated audio file
        """
        if not self.tts_voice:
            print("⚠ TTS not available. Text output only.")
            return None

        print(f"Synthesizing speech: {text[:50]}...")

        with wave.open(output_path, "w") as wav_file:
            self.tts_voice.synthesize(text, wav_file)

        print(f"✓ Audio saved to: {output_path}")
        return output_path

    def process_voice_query(
        self,
        audio_input_path: str,
        audio_output_path: str = "response.wav",
        conversation_history: list = None
    ) -> Dict[str, str]:
        """
        Complete pipeline: Speech → Text → LLM → Text → Speech

        Args:
            audio_input_path: Path to user's audio input
            audio_output_path: Path to save AI's audio response
            conversation_history: Previous conversation messages

        Returns:
            Dictionary with user_text, ai_text, and audio_path
        """
        print("\n" + "="*80)
        print("Processing Voice Query")
        print("="*80)

        # Step 1: Speech-to-Text
        print("\n[1/3] Speech-to-Text...")
        user_text = self.transcribe_audio(audio_input_path)

        # Step 2: LLM Processing
        print("\n[2/3] Generating AI Response...")
        ai_text = self.generate_response(user_text, conversation_history)

        # Step 3: Text-to-Speech
        print("\n[3/3] Text-to-Speech...")
        audio_path = self.synthesize_speech(ai_text, audio_output_path)

        print("\n" + "="*80)
        print("Processing Complete")
        print("="*80)

        return {
            "user_text": user_text,
            "ai_text": ai_text,
            "audio_path": audio_path
        }


def main():
    """
    Example usage of Amharic Health Assistant
    """
    print("\n🏥 Amharic Health Assistant - Voice Pipeline Demo\n")

    # Initialize assistant
    assistant = AmharicHealthAssistant(
        stt_model_size="small",  # Change to 'tiny' for faster/smaller, 'medium' for better accuracy
        llm_model_name="meta-llama/Llama-3.2-3B-Instruct",
        tts_model_path="models/am_ET-mekonnen-medium/am_ET-mekonnen-medium.onnx"
    )

    # Example 1: Process audio file
    print("\n📌 Example 1: Processing audio file")
    print("-" * 80)

    audio_file = "examples/patient_query_amharic.wav"

    if os.path.exists(audio_file):
        result = assistant.process_voice_query(audio_file)

        print("\n📊 Results:")
        print(f"User said: {result['user_text']}")
        print(f"AI responded: {result['ai_text']}")
        print(f"Audio saved to: {result['audio_path']}")
    else:
        print(f"⚠ Audio file not found: {audio_file}")
        print("Skipping audio processing example.")

    # Example 2: Text-only interaction (no audio)
    print("\n\n📌 Example 2: Text-only interaction")
    print("-" * 80)

    test_queries = [
        "ልጄ ለሦስት ቀናት ትኩሳት እና ተቅማጥ አለው። ምን ማድረግ አለብኝ?",
        "My child has fever and diarrhea for 3 days. What should I do?",
    ]

    conversation = []

    for query in test_queries:
        print(f"\n👤 User: {query}")
        response = assistant.generate_response(query, conversation)
        print(f"🤖 AI: {response}")

        # Update conversation history
        conversation.append({"role": "user", "content": query})
        conversation.append({"role": "assistant", "content": response})

    print("\n\n✅ Demo complete!")
    print("\nNext steps:")
    print("1. Record your own Amharic audio queries")
    print("2. Fine-tune the model on Amharic medical data")
    print("3. Deploy to mobile devices for offline use")


if __name__ == "__main__":
    main()


"""
Usage:

# Basic usage
python amharic_voice_assistant.py

# With custom models
python amharic_voice_assistant.py \
    --stt-model base \
    --llm-model path/to/fine-tuned-model \
    --tts-model models/piper-amharic.onnx

# Process specific audio file
python amharic_voice_assistant.py \
    --audio patient_query.wav \
    --output response.wav

# Interactive mode (coming soon)
python amharic_voice_assistant.py --interactive
"""
