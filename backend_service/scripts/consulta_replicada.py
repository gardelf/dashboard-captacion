import os
from supabase import create_client, Client
import json

# Usamos EXACTAMENTE la misma configuración que modulo_guardado_supabase.py
# que sabemos que funciona porque acabamos de ver sus logs de éxito.

SUPABASE_URL = os.environ.get('SUPABASE_URL', 'https://xoqgfxqfxkxqxqxqxqxq.supabase.co')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY')

def consultar_datos():
    if not SUPABASE_KEY:
        print("❌ Error: Falta SUPABASE_KEY")
        return

    print(f"🔌 Conectando a Supabase (URL: {SUPABASE_URL})...")
    
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Consulta simple: últimos 10 registros
        response = supabase.table('fichas')\
            .select('id, titulo, url, plataforma_social, fecha_creacion')\
            .order('fecha_creacion', desc=True)\
            .limit(10)\
            .execute()
            
        registros = response.data
        
        if not registros:
            print("⚠️ No se encontraron registros.")
            return
            
        # Formato tabla simple
        print("\n📊 ÚLTIMOS 10 REGISTROS EN BASE DE DATOS:")
        print("-" * 100)
        print(f"{'PLATAFORMA':<15} | {'TÍTULO (Cortado)':<50} | {'FECHA'}")
        print("-" * 100)
        
        for reg in registros:
            titulo = (reg.get('titulo') or "Sin título")[:47] + "..."
            plataforma = reg.get('plataforma_social') or "N/A"
            fecha = reg.get('fecha_creacion') or "N/A"
            
            print(f"{plataforma:<15} | {titulo:<50} | {fecha}")
            
        print("-" * 100)
        print(f"✅ Total consultados: {len(registros)}")

    except Exception as e:
        print(f"❌ Error en consulta: {str(e)}")

if __name__ == "__main__":
    consultar_datos()
