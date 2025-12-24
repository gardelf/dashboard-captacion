import os
import requests
import json

# Configuración Constante
SHEET_ID = '1-6e0U1SATcgs2V8u2fOoDoKIrLjzwJi8GxJtUwy9t_U'
RANGE_NAME = 'Signals!A2:E' # Saltamos encabezados

# Cache para claves (evitar múltiples llamadas a la API)
_claves_cache = None

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

def leer_claves_desde_sheets(api_key=None, forzar_recarga=False):
    """
    Lee todas las claves de configuración desde la pestaña 'Claves' de Google Sheets.
    Usa cache para evitar múltiples llamadas a la API.
    
    Args:
        api_key (str): Google API Key. Si no se proporciona, intenta usar una clave hardcoded temporal.
        forzar_recarga (bool): Si True, ignora el cache y recarga desde Sheets.
        
    Returns:
        dict: Diccionario con todas las claves de configuración.
              Retorna valores por defecto si falla la lectura.
    """
    global _claves_cache
    
    # Si ya tenemos cache y no se fuerza recarga, devolver cache
    if _claves_cache is not None and not forzar_recarga:
        return _claves_cache
    
    # API Key temporal para bootstrap (la real se leerá de Sheets)
    if not api_key:
        api_key = 'AIzaSyBk5KghTy3GkOMbCdZDcduaeyrQaaP_KcA'
    
    url = f"https://sheets.googleapis.com/v4/spreadsheets/{SHEET_ID}/values/Claves!A:B?key={api_key}"
    
    # Valores por defecto en caso de error
    claves_default = {
        'GOOGLE_API_KEY': 'AIzaSyBk5KghTy3GkOMbCdZDcduaeyrQaaP_KcA',
        'GOOGLE_CSE_ID': 'c3c4a5e5a6f8c4f9e',
        'OPENAI_API_KEY': '',
        'DATABASE_URL': '',
        'SHEET_ID': SHEET_ID,
        'LIMITE_KEYWORDS': 1,
        'LIMITE_ENRIQUECIMIENTO': 5,
        'NUM_RESULTADOS_GOOGLE': 10
    }
    
    try:
        response = requests.get(url, timeout=10)
        
        if response.status_code != 200:
            print(f"⚠️ Error leyendo pestaña Claves: {response.status_code}")
            print(f"⚠️ Usando valores por defecto")
            _claves_cache = claves_default
            return claves_default
        
        data = response.json()
        rows = data.get('values', [])
        
        if not rows:
            print("⚠️ Pestaña Claves vacía, usando valores por defecto")
            _claves_cache = claves_default
            return claves_default
        
        # Parsear filas en diccionario
        claves = {}
        for row in rows:
            if len(row) >= 2:
                clave = row[0].strip()
                valor = row[1].strip()
                
                # Convertir valores numéricos
                if clave in ['LIMITE_KEYWORDS', 'LIMITE_ENRIQUECIMIENTO', 'NUM_RESULTADOS_GOOGLE']:
                    try:
                        valor = int(valor)
                    except ValueError:
                        valor = claves_default.get(clave, 1)
                
                claves[clave] = valor
        
        # Asegurar que todas las claves necesarias existen
        for key, default_value in claves_default.items():
            if key not in claves:
                claves[key] = default_value
        
        # Guardar en cache
        _claves_cache = claves
        
        print(f"✅ Claves leídas desde Google Sheets (pestaña Claves)")
        return claves
        
    except Exception as e:
        print(f"❌ Excepción leyendo claves: {str(e)}")
        print(f"⚠️ Usando valores por defecto")
        _claves_cache = claves_default
        return claves_default

def obtener_clave(nombre_clave, api_key=None):
    """
    Obtiene una clave específica desde Google Sheets.
    
    Args:
        nombre_clave (str): Nombre de la clave a obtener (ej: 'GOOGLE_API_KEY')
        api_key (str): Google API Key para acceder a Sheets.
        
    Returns:
        str/int: Valor de la clave solicitada.
    """
    claves = leer_claves_desde_sheets(api_key)
    return claves.get(nombre_clave)
