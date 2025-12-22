import os
from supabase import create_client, Client

# Credenciales hardcodeadas (las mismas que en el script principal)
SUPABASE_URL = "https://imuhtilqwbqjuuvztfjp.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImltdWh0aWxxd2JxanV1dnp0ZmpwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjYwNzI5MzEsImV4cCI6MjA4MTY0ODkzMX0.aXHKbUUnzOXuiCbx3OalgHPXEQ2rbiw0eDG56y_MBU4"

def test_connection():
    print("🔌 PROBANDO CONEXIÓN A SUPABASE")
    print("==============================")
    print(f"URL: {SUPABASE_URL}")
    print(f"Key: {SUPABASE_KEY[:10]}...")
    
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Intentar una lectura simple (contar fichas)
        print("\n⏳ Intentando leer tabla 'fichas'...")
        response = supabase.table('fichas').select('count', count='exact').limit(1).execute()
        
        print(f"✅ ¡CONEXIÓN EXITOSA!")
        print(f"📊 Total de fichas en base de datos: {response.count}")
        
    except Exception as e:
        print(f"\n❌ ERROR DE CONEXIÓN:")
        print(f"{str(e)}")
        print("\nDiagnóstico probable:")
        if "getaddrinfo failed" in str(e) or "NewConnectionError" in str(e):
            print("👉 FALLO DNS/RED: El sandbox no puede resolver la dirección de Supabase.")
            print("   (Esto es normal en este entorno, pero funcionará en Render)")
        elif "401" in str(e) or "JWT" in str(e):
            print("👉 FALLO DE CREDENCIALES: La clave API es incorrecta o ha expirado.")

if __name__ == "__main__":
    test_connection()
