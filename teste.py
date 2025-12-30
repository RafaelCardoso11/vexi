import os
from google import genai
from google.genai import types
from pydantic import BaseModel, Field

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

MODEL_ID = "gemini-2.5-flash"

system_rules = """
Role: Bytecode Compiler.
10:Shape(1:Circ,2:Sq,3:Tri)
11:Color(1:R,2:B,3:G)
12:Speed(V)
20:Move(X,Y)
21:Rotate(D)
30:Seek(X,Y)
31:Consume
"""

comportamento_input = "A entidade deve iniciar definindo sua forma como Quadrado e cor Azul. Defina velocidade 5. Mova-se para x=50, y=50. Gire 90 graus. Busque o alvo em 100, 100 e finalmente Consuma."

class BytecodeOutput(BaseModel):
    bytecode: str = Field(description="ONLY integers separated by spaces. No colons, no commas. Example: '10 2 11 1'")
    
chat = client.chats.create(
    model=MODEL_ID,
    config=types.GenerateContentConfig(
        system_instruction=system_rules,
        response_mime_type="application/json",
        response_schema=BytecodeOutput,
        temperature=0.0
    )
)

print("--- COMPILADOR DE BYTECODE ATIVO ---")
print("Digite o comportamento (ou 'sair' para encerrar):")

while True:
    texto_usuario = input("\nTarefa > ")
    
    if texto_usuario.lower() in ["sair", "exit", "quit"]:
        break
        
    try:
        response = chat.send_message(texto_usuario)
        uso = response.usage_metadata
        print(f"Bytecode: {response.text.strip()}")
        print(f"--- [Tokens: Entrada: {uso.prompt_token_count} | Saída: {uso.candidates_token_count} | Total: {uso.total_token_count}] ---")
    except Exception as e:
        print(f"Erro: {e}")

print("\nEncerrando compilador...")