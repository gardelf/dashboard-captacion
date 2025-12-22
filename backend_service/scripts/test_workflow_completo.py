#!/usr/bin/env python3
"""
Test de Workflow Completo End-to-End
1. Búsqueda en Google
2. Guardado en TiDB
3. Enriquecimiento con ChatGPT
4. Verificación de resultados
"""

import sys
import os
import subprocess
import json
from datetime import datetime
import hashlib

sys.path.insert(0, '/home/ubuntu/dashboard-captacion/backend_service/scripts')

from modulo_busqueda_google import ejecutar_busqueda
from modulo_guardado import guardar_fichas

def generar_id_ficha(url):
    """Genera un ID único para una ficha"""
    timestamp = datetime.now().strftime('%Y%m%d')
    hash_url = hashlib.md5(url.encode()).hexdigest()[:8]
    return f"WF-{timestamp}-{hash_url}"

def extraer_dominio(url):
    """Extrae el dominio de una URL"""
    from urllib.parse import urlparse
    parsed = urlparse(url)
    return parsed.netloc

print("=" * 70)
print("🚀 TEST DE WORKFLOW COMPLETO END-TO-END")
print("=" * 70)
print()

# PASO 1: Búsqueda en Google
print("📍 PASO 1: BÚSQUEDA EN GOOGLE")
print("-" * 70)
keyword = "student accommodation Madrid 2026"
num_resultados = 3

print(f"Palabra clave: {keyword}")
print(f"Número de resultados: {num_resultados}")
print()

resultados_google = ejecutar_busqueda(keyword, num_resultados=num_resultados)

if not resultados_google:
    print("❌ No se encontraron resultados en Google")
    sys.exit(1)

print(f"✅ Encontrados {len(resultados_google)} resultados\n")
for i, r in enumerate(resultados_google, 1):
    print(f"  [{i}] {r['titulo'][:55]}...")
    print(f"      {r['url'][:60]}...")

# PASO 2: Preparar fichas para guardar
print()
print("📍 PASO 2: PREPARACIÓN DE FICHAS")
print("-" * 70)

fichas_preparadas = []
for resultado in resultados_google:
    ficha = {
        'id': generar_id_ficha(resultado['url']),
        'tipo': 'busqueda_google',
        'keyword': keyword,
        'url': resultado['url'],
        'titulo': resultado['titulo'],
        'snippet': resultado['snippet'],
        'dominio': extraer_dominio(resultado['url']),
        'fecha_detectada': datetime.now().isoformat(),
        'prioridad': 'Media',
        'procesada': 'NO'
    }
    fichas_preparadas.append(ficha)

print(f"✅ Preparadas {len(fichas_preparadas)} fichas para guardar\n")

# PASO 3: Guardar en TiDB
print("📍 PASO 3: GUARDADO EN TIDB")
print("-" * 70)

fichas_guardadas = guardar_fichas(fichas_preparadas)

print(f"\n✅ Guardadas {fichas_guardadas} fichas nuevas en TiDB\n")

# PASO 4: Enriquecimiento con ChatGPT
print("📍 PASO 4: ENRIQUECIMIENTO CON CHATGPT")
print("-" * 70)

# Ejecutar módulo de enriquecimiento
result = subprocess.run(
    ['python3', 'modulo_enriquecimiento_chatgpt.py', str(fichas_guardadas)],
    capture_output=True,
    text=True,
    cwd='/home/ubuntu/dashboard-captacion/backend_service/scripts'
)

print(result.stdout)

if result.returncode != 0:
    print(f"❌ Error en enriquecimiento: {result.stderr}")
else:
    print("✅ Enriquecimiento completado\n")

# PASO 5: Verificación final
print("📍 PASO 5: VERIFICACIÓN DE RESULTADOS")
print("-" * 70)

# Consultar fichas procesadas
query_script = """
const mysql = require('mysql2/promise');
(async () => {
    const conn = await mysql.createConnection(process.env.DATABASE_URL);
    const [rows] = await conn.query(
        'SELECT id, titulo, institucion, canal_recomendado, procesada FROM fichas WHERE procesada = "SI" ORDER BY fecha_creacion DESC LIMIT 3'
    );
    console.log(JSON.stringify(rows, null, 2));
    await conn.end();
})();
"""

result = subprocess.run(
    ['node', '-e', query_script],
    capture_output=True,
    text=True,
    cwd='/home/ubuntu/dashboard-captacion',
    env=os.environ.copy()
)

if result.returncode == 0:
    fichas_procesadas = json.loads(result.stdout)
    print(f"✅ Fichas procesadas en la base de datos: {len(fichas_procesadas)}\n")
    for ficha in fichas_procesadas:
        print(f"  • {ficha['id']}")
        print(f"    Título: {ficha['titulo'][:50]}...")
        print(f"    Institución: {ficha['institucion'] or 'N/A'}")
        print(f"    Canal: {ficha['canal_recomendado'] or 'N/A'}")
        print()

print("=" * 70)
print("✅ WORKFLOW COMPLETO FINALIZADO")
print("=" * 70)

