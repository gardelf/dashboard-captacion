import json
import uuid
from datetime import datetime
from urllib.parse import urlparse

def extraer_dominio(url):
    """Extrae el dominio limpio de una URL."""
    try:
        parsed = urlparse(url)
        domain = parsed.netloc
        if domain.startswith('www.'):
            domain = domain[4:]
        return domain
    except:
        return ""

def detectar_plataforma(url, dominio):
    """Detecta la plataforma social basada en la URL."""
    dominio = dominio.lower()
    if 'reddit.com' in dominio: return 'Reddit'
    if 'facebook.com' in dominio: return 'Facebook'
    if 'linkedin.com' in dominio: return 'LinkedIn'
    if 'instagram.com' in dominio: return 'Instagram'
    if 'twitter.com' in dominio or 'x.com' in dominio: return 'Twitter'
    return 'Web'

def extraer_username(url, plataforma):
    """Intenta extraer username de redes sociales."""
    try:
        path = urlparse(url).path
        parts = [p for p in path.split('/') if p]
        
        if plataforma == 'Reddit' and 'user' in parts:
            idx = parts.index('user')
            if idx + 1 < len(parts): return f"u/{parts[idx+1]}"
            
        if plataforma == 'Facebook' and len(parts) > 0:
            return parts[0]
            
        return ""
    except:
        return ""

def extraer_subreddit(url, plataforma):
    """Intenta extraer subreddit de Reddit."""
    try:
        if plataforma == 'Reddit':
            path = urlparse(url).path
            parts = [p for p in path.split('/') if p]
            if 'r' in parts:
                idx = parts.index('r')
                if idx + 1 < len(parts): return f"r/{parts[idx+1]}"
        return ""
    except:
        return ""

def normalizar_resultados(resultados_crudos, query_origen, prioridad_origen='Media'):
    """
    Convierte resultados crudos de Google en objetos JSON estructurados según 'Estructura_Fichas'.
    """
    fichas_normalizadas = []
    urls_vistas = set()
    
    print(f"🔄 Procesando {len(resultados_crudos)} resultados crudos para '{query_origen}'...")
    
    for res in resultados_crudos:
        url = res.get('url')
        
        # Validación básica
        if not url or url in urls_vistas:
            continue
            
        urls_vistas.add(url)
        
        # Extracción de metadatos
        dominio = extraer_dominio(url)
        plataforma = detectar_plataforma(url, dominio)
        username = extraer_username(url, plataforma)
        subreddit = extraer_subreddit(url, plataforma)
        
        # Generación de ID único
        fecha_hoy = datetime.now().strftime("%Y%m%d")
        unique_id = f"SIG-{fecha_hoy}-{str(uuid.uuid4())[:8]}"
        
        # Construcción del objeto JSON EXACTO según Estructura_Fichas
        ficha = {
            'id': unique_id,
            'tipo': 'búsqueda', # Valor por defecto, se podría refinar
            'keyword': query_origen,
            'url': url,
            'titulo': res.get('titulo', 'Sin título'),
            'institucion': None, # IA lo llenará
            'email': None,       # IA lo llenará
            'telefono': None,    # IA lo llenará
            'tiene_formulario': None, # IA lo llenará
            'plataforma_social': plataforma,
            'username': username,
            'subreddit': subreddit,
            'grupo_facebook': None, # Difícil de saber solo con URL
            'snippet': res.get('snippet', ''),
            'dominio': dominio,
            'fecha_detectada': datetime.now().strftime("%Y-%m-%d"),
            'prioridad': prioridad_origen,
            'propuesta_comunicativa': None, # IA lo llenará
            'canal_recomendado': None,      # IA lo llenará
            'estado': 'pendiente',
            'procesada': 'NO',
            'fecha_contacto': None,
            'fecha_creacion': datetime.now().isoformat(),
            'ultima_actualizacion': datetime.now().isoformat()
        }
        
        fichas_normalizadas.append(ficha)
        
    print(f"✅ Generadas {len(fichas_normalizadas)} fichas únicas normalizadas.")
    return fichas_normalizadas

def prueba_procesamiento():
    """Prueba unitaria avanzada"""
    datos_prueba = [
        {
            'titulo': 'Looking for housing near IE - Reddit', 
            'url': 'https://www.reddit.com/r/MBA/comments/xyz/looking_for_housing/', 
            'snippet': 'I am starting at IE in September...'
        },
        {
            'titulo': 'Student Services | IE University', 
            'url': 'https://www.ie.edu/student-services/', 
            'snippet': 'We help you find accommodation...'
        }
    ]
    
    resultado = normalizar_resultados(datos_prueba, "housing ie madrid", "Alta")
    
    print("\n📋 Resultado de prueba avanzada:")
    print(json.dumps(resultado, indent=2))
    
    # Verificaciones
    r1 = resultado[0]
    if r1['plataforma_social'] == 'Reddit' and r1['subreddit'] == 'r/MBA':
        print("\n✅ Extracción de Reddit correcta.")
    else:
        print("\n❌ Fallo en extracción de Reddit.")

if __name__ == "__main__":
    prueba_procesamiento()
