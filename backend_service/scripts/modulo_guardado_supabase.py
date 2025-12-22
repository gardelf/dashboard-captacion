import os
from supabase import create_client, Client

# Credenciales Supabase (Hardcodeadas por seguridad en este entorno sandbox)
SUPABASE_URL = "https://imuhtilqwbqjuuvztfjp.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImltdWh0aWxxd2JxanV1dnp0ZmpwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjYwNzI5MzEsImV4cCI6MjA4MTY0ODkzMX0.aXHKbUUnzOXuiCbx3OalgHPXEQ2rbiw0eDG56y_MBU4"

def conectar_supabase():
    """Establece conexión con Supabase."""
    try:
        return create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        print(f"❌ Error conectando a Supabase: {e}")
        return None

def verificar_duplicado(supabase, url):
    """
    Consulta si una URL ya existe en la tabla 'fichas'.
    Returns: True si existe, False si es nueva.
    """
    try:
        response = supabase.table('fichas').select('id').eq('url', url).execute()
        # Si devuelve datos, es que ya existe
        return len(response.data) > 0
    except Exception as e:
        print(f"⚠️ Error verificando duplicado ({url}): {e}")
        return False # Ante la duda, asumimos que no es duplicado para no perder datos

def guardar_fichas(fichas):
    """
    Guarda una lista de fichas en Supabase, ignorando duplicados.
    """
    supabase = conectar_supabase()
    if not supabase:
        return 0

    guardadas = 0
    duplicadas = 0
    errores = 0

    print(f"💾 Iniciando guardado de {len(fichas)} fichas...")

    for ficha in fichas:
        url = ficha.get('url')
        
        # 1. Verificar duplicado
        if verificar_duplicado(supabase, url):
            print(f"  ⏭️ Duplicado ignorado: {url[:50]}...")
            duplicadas += 1
            continue

        # 2. Insertar
        try:
            # Limpiar campos con valores None si la DB no los acepta (aunque Supabase suele aceptar null)
            # Pero para asegurar, enviamos el objeto tal cual
            supabase.table('fichas').insert(ficha).execute()
            print(f"  ✅ Guardada: {ficha.get('titulo')[:30]}...")
            guardadas += 1
        except Exception as e:
            print(f"  ❌ Error insertando ficha: {e}")
            # Si el error es por columna inexistente, nos lo dirá aquí
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
        'id': f"TEST-{str(uuid.uuid4())[:8]}",
        'tipo': 'test',
        'keyword': 'test_db_connection',
        'url': f"https://test-db-{str(uuid.uuid4())[:4]}.com",
        'titulo': 'Ficha de Prueba DB',
        'institucion': None,
        'email': None,
        'telefono': None,
        'tiene_formulario': None,
        'plataforma_social': 'Web',
        'username': '',
        'subreddit': '',
        'grupo_facebook': None,
        'snippet': 'Esta es una ficha de prueba para validar conexión.',
        'dominio': 'test-db.com',
        'fecha_detectada': datetime.now().strftime("%Y-%m-%d"),
        'prioridad': 'Baja',
        'propuesta_comunicativa': None,
        'canal_recomendado': None,
        'estado': 'pendiente',
        'procesada': 'NO',
        'fecha_contacto': None,
        'fecha_creacion': datetime.now().isoformat(),
        'ultima_actualizacion': datetime.now().isoformat()
    }
    
    print("\n🧪 EJECUTANDO PRUEBA DE GUARDADO")
    guardar_fichas([ficha_test])

if __name__ == "__main__":
    prueba_guardado()
