from openai import OpenAI
import json

OPENAI_API_KEY = "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"

SYSTEM_PROMPT = """Eres un asistente que ayuda a estudiantes internacionales a encontrar alojamiento en Madrid para el año 2026.

Analiza el siguiente resultado de búsqueda y extrae información útil.

Devuelve SOLO un JSON válido con estos campos:
{
  "institucion": "Nombre completo de la universidad u organización (null si no identificable)",
  "email": "Email de contacto si aparece (null si no)",
  "telefono": "Teléfono con código de país si aparece (null si no)",
  "tiene_formulario": "SI" | "NO" (si la URL parece ser un formulario de contacto),
  "canal_recomendado": "email" | "reddit" | "whatsapp" | "form" | "web",
  "propuesta_comunicativa": "Mensaje breve (2-4 líneas) personalizado para contactar"
}"""

client = OpenAI(api_key=OPENAI_API_KEY)

ficha_ejemplo = {
    'titulo': 'Ficha de Prueba PostgreSQL Local',
    'snippet': 'Esta es una ficha de prueba para validar conexión a PostgreSQL local.',
    'url': 'https://test-db-03bcb24f.com',
    'plataforma_social': 'Web',
    'keyword': 'test_db_connection',
    'dominio': 'test-db.com'
}

prompt_usuario = f"""
**Título:** {ficha_ejemplo.get('titulo', 'Sin título')}

**Snippet:** {ficha_ejemplo.get('snippet', 'Sin descripción')}

**URL:** {ficha_ejemplo.get('url', 'Sin URL')}

**Plataforma:** {ficha_ejemplo.get('plataforma_social', 'Web')}

**Keyword de búsqueda:** {ficha_ejemplo.get('keyword', 'Sin keyword')}

**Dominio:** {ficha_ejemplo.get('dominio', 'Desconocido')}
"""

print("🤖 Llamando a ChatGPT...")
response = client.chat.completions.create(
    model="gpt-4.1-mini",
    messages=[
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": prompt_usuario}
    ],
    temperature=0.7,
    max_tokens=500
)

contenido = response.choices[0].message.content.strip()

print("\n📄 RESPUESTA CRUDA DE CHATGPT:")
print("="*60)
print(contenido)
print("="*60)

# Limpiar si viene con ```json
if contenido.startswith("```"):
    contenido = contenido.split("```")[1]
    if contenido.startswith("json"):
        contenido = contenido[4:]

datos = json.loads(contenido.strip())

print("\n📊 DATOS PARSEADOS:")
print(json.dumps(datos, indent=2, ensure_ascii=False))

print("\n🔍 ANÁLISIS DE CAMPOS PROBLEMÁTICOS:")
print("="*60)
for campo, valor in datos.items():
    print(f"\n{campo}:")
    print(f"  Tipo: {type(valor)}")
    print(f"  Valor: {repr(valor)}")
    if isinstance(valor, str):
        print(f"  Longitud: {len(valor)} caracteres")
        tiene_saltos = '\n' in valor
        tiene_comillas = "'" in valor or '"' in valor
        print(f"  Contiene saltos de línea: {'Sí' if tiene_saltos else 'No'}")
        print(f"  Contiene comillas: {'Sí' if tiene_comillas else 'No'}")

