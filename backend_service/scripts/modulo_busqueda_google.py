import os
import requests
import time
import json
from datetime import datetime
from modulo_lectura_sheets import leer_claves_desde_sheets

# Cargar credenciales desde Google Sheets
_config = None

def _get_config():
    """Obtiene configuración (usa cache)"""
    global _config
    if _config is None:
        _config = leer_claves_desde_sheets()
    return _config

def ejecutar_busqueda(query, num_resultados=None):
    """
    Ejecuta una búsqueda en Google Custom Search API.
    
    Args:
        query (str): Término de búsqueda.
        num_resultados (int): Número de resultados a devolver. Si es None, usa NUM_RESULTADOS_GOOGLE de config.
        
    Returns:
        list: Lista de diccionarios con resultados.
    """
    config = _get_config()
    
    GOOGLE_API_KEY = config['GOOGLE_API_KEY']
    GOOGLE_CSE_ID = config['GOOGLE_CSE_ID']
    
    if num_resultados is None:
        num_resultados = config['NUM_RESULTADOS_GOOGLE']
    
    if not GOOGLE_API_KEY or not GOOGLE_CSE_ID:
        print("❌ Error: Faltan credenciales de Google Search")
        return []

    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        'key': GOOGLE_API_KEY,
        'cx': GOOGLE_CSE_ID,
        'q': query,
        'num': min(num_resultados, 10) # API limita a 10
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            items = data.get('items', [])
            
            resultados_limpios = []
            for item in items:
                resultados_limpios.append({
                    'titulo': item.get('title'),
                    'url': item.get('link'),
                    'snippet': item.get('snippet'),
                    'fecha_descubrimiento': datetime.now().isoformat()
                })
            return resultados_limpios
            
        elif response.status_code == 429:
            print("⚠️ Cuota excedida (429). Esperando...")
            return []
        else:
            print(f"⚠️ Error API Google ({response.status_code}): {response.text}")
            return []
            
    except Exception as e:
        print(f"❌ Excepción en búsqueda: {str(e)}")
        return []

def prueba_integracion():
    """Prueba de integración: Lectura Sheets -> Búsqueda Google"""
    from modulo_lectura_sheets import obtener_senales
    
    print("🚀 INICIANDO PRUEBA DE INTEGRACIÓN (PASO 2)")
    print("===========================================")
    
    config = _get_config()
    print(f"✅ Configuración cargada desde Google Sheets")
    print(f"   - GOOGLE_CSE_ID: {config['GOOGLE_CSE_ID']}")
    print(f"   - NUM_RESULTADOS_GOOGLE: {config['NUM_RESULTADOS_GOOGLE']}")
    
    # 1. Leer señales
    senales = obtener_senales(config['GOOGLE_API_KEY'])
    if not senales:
        print("❌ No se obtuvieron señales. Abortando.")
        return
        
    print(f"✅ Se obtuvieron {len(senales)} señales.")
    
    # 2. Ejecutar búsqueda para las primeras 3
    total_encontrados = 0
    
    print("\n🔎 Probando búsqueda con las primeras 3 señales:")
    for i, senal in enumerate(senales[:3]):
        query = senal['query']
        print(f"\n  [{i+1}/3] Buscando: '{query}'...")
        
        resultados = ejecutar_busqueda(query)
        count = len(resultados)
        total_encontrados += count
        
        print(f"    ✅ Encontrados: {count} resultados")
        if resultados:
            print(f"    Ejemplo: {resultados[0]['titulo']} ({resultados[0]['url'][:50]}...)")
            
        time.sleep(1) # Respetar rate limits
        
    print("\n📊 RESUMEN PRUEBA")
    print("=================")
    print(f"Total Búsquedas: 3")
    print(f"Total Resultados: {total_encontrados}")
    
    if total_encontrados > 0:
        print("\n✅ PASO 2 COMPLETADO CON ÉXITO: La búsqueda funciona.")
    else:
        print("\n⚠️ PASO 2 COMPLETADO PERO SIN RESULTADOS (Revisar queries o CSE).")

if __name__ == "__main__":
    prueba_integracion()
