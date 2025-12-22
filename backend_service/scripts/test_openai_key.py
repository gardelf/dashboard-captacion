from openai import OpenAI
import json

API_KEY = "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"

print("🔑 Probando API Key de OpenAI...")
print(f"   Key: {API_KEY[:20]}...{API_KEY[-10:]}")

try:
    client = OpenAI(api_key=API_KEY)
    
    print("\n🤖 Enviando mensaje de prueba a ChatGPT...")
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": "Di 'Hola' en JSON con formato: {\"mensaje\": \"...\"}"}
        ],
        temperature=0.7,
        max_tokens=50
    )
    
    contenido = response.choices[0].message.content.strip()
    
    print("\n✅ CONEXIÓN EXITOSA!")
    print(f"\n📄 Respuesta de ChatGPT:")
    print(contenido)
    
    print(f"\n📊 Uso de tokens:")
    print(f"   Prompt: {response.usage.prompt_tokens}")
    print(f"   Completion: {response.usage.completion_tokens}")
    print(f"   Total: {response.usage.total_tokens}")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

