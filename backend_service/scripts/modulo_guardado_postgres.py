"""
Módulo de Guardado - PostgreSQL (Render)
Guarda fichas procesadas en la base de datos PostgreSQL de Render.
"""

import os
import psycopg2
from datetime import datetime
import hashlib

# URL de PostgreSQL de Render
RENDER_DATABASE_URL = "postgresql://dashboard_captacion_db_user:zCQusHpUln7PINbsqKY3uedDk1tOjcBi@dpg-d54jlsdactks73agf7b0-a.frankfurt-postgres.render.com/dashboard_captacion_db"

def generar_id_ficha(url):
    """Genera un ID único para una ficha"""
    timestamp = datetime.now().strftime('%Y%m%d')
    hash_url = hashlib.md5(url.encode()).hexdigest()[:8]
    return f"RND-{timestamp}-{hash_url}"

def verificar_duplicado(url):
    """
    Consulta si una URL ya existe en la tabla 'fichas'.
    Returns: True si existe, False si es nueva.
    """
    try:
        conn = psycopg2.connect(RENDER_DATABASE_URL)
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

    for ficha in fichas:
        url = ficha.get('url')
        
        # 1. Verificar duplicado
        if verificar_duplicado(url):
            print(f"  ⏭️ Duplicado ignorado: {url[:50]}...")
            duplicadas += 1
            continue

        # 2. Insertar en PostgreSQL
        try:
            conn = psycopg2.connect(RENDER_DATABASE_URL)
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
