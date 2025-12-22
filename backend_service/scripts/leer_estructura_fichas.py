import os
import requests
import json

# Configuración
SHEET_ID = '1-6e0U1SATcgs2V8u2fOoDoKIrLjzwJi8GxJtUwy9t_U'
RANGE_NAME = 'Estructura_Fichas!A1:Z20' # Leemos un rango amplio para ver cabeceras y ejemplos
GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY', 'AIzaSyBk5KghTy3GkOMbCdZDcduaeyrQaaP_KcA')

def leer_estructura():
    if not GOOGLE_API_KEY:
        print("❌ Error: API Key no encontrada")
        return

    url = f"https://sheets.googleapis.com/v4/spreadsheets/{SHEET_ID}/values/{RANGE_NAME}?key={GOOGLE_API_KEY}"
    
    try:
        response = requests.get(url)
        if response.status_code != 200:
            print(f"❌ Error leyendo Sheet: {response.status_code}")
            return

        data = response.json()
        rows = data.get('values', [])
        
        if not rows:
            print("⚠️ La pestaña 'Estructura_Fichas' está vacía.")
            return

        print("📋 CONTENIDO DE 'Estructura_Fichas':")
        for i, row in enumerate(rows):
            print(f"Fila {i+1}: {row}")
            
    except Exception as e:
        print(f"❌ Excepción: {e}")

if __name__ == "__main__":
    leer_estructura()
