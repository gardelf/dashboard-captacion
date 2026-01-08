"""
Módulo de exportación a JSON
Exporta datos de SQLite a JSON estático para el dashboard React
"""
import sqlite3
import json
import os
from datetime import datetime

DB_PATH = os.getenv('DB_PATH', 'fichas.db')
JSON_OUTPUT = os.getenv('JSON_OUTPUT', 'fichas.json')

def exportar_a_json():
    """
    Exporta todas las fichas a JSON estático.
    Incluye estadísticas y metadatos.
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Obtener todas las fichas
        cursor.execute("""
            SELECT * FROM fichas 
            ORDER BY fecha_creacion DESC
        """)
        fichas_raw = cursor.fetchall()
        fichas = [dict(row) for row in fichas_raw]
        
        # Estadísticas
        cursor.execute("SELECT COUNT(*) as total FROM fichas")
        total = cursor.fetchone()['total']
        
        cursor.execute("SELECT COUNT(*) as pendientes FROM fichas WHERE estado = 'pendiente'")
        pendientes = cursor.fetchone()['pendientes']
        
        cursor.execute("SELECT COUNT(*) as contactados FROM fichas WHERE estado = 'contactado'")
        contactados = cursor.fetchone()['contactados']
        
        cursor.execute("SELECT COUNT(*) as descartados FROM fichas WHERE estado = 'descartado'")
        descartados = cursor.fetchone()['descartados']
        
        cursor.execute("SELECT COUNT(*) as procesadas FROM fichas WHERE procesada = 'SÍ'")
        procesadas = cursor.fetchone()['procesadas']
        
        # Prioridades
        cursor.execute("SELECT COUNT(*) as alta FROM fichas WHERE prioridad = 'ALTA'")
        alta = cursor.fetchone()['alta']
        
        cursor.execute("SELECT COUNT(*) as media FROM fichas WHERE prioridad = 'MEDIA'")
        media = cursor.fetchone()['media']
        
        cursor.execute("SELECT COUNT(*) as baja FROM fichas WHERE prioridad = 'BAJA'")
        baja = cursor.fetchone()['baja']
        
        conn.close()
        
        # Crear estructura JSON
        data = {
            'timestamp': datetime.now().isoformat(),
            'version': '1.0',
            'estadisticas': {
                'total': total,
                'pendientes': pendientes,
                'contactados': contactados,
                'descartados': descartados,
                'procesadas': procesadas,
                'prioridades': {
                    'alta': alta,
                    'media': media,
                    'baja': baja
                }
            },
            'fichas': fichas
        }
        
        # Guardar a JSON
        with open(JSON_OUTPUT, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Exportadas {len(fichas)} fichas a {JSON_OUTPUT}")
        print(f"   - Total: {total}")
        print(f"   - Pendientes: {pendientes}")
        print(f"   - Contactados: {contactados}")
        print(f"   - Descartados: {descartados}")
        print(f"   - Procesadas: {procesadas}")
        
        return JSON_OUTPUT
        
    except Exception as e:
        print(f"❌ Error exportando a JSON: {e}")
        return None

def exportar_a_csv():
    """
    Exporta fichas a CSV para análisis.
    """
    import csv
    
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM fichas ORDER BY fecha_creacion DESC")
        fichas = cursor.fetchall()
        conn.close()
        
        if not fichas:
            print("⚠️ No hay fichas para exportar a CSV")
            return None
        
        csv_path = JSON_OUTPUT.replace('.json', '.csv')
        
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fichas[0].keys())
            writer.writeheader()
            for row in fichas:
                writer.writerow(dict(row))
        
        print(f"✅ Exportadas {len(fichas)} fichas a {csv_path}")
        return csv_path
        
    except Exception as e:
        print(f"❌ Error exportando a CSV: {e}")
        return None

if __name__ == "__main__":
    # Test
    json_file = exportar_a_json()
    csv_file = exportar_a_csv()
    
    if json_file:
        print(f"\n✅ Archivos generados:")
        print(f"   - {json_file}")
        if csv_file:
            print(f"   - {csv_file}")
