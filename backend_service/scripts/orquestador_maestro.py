import time
import os
from modulo_lectura_sheets import obtener_senales, leer_claves_desde_sheets
from modulo_busqueda_google import ejecutar_busqueda
from modulo_procesamiento import normalizar_resultados
from modulo_guardado_postgres import guardar_fichas
from modulo_enriquecimiento_postgres import enriquecer_fichas

def ejecutar_flujo_completo():
    print("\n🚀 INICIANDO ORQUESTADOR MAESTRO")
    print("===================================")

    # 0. Cargar configuración desde Google Sheets
    print("\n⚙️ PASO 0: Cargando configuración desde Google Sheets (pestaña Claves)...")
    config = leer_claves_desde_sheets()
    
    GOOGLE_API_KEY = config['GOOGLE_API_KEY']
    LIMITE_KEYWORDS = config['LIMITE_KEYWORDS']
    LIMITE_ENRIQUECIMIENTO = config['LIMITE_ENRIQUECIMIENTO']
    
    print(f"✅ Configuración cargada:")
    print(f"   - LIMITE_KEYWORDS: {LIMITE_KEYWORDS}")
    print(f"   - LIMITE_ENRIQUECIMIENTO: {LIMITE_ENRIQUECIMIENTO}")
    print(f"   - GOOGLE_CSE_ID: {config['GOOGLE_CSE_ID']}")

    # 1. Lectura de Señales
    print("\n📡 PASO 1: Leyendo señales de Google Sheets (pestaña Signals)...")
    senales = obtener_senales(GOOGLE_API_KEY)
    if not senales:
        print("❌ No se encontraron señales. Abortando.")
        return

    print(f"✅ Encontradas {len(senales)} señales activas.")
    
    # Aplicar límite de keywords desde configuración
    senales_a_procesar = senales[:LIMITE_KEYWORDS]
    print(f"🎯 Procesando {len(senales_a_procesar)} señal(es) según LIMITE_KEYWORDS.")

    total_guardadas = 0
    total_duplicadas = 0

    # 2. Bucle de Búsqueda y Procesamiento
    for i, senal in enumerate(senales_a_procesar):
        query = senal['query']
        prioridad = senal.get('prioridad', 'Media')
        tipo = senal.get('tipo', 'búsqueda')
        
        print(f"\n🔍 [{i+1}/{len(senales_a_procesar)}] Buscando: '{query}'...")
        
        # Búsqueda
        resultados_crudos = ejecutar_busqueda(query)
        if not resultados_crudos:
            print("  ⚠️ Sin resultados en Google.")
            continue
            
        # Procesamiento
        print(f"  ⚙️ Procesando {len(resultados_crudos)} resultados...")
        fichas_limpias = normalizar_resultados(resultados_crudos, query, prioridad)
        
        # Guardado
        print(f"  💾 Guardando en PostgreSQL (Render)...")
        guardadas = guardar_fichas(fichas_limpias)
        total_guardadas += guardadas
        
        # Respetar límites de API (rate limit)
        time.sleep(1)

    print("\n===================================")
    print(f"🏁 BÚSQUEDA COMPLETADA")
    print(f"✅ Total Fichas Nuevas: {total_guardadas}")
    print("===================================")
    
    # 3. Enriquecimiento automático
    if total_guardadas > 0:
        print("\n🤖 PASO 3: Enriqueciendo fichas con ChatGPT...")
        print("===================================")
        fichas_enriquecidas = enriquecer_fichas(limite=LIMITE_ENRIQUECIMIENTO)
        print("\n===================================")
        print(f"🏁 PROCESO COMPLETO FINALIZADO")
        print(f"✅ Fichas guardadas: {total_guardadas}")
        print(f"✅ Fichas enriquecidas: {fichas_enriquecidas}")
        print("===================================")
    else:
        print("\n⚠️ No hay fichas nuevas para enriquecer.")

if __name__ == "__main__":
    ejecutar_flujo_completo()
