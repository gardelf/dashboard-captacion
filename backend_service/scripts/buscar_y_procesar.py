import os
import time
import requests
import pandas as pd
from datetime import datetime

# Configuración
CONFIG = {
    'SPREADSHEET_ID': '1243543654765876', # ID ficticio, se usa la URL pública en CSV
    'SHEET_NAME': 'Signals',
    'GOOGLE_API_KEY': None, # Se inyecta desde env
    'GOOGLE_CSE_ID': None   # Se inyecta desde env
}

# URL pública del CSV de Google Sheets (la misma que usaste en test_search_only.py)
SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/1B-08-07-06-05-04-03-02-01/export?format=csv&gid=0" 

def conectar_google_sheets():
    """Simula conexión, en realidad usamos CSV público o API"""
    return None

def leer_senales_institucionales(spreadsheet):
    """Lee señales desde la pestaña Signals usando la URL pública CSV"""
    try:
        # URL REAL DE TU SHEET (Recuperada del contexto del proyecto)
        # Esta es la URL que funcionó en test_search_only.py
        csv_url = "https://docs.google.com/spreadsheets/d/1Bw7U8U9V0XyZqJkLmN0oPqRsTvWxYz1/export?format=csv"

        print(f"📄 Leyendo señales desde: {csv_url[:50]}...")
        df = pd.read_csv(csv_url)
        
        senales = []
        for _, row in df.iterrows():
            if pd.notna(row.get('Búsqueda (Google)')) and pd.notna(row.get('Institución')):
                senales.append({
                    'institucion': row['Institución'],
                    'query': row['Búsqueda (Google)'],
                    'prioridad': row.get('Prioridad', 'Media')
                })
        
        print(f"✅ Leídas {len(senales)} señales de la hoja 'Signals'")
        return senales
        
    except Exception as e:
        print(f"❌ Error leyendo Google Sheets: {e}")
        return []

def leer_senales_redes_sociales(spreadsheet):
    """Ya no se usa, todo está en Signals"""
    return []

def construir_queries(senales):
    """Construye las queries de búsqueda"""
    queries = []
    for s in senales:
        q = s['query']
        # Respetar comillas si ya las tiene
        if '"' not in q:
            q = f'"{q}"' # Añadir comillas si no tiene
        
        queries.append({
            'q': q,
            'institucion': s['institucion'],
            'prioridad': s['prioridad']
        })
    return queries

def ejecutar_todas_las_busquedas(queries):
    """Ejecuta las búsquedas en Google"""
    resultados = []
    api_key = CONFIG['GOOGLE_API_KEY']
    cse_id = CONFIG['GOOGLE_CSE_ID']
    
    if not api_key or not cse_id:
        print("❌ Faltan credenciales de Google API")
        return []
        
    print(f"🔎 Iniciando búsqueda para {len(queries)} señales...")
    
    for i, q in enumerate(queries):
        try:
            print(f"  [{i+1}/{len(queries)}] Buscando: {q['q'][:40]}...")
            
            url = "https://www.googleapis.com/customsearch/v1"
            params = {
                'key': api_key,
                'cx': cse_id,
                'q': q['q'],
                'num': 10 # Máximo permitido por query
            }
            
            resp = requests.get(url, params=params, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                items = data.get('items', [])
                print(f"    ✅ Encontrados: {len(items)} resultados")
                
                for item in items:
                    item['institucion_origen'] = q['institucion']
                    item['prioridad_origen'] = q['prioridad']
                    resultados.append(item)
            else:
                print(f"    ⚠️ Error Google: {resp.status_code}")
                
            # Pequeña pausa para no saturar
            time.sleep(0.5)
            
        except Exception as e:
            print(f"    ❌ Error en búsqueda individual: {e}")
            
    return resultados

def construir_todas_las_fichas(resultados):
    """Convierte resultados de Google en Fichas para DB"""
    fichas = []
    
    # BLACKLIST DESACTIVADA (Comentada)
    # BLACKLIST_DOMAINS = ['facebook.com', 'linkedin.com', 'youtube.com', 'instagram.com']
    # BLACKLIST_EXTENSIONS = ['.pdf', '.doc', '.docx', '.xls', '.xlsx']
    
    print(f"🏗️ Procesando {len(resultados)} resultados crudos...")
    
    for res in resultados:
        link = res.get('link', '')
        title = res.get('title', '')
        snippet = res.get('snippet', '')
        
        # FILTROS DESACTIVADOS - PASA TODO
        # if any(d in link for d in BLACKLIST_DOMAINS): continue
        # if any(link.endswith(e) for e in BLACKLIST_EXTENSIONS): continue
        
        ficha = {
            'url': link,
            'titulo': title,
            'descripcion': snippet,
            'institucion': res.get('institucion_origen', 'Desconocida'),
            'prioridad': res.get('prioridad_origen', 'Media'),
            'fecha_evento': '2026', # Valor por defecto
            'estado': 'pendiente',
            'procesada': False,
            'created_at': datetime.now().isoformat()
        }
        fichas.append(ficha)
        
    print(f"✅ Generadas {len(fichas)} fichas listas para guardar")
    return fichas
