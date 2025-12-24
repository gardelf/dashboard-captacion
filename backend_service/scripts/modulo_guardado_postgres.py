"""
Módulo de Guardado - PostgreSQL (Render)
Guarda fichas procesadas en la base de datos PostgreSQL de Render.
"""

import os
import psycopg2
from datetime import datetime
import hashlib
from modulo_lectura_sheets import leer_claves_desde_sheets

# Cargar configuración desde Google Sheets
_config = None

def _get_config():
    """Obtiene configuración (usa cache)"""
    global _config
    if _config is None:
        _config = leer_claves_desde_sheets()
    return _config

def generar_id_ficha(url):
    """Genera un ID único para una ficha"""
    timestamp = datetime.now().strftime('%Y%m%d')
    hash_url = hashlib.md5(url.encode()).hexdigest()[:8]
    return f"RND-{timestamp}-{hash_url}"

def es_institucional(ficha):
    """
    Determina si una ficha es de una página institucional.
    Criterios:
    - Dominio termina en .edu, .ac.uk, .edu.es, .edu.au, etc.
    - URL contiene: /admissions/, /programs/, /housing/, /international/, /students/
    - Título contiene: University, Business School, College, Institute, Admissions
    """
    url = ficha.get('url', '').lower()
    dominio = ficha.get('dominio', '').lower()
    titulo = ficha.get('titulo', '').lower()
    
    # Dominios educativos
    dominios_edu = ['.edu', '.ac.uk', '.edu.es', '.edu.au', '.ac.nz', '.edu.mx']
    if any(dominio.endswith(ext) for ext in dominios_edu):
        return True
    
    # URLs institucionales
    keywords_url = ['/admissions/', '/programs/', '/housing/', '/international/', '/students/', '/study-abroad/']
    if any(keyword in url for keyword in keywords_url):
        return True
    
    # Títulos institucionales
    keywords_titulo = ['university', 'business school', 'college', 'institute', 'admissions', 'study abroad']
    if any(keyword in titulo for keyword in keywords_titulo):
        return True
    
    return False

def es_red_social(ficha):
    """
    Determina si una ficha es de una red social.
    Redes sociales: reddit, facebook, linkedin, twitter/x, instagram
    """
    dominio = ficha.get('dominio', '').lower()
    redes_sociales = ['reddit.com', 'facebook.com', 'linkedin.com', 'twitter.com', 'x.com', 'instagram.com']
    
    return any(red in dominio for red in redes_sociales)

def debe_guardar_ficha(ficha):
    """
    Determina si una ficha debe guardarse según las reglas de filtrado.
    
    Regla:
    - Si es red social → SIEMPRE guardar
    - Si es institucional Y (NO tiene email Y NO tiene formulario) → NO guardar
    - En cualquier otro caso → Guardar
    """
    # Redes sociales siempre se guardan
    if es_red_social(ficha):
        return True, "Red social"
    
    # Si no es institucional, guardar
    if not es_institucional(ficha):
        return True, "No institucional"
    
    # Es institucional: verificar email y formulario
    tiene_email = ficha.get('email') and ficha.get('email').strip()
    tiene_formulario = ficha.get('tiene_formulario') == True
    
    # Si NO tiene email Y NO tiene formulario → NO guardar
    if not tiene_email and not tiene_formulario:
        return False, "Institucional sin email ni formulario"
    
    # En cualquier otro caso, guardar
    return True, "Institucional con contacto"

def verificar_duplicado(url):
    """
    Consulta si una URL ya existe en la tabla 'fichas'.
    Returns: True si existe, False si es nueva.
    """
    config = _get_config()
    try:
        conn = psycopg2.connect(config['DATABASE_URL'])
        cursor = conn.cursor()
        
        cursor.execute("SELECT id FROM fichas WHERE url = %s LIMIT 1", (url,))
        result = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        return result is not None
        
    except Exception as e:
        print(f"⚠️ Error verificando duplicado ({url[:50]}...): {e}")
        return False

def guardar_fichas(fichas):
    """
    Guarda una lista de fichas en PostgreSQL de Render, ignorando duplicados.
    """
    if not fichas:
        print("⚠️ No hay fichas para guardar")
        return 0

    guardadas = 0
    duplicadas = 0
    errores = 0

    print(f"💾 Iniciando guardado de {len(fichas)} fichas en PostgreSQL (Render)...")

    filtradas = 0
    
    for ficha in fichas:
        url = ficha.get('url')
        
        # 1. Aplicar filtro institucional
        debe_guardar, razon = debe_guardar_ficha(ficha)
        if not debe_guardar:
            print(f"  🚫 Filtrada ({razon}): {url[:50]}...")
            filtradas += 1
            continue
        
        # 2. Verificar duplicado
        if verificar_duplicado(url):
            print(f"  ⏭️ Duplicado ignorado: {url[:50]}...")
            duplicadas += 1
            continue

        # 2. Insertar en PostgreSQL
        try:
            config = _get_config()
            conn = psycopg2.connect(config['DATABASE_URL'])
            cursor = conn.cursor()
            
            # Generar ID si no existe
            ficha_id = ficha.get('id') or generar_id_ficha(url)
            
            # Preparar valores
            valores = (
                ficha_id,
                ficha.get('tipo'),
                ficha.get('keyword'),
                ficha.get('url'),
                ficha.get('titulo'),
                ficha.get('snippet'),
                ficha.get('dominio'),
                ficha.get('institucion'),
                ficha.get('email'),
                ficha.get('telefono'),
                ficha.get('tiene_formulario'),
                ficha.get('plataforma_social'),
                ficha.get('username'),
                ficha.get('subreddit'),
                ficha.get('grupo_facebook'),
                ficha.get('fecha_detectada'),
                ficha.get('prioridad'),
                ficha.get('propuesta_comunicativa'),
                ficha.get('canal_recomendado'),
                ficha.get('estado', 'pendiente'),
                ficha.get('procesada', 'NO'),
                ficha.get('fecha_contacto')
            )
            
            cursor.execute("""
                INSERT INTO fichas (
                    id, tipo, keyword, url, titulo, snippet, dominio,
                    institucion, email, telefono, tiene_formulario,
                    plataforma_social, username, subreddit, grupo_facebook,
                    fecha_detectada, prioridad, propuesta_comunicativa,
                    canal_recomendado, estado, procesada, fecha_contacto
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
            """, valores)
            
            conn.commit()
            cursor.close()
            conn.close()
            
            print(f"  ✅ Guardada: {ficha_id}")
            guardadas += 1
            
        except Exception as e:
            print(f"  ❌ Error guardando {url[:50]}...: {e}")
            errores += 1

    print(f"\n📊 RESUMEN GUARDADO")
    print(f"  ✅ Nuevas: {guardadas}")
    print(f"  🚫 Filtradas: {filtradas}")
    print(f"  ⏭️ Duplicadas: {duplicadas}")
    print(f"  ❌ Errores: {errores}")
    
    return guardadas

if __name__ == "__main__":
    # Test
    ficha_test = {
        'tipo': 'test',
        'keyword': 'test keyword',
        'url': f'https://test-postgres-{datetime.now().timestamp()}.com',
        'titulo': 'Test PostgreSQL Render',
        'snippet': 'Probando guardado en PostgreSQL de Render',
        'dominio': 'test.com',
        'prioridad': 'Alta'
    }
    
    resultado = guardar_fichas([ficha_test])
    print(f"\n✅ Test completado: {resultado} ficha(s) guardada(s)")
