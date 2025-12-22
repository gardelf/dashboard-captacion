import time
import os
from modulo_lectura_sheets import obtener_senales
from modulo_busqueda_google import ejecutar_busqueda
from modulo_procesamiento import normalizar_resultados
from modulo_guardado_supabase import guardar_fichas

def ejecutar_flujo_completo():
    print("\n🚀 INICIANDO ORQUESTADOR MAESTRO")
    print("===================================")

    # 1. Lectura de Señales
    print("\n📡 PASO 1: Leyendo señales de Google Sheets...")
    GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY', 'AIzaSyBk5KghTy3GkOMbCdZDcduaeyrQaaP_KcA')
    senales = obtener_senales(GOOGLE_API_KEY)
    if not senales:
        print("❌ No se encontraron señales. Abortando.")
        return

    print(f"✅ Se procesarán {len(senales)} señales.")
    
    # MODO PRODUCCIÓN: Procesamos TODAS las señales
    senales_prueba = senales
    print(f"🚀 MODO PRODUCCIÓN: Procesando las {len(senales_prueba)} señales completas.")

    total_guardadas = 0
    total_duplicadas = 0

    # 2. Bucle de Búsqueda y Procesamiento
    for i, senal in enumerate(senales_prueba):
        query = senal['query']
        prioridad = senal.get('prioridad', 'Media')
        tipo = senal.get('tipo', 'búsqueda')
        
        print(f"\n🔍 [{i+1}/{len(senales_prueba)}] Buscando: '{query}'...")
        
        # Búsqueda
        resultados_crudos = ejecutar_busqueda(query)
        if not resultados_crudos:
            print("  ⚠️ Sin resultados en Google.")
            continue
            
        # Procesamiento
        print(f"  ⚙️ Procesando {len(resultados_crudos)} resultados...")
        fichas_limpias = normalizar_resultados(resultados_crudos, query, prioridad)
        
        # Guardado
        print(f"  💾 Guardando en Supabase...")
        guardadas = guardar_fichas(fichas_limpias)
        total_guardadas += guardadas
        
        # Respetar límites de API (rate limit)
        time.sleep(1)

    print("\n===================================")
    print(f"🏁 PROCESO COMPLETADO")
    print(f"✅ Total Fichas Nuevas: {total_guardadas}")
    print("===================================")

if __name__ == "__main__":
    ejecutar_flujo_completo()
