import os
import sys
import json
import requests
from datetime import datetime

# Configuración
CONFIG = {
    'GOOGLE_API_KEY': os.environ.get('GOOGLE_API_KEY'),
    'GOOGLE_CSE_ID': os.environ.get('GOOGLE_CSE_ID'),
    'SHEET_ID': '1-6e0U1SATcgs2V8u2fOoDoKIrLjzwJi8GxJtUwy9t_U',
    'SHEET_RANGE': 'Signals!A2:E'
}

def conectar_google_sheets():
    """Conecta a Google Sheets y devuelve los datos crudos"""
    url = f"https://sheets.googleapis.com/v4/spreadsheets/{CONFIG['SHEET_ID']}/values/{CONFIG['SHEET_RANGE']}?key={CONFIG['GOOGLE_API_KEY']}"
    response = requests.get(url)
    if response.status_code != 200:
        print(f"❌ Error conectando a Sheets: {response.text}")
        return []
    data = response.json()
    return data.get('values', [])

def procesar_filas(rows):
    """Procesa las filas de Google Sheets"""
    senales = []
    for row in rows:
        if len(row) >= 3:  # Asegurar columnas mínimas
            institucion = row[0]
            busqueda = row[1]
            prioridad = row[2] if len(row) > 2 else "Media"
            
            if busqueda and institucion:
                senales.append({
                    'institucion': institucion,
                    'busqueda': busqueda,
                    'prioridad': prioridad
                })
    return senales

def ejecutar_busqueda(senales):
    """Ejecuta búsquedas reales en Google"""
    total_encontrados = 0
    resultados = []
    
    print(f"🔎 Iniciando búsqueda para {len(senales)} señales...")
    
    # Limitamos a 5 señales para la prueba rápida
    for i, senal in enumerate(senales[:5]):
        print(f"  [{i+1}/{len(senales[:5])}] Buscando: {senal['busqueda']}...")
        try:
            url = f"https://www.googleapis.com/customsearch/v1?key={CONFIG['GOOGLE_API_KEY']}&cx={CONFIG['GOOGLE_CSE_ID']}&q={senal['busqueda']}"
            response = requests.get(url)
            data = response.json()
            
            items = data.get('items', [])
            count = len(items)
            total_encontrados += count
            
            print(f"    ✅ Encontrados: {count} resultados")
            
            for item in items:
                resultados.append({
                    'titulo': item.get('title'),
                    'url': item.get('link'),
                    'origen': senal['institucion']
                })
                
        except Exception as e:
            print(f"    ❌ Error: {e}")
            
    return total_encontrados, resultados

def main():
    print("🚀 INICIANDO PRUEBA DE BÚSQUEDA REAL (SIN FILTROS)")
    print("==================================================")
    
    # 1. Leer Sheets
    rows = conectar_google_sheets()
    if not rows:
        print("❌ No se pudieron leer datos de Sheets")
        return
        
    senales = procesar_filas(rows)
    print(f"✅ Leídas {len(senales)} señales de la hoja 'Signals'")
    
    # 2. Ejecutar Búsqueda
    total, resultados = ejecutar_busqueda(senales)
    
    print("\n📊 RESULTADOS DE LA PRUEBA")
    print("==========================")
    print(f"Total Búsquedas Ejecutadas: 5 (limitado por prueba)")
    print(f"Total Resultados Crudos: {total}")
    print(f"Promedio por búsqueda: {total/5 if total else 0}")
    
    # Mostrar muestra
    if resultados:
        print("\nEjemplos de lo encontrado (SIN FILTRAR):")
        for i, res in enumerate(resultados[:3]):
            print(f"  {i+1}. {res['titulo']} ({res['url']})")

if __name__ == "__main__":
    main()
