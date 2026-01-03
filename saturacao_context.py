import os
import time
import re
import numpy as np
import matplotlib.pyplot as plt
from google import genai

# ---------------- CONFIGURAÇÕES ----------------
MODEL_NAME = "gemini-2.5-flash-lite"
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

STEPS = [10, 50, 100, 250, 500, 1000, 2000]
REPEATS = 5
TARGET = "999"

# ---------------- GERADOR DE CONTEXTO ----------------
def stress_test_factory(n_ops, mode="python"):
    question = "What is the value of the initial key? Answer only with the number."

    if mode == "python":
        ctx = f"initial_key = {TARGET}\n"
        for i in range(n_ops):
            ctx += f"item_{i} = {i} * 2\nupdate_inventory(item_{i})\n"
        return f"{ctx}\nQuestion: {question}"

    ctx = f"100 {TARGET} "
    for i in range(n_ops):
        ctx += f"40 {i} {i*2} "
    rules = "Rules: 100:SetKey, 40:UpdateInventory\n"
    return f"{rules}{ctx}\n\nQuestion: {question}"

# ---------------- MÉTRICA DE ACURÁCIA ----------------
def exact_match(answer):
    return int(bool(re.fullmatch(rf"\b{TARGET}\b", answer.strip())))

# ---------------- ESTRUTURA DE DADOS ----------------
results = {
    "python": {"tokens": [], "latency": [], "acc": []},
    "vvm": {"tokens": [], "latency": [], "acc": []},
}

# ---------------- BENCHMARK ----------------
print(f"\n▶ Iniciando benchmark")
print(f"Modelo: {MODEL_NAME} | Repetições: {REPEATS}\n")

for n in STEPS:
    for mode in ["python", "vvm"]:
        latencies, tokens_list, accs = [], [], []

        for _ in range(REPEATS):
            prompt = stress_test_factory(n, mode)

            token_count = client.models.count_tokens(
                model=MODEL_NAME,
                contents=prompt
            ).total_tokens

            start = time.time()
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt
            )
            latency = time.time() - start

            acc = exact_match(response.text)

            latencies.append(latency)
            tokens_list.append(token_count)
            accs.append(acc)

        results[mode]["latency"].append((np.mean(latencies), np.std(latencies)))
        results[mode]["tokens"].append((np.mean(tokens_list), np.std(tokens_list)))
        results[mode]["acc"].append((np.mean(accs), np.std(accs)))

        print(
            f"Mode: {mode.upper()} | Ops: {n} | "
            f"Tokens: {np.mean(tokens_list):.1f}±{np.std(tokens_list):.1f} | "
            f"Lat: {np.mean(latencies):.2f}±{np.std(latencies):.2f}s | "
            f"Acc: {np.mean(accs):.2f}"
        )

# ---------------- PLOTS ----------------
ops = np.array(STEPS)

fig, axes = plt.subplots(1, 3, figsize=(22, 6))

# Tokens
for mode, color in [("python", "blue"), ("vvm", "red")]:
    mean = [v[0] for v in results[mode]["tokens"]]
    std = [v[1] for v in results[mode]["tokens"]]
    axes[0].errorbar(ops, mean, yerr=std, label=mode.upper(), marker='o', capsize=5)

axes[0].set_title("Consumo Médio de Tokens")
axes[0].set_xlabel("Número de Operações")
axes[0].set_ylabel("Tokens")
axes[0].legend()

# Latência
for mode, color in [("python", "blue"), ("vvm", "red")]:
    mean = [v[0] for v in results[mode]["latency"]]
    std = [v[1] for v in results[mode]["latency"]]
    axes[1].errorbar(ops, mean, yerr=std, label=mode.upper(), marker='s', capsize=5)

axes[1].set_title("Latência Média de Inferência")
axes[1].set_xlabel("Número de Operações")
axes[1].set_ylabel("Segundos")
axes[1].legend()

# Acurácia
for mode, color in [("python", "blue"), ("vvm", "red")]:
    mean = [v[0] for v in results[mode]["acc"]]
    axes[2].plot(ops, mean, label=mode.upper(), marker='d')

axes[2].set_title("Fidelidade da Resposta")
axes[2].set_ylim(-0.05, 1.05)
axes[2].set_xlabel("Número de Operações")
axes[2].set_ylabel("Acurácia Média")
axes[2].legend()

plt.tight_layout()
plt.savefig("baseline_mestrado.png", dpi=300)
plt.show()
