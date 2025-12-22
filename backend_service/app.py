from flask import Flask, jsonify
import subprocess
import os
import threading

app = Flask(__name__)

# Estado global para evitar ejecuciones concurrentes
is_running = False
last_run_status = {"status": "idle", "message": "Listo para ejecutar", "timestamp": None}

def run_script_background():
    global is_running, last_run_status
    is_running = True
    last_run_status = {"status": "running", "message": "Ejecutando búsqueda y análisis...", "timestamp": None}
    
    try:
        # Ruta al script unificado (relativa al contenedor)
        script_path = "scripts/run_search_and_analysis.py"
        
        # Ejecutar script y capturar salida
        result = subprocess.run(
            ["python3", script_path],
            capture_output=True,
            text=True,
            env={**os.environ, "PYTHONUNBUFFERED": "1"}
        )
        
        if result.returncode == 0:
            last_run_status = {
                "status": "success", 
                "message": "Proceso completado correctamente", 
                "output": result.stdout[-500:], # Últimos 500 caracteres
                "timestamp": os.popen("date -u +%Y-%m-%dT%H:%M:%SZ").read().strip()
            }
        else:
            last_run_status = {
                "status": "error", 
                "message": f"Error en ejecución (Exit code {result.returncode})", 
                "output": result.stderr[-500:],
                "timestamp": os.popen("date -u +%Y-%m-%dT%H:%M:%SZ").read().strip()
            }
            
    except Exception as e:
        last_run_status = {
            "status": "error", 
            "message": f"Excepción interna: {str(e)}", 
            "timestamp": os.popen("date -u +%Y-%m-%dT%H:%M:%SZ").read().strip()
        }
    finally:
        is_running = False

@app.route('/api/run-search', methods=['POST'])
def trigger_search():
    global is_running
    
    if is_running:
        return jsonify({"status": "busy", "message": "Ya hay un proceso en ejecución"}), 409
        
    # Iniciar en hilo separado
    thread = threading.Thread(target=run_script_background)
    thread.start()
    
    return jsonify({"status": "started", "message": "Proceso iniciado en segundo plano"}), 202

@app.route('/api/status', methods=['GET'])
def get_status():
    return jsonify({
        "is_running": is_running,
        "last_run": last_run_status
    })

if __name__ == '__main__':
    # Permitir acceso desde cualquier origen (CORS simplificado para dev)
    from flask_cors import CORS
    CORS(app)
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
