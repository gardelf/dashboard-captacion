"""
Módulo de enriquecimiento con ChatGPT usando SQLite
Lee el prompt desde Google Sheets (pestaña Prompt_ChatGPT)
Adaptado de modulo_enriquecimiento_postgres.py
"""
import sqlite3
import requests
import json
import os
from modulo_lectura_sheets import leer_claves_desde_sheets

DB_PATH = os.getenv('DB_PATH', 'fichas.db')

# Cache de configuración
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
        
        print("⚠️ Usando prompt por defecto")
        return None
            
    except Exception as e:
        print(f"⚠️ Error accediendo a Google Sheet: {e}")
        return None

def obtener_fichas_pendientes(limite=5):
    """Obtiene fichas pendientes de enriquecer desde SQLite"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
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
            cursor.execute("""
                SELECT id, tipo, keyword, url, titulo, snippet, dominio,
                       institucion, email, telefono, plataforma_social, 
                       username, subreddit, grupo_facebook
                FROM fichas 
                WHERE procesada = 'NO' 
                ORDER BY fecha_creacion ASC 
                LIMIT ?
            """, (limite,))
        
        fichas = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        print(f"✅ Obtenidas {len(fichas)} fichas pendientes de enriquecer")
        return fichas
        
    except Exception as e:
        print(f"❌ Error obteniendo fichas: {e}")
        return []

def enriquecer_con_chatgpt(ficha, prompt_base=None):
    """
    Enriquece una ficha usando ChatGPT.
    Retorna: {'propuesta': str, 'prioridad': str, 'canal': str}
    """
    config = _get_config()
    
    if not config.get('OPENAI_API_KEY'):
        print("❌ Error: OPENAI_API_KEY no configurada")
        return None
    
    # Leer prompt desde Sheets o usar por defecto
    prompt_custom = leer_prompt_desde_sheet()
    prompt = prompt_custom or prompt_base or """
    Analiza esta ficha de estudiante potencial y proporciona:
    1. Una propuesta comunicativa personalizada (máx 200 caracteres)
    2. Nivel de prioridad (ALTA, MEDIA, BAJA)
    3. Canal recomendado (email, reddit, whatsapp, facebook, formulario)
    
    Ficha:
    {ficha_json}
    
    Responde en JSON: {"propuesta": "...", "prioridad": "...", "canal": "..."}
    """
    
    ficha_json = json.dumps(ficha, ensure_ascii=False, indent=2)
    prompt_final = prompt.format(ficha_json=ficha_json)
    
    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {config['OPENAI_API_KEY']}",
                "Content-Type": "application/json"
            },
            json={
                "model": "gpt-4-turbo",
                "messages": [
                    {"role": "system", "content": "Eres un experto en captación de estudiantes internacionales."},
                    {"role": "user", "content": prompt_final}
                ],
                "temperature": 0.7,
                "max_tokens": 300
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            content = data['choices'][0]['message']['content']
            
            # Parsear JSON de respuesta
            try:
                resultado = json.loads(content)
                return {
                    'propuesta': resultado.get('propuesta', ''),
                    'prioridad': resultado.get('prioridad', 'MEDIA'),
                    'canal': resultado.get('canal', 'email')
                }
            except json.JSONDecodeError:
                print(f"⚠️ Error parseando respuesta de ChatGPT: {content[:100]}")
                return None
        else:
            print(f"❌ Error ChatGPT: {response.status_code} - {response.text[:100]}")
            return None
            
    except Exception as e:
        print(f"❌ Error llamando a ChatGPT: {e}")
        return None

def actualizar_ficha_enriquecida(ficha_id, propuesta, prioridad, canal):
    """Actualiza una ficha con datos enriquecidos"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE fichas 
            SET propuesta_comunicativa = ?,
                prioridad = ?,
                canal_recomendado = ?,
                procesada = 'SÍ',
                ultima_actualizacion = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (propuesta, prioridad, canal, ficha_id))
        
        conn.commit()
        conn.close()
        
        print(f"  ✅ Enriquecida: {ficha_id}")
        return True
        
    except Exception as e:
        print(f"  ❌ Error actualizando: {e}")
        return False

def enriquecer_fichas(limite=5):
    """
    Enriquece fichas pendientes con ChatGPT.
    """
    print("\n🤖 INICIANDO ENRIQUECIMIENTO CON CHATGPT")
    print("=" * 50)
    
    fichas = obtener_fichas_pendientes(limite)
    
    if not fichas:
        print("⚠️ No hay fichas pendientes de enriquecer")
        return 0
    
    enriquecidas = 0
    errores = 0
    
    for i, ficha in enumerate(fichas, 1):
        print(f"\n[{i}/{len(fichas)}] Enriqueciendo: {ficha['titulo'][:50]}...")
        
        resultado = enriquecer_con_chatgpt(ficha)
        
        if resultado:
            if actualizar_ficha_enriquecida(
                ficha['id'],
                resultado['propuesta'],
                resultado['prioridad'],
                resultado['canal']
            ):
                enriquecidas += 1
            else:
                errores += 1
        else:
            errores += 1
        
        # Rate limiting para OpenAI
        import time
        time.sleep(1)
    
    print("\n" + "=" * 50)
    print(f"✅ Enriquecidas: {enriquecidas}")
    print(f"❌ Errores: {errores}")
    print("=" * 50)
    
    return enriquecidas

if __name__ == "__main__":
    # Test
    enriquecidas = enriquecer_fichas(limite=2)
    print(f"\n✅ Test completado: {enriquecidas} ficha(s) enriquecida(s)")
