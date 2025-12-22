import os
import requests
import json

# Configuración
SHEET_ID = '1-6e0U1SATcgs2V8u2fOoDoKIrLjzwJi8GxJtUwy9t_U'
API_KEY = os.environ.get('GOOGLE_API_KEY')

# Lista de pestañas detectadas en el paso anterior
PESTANAS = [
    'Prompt_ChatGPT',
    'Dashboard',
    'Contexto_Piso_Estrategia',
    'Hoja 1',
    'Estructura_Fichas',
    'Signals',
    'Sin uso Señales_Redes_Sociales',
    'Sin Uso Palabras_Clave_Contacto',
    'Configuración',
    'Dashboard_Fichas',
    'Estadísticas',
    'Instrucciones_Dashboard'
]

def analizar_pestana(nombre_pestana):
    print(f"\n🔍 Analizando pestaña: '{nombre_pestana}'...")
    
    # Leemos las primeras 10 filas y 5 columnas para tener una idea clara
    url = f"https://sheets.googleapis.com/v4/spreadsheets/{SHEET_ID}/values/{nombre_pestana}!A1:E10?key={API_KEY}"
    
    try:
        response = requests.get(url)
        if response.status_code != 200:
            print(f"  ❌ Error leyendo '{nombre_pestana}': {response.status_code}")
            return

        data = response.json()
        rows = data.get('values', [])
        
        if not rows:
            print("  ⚠️ Pestaña vacía.")
            return

        print(f"  ✅ Filas encontradas: {len(rows)}")
        print("  📋 Muestra de contenido (primeras 3 filas):")
        for i, row in enumerate(rows[:3]):
            print(f"    Fila {i+1}: {row}")
            
        # Análisis heurístico del propósito
        headers = [h.lower() for h in rows[0]] if rows else []
        
        if 'institucion' in str(headers) and 'busqueda' in str(headers):
            print("  💡 PROPÓSITO DETECTADO: Fuente de Señales de Búsqueda (INPUT)")
        elif 'prompt' in str(headers) or 'rol' in str(headers):
            print("  💡 PROPÓSITO DETECTADO: Configuración de ChatGPT (PROMPT)")
        elif 'config' in str(headers) or 'valor' in str(headers):
            print("  💡 PROPÓSITO DETECTADO: Configuración del Sistema (CONFIG)")
        elif 'dashboard' in str(headers) or 'total' in str(headers):
            print("  💡 PROPÓSITO DETECTADO: Visualización de Datos (OUTPUT)")
        else:
            print("  ❓ Propósito no evidente automáticamente.")

    except Exception as e:
        print(f"  ❌ Excepción: {str(e)}")

def main():
    print("🚀 INICIANDO ANÁLISIS PROFUNDO DE GOOGLE SHEETS")
    print("===============================================")
    
    if not API_KEY:
        print("❌ Error: Falta GOOGLE_API_KEY")
        return

    for pestana in PESTANAS:
        analizar_pestana(pestana)
        
    print("\n✅ Análisis completado.")

if __name__ == "__main__":
    main()
