import json
import random

# ==========================================
# CONFIGURAÇÃO DA VVM (Tabela de Verdade)
# ==========================================
OPCODES = {
    "SPAWN": 1,
    "SET_SHAPE": 10,
    "SET_COLOR": 11,
    "SET_SPEED": 12,
    "MOVE": 20,
    "ROTATE": 21,
    "SEEK": 30,
    "CONSUME": 31
}

# Dicionários para dar variedade linguística
SHAPES = {1: "Círculo", 2: "Quadrado", 3: "Triângulo"}
COLORS = {1: "Vermelho", 2: "Azul", 3: "Verde"}

def generate_sample():
    """
    Gera um único exemplo de treinamento (Par Prompt -> Bytecode).
    """
    
    # Quantas ações essa entidade vai fazer? (Entre 3 e 8 passos)
    num_steps = random.randint(3, 8)
    
    narrative_parts = []
    bytecode_parts = []
    
    # Passo 1: Sempre começa com Spawn (para consistência)
    type_id = random.randint(1, 3)
    narrative_parts.append(f"Spawne uma entidade do tipo {type_id}.")
    bytecode_parts.extend([str(OPCODES["SPAWN"]), str(type_id)])
    
    # Passo 2: Gera ações aleatórias
    for _ in range(num_steps):
        action = random.choice(["MOVE", "COLOR", "SHAPE", "SPEED", "ROTATE", "SEEK", "CONSUME"])
        
        if action == "MOVE":
            x, y = random.randint(0, 100), random.randint(0, 100)
            narrative_parts.append(random.choice([
                f"Mova para x={x}, y={y}.",
                f"Vá para a posição {x}, {y}.",
                f"Desloque-se até {x} e {y}."
            ]))
            bytecode_parts.extend([str(OPCODES["MOVE"]), str(x), str(y)])
            
        elif action == "COLOR":
            c_id = random.randint(1, 3)
            c_name = COLORS[c_id]
            narrative_parts.append(random.choice([
                f"Mude a cor para {c_name}.",
                f"Fique {c_name} (ID {c_id}).",
                f"Defina a cor como {c_name}."
            ]))
            bytecode_parts.extend([str(OPCODES["SET_COLOR"]), str(c_id)])
            
        elif action == "SHAPE":
            s_id = random.randint(1, 3)
            s_name = SHAPES[s_id]
            narrative_parts.append(f"Transforme-se em um {s_name}.")
            bytecode_parts.extend([str(OPCODES["SET_SHAPE"]), str(s_id)])
            
        elif action == "SPEED":
            val = random.randint(1, 20)
            narrative_parts.append(f"Ajuste velocidade para {val}.")
            bytecode_parts.extend([str(OPCODES["SET_SPEED"]), str(val)])
            
        elif action == "ROTATE":
            deg = random.choice([45, 90, 180, 270])
            narrative_parts.append(f"Gire {deg} graus.")
            bytecode_parts.extend([str(OPCODES["ROTATE"]), str(deg)])

        elif action == "SEEK":
            tx, ty = random.randint(0, 100), random.randint(0, 100)
            narrative_parts.append(f"Busque o alvo em {tx}, {ty}.")
            bytecode_parts.extend([str(OPCODES["SEEK"]), str(tx), str(ty)])
            
        elif action == "CONSUME":
            narrative_parts.append("Execute consumir.")
            bytecode_parts.extend([str(OPCODES["CONSUME"])])

    # Monta as strings finais
    full_prompt = " ".join(narrative_parts)
    full_bytecode = " ".join(bytecode_parts)
    
    return full_prompt, full_bytecode

# ==========================================
# GERAÇÃO DO ARQUIVO
# ==========================================
NUM_EXAMPLES = 500 # 500 é um bom número para começar
OUTPUT_FILE = "vexi_dataset.jsonl"

print(f"🔨 Gerando {NUM_EXAMPLES} exemplos de treinamento...")

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    for _ in range(NUM_EXAMPLES):
        prompt, code = generate_sample()
        
        # Formato Padrão Chat (Aceito por Gemini e OpenAI)
        training_entry = {
            "messages": [
                {
                    "role": "system", 
                    "content": "You are VexiCompiler. Translate natural language instructions into raw integer bytecode sequences separated by spaces. No text, only numbers."
                },
                {
                    "role": "user", 
                    "content": prompt
                },
                {
                    "role": "model", # Nota: OpenAI usa 'assistant', Google usa 'model'
                    "content": code
                }
            ]
        }
        
        f.write(json.dumps(training_entry) + "\n")

print(f"✅ Sucesso! Arquivo '{OUTPUT_FILE}' criado.")
print("Exemplo gerado:")
print(f"User:  {prompt}")
print(f"Model: {code}")