import subprocess
import json
import os

api_key = "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"

ficha = {
    'titulo': 'Test',
    'snippet': 'Test snippet',
    'url': 'https://test.com',
    'plataforma_social': 'Web',
    'keyword': 'test',
    'dominio': 'test.com'
}

SYSTEM_PROMPT = "Eres un asistente. Responde solo con JSON: {\"test\": \"ok\"}"

payload = {
    "model": "gpt-4o-mini",
    "messages": [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": "Test"}
    ],
    "temperature": 0.7,
    "max_tokens": 100
}

payload_json = json.dumps(payload).replace("'", "'\\''")

cmd = (
    f'curl -s https://api.openai.com/v1/chat/completions '
    f'-H "Content-Type: application/json" '
    f'-H "Authorization: Bearer {api_key}" '
    f"-d '{payload_json}'"
)

print("🔧 Ejecutando curl...")
print(f"Comando (primeros 150 chars): {cmd[:150]}...")

env = {k: v for k, v in os.environ.items() if not k.startswith('OPENAI')}

result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30, env=env)

print(f"\n📊 Return code: {result.returncode}")
print(f"📊 Stderr: {result.stderr[:200] if result.stderr else 'vacío'}")
print(f"\n📄 Stdout (primeros 500 chars):")
print(result.stdout[:500])

if result.returncode == 0:
    try:
        response_data = json.loads(result.stdout)
        print("\n✅ JSON parseado correctamente")
        if 'error' in response_data:
            print(f"❌ Error de OpenAI: {response_data['error']}")
        else:
            print(f"✅ Respuesta: {response_data['choices'][0]['message']['content']}")
    except Exception as e:
        print(f"\n❌ Error parseando JSON: {e}")

