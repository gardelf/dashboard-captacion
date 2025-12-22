import os
from supabase import create_client, Client
import json

# Credenciales
SUPABASE_URL = os.environ.get('SUPABASE_URL', 'https://xoqgfxqfxkxqxqxqxqxq.supabase.co')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY')

if not SUPABASE_KEY:
    print("❌ Error: Falta SUPABASE_KEY")
    exit()

def ver_ultimos_registros():
    print(f"🔌 Conectando a Supabase: {SUPABASE_URL}")
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    try:
        # Consultar últimos 5 registros
        response = supabase.table('fichas')\
            .select('id, titulo, url, plataforma_social, fecha_creacion')\
            .order('fecha_creacion', desc=True)\
            .limit(5)\
            .execute()
            
        registros = response.data
        
        print(f"\n📊 ÚLTIMOS {len(registros)} REGISTROS EN BASE DE DATOS:")
        print("=====================================================")
        
        for i, reg in enumerate(registros):
            print(f"\n🔹 Registro #{i+1}")
            print(f"   ID: {reg['id']}")
            print(f"   Título: {reg['titulo'][:50]}...")
            print(f"   Plataforma: {reg['plataforma_social']}")
            print(f"   URL: {reg['url'][:60]}...")
            print(f"   Fecha: {reg['fecha_creacion']}")
            
        print("\n=====================================================")
        
    except Exception as e:
        print(f"❌ Error consultando Supabase: {str(e)}")

if __name__ == "__main__":
    ver_ultimos_registros()
