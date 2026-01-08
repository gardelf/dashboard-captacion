"""
Módulo de Guardado - SQLite (Local)
Guarda fichas procesadas en SQLite local.
Adaptado de modulo_guardado_postgres.py
"""
import sqlite3
import os
from datetime import datetime
import hashlib

DB_PATH = os.getenv('DB_PATH', 'fichas.db')

def inicializar_db():
    """Crea la tabla si no existe"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS fichas (
            id TEXT PRIMARY KEY,
            tipo TEXT,
            keyword TEXT,
            url TEXT UNIQUE NOT NULL,
            titulo TEXT,
            snippet TEXT,
            dominio TEXT,
            institucion TEXT,
            email TEXT,
            telefono TEXT,
            tiene_formulario BOOLEAN,
            plataforma_social TEXT,
            username TEXT,
            subreddit TEXT,
            grupo_facebook TEXT,
            fecha_detectada TEXT,
            prioridad TEXT,
            propuesta_comunicativa TEXT,
            canal_recomendado TEXT,
            estado TEXT DEFAULT 'pendiente',
            procesada TEXT DEFAULT 'NO',
            fecha_contacto TEXT,
            fecha_creacion TEXT DEFAULT CURRENT_TIMESTAMP,
            ultima_actualizacion TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_url ON fichas(url)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_estado ON fichas(estado)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_procesada ON fichas(procesada)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_fecha_creacion ON fichas(fecha_creacion)")
    
    conn.commit()
    conn.close()
    print(f"✅ Base de datos SQLite inicializada: {DB_PATH}")

def generar_id_ficha(url):
    """Genera un ID único para una ficha"""
    timestamp = datetime.now().strftime('%Y%m%d')
    hash_url = hashlib.md5(url.encode()).hexdigest()[:8]
    return f"RND-{timestamp}-{hash_url}"

def es_institucional(ficha):
    """
    Determina si una ficha es de una página institucional.
    """
    url = ficha.get('url', '').lower()
    dominio = ficha.get('dominio', '').lower()
    titulo = ficha.get('titulo', '').lower()
    
    dominios_edu = ['.edu', '.ac.uk', '.edu.es', '.edu.au', '.ac.nz', '.edu.mx']
    if any(dominio.endswith(ext) for ext in dominios_edu):
        return True
    
    keywords_url = ['/admissions/', '/programs/', '/housing/', '/international/', '/students/', '/study-abroad/']
    if any(keyword in url for keyword in keywords_url):
        return True
    
    keywords_titulo = ['university', 'business school', 'college', 'institute', 'admissions', 'study abroad']
    if any(keyword in titulo for keyword in keywords_titulo):
        return True
    
    return False

def es_red_social(ficha):
    """Determina si una ficha es de una red social"""
    dominio = ficha.get('dominio', '').lower()
    redes_sociales = ['reddit.com', 'facebook.com', 'linkedin.com', 'twitter.com', 'x.com', 'instagram.com']
    return any(red in dominio for red in redes_sociales)

def debe_guardar_ficha(ficha):
    """
    Determina si una ficha debe guardarse según las reglas de filtrado.
    - Si es red social → SIEMPRE guardar
    - Si es institucional Y (NO tiene email Y NO tiene formulario) → NO guardar
    - En cualquier otro caso → Guardar
    """
    if es_red_social(ficha):
        return True, "Red social"
    
    if not es_institucional(ficha):
        return True, "No institucional"
    
    tiene_email = ficha.get('email') and ficha.get('email').strip()
    tiene_formulario = ficha.get('tiene_formulario') == True
    
    if not tiene_email and not tiene_formulario:
        return False, "Institucional sin email ni formulario"
    
    return True, "Institucional con contacto"

def verificar_duplicado(url):
    """Verifica si una URL ya existe"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM fichas WHERE url = ? LIMIT 1", (url,))
        result = cursor.fetchone()
        conn.close()
        return result is not None
    except Exception as e:
        print(f"⚠️ Error verificando duplicado: {e}")
        return False

def guardar_fichas(fichas):
    """Guarda fichas en SQLite, ignorando duplicados"""
    if not fichas:
        print("⚠️ No hay fichas para guardar")
        return 0
    
    inicializar_db()
    
    guardadas = 0
    duplicadas = 0
    filtradas = 0
    errores = 0
    
    print(f"💾 Iniciando guardado de {len(fichas)} fichas en SQLite...")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
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
        
        # 3. Insertar en SQLite
        try:
            ficha_id = ficha.get('id') or generar_id_ficha(url)
            
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
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, valores)
            
            print(f"  ✅ Guardada: {ficha_id}")
            guardadas += 1
            
        except sqlite3.IntegrityError:
            print(f"  ⏭️ Duplicado (UNIQUE constraint): {url[:50]}...")
            duplicadas += 1
        except Exception as e:
            print(f"  ❌ Error guardando: {e}")
            errores += 1
    
    conn.commit()
    conn.close()
    
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
        'url': f'https://test-sqlite-{datetime.now().timestamp()}.com',
        'titulo': 'Test SQLite',
        'snippet': 'Probando guardado en SQLite',
        'dominio': 'test.com',
        'prioridad': 'Alta'
    }
    
    resultado = guardar_fichas([ficha_test])
    print(f"\n✅ Test completado: {resultado} ficha(s) guardada(s)")
