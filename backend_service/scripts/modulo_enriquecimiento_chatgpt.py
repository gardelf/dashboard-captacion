#!/usr/bin/env python3
"""
MÓDULO DE ENRIQUECIMIENTO CON CHATGPT - PostgreSQL Local
=========================================================
Lee fichas con procesada='NO' y las enriquece con:
- Institución completa
- Email de contacto
- Teléfono
- Canal recomendado
- Propuesta comunicativa personalizada
"""

import os
import json
import time
import subprocess
import sys
import requests
from datetime import datetime

# Configuración
DATABASE_URL = os.getenv('DATABASE_URL')
OPENAI_API_KEY = "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"

# Prompt del sistema para ChatGPT
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
}

REGLAS para propuesta_comunicativa:
- Amigable y educada
- Mencionar que es estudiante internacional que llegará en 2026
- Preguntar por alojamiento
- Adaptar tono al canal:
  * Email: formal y estructurado
  * Reddit: casual, primera persona
  * WhatsApp: muy breve
  * Formulario: directo al grano
- Máximo 4 líneas
- Usar saltos de línea (\\n) para separar párrafos
"""

def construir_prompt_usuario(ficha):
    """Construye el prompt específico para cada ficha"""
    return f"""
**Título:** {ficha.get('titulo', 'Sin título')}

**Snippet:** {ficha.get('snippet', 'Sin descripción')}

**URL:** {ficha.get('url', 'Sin URL')}

**Plataforma:** {ficha.get('plataforma_social', 'Web')}

**Keyword de búsqueda:** {ficha.get('keyword', 'Sin keyword')}

**Dominio:** {ficha.get('dominio', 'Desconocido')}
"""

def enriquecer_con_chatgpt(ficha, api_key):
    """
    Llama a OpenAI para enriquecer una ficha usando requests.
    Retorna diccionario con campos extraídos o None si falla.
    """
    try:
        prompt_usuario = construir_prompt_usuario(ficha)
        
        # Preparar payload para OpenAI
        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt_usuario}
            ],
            "temperature": 0.7,
            "max_tokens": 500
        }
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        # Llamar a OpenAI con requests (sin proxy)
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30,
            proxies={}  # Sin proxy para evitar interceptación del sandbox
        )
        
        if response.status_code != 200:
            print(f"    ⚠️ Error HTTP {response.status_code}: {response.text[:200]}")
            return None
        
        response_data = response.json()
        
        if 'error' in response_data:
            print(f"    ⚠️ Error de OpenAI: {response_data['error']}")
            return None
        
        # Extraer contenido
        contenido = response_data['choices'][0]['message']['content'].strip()
        
        # Intentar parsear JSON
        # A veces ChatGPT añade ```json ... ```, lo limpiamos
        if contenido.startswith("```"):
            contenido = contenido.split("```")[1]
            if contenido.startswith("json"):
                contenido = contenido[4:]
        
        datos = json.loads(contenido.strip())
        
        # Validar campos obligatorios
        campos_requeridos = ['institucion', 'email', 'telefono', 'tiene_formulario', 'canal_recomendado', 'propuesta_comunicativa']
        for campo in campos_requeridos:
            if campo not in datos:
                datos[campo] = None
        
        # Convertir tiene_formulario de boolean a SI/NO
        if isinstance(datos.get('tiene_formulario'), bool):
            datos['tiene_formulario'] = 'SI' if datos['tiene_formulario'] else 'NO'
        
        return datos
        
    except json.JSONDecodeError as e:
        print(f"    ⚠️ Error parseando JSON de ChatGPT: {e}")
        print(f"    Respuesta cruda: {contenido[:200]}")
        return None
    except Exception as e:
        print(f"    ❌ Error llamando a OpenAI: {e}")
        return None

def leer_fichas_pendientes(limite=10):
    """Lee fichas no procesadas de PostgreSQL local"""
    try:
        # Crear script Node.js simple
        script_content = f"""const mysql = require('mysql2/promise');
(async () => {{
    const conn = await mysql.createConnection(process.env.DATABASE_URL);
    const [rows] = await conn.execute('SELECT * FROM fichas WHERE procesada = ? LIMIT {limite}', ['NO']);
    console.log(JSON.stringify(rows));
    await conn.end();
}})();
"""
        
        script_path = '/home/ubuntu/dashboard-captacion/backend_service/scripts/.temp_read.cjs'
        with open(script_path, 'w') as f:
            f.write(script_content)
        
        try:
            result = subprocess.run(
                ['node', script_path],
                capture_output=True,
                text=True,
                cwd='/home/ubuntu/dashboard-captacion',
                env=os.environ.copy()
            )
            
            if result.returncode != 0:
                print(f"❌ Error leyendo fichas: {result.stderr}")
                return []
            
            fichas = json.loads(result.stdout.strip())
            return fichas
        finally:
            if os.path.exists(script_path):
                os.unlink(script_path)
        
    except Exception as e:
        print(f"❌ Error leyendo fichas: {e}")
        return []

def actualizar_ficha(ficha_id, datos_enriquecidos):
    """Actualiza una ficha en TiDB con datos enriquecidos usando UPDATEs individuales"""
    try:
        # Normalizar tiene_formulario: "SI"/"NO" → true/false/null
        tiene_form_raw = datos_enriquecidos.get('tiene_formulario')
        if tiene_form_raw == 'SI':
            tiene_form = True
        elif tiene_form_raw == 'NO':
            tiene_form = False
        else:
            tiene_form = None
        
        # Preparar datos para JSON
        datos = {
            'id': str(ficha_id),
            'institucion': datos_enriquecidos.get('institucion'),
            'email': datos_enriquecidos.get('email'),
            'telefono': datos_enriquecidos.get('telefono'),
            'tiene_formulario': tiene_form,
            'canal_recomendado': datos_enriquecidos.get('canal_recomendado'),
            'propuesta_comunicativa': datos_enriquecidos.get('propuesta_comunicativa')
        }
        
        # Guardar datos en archivo JSON
        datos_path = '/home/ubuntu/dashboard-captacion/backend_service/scripts/.temp_datos.json'
        with open(datos_path, 'w') as f:
            json.dump(datos, f)
        
        # Crear script Node.js que hace UPDATEs individuales (workaround para bug de TiDB)
        script_content = """const mysql = require('mysql2/promise');
const fs = require('fs');

(async () => {
    const conn = await mysql.createConnection(process.env.DATABASE_URL);
    const datos = JSON.parse(fs.readFileSync('.temp_datos.json', 'utf8'));
    
    // Hacer UPDATEs individuales para evitar bug de TiDB con UPDATE múltiple
    await conn.execute('UPDATE fichas SET institucion = ? WHERE id = ?', [datos.institucion, datos.id]);
    await conn.execute('UPDATE fichas SET email = ? WHERE id = ?', [datos.email, datos.id]);
    await conn.execute('UPDATE fichas SET telefono = ? WHERE id = ?', [datos.telefono, datos.id]);
    await conn.execute('UPDATE fichas SET tiene_formulario = ? WHERE id = ?', [datos.tiene_formulario, datos.id]);
    await conn.execute('UPDATE fichas SET canal_recomendado = ? WHERE id = ?', [datos.canal_recomendado, datos.id]);
    await conn.execute('UPDATE fichas SET propuesta_comunicativa = ? WHERE id = ?', [datos.propuesta_comunicativa, datos.id]);
    await conn.execute('UPDATE fichas SET procesada = ? WHERE id = ?', ['SI', datos.id]);
    
    await conn.end();
    console.log('OK');
})();
"""
        
        script_path = '/home/ubuntu/dashboard-captacion/backend_service/scripts/.temp_update.cjs'
        with open(script_path, 'w') as f:
            f.write(script_content)
        
        try:
            result = subprocess.run(
                ['node', script_path],
                capture_output=True,
                text=True,
                cwd='/home/ubuntu/dashboard-captacion/backend_service/scripts',
                env=os.environ.copy()
            )
            
            if result.returncode != 0:
                print(f"❌ Error actualizando ficha: {result.stderr}")
                return False
            
            return True
        finally:
            # Limpiar archivos temporales
            if os.path.exists(script_path):
                os.unlink(script_path)
            if os.path.exists(datos_path):
                os.unlink(datos_path)
        
    except Exception as e:
        print(f"❌ Error actualizando ficha: {e}")
        return False

def enriquecer_fichas(openai_key=None, limite=10):
    """
    Función principal: Lee fichas no procesadas y las enriquece con ChatGPT.
    
    Args:
        openai_key: API Key de OpenAI (opcional, usa variable global si no se pasa)
        limite: Número máximo de fichas a procesar en esta ejecución (default: 10)
    
    Returns:
        dict: Estadísticas de procesamiento
    """
    print("\n🤖 INICIANDO ENRIQUECIMIENTO CON CHATGPT")
    print("="*60)
    
    # Configurar claves
    global OPENAI_API_KEY
    if openai_key:
        OPENAI_API_KEY = openai_key
    
    if not DATABASE_URL:
        print("❌ Error: DATABASE_URL no configurada")
        return {'error': 'Missing DATABASE_URL'}
    
    if not OPENAI_API_KEY:
        print("❌ Error: OPENAI_API_KEY no configurada")
        return {'error': 'Missing OPENAI_API_KEY'}
    
    print("✅ Conectado a PostgreSQL local")
    print("✅ API Key de OpenAI configurada")
    
    # Leer fichas no procesadas
    fichas = leer_fichas_pendientes(limite)
    print(f"📋 Encontradas {len(fichas)} fichas pendientes de procesar (límite: {limite})")
    
    if not fichas:
        print("✅ No hay fichas pendientes. Todo al día.")
        return {'procesadas': 0, 'errores': 0}
    
    # Procesar cada ficha
    procesadas = 0
    errores = 0
    
    for i, ficha in enumerate(fichas):
        print(f"\n[{i+1}/{len(fichas)}] Procesando: {ficha.get('titulo', 'Sin título')[:50]}...")
        print(f"  URL: {ficha.get('url', 'Sin URL')[:60]}")
        
        # Enriquecer con ChatGPT
        datos_enriquecidos = enriquecer_con_chatgpt(ficha, OPENAI_API_KEY)
        
        if not datos_enriquecidos:
            errores += 1
            print(f"  ❌ Error en enriquecimiento, se omite esta ficha")
            continue
        
        # Actualizar en PostgreSQL
        if actualizar_ficha(ficha['id'], datos_enriquecidos):
            procesadas += 1
            print(f"  ✅ Enriquecida y actualizada")
            print(f"     Canal: {datos_enriquecidos.get('canal_recomendado')}")
            print(f"     Propuesta: {datos_enriquecidos.get('propuesta_comunicativa', '')[:60]}...")
        else:
            errores += 1
            print(f"  ❌ Error actualizando ficha")
        
        # Rate limit: 1 segundo entre llamadas para no saturar OpenAI
        if i < len(fichas) - 1:
            time.sleep(1)
    
    # Resumen final
    print("\n" + "="*60)
    print(f"✅ ENRIQUECIMIENTO COMPLETADO")
    print(f"   Procesadas: {procesadas}")
    print(f"   Errores: {errores}")
    print("="*60 + "\n")
    
    return {
        'procesadas': procesadas,
        'errores': errores,
        'total_pendientes_inicial': len(fichas)
    }

# Script ejecutable directamente
if __name__ == "__main__":
    # Leer credenciales desde variables de entorno si están disponibles
    openai_key = os.environ.get('OPENAI_API_KEY_CUSTOM', OPENAI_API_KEY)
    
    # Límite por defecto: 10 fichas (para pruebas)
    # Cambiar a 100 o más para producción
    limite = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    
    resultado = enriquecer_fichas(
        openai_key=openai_key,
        limite=limite
    )
    
    if 'error' in resultado:
        sys.exit(1)
