import os
from time import time
from urllib import response
from google import genai

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
MODEL_NAME = "gemini-2.5-flash-lite"

def stress_test_factory(n_operations, mode="python"):
    """
    Gera um prompt de teste de estresse para comparar verbosidade.
    """
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

N_NOISE = 500

for mode in ["python", "vvm"]:
    prompt = stress_test_factory(N_NOISE, mode)
    
    token_count_resp = client.models.count_tokens(model=MODEL_NAME, contents=prompt)
    tokens = token_count_resp.total_tokens
    
    start_time = time()
    try:
        response = client.models.generate_content(model=MODEL_NAME, contents=prompt)
        answer = response.text.strip()
    except Exception as e:
        answer = f"Erro na chamada: {e}"
    
    duration = time() - start_time
    
    print(f"MODE: {mode.upper()}")
    print(f"Tokens no Contexto: {tokens}")
    print(f"Resposta da IA: {answer}")
    print(f"Latência: {duration:.2f}s")
    print("-" * 30)