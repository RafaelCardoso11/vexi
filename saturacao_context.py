import os
import time
import matplotlib.pyplot as plt
import numpy as np
from google import genai

# Configurações do Cliente
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
MODEL_NAME = "gemini-2.5-flash-lite"

def stress_test_factory(n_operations, mode="python"):
    first_instruction_py = "initial_key = 999\n"
    first_instruction_vvm = "100 999 "
    
    noise_py = "".join([f"item_{i} = {i} * 2\nupdate_inventory(item_{i})\n" for i in range(n_operations)])
    noise_vvm = "".join([f"40 {i} {i*2} " for i in range(n_operations)])
    
    question = "\n\nQuestion: What is the value of the initial key? Answer only with the number."
    
    if mode == "python":
        return f"Context (Python):\n{first_instruction_py}{noise_py}{question}"
    else:
        rules = "Bytecode Rules: 100:SetKey(Value), 40:UpdateInventory(ID, Value)."
        return f"{rules}\nContext (VVM):\n{first_instruction_vvm}{noise_vvm}{question}"

# Parâmetros do experimento
steps = [10, 50, 100, 250, 500, 1000, 2000]
data = {"python": {"tokens": [], "latency": []}, "vvm": {"tokens": [], "latency": []}}

print(f"Iniciando Benchmark Progressivo: {steps} operações\n")

for n in steps:
    for mode in ["python", "vvm"]:
        prompt = stress_test_factory(n, mode)
        
        # Coleta de Tokens
        t_resp = client.models.count_tokens(model=MODEL_NAME, contents=prompt)
        tokens = t_resp.total_tokens
        
        # Coleta de Latência
        start = time.time()
        try:
            response = client.models.generate_content(model=MODEL_NAME, contents=prompt)
            _ = response.text.strip()
        except:
            pass
        end = time.time()
        
        data[mode]["tokens"].append(tokens)
        data[mode]["latency"].append(end - start)
        print(f"Mode: {mode.upper()} | Ops: {n} | Tokens: {tokens} | Lat: {end-start:.2f}s")

# --- GERAÇÃO DO GRÁFICO AUTOMÁTICO ---
fig, ax1 = plt.subplots(figsize=(10, 6))

# Eixo 1: Consumo de Tokens (Barras)
color_py = '#3498db' # Azul
color_vvm = '#e74c3c' # Vermelho
width = 15

ax1.set_xlabel('Número de Operações (Complexidade)')
ax1.set_ylabel('Consumo de Tokens (Janela de Contexto)', color='black')
ax1.bar(np.array(steps) - width/2, data["python"]["tokens"], width=width, label='Tokens: Python', color=color_py, alpha=0.7)
ax1.bar(np.array(steps) + width/2, data["vvm"]["tokens"], width=width, label='Tokens: VVM', color=color_vvm, alpha=0.7)
ax1.tick_params(axis='y')

# Eixo 2: Latência (Linhas)
ax2 = ax1.twinx()
ax2.set_ylabel('Latência de Resposta (Segundos)', color='darkgreen')
ax2.plot(steps, data["python"]["latency"], marker='o', linestyle='--', color='blue', label='Latência: Python')
ax2.plot(steps, data["vvm"]["latency"], marker='s', linestyle='-', color='red', label='Latência: VVM')
ax2.tick_params(axis='y', labelcolor='darkgreen')

plt.title(f'Benchmark de Escalabilidade Semântica: VVM vs Python\nModelo: {MODEL_NAME}')
fig.tight_layout()
ax1.legend(loc='upper left')
ax2.legend(loc='upper right')

# Salva para o projeto
plt.savefig("benchmark_escalabilidade.png", dpi=300)
print("\n✅ Gráfico 'benchmark_escalabilidade.png' gerado com sucesso.")
plt.show()