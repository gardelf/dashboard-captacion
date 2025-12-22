import os
import requests
import json

# Configuración extraída de test_search_only.py (que sabemos que funciona)
SHEET_ID = '1-6e0U1SATcgs2V8u2fOoDoKIrLjzwJi8GxJtUwy9t_U'
API_KEY = os.environ.get('GOOGLE_API_KEY')

def listar_pestanas():
    print(f"🔍 Inspeccionando Google Sheet ID: {SHEET_ID}")
    
    if not API_KEY:
        print("❌ Error: No se encontró GOOGLE_API_KEY en variables de entorno")
        return

    # Endpoint para obtener metadatos del spreadsheet (incluye lista de hojas)
    url = f"https://sheets.googleapis.com/v4/spreadsheets/{SHEET_ID}?key={API_KEY}"
    
    try:
        response = requests.get(url)
        if response.status_code != 200:
            print(f"❌ Error al conectar con Google API: {response.status_code}")
            print(response.text)
            return

        data = response.json()
        sheets = data.get('sheets', [])
        
        print(f"✅ Conexión exitosa. Se encontraron {len(sheets)} pestañas:")
        print("="*50)
        
        for sheet in sheets:
            props = sheet.get('properties', {})
            title = props.get('title', 'Sin Título')
            sheet_id = props.get('sheetId', 'N/A')
            index = props.get('index', 'N/A')
            print(f"📄 Pestaña: '{title}' (ID: {sheet_id}, Índice: {index})")
            
        print("="*50)

    except Exception as e:
        print(f"❌ Excepción durante la conexión: {str(e)}")

if __name__ == "__main__":
    listar_pestanas()
