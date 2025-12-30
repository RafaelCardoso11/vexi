# ============================================================
# VVM REALTIME BENCHMARK — OTIMIZADO
# Tokenization + Execution + Scale + Cost
# VVM via NumPy + Numba
# ============================================================

import time
import matplotlib.pyplot as plt
import numpy as np
import tiktoken
from dataclasses import dataclass
from numba import njit
from transformers import AutoTokenizer
from typing import Union


tokenizers = {
     # OpenAI / GPT
    "GPT-cl100k": tiktoken.get_encoding("cl100k_base"),
    "o200k_base": tiktoken.get_encoding("o200k_base"),
    "p50k_base": tiktoken.get_encoding("p50k_base"),
    "GPT-2 BPE": tiktoken.get_encoding("gpt2"),

    # Hugging Face Transformers
    "CodeGen BPE": AutoTokenizer.from_pretrained("Salesforce/codegen-350M-mono"),
    "BERT WordPiece": AutoTokenizer.from_pretrained("bert-base-uncased"),
    "T5 SentencePiece": AutoTokenizer.from_pretrained("t5-small"),
    "DistilGPT2 BPE": AutoTokenizer.from_pretrained("distilgpt2"),
    
    # LLaMA (Meta AI)
    "LLaMA-SP": AutoTokenizer.from_pretrained(
        "hf-internal-testing/llama-tokenizer", use_fast=False
    ),
}


def count_tokens(tokenizer, text: str) -> int:
    if hasattr(tokenizer, "encode") and not hasattr(tokenizer, "__call__"):
        return len(tokenizer.encode(text))
    return len(tokenizer(text)["input_ids"])

# ----------------------------
# ENTITY STATE
# ----------------------------
@dataclass
class EntityState:
    x: int = 0
    y: int = 0
    rotation: int = 0
    color: int = 0
    speed: int = 1
    shape: int = 1

# ----------------------------
# OPCODES
# ----------------------------
SET_SHAPE = 10
SET_COLOR = 11
SET_SPEED = 12
MOVE      = 20
ROTATE    = 21
SEEK      = 30
CONSUME   = 31

# ----------------------------
# VVM EXECUTION — Numba + NumPy
# ----------------------------
@njit
def execute_instruction(state_arr, ip, program):
    opcode = program[ip]
    ip += 1
    
    if opcode == SET_SHAPE:
        state_arr[5] = program[ip]  # shape
        ip += 1
    elif opcode == SET_COLOR:
        state_arr[3] = program[ip]  # color
        ip += 1
    elif opcode == SET_SPEED:
        state_arr[4] = program[ip]  # speed
        ip += 1
    elif opcode == MOVE:
        dx = program[ip]
        dy = program[ip+1]
        state_arr[0] += dx * state_arr[4]
        state_arr[1] += dy * state_arr[4]
        ip += 2
    elif opcode == ROTATE:
        state_arr[2] += program[ip]
        ip += 1
    elif opcode == SEEK:
        tx = program[ip]
        ty = program[ip+1]
        ip += 2
        if state_arr[0] < tx: state_arr[0] += state_arr[4]
        if state_arr[0] > tx: state_arr[0] -= state_arr[4]
        if state_arr[1] < ty: state_arr[1] += state_arr[4]
        if state_arr[1] > ty: state_arr[1] -= state_arr[4]
    elif opcode == CONSUME:
        pass
    else:
        raise ValueError(f"Invalid opcode {opcode}")
    
    return ip

@njit
def run_program(state_arr, program):
    ip = 0
    while ip < len(program):
        ip = execute_instruction(state_arr, ip, program)

def entity_to_array(entity: EntityState):
    return np.array([entity.x, entity.y, entity.rotation, entity.color, entity.speed, entity.shape], dtype=np.int64)

def array_to_entity(state_arr, entity: EntityState):
    entity.x, entity.y, entity.rotation, entity.color, entity.speed, entity.shape = state_arr

# ----------------------------
# SEMANTICALLY EQUIVALENT PROGRAMS
# ----------------------------
VVM_PROGRAM = np.array([
    SET_COLOR, 1,        # BLUE
    SET_SPEED, 1,
    MOVE, 3, 2,
    SET_SHAPE, 2,        # CIRCLE
    SET_COLOR, 2,        # RED
    ROTATE, 90,
    SET_COLOR, 3,        # GOLD
    CONSUME,
    SEEK, 10, 10
], dtype=np.int64)

# ----------------------------
# TRADITIONAL CODE (REFERENCE)
# ----------------------------
TRADITIONAL_CODE = """
def set_shape(e, v): e.shape = v
def set_color(e, v): e.color = v
def set_speed(e, v): e.speed = v
def move(e, dx, dy): e.x += dx * e.speed; e.y += dy * e.speed
def rotate(e, a): e.rotation += a
def seek(e, tx, ty):
    if e.x < tx: e.x += e.speed
    if e.x > tx: e.x -= e.speed
    if e.y < ty: e.y += e.speed
    if e.y > ty: e.y -= e.speed
def consume(e): pass

set_color(entity, 1)
set_speed(entity, 1)
move(entity, 3, 2)

set_shape(entity, 2)
set_color(entity, 2)
rotate(entity, 90)

set_color(entity, 3)
consume(entity)

seek(entity, 10, 10)
"""

# ----------------------------
# BENCHMARK 1 — TOKENIZATION
# ----------------------------
print("\n" + "="*60)
print("BENCHMARK 1 — TOKENIZATION")
print("="*60)

# ----------------------------
# SERIALIZATION (TOKEN OPTIMIZED)
# ----------------------------
def serialize_program(data: Union[list, np.ndarray]) -> str:
    """
    Serializa uma lista ou numpy array para string.
    """
    if isinstance(data, np.ndarray):
        data = data.tolist()
    return ' '.join(map(str, data))


SERIALIZED_VVM = serialize_program(VVM_PROGRAM)
for name, tokenizer in tokenizers.items():
    trad_tokens = count_tokens(tokenizer, TRADITIONAL_CODE)
    vvm_tokens = count_tokens(tokenizer, SERIALIZED_VVM)
    reduction = (1 - vvm_tokens / trad_tokens) * 100

    print(f"""
[TOKENIZER] {name}
Traditional: {trad_tokens}
VVM:         {vvm_tokens}
Reduction:   {reduction:.2f}%
""")

# ----------------------------
# BENCHMARK 2 — EXECUTION
# ----------------------------
print("\n" + "="*60)
print("BENCHMARK 2 — EXECUTION")
print("="*60)

entity = EntityState()
state_arr = entity_to_array(entity)
run_program(state_arr, VVM_PROGRAM)
array_to_entity(state_arr, entity)

print("Final entity state (VVM):", entity)

# ----------------------------
# EXECUTANDO TRADITIONAL_CODE COM exec()
# ----------------------------
entity_trad = EntityState()
exec_env = {"entity": entity_trad}
exec(TRADITIONAL_CODE, exec_env)
print("Final entity state (TRADITIONAL_CODE):", entity_trad)

# ----------------------------
# BENCHMARK 3 — SCALE
# ----------------------------
ITERATIONS = [1, 10, 100, 1_000, 10_000, 100_000]
tokenizer_base = tokenizers["GPT-cl100k"]

tokens_traditional = []
tokens_vvm = []
time_traditional = []
time_vvm = []

for n in ITERATIONS:
    tokens_traditional.append(count_tokens(tokenizer_base, TRADITIONAL_CODE) * n)
    tokens_vvm.append(count_tokens(tokenizer_base, SERIALIZED_VVM) * n)

    # VVM
    state_arr = entity_to_array(EntityState())
    start = time.perf_counter()
    for _ in range(n):
        run_program(state_arr, VVM_PROGRAM)
    time_vvm.append(time.perf_counter() - start)

    # Traditional (somente overhead, simulação)
    start = time.perf_counter()
    for _ in range(n):
        pass
    time_traditional.append(time.perf_counter() - start)

# ----------------------------
# COST MODEL — GPT-5.2
# ----------------------------
COST_INPUT = 1.75
COST_CACHE = 0.175
CACHE_RATIO = 0.70

EFFECTIVE_COST = COST_INPUT * (1 - CACHE_RATIO) + COST_CACHE * CACHE_RATIO

cost_traditional = [(t / 1_000_000) * EFFECTIVE_COST for t in tokens_traditional]
cost_vvm = [(t / 1_000_000) * EFFECTIVE_COST for t in tokens_vvm]

# ----------------------------
# PLOTS
# ----------------------------
fig, axes = plt.subplots(1, 3, figsize=(20, 6))

axes[0].plot(ITERATIONS, tokens_traditional, marker="o", label="Traditional")
axes[0].plot(ITERATIONS, tokens_vvm, marker="o", label="VVM")
axes[0].set_xscale("log"); axes[0].set_yscale("log")
axes[0].set_title("Tokens vs Scale")
axes[0].legend(); axes[0].grid(True)

axes[1].plot(ITERATIONS, time_traditional, marker="o", label="Traditional")
axes[1].plot(ITERATIONS, time_vvm, marker="o", label="VVM")
axes[1].set_xscale("log"); axes[1].set_yscale("log")
axes[1].set_title("Execution Time vs Scale")
axes[1].legend(); axes[1].grid(True)

axes[2].plot(ITERATIONS, cost_traditional, marker="o", label="Traditional")
axes[2].plot(ITERATIONS, cost_vvm, marker="o", label="VVM")
axes[2].set_xscale("log"); axes[2].set_yscale("log")
axes[2].set_title("Cost vs Scale (GPT-5.2)")
axes[2].legend(); axes[2].grid(True)

plt.suptitle("VVM Realtime Benchmark — Semantic Equivalence (Numba + NumPy)")
plt.tight_layout()
plt.show()

print("\n✅ Benchmark completed (optimized VVM with Numba + NumPy).")
