#!/usr/bin/env python3
"""
VERIFICADOR DE API KEY DE OPENAI
=================================
Prueba tu API key de OpenAI con diferentes métodos para verificar que funciona.
"""

import subprocess
import json
import os
import sys

# TU API KEY AQUÍ
API_KEY = "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"

print("="*70)
print("🔑 VERIFICADOR DE API KEY DE OPENAI")
print("="*70)
print(f"\nAPI Key: {API_KEY[:30]}...{API_KEY[-20:]}")
print(f"Longitud: {len(API_KEY)} caracteres")
print()

# ============================================================================
# PRUEBA 1: curl directo con entorno limpio
# ============================================================================
print("="*70)
print("PRUEBA 1: curl con entorno limpio (sin variables OPENAI del sandbox)")
print("="*70)

payload = {
    "model": "gpt-4o-mini",
    "messages": [{"role": "user", "content": "Di solo: OK"}],
    "max_tokens": 5
}

cmd = (
    f'curl -s https://api.openai.com/v1/chat/completions '
    f'-H "Content-Type: application/json" '
    f'-H "Authorization: Bearer {API_KEY}" '
    f"-d '{json.dumps(payload)}'"
)

# Entorno sin variables OPENAI
env = {k: v for k, v in os.environ.items() if not k.startswith('OPENAI')}

try:
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=15, env=env)
    
    if result.returncode == 0:
        response = json.loads(result.stdout)
        if 'error' in response:
            print(f"❌ Error de OpenAI: {response['error']['message']}")
        else:
            print(f"✅ ÉXITO!")
            print(f"   Respuesta: {response['choices'][0]['message']['content']}")
            print(f"   Modelo: {response['model']}")
            print(f"   Tokens usados: {response['usage']['total_tokens']}")
    else:
        print(f"❌ Error en curl: {result.stderr}")
except Exception as e:
    print(f"❌ Excepción: {e}")

print()

# ============================================================================
# PRUEBA 2: curl con variables de entorno del sandbox
# ============================================================================
print("="*70)
print("PRUEBA 2: curl CON variables OPENAI del sandbox (para comparar)")
print("="*70)

try:
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=15)
    
    if result.returncode == 0:
        response = json.loads(result.stdout)
        if 'error' in response:
            print(f"❌ Error de OpenAI: {response['error']['message']}")
            print(f"   Esto confirma que el sandbox está interceptando la llamada")
        else:
            print(f"✅ ÉXITO!")
            print(f"   Respuesta: {response['choices'][0]['message']['content']}")
    else:
        print(f"❌ Error en curl: {result.stderr}")
except Exception as e:
    print(f"❌ Excepción: {e}")

print()

# ============================================================================
# PRUEBA 3: Verificar qué variables OPENAI están configuradas
# ============================================================================
print("="*70)
print("PRUEBA 3: Variables de entorno OPENAI en el sandbox")
print("="*70)

openai_vars = {k: v for k, v in os.environ.items() if 'OPENAI' in k.upper()}
if openai_vars:
    for key, value in openai_vars.items():
        if 'KEY' in key.upper():
            print(f"   {key} = {value[:20]}...{value[-10:]}")
        else:
            print(f"   {key} = {value}")
else:
    print("   No hay variables OPENAI configuradas")

print()

# ============================================================================
# PRUEBA 4: Intentar con requests de Python
# ============================================================================
print("="*70)
print("PRUEBA 4: requests de Python (si está instalado)")
print("="*70)

try:
    import requests
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    
    # Intentar sin proxy
    response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers=headers,
        json=payload,
        timeout=15,
        proxies={}  # Sin proxy
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ ÉXITO!")
        print(f"   Respuesta: {data['choices'][0]['message']['content']}")
        print(f"   Modelo: {data['model']}")
    else:
        print(f"❌ Error HTTP {response.status_code}")
        print(f"   {response.json()}")
        
except ImportError:
    print("⚠️  requests no está instalado")
except Exception as e:
    print(f"❌ Excepción: {e}")

print()

# ============================================================================
# RESUMEN
# ============================================================================
print("="*70)
print("📊 RESUMEN")
print("="*70)
print("""
Si la PRUEBA 1 funciona pero la PRUEBA 2 falla:
  → Tu API key es válida
  → El sandbox de Manus está interceptando las llamadas
  → Solución: usar entorno limpio (sin variables OPENAI)

Si todas las pruebas fallan:
  → Verifica tu API key en https://platform.openai.com/api-keys
  → Verifica que tengas créditos en https://platform.openai.com/usage
  → Verifica límites en https://platform.openai.com/settings/organization/limits

Si la PRUEBA 4 funciona:
  → Podemos usar requests en lugar de curl
""")
print("="*70)
