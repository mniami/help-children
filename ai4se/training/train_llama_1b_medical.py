"""
Train high-accuracy medical model for MEIZU Mblu 21 (4GB RAM)

Model: Llama-3.2-1B-Instruct
- Parameters: 1.23B
- Quantized size: ~600MB (Q4) 
- RAM usage: ~1.5GB
- Quality: Significantly better than 135M model
- Speed: 4-8 tokens/second on Unisoc T606

This is the optimal model for:
- Medical accuracy (critical for health decisions)
- Mobile device constraints (4GB RAM)
- Offline operation
- Real-world inference speed
"""

import os
import json
import torch
from dataclasses import dataclass, field
from typing import Optional
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling,
    HfArgumentParser
)
from peft import LoraConfig, get_peft_model
from datasets import load_dataset


@dataclass
class ModelArguments:
    """Arguments pertaining to model setup"""
    base_model: str = field(
        default="meta-llama/Llama-3.2-1B-Instruct",
        metadata={"help": "Base model to fine-tune"}
    )
    lora_rank: int = field(
        default=16,
        metadata={"help": "LoRA rank (higher = more parameters, better quality)"}
    )
    lora_alpha: int = field(
        default=32,
        metadata={"help": "LoRA alpha (scaling factor)"}
    )
    lora_dropout: float = field(
        default=0.05,
        metadata={"help": "LoRA dropout rate"}
    )


@dataclass
class DataArguments:
    """Arguments pertaining to data"""
    dataset_path: str = field(
        metadata={"help": "Path to training dataset (JSONL format)"}
    )
    max_seq_length: int = field(
        default=512,
        metadata={"help": "Maximum sequence length (512 for medical conversations)"}
    )
    validation_split: float = field(
        default=0.1,
        metadata={"help": "Fraction of data for validation"}
    )


@dataclass
class TrainArguments(TrainingArguments):
    """Training arguments"""
    output_dir: str = field(
        default="./models/llama-1b-medical-lora",
        metadata={"help": "Output directory for model"}
    )
    num_train_epochs: int = field(
        default=3,
        metadata={"help": "Number of training epochs (more = better quality)"}
    )
    per_device_train_batch_size: int = field(
        default=1,
        metadata={"help": "Batch size per device"}
    )
    gradient_accumulation_steps: int = field(
        default=4,
        metadata={"help": "Gradient accumulation steps (effective batch size = 4)"}
    )
    learning_rate: float = field(
        default=2e-4,
        metadata={"help": "Learning rate"}
    )
    logging_steps: int = field(
        default=5,
        metadata={"help": "Log every N steps"}
    )
    save_steps: int = field(
        default=50,
        metadata={"help": "Save checkpoint every N steps"}
    )
    warmup_ratio: float = field(
        default=0.1,
        metadata={"help": "Warmup ratio for learning rate"}
    )


def load_model_and_tokenizer(model_args):
    """Load base model (CPU compatible)"""
    print(f"Loading base model: {model_args.base_model}")
    print("Note: Llama-3.2-1B has 1.23B parameters - higher quality than 135M")
    print()

    # Load tokenizer
    tokenizer = AutoTokenizer.from_pretrained(model_args.base_model)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right"

    # Load model in float32 for CPU
    print("Loading model for CPU training...")
    print("This may take 2-3 minutes (1.23B parameters)...")
    model = AutoModelForCausalLM.from_pretrained(
        model_args.base_model,
        torch_dtype=torch.float32,
        trust_remote_code=True
    )

    return model, tokenizer


def setup_lora(model, model_args):
    """Configure and apply LoRA"""
    print("\n" + "=" * 60)
    print("Setting up LoRA configuration...")
    print("=" * 60)

    # Llama uses different attention module names
    lora_config = LoraConfig(
        r=model_args.lora_rank,
        lora_alpha=model_args.lora_alpha,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
        lora_dropout=model_args.lora_dropout,
        bias="none",
        task_type="CAUSAL_LM"
    )

    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()
    print()

    return model


def prepare_dataset(data_args, tokenizer):
    """Load and tokenize dataset"""
    print("=" * 60)
    print(f"Loading dataset from: {data_args.dataset_path}")
    print("=" * 60)

    # Load JSONL dataset
    dataset = load_dataset('json', data_files=data_args.dataset_path)

    # Format conversations using Llama 3 chat template
    def format_conversation(example):
        """Format messages into Llama 3 chat template"""
        messages = example.get('messages', [])
        
        # Use Llama 3 template with special tokens
        conversation = "<|begin_of_text|>"
        
        for msg in messages:
            role = msg['role']
            content = msg['content']

            if role == "system":
                conversation += f"<|start_header_id|>system<|end_header_id|>\n\n{content}<|eot_id|>"
            elif role == "user":
                conversation += f"<|start_header_id|>user<|end_header_id|>\n\n{content}<|eot_id|>"
            elif role == "assistant":
                conversation += f"<|start_header_id|>assistant<|end_header_id|>\n\n{content}<|eot_id|>"

        return {"text": conversation}

    # Format all examples
    dataset = dataset.map(format_conversation)
    print(f"Loaded {len(dataset['train'])} examples")

    # Tokenize
    def tokenize_function(examples):
        return tokenizer(
            examples['text'],
            truncation=True,
            max_length=data_args.max_seq_length,
            padding="max_length"
        )

    print("Tokenizing dataset...")
    tokenized_dataset = dataset.map(
        tokenize_function,
        batched=True,
        remove_columns=dataset["train"].column_names
    )

    # Split train/validation
    train_val = tokenized_dataset["train"].train_test_split(
        test_size=data_args.validation_split,
        seed=42
    )

    return train_val["train"], train_val["test"]


def main():
    """Main training function"""
    # Parse arguments
    parser = HfArgumentParser((ModelArguments, DataArguments, TrainArguments))
    model_args, data_args, training_args = parser.parse_args_into_dataclasses()

    print("\n" + "=" * 60)
    print("AI4SE High-Accuracy Medical Model Training")
    print("Target Device: MEIZU Mblu 21 (4GB RAM, Unisoc T606)")
    print("=" * 60 + "\n")

    # Load model and tokenizer
    model, tokenizer = load_model_and_tokenizer(model_args)

    # Setup LoRA
    model = setup_lora(model, model_args)

    # Prepare dataset
    train_dataset, eval_dataset = prepare_dataset(data_args, tokenizer)

    print("\n" + "=" * 60)
    print("Training Configuration")
    print("=" * 60)
    print(f"Training samples: {len(train_dataset)}")
    print(f"Validation samples: {len(eval_dataset)}")
    print(f"Epochs: {training_args.num_train_epochs}")
    print(f"Effective batch size: {training_args.per_device_train_batch_size * training_args.gradient_accumulation_steps}")
    print(f"Learning rate: {training_args.learning_rate}")
    print()

    # Data collator
    data_collator = DataCollatorForLanguageModeling(
        tokenizer=tokenizer,
        mlm=False
    )

    # Initialize trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
        data_collator=data_collator
    )

    # Train
    print("=" * 60)
    print("Starting training...")
    print("=" * 60)
    print("⏰ Estimated time on CPU: 10-30 minutes (depends on dataset size)")
    print("💡 Tip: For faster training, use a GPU if available")
    print()
    
    trainer.train()

    # Save LoRA adapter
    print(f"\n{'=' * 60}")
    print(f"Saving LoRA adapter to {training_args.output_dir}")
    print("=" * 60)
    model.save_pretrained(training_args.output_dir)
    tokenizer.save_pretrained(training_args.output_dir)

    # Evaluate
    print("\n" + "=" * 60)
    print("Evaluating model...")
    print("=" * 60)
    metrics = trainer.evaluate()
    print(f"Validation metrics: {metrics}")

    print("\n" + "=" * 60)
    print("✅ Training complete!")
    print("=" * 60)
    print(f"📁 Model saved to: {training_args.output_dir}")
    print(f"📊 Final validation loss: {metrics['eval_loss']:.4f}")
    print()
    print("Next steps:")
    print("1. Test model: python training/test_model_llama.py")
    print("2. Merge adapter: python training/optimize_for_mobile.py")
    print("3. Quantize to Q4: ~600MB for MEIZU device")
    print()


if __name__ == "__main__":
    main()
