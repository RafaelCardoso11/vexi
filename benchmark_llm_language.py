# ============================================================
# BENCHMARK VVM REALTIME
# Tokenização + Execução + Escala + Custo
# Foco: Desenvolvimento Realtime (Lovable, Replit, Cursor)
# Modelo de custo: GPT-5.2 (https://openai.com/pt-BR/api/pricing/)
# ============================================================

import time
import matplotlib.pyplot as plt
from dataclasses import dataclass

# ----------------------------
# TOKENIZERS (SEM GATED REPOS)
# ----------------------------
import tiktoken
from transformers import AutoTokenizer

tokenizers = {
    "GPT-cl100k": tiktoken.get_encoding("cl100k_base"),
    "LLaMA-SP": AutoTokenizer.from_pretrained(
        "hf-internal-testing/llama-tokenizer", use_fast=False
    ),
    "BERT-WordPiece": AutoTokenizer.from_pretrained("bert-base-uncased")
}

def contar_tokens(tokenizer, texto: str) -> int:
    if hasattr(tokenizer, "encode") and not hasattr(tokenizer, "__call__"):
        return len(tokenizer.encode(texto))
    return len(tokenizer(texto)["input_ids"])


# ----------------------------
# MODELO DE ESTADO
# ----------------------------
@dataclass
class Entidade:
    x: int = 0
    y: int = 0
    rotacao: int = 0
    cor: str = "branco"
    velocidade: int = 1


# ----------------------------
# CODEBOOK VVM
# ----------------------------
CODEBOOK = {
    "01": "MOVE",
    "02": "ROT",
    "03": "SET",
    "04": "SEEK"
}


# ----------------------------
# INTERPRETADOR VVM
# ----------------------------
class VVMInterpreter:

    def __init__(self, entidade: Entidade):
        self.entidade = entidade

    def executar(self, hexcode: str):
        tokens = hexcode.split()
        opcode = tokens[0]
        args = tokens[1:]

        if opcode not in CODEBOOK:
            raise ValueError(f"Opcode inválido: {opcode}")

        if opcode == "01":
            dx, dy = map(int, args)
            self.entidade.x += dx
            self.entidade.y += dy

        elif opcode == "02":
            self.entidade.rotacao += int(args[0])

        elif opcode == "03":
            self.entidade.cor = args[0]
            self.entidade.velocidade = int(args[1])

        elif opcode == "04":
            alvo_x, alvo_y = map(int, args)
            if self.entidade.x < alvo_x:
                self.entidade.x += self.entidade.velocidade
            if self.entidade.x > alvo_x:
                self.entidade.x -= self.entidade.velocidade
            if self.entidade.y < alvo_y:
                self.entidade.y += self.entidade.velocidade
            if self.entidade.y > alvo_y:
                self.entidade.y -= self.entidade.velocidade


# ----------------------------
# TAREFAS (CARGA BASE)
# ----------------------------
tarefas = [
    "Mover Quadrado",
    "Girar Círculo",
    "Mudar Cor e Velocidade",
    "Seguir Jogador"
]

codigo_tradicional = {
    "Mover Quadrado": """
def mover_quadrado(entidade, dx, dy):
    entidade.x += dx
    entidade.y += dy
""",
    "Girar Círculo": """
def girar_circulo(entidade, angulo):
    entidade.rotacao += angulo
""",
    "Mudar Cor e Velocidade": """
def mudar_cor_velocidade(entidade, cor, velocidade):
    entidade.cor = cor
    entidade.velocidade = velocidade
""",
    "Seguir Jogador": """
def seguir_jogador(inimigo, jogador):
    if inimigo.x < jogador.x:
        inimigo.x += inimigo.velocidade
    if inimigo.x > jogador.x:
        inimigo.x -= inimigo.velocidade
    if inimigo.y < jogador.y:
        inimigo.y += inimigo.velocidade
    if inimigo.y > jogador.y:
        inimigo.y -= inimigo.velocidade
"""
}

codigo_vvm = {
    "Mover Quadrado": "01 3 2",
    "Girar Círculo": "02 90",
    "Mudar Cor e Velocidade": "03 vermelho 2",
    "Seguir Jogador": "04 10 10"
}


# ============================================================
# BENCHMARK 1 — TOKENIZAÇÃO
# ============================================================

print("\n" + "="*60)
print("BENCHMARK 1 — TOKENIZAÇÃO MULTI-TOKENIZER")
print("="*60)

resultados = {}

for nome, tokenizer in tokenizers.items():
    trad = sum(contar_tokens(tokenizer, codigo_tradicional[t]) for t in tarefas)
    vvm = sum(contar_tokens(tokenizer, codigo_vvm[t]) for t in tarefas)
    economia = (1 - vvm / trad) * 100
    resultados[nome] = (trad, vvm, economia)

    print(f"""
[TOKENIZER] {nome}
  Tradicional: {trad}
  VVM:         {vvm}
  Redução (%): {economia:.2f}
""")


# ============================================================
# BENCHMARK 2 — EXECUÇÃO VVM
# ============================================================

print("\n" + "="*60)
print("BENCHMARK 2 — EXECUÇÃO REAL DA VVM")
print("="*60)

entidade = Entidade()
vm = VVMInterpreter(entidade)

for instrucao in codigo_vvm.values():
    vm.executar(instrucao)

print(entidade)


# ============================================================
# BENCHMARK 3 — ESCALA
# ============================================================

ITERACOES = [1, 10, 100, 1_000, 10_000, 100_000]
tokenizer_base = tokenizers["GPT-cl100k"]

tokens_trad_escala = []
tokens_vvm_escala = []
tempo_trad = []
tempo_vvm = []

for n in ITERACOES:
    t_trad = sum(
        contar_tokens(tokenizer_base, codigo_tradicional[t]) * n
        for t in tarefas
    )
    t_vvm = sum(
        contar_tokens(tokenizer_base, codigo_vvm[t]) * n
        for t in tarefas
    )

    tokens_trad_escala.append(t_trad)
    tokens_vvm_escala.append(t_vvm)

    ini = time.perf_counter()
    for _ in range(n):
        for instrucao in codigo_vvm.values():
            vm.executar(instrucao)
    tempo_vvm.append(time.perf_counter() - ini)

    ini = time.perf_counter()
    for _ in range(n):
        for _ in tarefas:
            pass
    tempo_trad.append(time.perf_counter() - ini)


# ============================================================
# CUSTO — GPT-5.2 (INPUT-DOMINANTE)
# ============================================================

CUSTO_INPUT = 1.75   # US$ / 1M tokens
CUSTO_CACHE = 0.175
PERCENTUAL_CACHE = 0.70  # IDEs realtime

CUSTO_EFETIVO = CUSTO_INPUT * (1 - PERCENTUAL_CACHE) + CUSTO_CACHE * PERCENTUAL_CACHE

custos_trad = [(t / 1_000_000) * CUSTO_EFETIVO for t in tokens_trad_escala]
custos_vvm = [(t / 1_000_000) * CUSTO_EFETIVO for t in tokens_vvm_escala]


# ============================================================
# GRÁFICOS — LADO A LADO
# ============================================================

fig, axes = plt.subplots(1, 3, figsize=(20, 6))

axes[0].plot(ITERACOES, tokens_trad_escala, marker="o", label="Tradicional")
axes[0].plot(ITERACOES, tokens_vvm_escala, marker="o", label="VVM")
axes[0].set_xscale("log"); axes[0].set_yscale("log")
axes[0].set_title("Tokens × Escala"); axes[0].legend(); axes[0].grid(True)

axes[1].plot(ITERACOES, tempo_trad, marker="o", label="Tradicional")
axes[1].plot(ITERACOES, tempo_vvm, marker="o", label="VVM")
axes[1].set_xscale("log"); axes[1].set_yscale("log")
axes[1].set_title("Tempo × Escala"); axes[1].legend(); axes[1].grid(True)

axes[2].plot(ITERACOES, custos_trad, marker="o", label="Tradicional")
axes[2].plot(ITERACOES, custos_vvm, marker="o", label="VVM")
axes[2].set_xscale("log"); axes[2].set_yscale("log")
axes[2].set_title("Custo × Escala (GPT-5.2)"); axes[2].legend(); axes[2].grid(True)

plt.suptitle("Benchmark VVM Realtime — Tokens, Tempo e Custo (GPT-5.2)")
plt.tight_layout()
plt.show()


print("\n✅ Benchmark finalizado com GPT-5.2.")
