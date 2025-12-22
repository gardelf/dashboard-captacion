"""
Módulo de Guardado - PostgreSQL Local
Guarda fichas procesadas en la base de datos PostgreSQL local usando mysql2.
"""

import os
import sys
import subprocess
import json
from datetime import datetime

# Obtener DATABASE_URL del entorno
DATABASE_URL = os.getenv('DATABASE_URL')

if not DATABASE_URL:
    print("❌ ERROR: DATABASE_URL no está configurada en el entorno")
    sys.exit(1)

def verificar_duplicado(url):
    """
    Consulta si una URL ya existe en la tabla 'fichas'.
    Returns: True si existe, False si es nueva.
    """
    try:
        # Usamos node para ejecutar una consulta SQL directa
        query = f"SELECT id FROM fichas WHERE url = {json.dumps(url)} LIMIT 1"
        result = subprocess.run(
            ['node', '-e', f"""
const mysql = require('mysql2/promise');
(async () => {{
    const conn = await mysql.createConnection(process.env.DATABASE_URL);
    const [rows] = await conn.execute({json.dumps(query)});
    console.log(JSON.stringify(rows));
    await conn.end();
}})();
            """],
            capture_output=True,
            text=True,
            cwd='/home/ubuntu/dashboard-captacion',
            env=os.environ.copy()
        )
        
        if result.returncode != 0:
            print(f"⚠️ Error verificando duplicado: {result.stderr}")
            return False
        
        rows = json.loads(result.stdout.strip())
        return len(rows) > 0
        
    except Exception as e:
        print(f"⚠️ Error verificando duplicado ({url}): {e}")
        return False

def guardar_fichas(fichas):
    """
    Guarda una lista de fichas en PostgreSQL local, ignorando duplicados.
    """
    if not fichas:
        print("⚠️ No hay fichas para guardar")
        return 0

    guardadas = 0
    duplicadas = 0
    errores = 0

    print(f"💾 Iniciando guardado de {len(fichas)} fichas en PostgreSQL local...")

    for ficha in fichas:
        url = ficha.get('url')
        
        # 1. Verificar duplicado
        if verificar_duplicado(url):
            print(f"  ⏭️ Duplicado ignorado: {url[:50]}...")
            duplicadas += 1
            continue

        # 2. Insertar usando node script
        try:
            # Preparar valores para inserción
            valores = {
                'id': ficha.get('id'),
                'tipo': ficha.get('tipo'),
                'keyword': ficha.get('keyword'),
                'url': ficha.get('url'),
                'titulo': ficha.get('titulo'),
                'snippet': ficha.get('snippet'),
                'dominio': ficha.get('dominio'),
                'institucion': ficha.get('institucion'),
                'email': ficha.get('email'),
                'telefono': ficha.get('telefono'),
                'tiene_formulario': ficha.get('tiene_formulario'),
                'plataforma_social': ficha.get('plataforma_social'),
                'username': ficha.get('username'),
                'subreddit': ficha.get('subreddit'),
                'grupo_facebook': ficha.get('grupo_facebook'),
                'fecha_detectada': ficha.get('fecha_detectada'),
                'prioridad': ficha.get('prioridad'),
                'propuesta_comunicativa': ficha.get('propuesta_comunicativa'),
                'canal_recomendado': ficha.get('canal_recomendado'),
                'estado': ficha.get('estado', 'pendiente'),
                'procesada': ficha.get('procesada', 'NO'),
                'fecha_contacto': ficha.get('fecha_contacto'),
            }
            
            # Crear script Node.js para inserción
            node_script = f"""
const mysql = require('mysql2/promise');
(async () => {{
    const conn = await mysql.createConnection(process.env.DATABASE_URL);
    const valores = {json.dumps(valores)};
    
    const query = `INSERT INTO fichas (
        id, tipo, keyword, url, titulo, snippet, dominio, institucion, email, telefono,
        tiene_formulario, plataforma_social, username, subreddit, grupo_facebook,
        fecha_detectada, prioridad, propuesta_comunicativa, canal_recomendado,
        estado, procesada, fecha_contacto
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`;
    
    const params = [
        valores.id, valores.tipo, valores.keyword, valores.url, valores.titulo,
        valores.snippet, valores.dominio, valores.institucion, valores.email,
        valores.telefono, valores.tiene_formulario, valores.plataforma_social,
        valores.username, valores.subreddit, valores.grupo_facebook,
        valores.fecha_detectada, valores.prioridad, valores.propuesta_comunicativa,
        valores.canal_recomendado, valores.estado, valores.procesada, valores.fecha_contacto
    ];
    
    await conn.execute(query, params);
    await conn.end();
    console.log('OK');
}})();
            """
            
            result = subprocess.run(
                ['node', '-e', node_script],
                capture_output=True,
                text=True,
                cwd='/home/ubuntu/dashboard-captacion',
                env=os.environ.copy()
            )
            
            if result.returncode != 0:
                print(f"  ❌ Error insertando ficha: {result.stderr}")
                errores += 1
            else:
                titulo = ficha.get('titulo', '')[:30] if ficha.get('titulo') else 'Sin título'
                print(f"  ✅ Guardada: {titulo}...")
                guardadas += 1
                
        except Exception as e:
            print(f"  ❌ Error insertando ficha: {e}")
            errores += 1

    print(f"\n📊 RESUMEN GUARDADO")
    print(f"  ✅ Nuevas: {guardadas}")
    print(f"  ⏭️ Duplicadas: {duplicadas}")
    print(f"  ❌ Errores: {errores}")
    
    return guardadas

def prueba_guardado():
    """Prueba unitaria con una ficha ficticia."""
    import uuid
    from datetime import datetime
    
    # Ficha de prueba
    ficha_test = {
        'id': f"TEST-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8]}",
        'tipo': 'test',
        'keyword': 'test_db_connection',
        'url': f"https://test-db-{str(uuid.uuid4())[:8]}.com",
        'titulo': 'Ficha de Prueba PostgreSQL Local',
        'institucion': None,
        'email': None,
        'telefono': None,
        'tiene_formulario': None,
        'plataforma_social': 'Web',
        'username': '',
        'subreddit': '',
        'grupo_facebook': None,
        'snippet': 'Esta es una ficha de prueba para validar conexión a PostgreSQL local.',
        'dominio': 'test-db.com',
        'fecha_detectada': datetime.now().strftime("%Y-%m-%d"),
        'prioridad': 'Baja',
        'propuesta_comunicativa': None,
        'canal_recomendado': None,
        'estado': 'pendiente',
        'procesada': 'NO',
        'fecha_contacto': None,
    }
    
    print("\n🧪 EJECUTANDO PRUEBA DE GUARDADO EN POSTGRESQL LOCAL")
    guardar_fichas([ficha_test])

if __name__ == "__main__":
    prueba_guardado()
