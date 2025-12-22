import os
import requests
import json

# Configuración
SHEET_ID = '1-6e0U1SATcgs2V8u2fOoDoKIrLjzwJi8GxJtUwy9t_U'
API_KEY = os.environ.get('GOOGLE_API_KEY')
RANGE_NAME = 'Signals!A2:E' # Empezamos en A2 para saltar encabezados

def leer_senales_correctas():
    print(f"🔍 Leyendo pestaña 'Signals' con estructura corregida...")
    
    if not API_KEY:
        print("❌ Error: Falta GOOGLE_API_KEY")
        return []

    url = f"https://sheets.googleapis.com/v4/spreadsheets/{SHEET_ID}/values/{RANGE_NAME}?key={API_KEY}"
    
    try:
        response = requests.get(url)
        if response.status_code != 200:
            print(f"❌ Error API: {response.status_code} - {response.text}")
            return []

        data = response.json()
        rows = data.get('values', [])
        
        print(f"✅ Filas crudas recuperadas: {len(rows)}")
        
        senales_validas = []
        
        for i, row in enumerate(rows):
            # Estructura esperada: [ID, Señal, Tipo, Activa, Notas]
            # Índices: 0=ID, 1=Señal, 2=Tipo, 3=Activa, 4=Notas
            
            if len(row) < 4:
                print(f"  ⚠️ Fila {i+2} incompleta, saltando: {row}")
                continue
                
            senal_texto = row[1].strip()
            activa = row[3].strip().upper()
            
            if activa == 'SÍ' and senal_texto:
                senales_validas.append({
                    'query': senal_texto,
                    'origen': 'Signals_Sheet', # Usamos un valor genérico ya que no hay columna Institución
                    'fila': i + 2
                })
            else:
                # Opcional: Mostrar qué se ignora para depuración
                # print(f"  Ignorando fila {i+2}: Activa='{activa}'")
                pass
                
        print(f"\n✅ Señales válidas para procesar: {len(senales_validas)}")
        
        if senales_validas:
            print("\n📋 Primeras 5 señales a buscar:")
            for s in senales_validas[:5]:
                print(f"  - Fila {s['fila']}: '{s['query']}'")
                
        return senales_validas

    except Exception as e:
        print(f"❌ Excepción: {str(e)}")
        return []

if __name__ == "__main__":
    leer_senales_correctas()
