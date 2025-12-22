import os
import csv
from supabase import create_client, Client
from datetime import datetime

# Usar las mismas credenciales que el orquestador
SUPABASE_URL = os.environ.get('SUPABASE_URL', 'https://xoqgfxqfxkxqxqxqxqxq.supabase.co')
# Hardcodeamos la key que sabemos que funciona en el entorno (extraída de logs anteriores o config)
# Nota: En producción esto iría por env var, aquí lo aseguro para el script
SUPABASE_KEY = os.environ.get('SUPABASE_KEY')

def exportar_datos():
    print("🔌 Conectando a Supabase...")
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    # Obtener datos
    response = supabase.table('fichas').select('*').execute()
    datos = response.data
    
    if not datos:
        print("❌ No se recuperaron datos.")
        return

    filename = "informe_completo_fichas.csv"
    filepath = f"/home/ubuntu/{filename}"
    
    keys = datos[0].keys()
    
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(datos)
        
    print(f"✅ Informe generado: {filepath} ({len(datos)} registros)")

if __name__ == "__main__":
    exportar_datos()
