import os
import requests
import json

# Configuración Constante
SHEET_ID = '1-6e0U1SATcgs2V8u2fOoDoKIrLjzwJi8GxJtUwy9t_U'
RANGE_NAME = 'Signals!A2:E' # Saltamos encabezados

def obtener_senales(api_key):
    """
    Lee las señales de búsqueda desde la pestaña 'Signals' de Google Sheets.
    
    Args:
        api_key (str): Google API Key válida.
        
    Returns:
        list: Lista de diccionarios con {'query': str, 'origen': str, 'fila': int}
    """
    if not api_key:
        print("❌ Error: API Key no proporcionada a obtener_senales()")
        return []

    url = f"https://sheets.googleapis.com/v4/spreadsheets/{SHEET_ID}/values/{RANGE_NAME}?key={api_key}"
    
    try:
        response = requests.get(url)
        if response.status_code != 200:
            print(f"❌ Error conectando a Google Sheets: {response.status_code} - {response.text}")
            return []

        data = response.json()
        rows = data.get('values', [])
        
        senales_validas = []
        
        for i, row in enumerate(rows):
            # Estructura esperada: [ID, Señal, Tipo, Activa, Notas]
            if len(row) < 4:
                continue
                
            senal_texto = row[1].strip()
            activa = row[3].strip().upper()
            
            if activa == 'SÍ' and senal_texto:
                senales_validas.append({
                    'query': senal_texto,
                    'origen': 'Signals_Sheet',
                    'fila': i + 2
                })
                
        print(f"✅ Módulo Lectura: {len(senales_validas)} señales extraídas correctamente.")
        return senales_validas

    except Exception as e:
        print(f"❌ Excepción en módulo de lectura: {str(e)}")
        return []
