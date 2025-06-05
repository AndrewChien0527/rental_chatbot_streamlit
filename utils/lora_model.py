from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments, Trainer
from peft import get_peft_model, LoraConfig
from datasets import Dataset
def load_qa_from_txt(filename):
    qa_data = []
    with open(filename, "r", encoding="utf-8") as f:
        lines = f.readlines()

    question = None
    answer = None
    for line in lines:
        line = line.strip()
        if line.startswith("Q") or line.startswith("Q:"):
            question = line.split(":", 1)[1].strip()
        elif line.startswith("A") or line.startswith("A:"):
            answer = line.split(":", 1)[1].strip()
        
        if question and answer:
            qa_data.append({"question": question, "answer": answer})
            question = None
            answer = None

    return qa_data
def preprocess_qa(example):
    # Concatenate question and answer into single string for causal LM style training
    # Format your prompt+response as you want the model to learn it

    text = f"Q: {example['question']} A: {example['answer']}"

    # Tokenize the whole text
    encoding = tokenizer(
        text,
        truncation=True,
        max_length=512,
        padding="max_length"
    )

    input_ids = encoding["input_ids"]
    attention_mask = encoding["attention_mask"]

    # For causal LM, labels = input_ids (predict next token)
    labels = input_ids.copy()  # or input_ids[:]

    return {
        "input_ids": input_ids,
        "attention_mask": attention_mask,
        "labels": labels
    }

# Load pre-trained model and tokenizer
model_name = "liswei/Taiwan-ELM-270M-Instruct"
model = AutoModelForCausalLM.from_pretrained(model_name,trust_remote_code=True)
tokenizer = AutoTokenizer.from_pretrained(model_name)
# Define LoRA configuration
lora_config = LoraConfig(
    r=8,
    lora_alpha=16,
    target_modules = ["qkv_proj", "out_proj"],
    lora_dropout=0.1,
    bias="none",
    task_type="CAUSAL_LM"
)

# Apply LoRA to the model
model = get_peft_model(model, lora_config)

# Load and preprocess dataset
data = load_qa_from_txt("data/lora.txt")
# Convert to Hugging Face Dataset
dataset = Dataset.from_list(data)
dataset = dataset.map(preprocess_qa)

# Tokenize
def tokenize_function(example):
    prompt = (
        f"[INST] <<SYS>>\n你是一個專業的法律助理，請根據提供的資訊回答問題。\n<</SYS>>\n\n"
        f"Q: {example['question']}\nA: {example['answer']} [/INST]"
    )
    tokenized = tokenizer(
        prompt,
        truncation=True,
        max_length=512,
        padding="max_length"
    )
    tokenized["labels"] = tokenized["input_ids"].copy()
    return tokenized

tokenized_dataset = dataset.map(tokenize_function)

# Training configuration
training_args = TrainingArguments(
    output_dir="./lora_model",
    #evaluation_strategy="epoch",
    learning_rate=2e-5,
    per_device_train_batch_size=4,
    per_device_eval_batch_size=4,
    num_train_epochs=3,
    weight_decay=0.01,
    logging_dir="./logs",
    logging_steps=10,
)

# Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset,
    eval_dataset=tokenized_dataset,
    tokenizer=tokenizer,
)

# Train
trainer.train()

# Save model and tokenizer
model.save_pretrained("./lora_model")
tokenizer.save_pretrained("./lora_model")

