# 📋 WORKFLOW COMPLETO - SISTEMA DE CAPTACIÓN DE ESTUDIANTES

## 🎯 Objetivo General

Sistema automatizado para buscar, procesar y enriquecer información de estudiantes potenciales interesados en alojamiento en España, almacenando todo en PostgreSQL de Render.

---

## 🗂️ ARQUITECTURA DEL SISTEMA

### Componentes principales:

1. **Google Sheets** → Fuente de palabras clave
2. **Google Custom Search API** → Búsqueda de resultados
3. **Módulo de Guardado** → Almacenamiento en PostgreSQL (Render)
4. **OpenAI ChatGPT** → Enriquecimiento de datos
5. **PostgreSQL (Render)** → Base de datos de producción

### Ubicación de archivos:

```
/home/ubuntu/dashboard-captacion/
├── backend_service/
│   └── scripts/
│       ├── modulo_busqueda_google.py          # Búsqueda en Google
│       ├── modulo_guardado_postgres.py        # Guardado en PostgreSQL
│       ├── modulo_enriquecimiento_postgres.py # Enriquecimiento con ChatGPT
│       └── leer_google_sheets.py              # Lectura de keywords
└── drizzle/
    └── schema.ts                               # Esquema de base de datos
```

---

## 📊 FASE 1: LECTURA DE GOOGLE SHEETS

### Objetivo:
Obtener las palabras clave (keywords) desde un Google Sheet compartido.

### Archivo:
`backend_service/scripts/leer_google_sheets.py`

### Proceso paso a paso:

#### 1.1 Configuración de credenciales

```python
SPREADSHEET_ID = "1vJxRPwXAV0bHgZ0Qj4pAY3Lj5KqWmNnOoPpQqRrSs"
RANGE_NAME = "Keywords!A2:A"  # Columna A, desde fila 2
```

**Credenciales de Google:**
- Service Account configurado con acceso a Google Sheets API
- Archivo JSON de credenciales almacenado de forma segura
- Permisos de lectura sobre el spreadsheet

#### 1.2 Conexión a Google Sheets API

```python
from google.oauth2 import service_account
from googleapiclient.discovery import build

credentials = service_account.Credentials.from_service_account_file(
    'credentials.json',
    scopes=['https://www.googleapis.com/auth/spreadsheets.readonly']
)

service = build('sheets', 'v4', credentials=credentials)
```

#### 1.3 Lectura de keywords

```python
def leer_keywords_desde_sheets():
    """
    Lee keywords desde Google Sheets.
    Returns: Lista de strings (keywords)
    """
    result = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID,
        range=RANGE_NAME
    ).execute()
    
    values = result.get('values', [])
    keywords = [row[0] for row in values if row]  # Filtrar filas vacías
    
    return keywords
```

#### 1.4 Limpieza y validación

- **Eliminar duplicados**: `list(set(keywords))`
- **Eliminar espacios**: `keyword.strip()`
- **Filtrar vacíos**: `if keyword`
- **Convertir a minúsculas**: `keyword.lower()` (opcional)

#### 1.5 Output

```python
[
    "student accommodation Madrid 2026",
    "student housing Barcelona 2026",
    "alojamiento estudiantes Valencia 2026",
    ...
]
```

---

## 🔍 FASE 2: BÚSQUEDA EN GOOGLE

### Objetivo:
Para cada keyword, buscar resultados relevantes usando Google Custom Search API.

### Archivo:
`backend_service/scripts/modulo_busqueda_google.py`

### Proceso paso a paso:

#### 2.1 Configuración de API

```python
GOOGLE_API_KEY = 'AIzaSyBk5KghTy3GkOMbCdZDcduaeyrQaaP_KcA'
GOOGLE_CSE_ID = '0679f1599bd26402e'
```

**Límites de la API:**
- 100 búsquedas/día (plan gratuito)
- Máximo 10 resultados por búsqueda
- Rate limit: 10 queries/segundo

#### 2.2 Función de búsqueda

```python
def ejecutar_busqueda(query, num_resultados=10):
    """
    Ejecuta una búsqueda en Google Custom Search API.
    
    Args:
        query (str): Término de búsqueda
        num_resultados (int): Número de resultados (max 10)
        
    Returns:
        list: Lista de diccionarios con resultados
    """
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        'key': GOOGLE_API_KEY,
        'cx': GOOGLE_CSE_ID,
        'q': query,
        'num': min(num_resultados, 10)  # API limita a 10
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            items = data.get('items', [])
            
            resultados_limpios = []
            for item in items:
                resultados_limpios.append({
                    'titulo': item.get('title'),
                    'url': item.get('link'),
                    'snippet': item.get('snippet'),
                    'fecha_descubrimiento': datetime.now().isoformat()
                })
            return resultados_limpios
        else:
            print(f"❌ Error API: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return []
```

#### 2.3 Procesamiento de resultados

Para cada resultado de Google, se extrae:

| Campo | Descripción | Ejemplo |
|-------|-------------|---------|
| **titulo** | Título de la página | "Student Housing Madrid 2026" |
| **url** | URL completa | "https://example.com/housing" |
| **snippet** | Descripción corta (160 chars) | "Looking for student accommodation..." |
| **fecha_descubrimiento** | Timestamp ISO | "2025-12-22T10:30:45.123456" |

#### 2.4 Manejo de errores

- **Timeout**: 10 segundos máximo por búsqueda
- **Rate limiting**: Esperar 1 segundo entre búsquedas
- **Cuota excedida**: Registrar error y continuar con siguiente keyword
- **Sin resultados**: Devolver lista vacía `[]`

#### 2.5 Output

```python
[
    {
        'titulo': 'Apartments for students in Madrid | MadridEasy',
        'url': 'https://madrideasy.com/en',
        'snippet': 'Find the best student accommodation in Madrid...',
        'fecha_descubrimiento': '2025-12-22T10:30:45.123456'
    },
    {
        'titulo': 'Student housing Barcelona 2026',
        'url': 'https://barcelona-housing.com',
        'snippet': 'Affordable rooms for international students...',
        'fecha_descubrimiento': '2025-12-22T10:30:46.789012'
    },
    ...
]
```

---

## 💾 FASE 3: GUARDADO EN POSTGRESQL

### Objetivo:
Almacenar resultados en PostgreSQL de Render, evitando duplicados.

### Archivo:
`backend_service/scripts/modulo_guardado_postgres.py`

### Proceso paso a paso:

#### 3.1 Conexión a PostgreSQL

```python
RENDER_DATABASE_URL = "postgresql://dashboard_captacion_db_user:zCQusHpUln7PINbsqKY3uedDk1tOjcBi@dpg-d54jlsdactks73agf7b0-a.frankfurt-postgres.render.com/dashboard_captacion_db"

conn = psycopg2.connect(RENDER_DATABASE_URL)
cursor = conn.cursor()
```

#### 3.2 Generación de ID único

```python
def generar_id_ficha(url):
    """
    Genera un ID único para una ficha.
    
    Formato: RND-YYYYMMDD-HASH8
    Ejemplo: RND-20251222-748407b5
    """
    timestamp = datetime.now().strftime('%Y%m%d')
    hash_url = hashlib.md5(url.encode()).hexdigest()[:8]
    return f"RND-{timestamp}-{hash_url}"
```

**Componentes del ID:**
- `RND`: Prefijo (Render)
- `20251222`: Fecha de creación
- `748407b5`: Hash MD5 de la URL (primeros 8 caracteres)

#### 3.3 Detección de duplicados

```python
def verificar_duplicado(url):
    """
    Consulta si una URL ya existe en la tabla 'fichas'.
    Returns: True si existe, False si es nueva.
    """
    try:
        conn = psycopg2.connect(RENDER_DATABASE_URL)
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT id FROM fichas WHERE url = %s LIMIT 1",
            (url,)
        )
        result = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        return result is not None  # True si existe
        
    except Exception as e:
        print(f"⚠️ Error verificando duplicado: {e}")
        return False  # En caso de error, asumir que es nueva
```

**Criterio de duplicado:**
- Se compara la URL completa (exacta)
- Si existe, se omite el guardado
- Se registra en log como "⏭️ Duplicado ignorado"

#### 3.4 Preparación de datos

```python
def preparar_ficha(resultado, keyword):
    """
    Convierte un resultado de Google en una ficha lista para guardar.
    """
    from urllib.parse import urlparse
    
    return {
        'id': generar_id_ficha(resultado['url']),
        'tipo': 'busqueda_google',
        'keyword': keyword,
        'url': resultado['url'],
        'titulo': resultado['titulo'],
        'snippet': resultado['snippet'],
        'dominio': urlparse(resultado['url']).netloc,
        'fecha_detectada': datetime.now().isoformat(),
        'prioridad': 'Media',
        'procesada': 'NO',
        
        # Campos vacíos (se llenarán con ChatGPT)
        'institucion': None,
        'email': None,
        'telefono': None,
        'tiene_formulario': None,
        'plataforma_social': None,
        'username': None,
        'subreddit': None,
        'grupo_facebook': None,
        'propuesta_comunicativa': None,
        'canal_recomendado': None,
        'estado': 'pendiente',
        'fecha_contacto': None
    }
```

#### 3.5 Inserción en PostgreSQL

```python
def guardar_fichas(fichas):
    """
    Guarda una lista de fichas en PostgreSQL, ignorando duplicados.
    
    Returns: Número de fichas guardadas (int)
    """
    guardadas = 0
    duplicadas = 0
    errores = 0
    
    for ficha in fichas:
        url = ficha.get('url')
        
        # 1. Verificar duplicado
        if verificar_duplicado(url):
            print(f"  ⏭️ Duplicado ignorado: {url[:50]}...")
            duplicadas += 1
            continue
        
        # 2. Insertar en PostgreSQL
        try:
            conn = psycopg2.connect(RENDER_DATABASE_URL)
            cursor = conn.cursor()
            
            valores = (
                ficha['id'],
                ficha['tipo'],
                ficha['keyword'],
                ficha['url'],
                ficha['titulo'],
                ficha['snippet'],
                ficha['dominio'],
                ficha.get('institucion'),
                ficha.get('email'),
                ficha.get('telefono'),
                ficha.get('tiene_formulario'),
                ficha.get('plataforma_social'),
                ficha.get('username'),
                ficha.get('subreddit'),
                ficha.get('grupo_facebook'),
                ficha.get('fecha_detectada'),
                ficha.get('prioridad'),
                ficha.get('propuesta_comunicativa'),
                ficha.get('canal_recomendado'),
                ficha.get('estado', 'pendiente'),
                ficha.get('procesada', 'NO'),
                ficha.get('fecha_contacto')
            )
            
            cursor.execute("""
                INSERT INTO fichas (
                    id, tipo, keyword, url, titulo, snippet, dominio,
                    institucion, email, telefono, tiene_formulario,
                    plataforma_social, username, subreddit, grupo_facebook,
                    fecha_detectada, prioridad, propuesta_comunicativa,
                    canal_recomendado, estado, procesada, fecha_contacto
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
            """, valores)
            
            conn.commit()
            cursor.close()
            conn.close()
            
            print(f"  ✅ Guardada: {ficha['id']}")
            guardadas += 1
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
            errores += 1
    
    print(f"\n📊 RESUMEN GUARDADO")
    print(f"  ✅ Nuevas: {guardadas}")
    print(f"  ⏭️ Duplicadas: {duplicadas}")
    print(f"  ❌ Errores: {errores}")
    
    return guardadas
```

#### 3.6 Esquema de la tabla `fichas`

```sql
CREATE TABLE fichas (
    -- Identificación
    id VARCHAR(64) PRIMARY KEY,
    tipo TEXT,                          -- 'busqueda_google', 'reddit', 'facebook'
    keyword TEXT,                       -- Palabra clave usada
    
    -- Datos de origen
    url TEXT NOT NULL,                  -- URL del resultado
    titulo TEXT,                        -- Título de la página
    snippet TEXT,                       -- Descripción corta
    dominio TEXT,                       -- Dominio extraído
    
    -- Datos enriquecidos (ChatGPT)
    institucion TEXT,                   -- Universidad/institución
    email TEXT,                         -- Email de contacto
    telefono TEXT,                      -- Teléfono
    tiene_formulario BOOLEAN,           -- true/false
    plataforma_social TEXT,             -- 'reddit', 'facebook', 'twitter'
    username TEXT,                      -- Usuario de red social
    subreddit TEXT,                     -- Subreddit (si aplica)
    grupo_facebook TEXT,                -- Grupo de Facebook (si aplica)
    
    -- Gestión
    fecha_detectada TIMESTAMP,          -- Cuándo se encontró
    prioridad TEXT,                     -- 'Alta', 'Media', 'Baja'
    propuesta_comunicativa TEXT,        -- Mensaje generado por ChatGPT
    canal_recomendado TEXT,             -- 'email', 'reddit', 'web', etc.
    estado VARCHAR(32) DEFAULT 'pendiente',  -- 'pendiente', 'contactado', 'respondido'
    procesada VARCHAR(8) DEFAULT 'NO',  -- 'SI', 'NO'
    fecha_contacto TIMESTAMP,           -- Cuándo se contactó
    
    -- Auditoría
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    ultima_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);
```

#### 3.7 Output

```
💾 Iniciando guardado de 3 fichas en PostgreSQL (Render)...
  ✅ Guardada: RND-20251222-748407b5
  ✅ Guardada: RND-20251222-74afeb9a
  ⏭️ Duplicado ignorado: https://madrideasy.com/en...

📊 RESUMEN GUARDADO
  ✅ Nuevas: 2
  ⏭️ Duplicadas: 1
  ❌ Errores: 0
```

---

## 🤖 FASE 4: ENRIQUECIMIENTO CON CHATGPT

### Objetivo:
Analizar cada ficha con ChatGPT para extraer información adicional y generar propuestas de contacto personalizadas.

### Archivo:
`backend_service/scripts/modulo_enriquecimiento_postgres.py`

### Proceso paso a paso:

#### 4.1 Configuración de OpenAI

```python
OPENAI_API_KEY = "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"

OPENAI_MODEL = "gpt-4o-mini"  # Modelo optimizado (más rápido y económico)
```

**Costos aproximados (gpt-4o-mini):**
- Input: $0.15 / 1M tokens
- Output: $0.60 / 1M tokens
- ~$0.001 por ficha enriquecida

#### 4.2 Lectura de fichas pendientes

```python
def leer_fichas_pendientes(limite=10):
    """
    Lee fichas no procesadas de PostgreSQL.
    
    Args:
        limite (int): Máximo de fichas a procesar
        
    Returns:
        list: Lista de diccionarios con fichas
    """
    try:
        conn = psycopg2.connect(RENDER_DATABASE_URL)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, titulo, snippet, url 
            FROM fichas 
            WHERE procesada = 'NO' 
            ORDER BY fecha_creacion DESC 
            LIMIT %s
        """, (limite,))
        
        fichas = []
        for row in cursor.fetchall():
            fichas.append({
                'id': row[0],
                'titulo': row[1],
                'snippet': row[2],
                'url': row[3]
            })
        
        cursor.close()
        conn.close()
        
        return fichas
        
    except Exception as e:
        print(f"❌ Error leyendo fichas: {e}")
        return []
```

#### 4.3 Prompt de enriquecimiento

```python
def enriquecer_con_chatgpt(ficha, api_key):
    """
    Enriquece una ficha usando ChatGPT.
    
    Args:
        ficha (dict): Ficha con titulo, snippet, url
        api_key (str): API key de OpenAI
        
    Returns:
        dict: Datos enriquecidos o None si falla
    """
    prompt = f"""
Analiza esta información de un estudiante potencial y extrae:

Título: {ficha['titulo']}
Descripción: {ficha['snippet']}
URL: {ficha['url']}

Responde SOLO con un JSON válido (sin markdown, sin explicaciones) con esta estructura:
{{
  "institucion": "nombre de la institución educativa mencionada o null",
  "email": "email de contacto encontrado o null",
  "telefono": "teléfono encontrado o null",
  "tiene_formulario": "SI si menciona formulario de contacto, NO si no",
  "canal_recomendado": "reddit/facebook/email/web/whatsapp según la URL y contexto",
  "propuesta_comunicativa": "mensaje personalizado en español para contactar (máx 200 caracteres)"
}}
"""
```

**Instrucciones del prompt:**
1. **Formato estricto**: JSON sin markdown ni explicaciones
2. **Campos obligatorios**: Todos los campos deben estar presentes
3. **Valores null**: Usar `null` si no se encuentra información
4. **Longitud**: Propuesta comunicativa máximo 200 caracteres
5. **Idioma**: Propuesta en español

#### 4.4 Llamada a OpenAI API

```python
    try:
        response = requests.post(
            'https://api.openai.com/v1/chat/completions',
            headers={
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            },
            json={
                'model': 'gpt-4o-mini',
                'messages': [{'role': 'user', 'content': prompt}],
                'temperature': 0.7,
                'max_tokens': 500
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            content = data['choices'][0]['message']['content'].strip()
            
            # Limpiar markdown si existe
            if content.startswith('```'):
                content = content.split('\n', 1)[1]
                content = content.rsplit('\n```', 1)[0]
            
            return json.loads(content)
        else:
            print(f"  ❌ Error API OpenAI: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"  ❌ Error enriqueciendo: {e}")
        return None
```

**Manejo de errores:**
- **Timeout**: 30 segundos máximo
- **Rate limiting**: OpenAI tiene límites por minuto
- **Formato inválido**: Limpiar markdown automáticamente
- **JSON malformado**: Capturar excepción y registrar error

#### 4.5 Ejemplo de respuesta de ChatGPT

```json
{
  "institucion": "Universitat Autònoma de Barcelona",
  "email": null,
  "telefono": null,
  "tiene_formulario": "SI",
  "canal_recomendado": "web",
  "propuesta_comunicativa": "Hola, estoy interesado en el programa de estudios en Barcelona para 2026. ¿Podrían enviarme más información sobre alojamiento?"
}
```

#### 4.6 Normalización de datos

```python
def normalizar_datos_enriquecidos(datos):
    """
    Normaliza los datos de ChatGPT para PostgreSQL.
    
    Conversiones:
    - "SI" → True
    - "NO" → False
    - null → None
    """
    # Normalizar tiene_formulario: "SI"/"NO" → true/false/null
    tiene_form_raw = datos.get('tiene_formulario')
    if tiene_form_raw == 'SI':
        datos['tiene_formulario'] = True
    elif tiene_form_raw == 'NO':
        datos['tiene_formulario'] = False
    else:
        datos['tiene_formulario'] = None
    
    return datos
```

**Razón de normalización:**
- PostgreSQL espera `BOOLEAN` (true/false)
- ChatGPT devuelve strings ("SI"/"NO")
- Sin normalización → error `Truncated incorrect INTEGER value`

#### 4.7 Actualización en PostgreSQL

```python
def actualizar_ficha(ficha_id, datos_enriquecidos):
    """
    Actualiza una ficha en PostgreSQL con datos enriquecidos.
    
    Args:
        ficha_id (str): ID de la ficha
        datos_enriquecidos (dict): Datos de ChatGPT normalizados
        
    Returns:
        bool: True si éxito, False si error
    """
    try:
        # Normalizar datos
        datos = normalizar_datos_enriquecidos(datos_enriquecidos)
        
        conn = psycopg2.connect(RENDER_DATABASE_URL)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE fichas 
            SET 
                institucion = %s,
                email = %s,
                telefono = %s,
                tiene_formulario = %s,
                canal_recomendado = %s,
                propuesta_comunicativa = %s,
                procesada = 'SI',
                ultima_actualizacion = CURRENT_TIMESTAMP
            WHERE id = %s
        """, (
            datos.get('institucion'),
            datos.get('email'),
            datos.get('telefono'),
            datos.get('tiene_formulario'),  # Ya normalizado a boolean
            datos.get('canal_recomendado'),
            datos.get('propuesta_comunicativa'),
            ficha_id
        ))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error actualizando ficha: {e}")
        return False
```

**Campos actualizados:**
- `institucion`: Nombre de la institución
- `email`: Email de contacto (si se encuentra)
- `telefono`: Teléfono (si se encuentra)
- `tiene_formulario`: Boolean (true/false/null)
- `canal_recomendado`: Canal sugerido
- `propuesta_comunicativa`: Mensaje personalizado
- `procesada`: Marcado como 'SI'
- `ultima_actualizacion`: Timestamp actual

#### 4.8 Función principal de enriquecimiento

```python
def enriquecer_fichas(openai_key=None, limite=10):
    """
    Función principal: Lee fichas no procesadas y las enriquece con ChatGPT.
    
    Args:
        openai_key (str): API key de OpenAI (opcional)
        limite (int): Máximo de fichas a procesar
    """
    api_key = openai_key or OPENAI_API_KEY
    
    print("🤖 INICIANDO ENRIQUECIMIENTO CON CHATGPT")
    print("=" * 60)
    
    # Leer fichas pendientes
    fichas = leer_fichas_pendientes(limite)
    print(f"📋 Encontradas {len(fichas)} fichas pendientes")
    
    if not fichas:
        print("✅ No hay fichas pendientes. Todo al día.")
        return
    
    procesadas = 0
    errores = 0
    
    for i, ficha in enumerate(fichas, 1):
        print(f"\n[{i}/{len(fichas)}] Procesando: {ficha['titulo'][:50]}...")
        
        # Enriquecer con ChatGPT
        datos = enriquecer_con_chatgpt(ficha, api_key)
        
        if datos:
            # Actualizar en BD
            if actualizar_ficha(ficha['id'], datos):
                print(f"  ✅ Enriquecida y actualizada")
                print(f"     Canal: {datos.get('canal_recomendado')}")
                print(f"     Propuesta: {datos.get('propuesta_comunicativa', '')[:60]}...")
                procesadas += 1
            else:
                errores += 1
        else:
            errores += 1
    
    print(f"\n{'=' * 60}")
    print("✅ ENRIQUECIMIENTO COMPLETADO")
    print(f"   Procesadas: {procesadas}")
    print(f"   Errores: {errores}")
    print("=" * 60)
```

#### 4.9 Output

```
🤖 INICIANDO ENRIQUECIMIENTO CON CHATGPT
============================================================
✅ Conectado a PostgreSQL (Render)
✅ API Key de OpenAI configurada
📋 Encontradas 2 fichas pendientes de procesar (límite: 2)

[1/2] Procesando: Study Abroad in Barcelona, Spain - Universitat Aut...
  URL: https://www.aifsabroad.com/programs/study-abroad-barcelona-s...
  ✅ Enriquecida y actualizada
     Canal: web
     Propuesta: Hola, estoy interesado en el programa de estudios en Barcelo...

[2/2] Procesando: Pallars | Barcelona Student Accommodation | aparto...
  URL: https://apartostudent.com/locations/barcelona/pallars...
  ✅ Enriquecida y actualizada
     Canal: web
     Propuesta: Hola, estoy interesado en la residencia estudiantil en Barce...

============================================================
✅ ENRIQUECIMIENTO COMPLETADO
   Procesadas: 2
   Errores: 0
============================================================
```

---

## 🔄 WORKFLOW COMPLETO INTEGRADO

### Script maestro:

```python
#!/usr/bin/env python3
"""
Workflow completo: Google Sheets → Búsqueda → Guardado → Enriquecimiento
"""

from leer_google_sheets import leer_keywords_desde_sheets
from modulo_busqueda_google import ejecutar_busqueda
from modulo_guardado_postgres import guardar_fichas, preparar_ficha
from modulo_enriquecimiento_postgres import enriquecer_fichas

def ejecutar_workflow_completo():
    """
    Ejecuta el workflow completo de captación de estudiantes.
    """
    print("=" * 70)
    print("🚀 WORKFLOW COMPLETO - CAPTACIÓN DE ESTUDIANTES")
    print("=" * 70)
    print()
    
    # PASO 1: Leer keywords de Google Sheets
    print("📍 PASO 1: LECTURA DE KEYWORDS (GOOGLE SHEETS)")
    print("-" * 70)
    keywords = leer_keywords_desde_sheets()
    print(f"✅ Leídas {len(keywords)} keywords\n")
    
    total_guardadas = 0
    
    # PASO 2 y 3: Para cada keyword, buscar y guardar
    for i, keyword in enumerate(keywords, 1):
        print(f"\n📍 KEYWORD {i}/{len(keywords)}: {keyword}")
        print("-" * 70)
        
        # Buscar en Google
        resultados = ejecutar_busqueda(keyword, num_resultados=10)
        print(f"  🔍 Encontrados {len(resultados)} resultados")
        
        if not resultados:
            continue
        
        # Preparar fichas
        fichas = [preparar_ficha(r, keyword) for r in resultados]
        
        # Guardar en PostgreSQL
        guardadas = guardar_fichas(fichas)
        total_guardadas += guardadas
        
        # Esperar 1 segundo entre keywords (rate limiting)
        time.sleep(1)
    
    print(f"\n{'=' * 70}")
    print(f"✅ BÚSQUEDA Y GUARDADO COMPLETADOS")
    print(f"   Total fichas guardadas: {total_guardadas}")
    print("=" * 70)
    print()
    
    # PASO 4: Enriquecer todas las fichas pendientes
    if total_guardadas > 0:
        print("📍 PASO 4: ENRIQUECIMIENTO CON CHATGPT")
        print("-" * 70)
        enriquecer_fichas(limite=total_guardadas)
    
    print("\n" + "=" * 70)
    print("✅ WORKFLOW COMPLETO FINALIZADO")
    print("=" * 70)

if __name__ == "__main__":
    ejecutar_workflow_completo()
```

---

## 📊 RESUMEN DE DATOS

### Datos iniciales (de Google):

| Campo | Fuente | Ejemplo |
|-------|--------|---------|
| titulo | Google Search | "Student Housing Madrid 2026" |
| url | Google Search | "https://example.com" |
| snippet | Google Search | "Looking for accommodation..." |
| keyword | Google Sheets | "student accommodation Madrid 2026" |
| dominio | Extraído de URL | "example.com" |
| fecha_detectada | Timestamp | "2025-12-22T10:30:45" |

### Datos enriquecidos (de ChatGPT):

| Campo | Fuente | Ejemplo |
|-------|--------|---------|
| institucion | ChatGPT | "Universidad Complutense" |
| email | ChatGPT | "contact@example.com" o null |
| telefono | ChatGPT | "+34 123 456 789" o null |
| tiene_formulario | ChatGPT | true/false |
| canal_recomendado | ChatGPT | "reddit", "web", "email" |
| propuesta_comunicativa | ChatGPT | "Hola, estoy interesado en..." |

### Datos de gestión:

| Campo | Valor por defecto | Descripción |
|-------|-------------------|-------------|
| estado | "pendiente" | Estado del contacto |
| procesada | "NO" → "SI" | Procesada por ChatGPT |
| prioridad | "Media" | Prioridad de contacto |
| fecha_contacto | null | Cuándo se contactó |
| fecha_creacion | CURRENT_TIMESTAMP | Cuándo se creó |
| ultima_actualizacion | CURRENT_TIMESTAMP | Última modificación |

---

## 🛡️ MANEJO DE ERRORES

### Errores comunes y soluciones:

| Error | Causa | Solución |
|-------|-------|----------|
| **Cuota Google API excedida** | Más de 100 búsquedas/día | Esperar 24h o usar otra API key |
| **Timeout OpenAI** | Respuesta > 30s | Reintentar con timeout mayor |
| **Duplicado en BD** | URL ya existe | Omitir (esperado) |
| **JSON malformado (ChatGPT)** | Respuesta con markdown | Limpiar automáticamente |
| **Error de conexión PostgreSQL** | Red/credenciales | Verificar DATABASE_URL |
| **Truncated INTEGER value** | Tipo de dato incorrecto | Normalizar boolean |

---

## 📈 MÉTRICAS Y LOGS

### Logs generados:

```
💾 Iniciando guardado de 10 fichas en PostgreSQL (Render)...
  ✅ Guardada: RND-20251222-748407b5
  ✅ Guardada: RND-20251222-74afeb9a
  ⏭️ Duplicado ignorado: https://example.com
  ❌ Error guardando https://broken.com: Connection timeout

📊 RESUMEN GUARDADO
  ✅ Nuevas: 8
  ⏭️ Duplicadas: 1
  ❌ Errores: 1
```

### Métricas clave:

- **Tasa de duplicados**: % de URLs ya existentes
- **Tasa de enriquecimiento**: % de fichas procesadas con éxito
- **Tiempo promedio**: Segundos por ficha
- **Costo OpenAI**: Dólares gastados en enriquecimiento

---

## 🔐 CREDENCIALES Y SEGURIDAD

### Variables de entorno necesarias:

```bash
# PostgreSQL (Render)
RENDER_DATABASE_URL="postgresql://user:pass@host/db"

# Google APIs
GOOGLE_API_KEY="AIzaSy..."
GOOGLE_CSE_ID="0679f1..."
GOOGLE_SHEETS_CREDENTIALS="path/to/credentials.json"

# OpenAI
OPENAI_API_KEY="sk-proj-..."
```

### Buenas prácticas:

1. **Nunca hardcodear credenciales** en el código
2. **Usar variables de entorno** o archivos .env
3. **Rotar API keys** periódicamente
4. **Limitar permisos** de service accounts
5. **Monitorear uso** de APIs para detectar abusos

---

## ✅ CHECKLIST DE VERIFICACIÓN

Antes de ejecutar el workflow completo:

- [ ] Google Sheets accesible con keywords
- [ ] Google Custom Search API configurada
- [ ] PostgreSQL de Render creado y accesible
- [ ] Tabla `fichas` creada con esquema correcto
- [ ] OpenAI API key válida con créditos
- [ ] Todas las dependencias Python instaladas (`psycopg2-binary`, `requests`)
- [ ] Variables de entorno configuradas
- [ ] Módulos Python en el PATH correcto

---

## 🎯 RESULTADO FINAL

Al completar el workflow, tendrás en PostgreSQL de Render:

- **Fichas completas** con todos los datos
- **Sin duplicados** (URLs únicas)
- **Enriquecidas con IA** (institución, canal, propuesta)
- **Listas para contactar** con propuestas personalizadas
- **Trazabilidad completa** (fecha creación, última actualización)

**Ejemplo de ficha completa:**

```json
{
  "id": "RND-20251222-748407b5",
  "tipo": "busqueda_google",
  "keyword": "student accommodation Madrid 2026",
  "url": "https://madrideasy.com/en",
  "titulo": "Apartments for students in Madrid",
  "snippet": "Find the best student accommodation...",
  "dominio": "madrideasy.com",
  "institucion": "Universidad Complutense",
  "email": null,
  "telefono": null,
  "tiene_formulario": true,
  "canal_recomendado": "web",
  "propuesta_comunicativa": "Hola, estoy interesado en alojamiento para estudiantes en Madrid para 2026...",
  "estado": "pendiente",
  "procesada": "SI",
  "prioridad": "Alta",
  "fecha_detectada": "2025-12-22T10:30:45",
  "fecha_creacion": "2025-12-22T10:30:46",
  "ultima_actualizacion": "2025-12-22T10:31:15"
}
```

---

**FIN DE LA DOCUMENTACIÓN**
