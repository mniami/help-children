"""
Test script to verify fine-tuned medical model
"""

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

def test_model(model_path, base_model_name):
    """Test the fine-tuned model"""
    
    print("=" * 60)
    print("Loading fine-tuned medical model...")
    print("=" * 60)
    
    # Load tokenizer
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    
    # Load base model
    base_model = AutoModelForCausalLM.from_pretrained(
        base_model_name,
        torch_dtype=torch.float32,
        trust_remote_code=True
    )
    
    # Load LoRA adapter
    model = PeftModel.from_pretrained(base_model, model_path)
    model.eval()
    
    print("✅ Model loaded successfully!\n")
    
    # Test cases
    test_prompts = [
        {
            "name": "Child with fever and diarrhea",
            "prompt": "System: You are a medical assistant for primary health diagnosis in rural areas.\n\nUser: My child has fever and diarrhea for 3 days. What should I do?\n\nAssistant:"
        },
        {
            "name": "Chest pain case",
            "prompt": "System: You are a medical assistant for primary health diagnosis in rural areas.\n\nUser: I have chest pain and difficulty breathing.\n\nAssistant:"
        }
    ]
    
    for i, test_case in enumerate(test_prompts, 1):
        print("\n" + "=" * 60)
        print(f"Test Case {i}: {test_case['name']}")
        print("=" * 60)
        print(f"\nPrompt:\n{test_case['prompt']}\n")
        
        # Generate response
        inputs = tokenizer(test_case['prompt'], return_tensors="pt")
        
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=150,
                temperature=0.7,
                do_sample=True,
                top_p=0.9,
                repetition_penalty=1.1
            )
        
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Extract just the assistant's response
        if "Assistant:" in response:
            assistant_response = response.split("Assistant:")[-1].strip()
            print(f"Response:\n{assistant_response[:300]}...")
        else:
            print(f"Full Response:\n{response[:300]}...")
        
        print("\n" + "-" * 60)
    
    print("\n✅ Testing complete!")
    print("=" * 60)


if __name__ == "__main__":
    model_path = "models/medical-lora-test"
    base_model_name = "HuggingFaceTB/SmolLM2-135M-Instruct"
    
    test_model(model_path, base_model_name)
