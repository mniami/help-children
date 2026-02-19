"""
Medical Domain Fine-Tuning Script for AI4SE Health Assistant (CPU Version)

This script fine-tunes a base language model using LoRA (Low-Rank Adaptation)
on medical domain data for primary health care in resource-limited settings.
Optimized for CPU training.

Requirements:
    pip install transformers peft accelerate datasets torch
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
        default="HuggingFaceTB/SmolLM2-135M-Instruct",
        metadata={"help": "Base model to fine-tune"}
    )
    lora_rank: int = field(
        default=8,
        metadata={"help": "LoRA rank (higher = more parameters)"}
    )
    lora_alpha: int = field(
        default=16,
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
        default=256,
        metadata={"help": "Maximum sequence length"}
    )
    validation_split: float = field(
        default=0.1,
        metadata={"help": "Fraction of data for validation"}
    )


@dataclass
class TrainArguments(TrainingArguments):
    """Training arguments"""
    output_dir: str = field(
        default="./models/medical-lora",
        metadata={"help": "Output directory for model"}
    )
    num_train_epochs: int = field(
        default=1,
        metadata={"help": "Number of training epochs"}
    )
    per_device_train_batch_size: int = field(
        default=1,
        metadata={"help": "Batch size per device"}
    )
    gradient_accumulation_steps: int = field(
        default=2,
        metadata={"help": "Gradient accumulation steps"}
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


def load_model_and_tokenizer(model_args):
    """Load base model (CPU compatible)"""
    print(f"Loading base model: {model_args.base_model}")

    # Load tokenizer
    tokenizer = AutoTokenizer.from_pretrained(model_args.base_model)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right"

    # Load model in float32 for CPU
    print("Loading model for CPU training...")
    model = AutoModelForCausalLM.from_pretrained(
        model_args.base_model,
        torch_dtype=torch.float32,
        trust_remote_code=True
    )

    return model, tokenizer


def setup_lora(model, model_args):
    """Configure and apply LoRA"""
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
    model.print_trainable_parameters()

    return model


def prepare_dataset(data_args, tokenizer):
    """Load and tokenize dataset"""
    print(f"Loading dataset from: {data_args.dataset_path}")

    # Load JSONL dataset
    dataset = load_dataset('json', data_files=data_args.dataset_path)

    # Format conversations
    def format_conversation(example):
        """Format messages into prompt template"""
        messages = example.get('messages', [])

        # Build simple conversation format
        conversation = ""
        for msg in messages:
            role = msg['role']
            content = msg['content']

            if role == "system":
                conversation += f"System: {content}\n\n"
            elif role == "user":
                conversation += f"User: {content}\n\n"
            elif role == "assistant":
                conversation += f"Assistant: {content}\n\n"

        return {"text": conversation}

    # Format all examples
    dataset = dataset.map(format_conversation)

    # Tokenize
    def tokenize_function(examples):
        return tokenizer(
            examples['text'],
            truncation=True,
            max_length=data_args.max_seq_length,
            padding="max_length"
        )

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

    # Load model and tokenizer
    model, tokenizer = load_model_and_tokenizer(model_args)

    # Setup LoRA
    model = setup_lora(model, model_args)

    # Prepare dataset
    train_dataset, eval_dataset = prepare_dataset(data_args, tokenizer)

    print(f"Training samples: {len(train_dataset)}")
    print(f"Validation samples: {len(eval_dataset)}")

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
    print("\n" + "="*50)
    print("Starting training...")
    print("="*50 + "\n")
    trainer.train()

    # Save LoRA adapter
    print(f"\nSaving LoRA adapter to {training_args.output_dir}")
    model.save_pretrained(training_args.output_dir)
    tokenizer.save_pretrained(training_args.output_dir)

    # Evaluate
    print("\nEvaluating model...")
    metrics = trainer.evaluate()
    print(f"Validation metrics: {metrics}")

    print("\n✅ Training complete!")
    print(f"   Model saved to: {training_args.output_dir}")


if __name__ == "__main__":
    main()
