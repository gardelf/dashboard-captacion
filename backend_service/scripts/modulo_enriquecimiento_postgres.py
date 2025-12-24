#!/usr/bin/env python3
"""
Módulo de enriquecimiento con ChatGPT usando PostgreSQL de Render
Lee el prompt desde Google Sheets (pestaña Prompt_ChatGPT)
"""

import psycopg2
import requests
import json
import os
from modulo_lectura_sheets import leer_claves_desde_sheets

# Cargar configuración desde Google Sheets
_config = None

def _get_config():
    """Obtiene configuración (usa cache)"""
    global _config
    if _config is None:
        _config = leer_claves_desde_sheets()
    return _config

def leer_prompt_desde_sheet():
    """Lee el prompt de ChatGPT desde Google Sheets"""
    config = _get_config()
    try:
        url = f"https://sheets.googleapis.com/v4/spreadsheets/{config['SHEET_ID']}/values/Prompt_ChatGPT!A7?key={config['GOOGLE_API_KEY']}"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            rows = data.get('values', [])
            if rows and len(rows) > 0 and len(rows[0]) > 0:
                prompt = rows[0][0]
                print(f"✅ Prompt leído desde Google Sheet ({len(prompt)} caracteres)")
                return prompt
            else:
                print("⚠️ Prompt vacío en Google Sheet, usando prompt por defecto")
                return None
        else:
            print(f"⚠️ Error leyendo Google Sheet: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"⚠️ Error accediendo a Google Sheet: {e}")
        return None

def obtener_fichas_pendientes(limite=5):
    """Obtiene fichas pendientes de enriquecer desde PostgreSQL"""
    config = _get_config()
    try:
        conn = psycopg2.connect(config['DATABASE_URL'])
        cursor = conn.cursor()
        
        if limite is None:
            cursor.execute("""
                SELECT id, tipo, keyword, url, titulo, snippet, dominio,
                       institucion, email, telefono, plataforma_social, 
                       username, subreddit, grupo_facebook
                FROM fichas 
                WHERE procesada = 'NO' 
                ORDER BY fecha_creacion ASC
            """)
        else:
            cursor.execute(f"""
                SELECT id, tipo, keyword, url, titulo, snippet, dominio,
                       institucion, email, telefono, plataforma_social, 
                       username, subreddit, grupo_facebook
                FROM fichas 
                WHERE procesada = 'NO' 
                ORDER BY fecha_creacion ASC 
                LIMIT {limite}
            """)
        
        columnas = [desc[0] for desc in cursor.description]
        fichas = []
        
        for row in cursor.fetchall():
            ficha = dict(zip(columnas, row))
            fichas.append(ficha)
        
        cursor.close()
        conn.close()
        
        return fichas
        
    except Exception as e:
        print(f"❌ Error leyendo fichas: {e}")
        return []

def enriquecer_con_chatgpt(ficha, prompt_system, api_key=None):
    """Enriquece una ficha usando ChatGPT con el prompt del Google Sheet"""
    if api_key is None:
        config = _get_config()
        api_key = config['OPENAI_API_KEY']
    
    # Construir el JSON de la ficha para enviar a ChatGPT (TODOS LOS CAMPOS)
    ficha_json = {
        "id": ficha.get('id'),
        "tipo": ficha.get('tipo'),
        "keyword": ficha.get('keyword'),
        "url": ficha.get('url'),
        "titulo": ficha.get('titulo'),
        "snippet": ficha.get('snippet'),
        "dominio": ficha.get('dominio'),
        "institucion": ficha.get('institucion'),
        "email": ficha.get('email'),
        "telefono": ficha.get('telefono'),
        "tiene_formulario": ficha.get('tiene_formulario'),
        "plataforma_social": ficha.get('plataforma_social'),
        "username": ficha.get('username'),
        "subreddit": ficha.get('subreddit'),
        "grupo_facebook": ficha.get('grupo_facebook'),
        "fecha_detectada": str(ficha.get('fecha_detectada')) if ficha.get('fecha_detectada') else None,
        "estado": ficha.get('estado'),
        "procesada": ficha.get('procesada'),
        "fecha_contacto": str(ficha.get('fecha_contacto')) if ficha.get('fecha_contacto') else None,
        "fecha_creacion": str(ficha.get('fecha_creacion')) if ficha.get('fecha_creacion') else None,
        "ultima_actualizacion": str(ficha.get('ultima_actualizacion')) if ficha.get('ultima_actualizacion') else None
    }
    
    # Mensaje del usuario: el JSON de la ficha
    user_message = json.dumps(ficha_json, ensure_ascii=False, indent=2)
    
    try:
        response = requests.post(
            'https://api.openai.com/v1/chat/completions',
            headers={
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            },
            json={
                'model': 'gpt-4o-mini',
                'messages': [
                    {'role': 'system', 'content': prompt_system},
                    {'role': 'user', 'content': user_message}
                ],
                'temperature': 0.7,
                'max_tokens': 800,
                'response_format': {'type': 'json_object'}
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            content = data['choices'][0]['message']['content'].strip()
            
            # Parsear JSON
            resultado = json.loads(content)
            
            # Asegurar que tenga los campos necesarios
            return {
                'prioridad': resultado.get('prioridad', 'media'),
                'canal_recomendado': resultado.get('canal_recomendado', 'web'),
                'propuesta_comunicativa': resultado.get('propuesta_comunicativa', ''),
                'estado': resultado.get('estado', 'pendiente'),
                'procesada': resultado.get('procesada', True)
            }
        else:
            print(f"  ❌ Error API OpenAI: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"  ❌ Error enriqueciendo: {e}")
        return None

def actualizar_ficha(ficha_id, datos_enriquecidos):
    """Actualiza una ficha en PostgreSQL con datos enriquecidos"""
    config = _get_config()
    try:
        conn = psycopg2.connect(config['DATABASE_URL'])
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE fichas 
            SET 
                prioridad = %s,
                canal_recomendado = %s,
                propuesta_comunicativa = %s,
                estado = %s,
                procesada = 'SI',
                ultima_actualizacion = CURRENT_TIMESTAMP
            WHERE id = %s
        """, (
            datos_enriquecidos.get('prioridad'),
            datos_enriquecidos.get('canal_recomendado'),
            datos_enriquecidos.get('propuesta_comunicativa'),
            datos_enriquecidos.get('estado', 'pendiente'),
            ficha_id
        ))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error actualizando ficha: {e}")
        return False

def enriquecer_fichas(openai_key=None, limite=None):
    """
    Función principal: Lee fichas no procesadas y las enriquece con ChatGPT.
    """
    config = _get_config()
    
    api_key = openai_key or config['OPENAI_API_KEY']
    
    if limite is None:
        limite = config['LIMITE_ENRIQUECIMIENTO']
    
    print("🤖 INICIANDO ENRIQUECIMIENTO CON CHATGPT")
    print("=" * 60)
    
    # Leer prompt desde Google Sheet
    prompt_system = leer_prompt_desde_sheet()
    
    if not prompt_system:
        print("❌ No se pudo leer el prompt desde Google Sheet")
        return
    
    # Conectar a PostgreSQL
    try:
        conn = psycopg2.connect(config['DATABASE_URL'])
        conn.close()
        print("✅ Conectado a PostgreSQL (Render)")
    except Exception as e:
        print(f"❌ Error conectando a PostgreSQL: {e}")
        return
    
    # Verificar API Key
    if not api_key:
        print("❌ API Key de OpenAI no configurada")
        return
    
    print("✅ API Key de OpenAI configurada")
    
    # Leer fichas pendientes
    fichas = obtener_fichas_pendientes(limite)
    
    if not fichas:
        print("📋 No hay fichas pendientes de procesar")
        return
    
    print(f"📋 Encontradas {len(fichas)} fichas pendientes de procesar (límite: {limite})")
    print()
    
    procesadas = 0
    errores = 0
    
    for i, ficha in enumerate(fichas, 1):
        titulo_corto = (ficha['titulo'] or 'Sin título')[:50]
        print(f"[{i}/{len(fichas)}] Procesando: {titulo_corto}...")
        print(f"  URL: {ficha['url'][:50]}...")
        
        # Enriquecer con ChatGPT
        datos = enriquecer_con_chatgpt(ficha, prompt_system, api_key)
        
        if datos:
            # Actualizar en PostgreSQL
            if actualizar_ficha(ficha['id'], datos):
                print(f"  ✅ Enriquecida y actualizada")
                print(f"     Prioridad: {datos.get('prioridad')}")
                print(f"     Canal: {datos.get('canal_recomendado')}")
                propuesta_preview = (datos.get('propuesta_comunicativa', '') or '')[:60]
                print(f"     Propuesta: {propuesta_preview}...")
                procesadas += 1
            else:
                print(f"  ❌ Error al actualizar")
                errores += 1
        else:
            print(f"  ❌ Error al enriquecer")
            errores += 1
    
    print()
    print("=" * 60)
    print("✅ ENRIQUECIMIENTO COMPLETADO")
    print(f"   Procesadas: {procesadas}")
    print(f"   Errores: {errores}")
    print("=" * 60)

if __name__ == "__main__":
    enriquecer_fichas(limite=5)
