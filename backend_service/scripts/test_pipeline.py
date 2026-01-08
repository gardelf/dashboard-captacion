import os
os.environ['LIMITE_KEYWORDS'] = '3'
os.environ['LIMITE_ENRIQUECIMIENTO'] = '1'

from modulo_lectura_sheets import leer_claves_desde_sheets
from modulo_guardado_sqlite import inicializar_db
from modulo_exportacion_json import exportar_a_json
import sqlite3

print("\n✅ TEST 1: Inicializar BD SQLite")
inicializar_db()

print("\n✅ TEST 2: Verificar tabla fichas")
conn = sqlite3.connect('fichas.db')
cursor = conn.cursor()
cursor.execute("SELECT COUNT(*) FROM fichas")
count = cursor.fetchone()[0]
print(f"   Fichas en BD: {count}")
conn.close()

print("\n✅ TEST 3: Exportar a JSON")
json_file = exportar_a_json()

print("\n✅ TEST 4: Verificar JSON")
import json
with open(json_file, 'r') as f:
    data = json.load(f)
    print(f"   Total fichas en JSON: {len(data['fichas'])}")
    print(f"   Estadísticas: {data['estadisticas']}")

print("\n✅ TODOS LOS TESTS PASARON")
