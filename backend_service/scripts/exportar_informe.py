import os
import csv
from supabase import create_client, Client
from datetime import datetime

# Credenciales
SUPABASE_URL = os.environ.get('SUPABASE_URL', 'https://xoqgfxqfxkxqxqxqxqxq.supabase.co')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY')

def exportar_csv():
    if not SUPABASE_KEY:
        print("❌ Error: Falta SUPABASE_KEY")
        return

    print(f"🔌 Conectando a Supabase para exportar informe...")
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    try:
        # Obtener TODAS las fichas (sin límite)
        response = supabase.table('fichas')\
            .select('*')\
            .order('fecha_creacion', desc=True)\
            .execute()
            
        fichas = response.data
        
        if not fichas:
            print("⚠️ No hay fichas para exportar.")
            return

        filename = f"informe_fichas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        filepath = f"/home/ubuntu/{filename}"
        
        # Escribir CSV
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            # Usar las claves del primer registro como encabezados
            fieldnames = fichas[0].keys()
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for ficha in fichas:
                writer.writerow(ficha)
                
        print(f"✅ Informe generado exitosamente: {filepath}")
        print(f"📊 Total registros exportados: {len(fichas)}")
        
    except Exception as e:
        print(f"❌ Error exportando CSV: {str(e)}")

if __name__ == "__main__":
    exportar_csv()
