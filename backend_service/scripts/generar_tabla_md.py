import os
from supabase import create_client, Client

# Usar credenciales del entorno (las mismas que usa el orquestador)
SUPABASE_URL = os.environ.get('SUPABASE_URL', 'https://xoqgfxqfxkxqxqxqxqxq.supabase.co')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY')

def generar_tabla():
    if not SUPABASE_KEY:
        print("❌ Error: Falta SUPABASE_KEY")
        return

    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Obtener últimos 15 registros
        response = supabase.table('fichas')\
            .select('titulo, plataforma_social, fecha_creacion, url')\
            .order('fecha_creacion', desc=True)\
            .limit(15)\
            .execute()
            
        registros = response.data
        
        if not registros:
            print("⚠️ No se encontraron registros.")
            return

        # Generar tabla Markdown
        print("\n### 📊 Últimos 15 Registros Captados\n")
        print("| Plataforma | Título | Fecha | Enlace |")
        print("| :--- | :--- | :--- | :--- |")
        
        for reg in registros:
            titulo = (reg.get('titulo') or "Sin título").replace("|", "-")[:50]
            if len(reg.get('titulo') or "") > 50: titulo += "..."
            
            plataforma = reg.get('plataforma_social') or "N/A"
            fecha = (reg.get('fecha_creacion') or "")[:10]
            url = reg.get('url') or "#"
            
            print(f"| **{plataforma}** | {titulo} | {fecha} | [Ver]({url}) |")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    generar_tabla()
