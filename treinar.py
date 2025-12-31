import torch
import os
from datasets import load_dataset
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import LoraConfig
from trl import SFTTrainer, SFTConfig # <--- Importamos SFTConfig agora

# Configuração básica
MODEL_NAME = "Qwen/Qwen2.5-1.5B-Instruct"
OUTPUT_DIR = "./vexi-lora-mac"

# 1. Carregar Dataset
print(">>> Carregando dataset...")
dataset = load_dataset("json", data_files="dataset.jsonl")

# 2. Configurar Tokenizer
print(">>> Carregando tokenizer...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
tokenizer.padding_side = "right"
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token

# 3. Função de Formatação
def formatting_prompts_func(examples):
    output_texts = []
    for i in range(len(examples['input'])):
        messages = [
            {"role": "user", "content": examples['input'][i]},
            {"role": "assistant", "content": examples['output'][i]}
        ]
        text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=False)
        output_texts.append(text)
    return output_texts

# 4. Carregar Modelo (Otimizado para Mac 8GB)
print(">>> Carregando modelo na GPU (MPS)...")
model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    torch_dtype=torch.float16, 
    device_map="mps",
    use_cache=False
)

model.gradient_checkpointing_enable() 
model.enable_input_require_grads()

# 5. Configuração LoRA
peft_config = LoraConfig(
    r=8,
    lora_alpha=16,
    target_modules=["q_proj", "v_proj", "k_proj", "o_proj"],
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM"
)

# 6. SFTConfig (Substitui TrainingArguments)
# O max_seq_length agora VEM AQUI DENTRO
args = SFTConfig(
    output_dir=OUTPUT_DIR,
    max_length=512,             # <--- MUDANÇA: Configurado aqui agora
    per_device_train_batch_size=1,
    gradient_accumulation_steps=8,
    num_train_epochs=3,
    learning_rate=2e-4,
    fp16=False,
    bf16=False,
    optim="adamw_torch",
    logging_steps=5,
    save_strategy="epoch",
    report_to="none",
    ddp_find_unused_parameters=False,
    packing=False,                  # <--- MUDANÇA: Configurado aqui agora
    dataset_text_field="text",      # Necessário para calar avisos, mas usaremos formatting_func
)

# 7. Inicializar SFTTrainer
print(">>> Iniciando Trainer...")
trainer = SFTTrainer(
    model=model,
    train_dataset=dataset["train"],
    peft_config=peft_config,
    formatting_func=formatting_prompts_func,
    processing_class=tokenizer,
    args=args
    # Note que removemos max_seq_length e packing daqui, pois já estão em 'args'
)

# 8. Treinar
print(">>> Treinamento iniciado...")
trainer.train()

print(f">>> Treino finalizado! Salvando em {OUTPUT_DIR}")
trainer.save_model(OUTPUT_DIR)