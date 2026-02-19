"""
Amharic Medical Fine-Tuning Script

This script fine-tunes Llama-3.2-3B on Amharic medical dialogue data.
Uses LoRA for efficient training on a single GPU.

Requirements:
    pip install transformers peft accelerate bitsandbytes datasets torch
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
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from datasets import load_dataset


@dataclass
class ModelArguments:
    """Arguments for model configuration"""
    base_model: str = field(
        default="meta-llama/Llama-3.2-3B-Instruct",
        metadata={"help": "Base model to fine-tune (supports Amharic)"}
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
    """Arguments for data configuration"""
    dataset_path: str = field(
        metadata={"help": "Path to Amharic medical training dataset (JSONL)"}
    )
    max_seq_length: int = field(
        default=1024,
        metadata={"help": "Maximum sequence length (longer for Amharic + English)"}
    )
    validation_split: float = field(
        default=0.1,
        metadata={"help": "Fraction of data for validation"}
    )


@dataclass
class TrainArguments(TrainingArguments):
    """Training configuration"""
    output_dir: str = field(
        default="./models/llama-3.2-3b-amharic-medical-lora",
        metadata={"help": "Output directory for LoRA adapter"}
    )
    num_train_epochs: int = field(
        default=3,
        metadata={"help": "Number of training epochs"}
    )
    per_device_train_batch_size: int = field(
        default=4,
        metadata={"help": "Batch size per device"}
    )
    gradient_accumulation_steps: int = field(
        default=4,
        metadata={"help": "Gradient accumulation steps"}
    )
    learning_rate: float = field(
        default=2e-4,
        metadata={"help": "Learning rate"}
    )
    optim: str = field(
        default="paged_adamw_8bit",
        metadata={"help": "Optimizer (paged_adamw_8bit for low memory)"}
    )
    logging_steps: int = field(
        default=10,
        metadata={"help": "Log every N steps"}
    )
    save_steps: int = field(
        default=100,
        metadata={"help": "Save checkpoint every N steps"}
    )
    warmup_steps: int = field(
        default=50,
        metadata={"help": "Warmup steps"}
    )


def load_model_and_tokenizer(model_args):
    """Load base model in 4-bit quantization for efficient training"""
    print(f"Loading base model: {model_args.base_model}")
    print("This model has multilingual support including Amharic (አማርኛ)")

    # Load tokenizer
    tokenizer = AutoTokenizer.from_pretrained(model_args.base_model)
    tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right"

    # Test Amharic tokenization
    test_amharic = "ልጄ ትኩሳት አለው"
    tokens = tokenizer.encode(test_amharic)
    print(f"✓ Amharic tokenization test: '{test_amharic}' → {len(tokens)} tokens")

    # Load model in 4-bit for memory efficiency
    model = AutoModelForCausalLM.from_pretrained(
        model_args.base_model,
        load_in_4bit=True,
        torch_dtype=torch.float16,
        device_map="auto",
        trust_remote_code=True
    )

    # Prepare for training
    model = prepare_model_for_kbit_training(model)
    model.config.use_cache = False  # Required for gradient checkpointing

    return model, tokenizer


def setup_lora(model, model_args):
    """Configure and apply LoRA for parameter-efficient fine-tuning"""
    print("Setting up LoRA configuration...")

    lora_config = LoraConfig(
        r=model_args.lora_rank,
        lora_alpha=model_args.lora_alpha,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
        lora_dropout=model_args.lora_dropout,
        bias="none",
        task_type="CAUSAL_LM"
    )

    model = get_peft_model(model, lora_config)

    # Print trainable parameters
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    total_params = sum(p.numel() for p in model.parameters())
    trainable_pct = 100 * trainable_params / total_params

    print(f"Trainable parameters: {trainable_params:,} ({trainable_pct:.2f}%)")
    print(f"Total parameters: {total_params:,}")

    return model


def prepare_dataset(data_args, tokenizer):
    """Load and format Amharic medical dataset"""
    print(f"Loading Amharic dataset from: {data_args.dataset_path}")

    # Load JSONL dataset
    dataset = load_dataset('json', data_files=data_args.dataset_path)

    print(f"Loaded {len(dataset['train'])} examples")

    # Show sample
    sample = dataset["train"][0]
    print("\nSample conversation:")
    for msg in sample.get('messages', [])[:2]:
        content_preview = msg['content'][:100] + "..." if len(msg['content']) > 100 else msg['content']
        print(f"  {msg['role']}: {content_preview}")

    # Format conversations into prompt template
    def format_conversation(example):
        """Format messages into Llama-3 chat template"""
        messages = example.get('messages', [])

        # Apply chat template
        formatted = tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=False
        )

        return {"text": formatted}

    # Format all examples
    dataset = dataset.map(
        format_conversation,
        remove_columns=dataset["train"].column_names
    )

    # Tokenize
    def tokenize_function(examples):
        return tokenizer(
            examples['text'],
            truncation=True,
            max_length=data_args.max_seq_length,
            padding="max_length",
            return_tensors=None
        )

    tokenized_dataset = dataset.map(
        tokenize_function,
        batched=True,
        remove_columns=["text"]
    )

    # Split train/validation
    train_val = tokenized_dataset["train"].train_test_split(
        test_size=data_args.validation_split,
        seed=42
    )

    print(f"Training samples: {len(train_val['train'])}")
    print(f"Validation samples: {len(train_val['test'])}")

    return train_val["train"], train_val["test"]


def main():
    """Main training function"""
    print("\n" + "="*80)
    print("🇪🇹 Amharic Medical Domain Fine-Tuning")
    print("="*80 + "\n")

    # Parse arguments
    parser = HfArgumentParser((ModelArguments, DataArguments, TrainArguments))
    model_args, data_args, training_args = parser.parse_args_into_dataclasses()

    # Load model and tokenizer
    model, tokenizer = load_model_and_tokenizer(model_args)

    # Setup LoRA
    model = setup_lora(model, model_args)

    # Prepare dataset
    train_dataset, eval_dataset = prepare_dataset(data_args, tokenizer)

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
    print("\n" + "="*80)
    print("Starting training...")
    print("="*80 + "\n")

    trainer.train()

    # Save LoRA adapter
    print("\n" + "="*80)
    print(f"Saving LoRA adapter to {training_args.output_dir}")
    print("="*80)

    model.save_pretrained(training_args.output_dir)
    tokenizer.save_pretrained(training_args.output_dir)

    # Evaluate
    print("\nEvaluating model...")
    metrics = trainer.evaluate()
    print(f"Validation Loss: {metrics['eval_loss']:.4f}")
    print(f"Perplexity: {torch.exp(torch.tensor(metrics['eval_loss'])):.2f}")

    print("\n✅ Training complete!")
    print(f"\nLoRA adapter saved to: {training_args.output_dir}")
    print("\nTo use this model:")
    print("1. Merge LoRA with base model")
    print("2. Quantize to GGUF/ONNX/WebLLM")
    print("3. Deploy to mobile devices")


if __name__ == "__main__":
    main()


"""
Usage Examples:

# Train with default settings
python train_amharic_lora.py \
  --dataset_path datasets/amharic_medical_training.jsonl

# Train with custom hyperparameters
python train_amharic_lora.py \
  --dataset_path datasets/amharic_medical_training.jsonl \
  --base_model meta-llama/Llama-3.2-3B-Instruct \
  --lora_rank 32 \
  --lora_alpha 64 \
  --num_train_epochs 5 \
  --per_device_train_batch_size 8 \
  --learning_rate 1e-4 \
  --output_dir models/amharic-medical-high-quality

# Train on smaller dataset for testing
python train_amharic_lora.py \
  --dataset_path datasets/amharic_medical_sample.jsonl \
  --num_train_epochs 1 \
  --save_steps 10

# Resume training from checkpoint
python train_amharic_lora.py \
  --dataset_path datasets/amharic_medical_training.jsonl \
  --output_dir models/llama-3.2-3b-amharic-medical-lora \
  --resume_from_checkpoint models/llama-3.2-3b-amharic-medical-lora/checkpoint-500
"""
