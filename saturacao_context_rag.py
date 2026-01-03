import os
import time
import re
import numpy as np
import matplotlib.pyplot as plt
from google import genai
from sentence_transformers import SentenceTransformer
import faiss

# ---------------- CONFIG ----------------
MODEL_NAME = "gemini-2.0-flash-lite"
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

STEPS = [10, 100, 500, 1000]
REPEATS = 5

# ---------------- DATA GEN ----------------
def stress_test_factory(n_ops, mode="python"):
    expected = "999"
    question = "What is the value of the initial key? Answer only with the number."

    if mode == "python":
        ctx = f"initial_key = {expected}\n"
        for i in range(n_ops):
            ctx += f"item_{i} = {i} * 2\nupdate_inventory(item_{i})\n"
        return ctx, question, expected

    ctx = f"100 {expected} "
    for i in range(n_ops):
        ctx += f"40 {i} {i*2} "
    ctx = "Rules: 100:SetKey, 40:UpdateInv\n" + ctx
    return ctx, question, expected

# ---------------- RAG ----------------
def run_rag(context, query):
    start = time.time()
    chunks = context.split("\n")
    emb = embedding_model.encode(chunks)

    index = faiss.IndexFlatL2(emb.shape[1])
    index.add(np.array(emb).astype("float32"))

    q_emb = embedding_model.encode([query])
    _, I = index.search(np.array(q_emb).astype("float32"), k=2)

    retrieved = "\n".join(chunks[i] for i in I[0])
    return retrieved, time.time() - start

# ---------------- METRIC ----------------
def exact_match(answer, target):
    return int(bool(re.fullmatch(rf"\b{target}\b", answer.strip())))

# ---------------- BENCHMARK ----------------
results = {
    m: {"lat": [], "tok": [], "acc": []}
    for m in ["python", "vvm", "rag"]
}

for n in STEPS:
    for _ in range(REPEATS):

        ctx_py, q, tgt = stress_test_factory(n, "python")
        ctx_vvm, _, _ = stress_test_factory(n, "vvm")

        configs = {
            "python": ctx_py,
            "vvm": ctx_vvm,
            "rag": ctx_py
        }

        for mode, ctx in configs.items():
            overhead = 0

            if mode == "rag":
                ctx, overhead = run_rag(ctx, q)
                prompt = f"Context:\n{ctx}\n\nQuestion: {q}"
            else:
                prompt = f"{ctx}\n\nQuestion: {q}"

            tokens = client.models.count_tokens(
                model=MODEL_NAME,
                contents=prompt
            ).total_tokens

            t0 = time.time()
            resp = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt
            )
            latency = (time.time() - t0) + overhead

            acc = exact_match(resp.text, tgt)

            results[mode]["lat"].append(latency)
            results[mode]["tok"].append(tokens)
            results[mode]["acc"].append(acc)

# ---------------- PLOT ----------------
def mean_std(arr):
    return np.mean(arr), np.std(arr)

labels = ["Python", "VVM", "RAG"]

fig, ax = plt.subplots(1, 3, figsize=(20, 6))

for i, metric in enumerate(["lat", "tok", "acc"]):
    means = []
    stds = []

    for m in ["python", "vvm", "rag"]:
        m_mean, m_std = mean_std(results[m][metric])
        means.append(m_mean)
        stds.append(m_std)

    ax[i].bar(labels, means, yerr=stds, capsize=5)
    ax[i].set_title(metric.upper())

plt.tight_layout()
plt.savefig("benchmark_mestrado_final.png")
plt.show()
