#!/usr/bin/env python3
"""
SCRIPT UNIFICADO DE BÚSQUEDA Y ANÁLISIS
=======================================
Este script orquesta todo el proceso:
1. Lee configuración de Google Sheets
2. Ejecuta búsquedas en Google (buscar_y_procesar.py)
3. Guarda resultados en Supabase
4. Ejecuta análisis con ChatGPT (analizar_con_chatgpt.py)

Diseñado para ser ejecutado manualmente desde el Dashboard o automáticamente por cron.
"""

import os
import sys
import json
import time
from datetime import datetime
from supabase import create_client, Client

# Importar módulos existentes
# Añadimos el directorio actual al path para poder importar
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    import buscar_y_procesar as buscador
    import analizar_con_chatgpt as analizador
except ImportError as e:
    print(f"❌ Error importando módulos: {e}")
    sys.exit(1)

# Configuración Supabase
SUPABASE_URL = "https://imuhtilqwbqjuuvztfjp.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImltdWh0aWxxd2JxanV1dnp0ZmpwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjYwNzI5MzEsImV4cCI6MjA4MTY0ODkzMX0.aXHKbUUnzOXuiCbx3OalgHPXEQ2rbiw0eDG56y_MBU4"

def guardar_fichas_en_supabase(fichas):
    """Guarda las fichas encontradas en Supabase"""
    print(f"\n💾 Guardando {len(fichas)} fichas en Supabase...")
    
    if not SUPABASE_KEY:
        print("❌ Error: SUPABASE_KEY no configurada")
        return 0
        
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    guardadas = 0
    duplicadas = 0
    errores = 0
    
    for ficha in fichas:
        try:
            # Verificar si ya existe por URL
            result = supabase.table('fichas').select('id').eq('url', ficha['url']).execute()
            
            if result.data:
                duplicadas += 1
                continue
                
            # Insertar nueva ficha
            # Limpiar campos que no existen en la tabla o tienen formato incorrecto
            ficha_limpia = {k: v for k, v in ficha.items() if v is not None}
            
            # Asegurar que procesada es False para que el analizador la coja
            ficha_limpia['procesada'] = False
            ficha_limpia['propuesta_comunicativa'] = None # Forzar null para análisis
            
            supabase.table('fichas').insert(ficha_limpia).execute()
            guardadas += 1
            
        except Exception as e:
            print(f"  ⚠️ Error guardando ficha {ficha.get('url', 'sin-url')}: {e}")
            errores += 1
            
    print(f"  ✅ Resumen guardado: {guardadas} nuevas, {duplicadas} duplicadas, {errores} errores\n")
    return guardadas

def main():
    start_time = time.time()
    print("\n" + "="*70)
    print("🚀 INICIANDO PROCESO COMPLETO: BÚSQUEDA + ANÁLISIS")
    print("="*70)
    
    # 1. EJECUTAR BÚSQUEDA
    print("\n🔹 FASE 1: BÚSQUEDA EN GOOGLE")
    try:
        # Configurar credenciales desde entorno si no están en el archivo de config
        if not buscador.CONFIG['GOOGLE_API_KEY']:
            buscador.CONFIG['GOOGLE_API_KEY'] = os.environ.get('GOOGLE_API_KEY')
        if not buscador.CONFIG['GOOGLE_CSE_ID']:
            buscador.CONFIG['GOOGLE_CSE_ID'] = os.environ.get('GOOGLE_CSE_ID')
            
        # Ejecutar flujo de búsqueda
        spreadsheet = buscador.conectar_google_sheets()
        senales_inst = buscador.leer_senales_institucionales(spreadsheet)
        senales_social = buscador.leer_senales_redes_sociales(spreadsheet)
        
        todas_senales = senales_inst + senales_social
        
        if not todas_senales:
            print("⚠️ No hay señales activas. Terminando.")
            return
            
        queries = buscador.construir_queries(todas_senales)
        resultados = buscador.ejecutar_todas_las_busquedas(queries)
        
        if not resultados:
            print("⚠️ No se encontraron resultados. Terminando.")
            return
            
        fichas = buscador.construir_todas_las_fichas(resultados)
        
        # Guardar en Supabase
        nuevas_fichas = guardar_fichas_en_supabase(fichas)
        
    except Exception as e:
        print(f"❌ Error crítico en fase de búsqueda: {e}")
        import traceback
        traceback.print_exc()
        return

    # 2. EJECUTAR ANÁLISIS
    if nuevas_fichas > 0:
        print("\n🔹 FASE 2: ANÁLISIS CON CHATGPT")
        try:
            # Configurar credenciales
            if not analizador.SUPABASE_KEY:
                analizador.SUPABASE_KEY = SUPABASE_KEY
                
            # Ejecutar análisis
            analizador.procesar_fichas()
            
        except Exception as e:
            print(f"❌ Error crítico en fase de análisis: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("\n🔹 FASE 2: ANÁLISIS OMITIDO (No hay nuevas fichas)")

    duration = time.time() - start_time
    print("\n" + "="*70)
    print(f"✅ PROCESO FINALIZADO en {duration:.1f} segundos")
    print("="*70 + "\n")

if __name__ == "__main__":
    main()
