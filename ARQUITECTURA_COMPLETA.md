# 🏗️ Arquitectura Completa del Sistema de Captación de Estudiantes

**Fecha de documentación:** 2024-12-22  
**Versión:** 1.0  
**Proyecto:** Dashboard Captación Estudiantes

---

## 📋 Índice

1. [Visión General](#visión-general)
2. [Flujo de Datos Completo](#flujo-de-datos-completo)
3. [Componentes del Backend](#componentes-del-backend)
4. [Esquema de Datos](#esquema-de-datos)
5. [Componentes del Frontend](#componentes-del-frontend)
6. [Credenciales y Configuración](#credenciales-y-configuración)
7. [Limitaciones Conocidas](#limitaciones-conocidas)

---

## 🎯 Visión General

El sistema automatiza la detección de oportunidades de captación de estudiantes internacionales mediante:
- Lectura de señales de búsqueda desde Google Sheets
- Búsqueda automatizada en Google Custom Search
- Procesamiento y normalización de resultados
- Almacenamiento en **PostgreSQL LOCAL** (dentro del proyecto)
- Visualización y gestión en Dashboard web

**⚠️ IMPORTANTE:** La base de datos objetivo es **PostgreSQL local** (no Supabase externa) para evitar problemas de DNS en producción y tener todo el stack contenido en la imagen Docker que se desplegará en Render.

---

## 🔄 Flujo de Datos Completo

```
┌─────────────────────┐
│  Google Sheets      │
│  (Signals Database) │
│  Pestaña: Signals   │
└──────────┬──────────┘
           │
           │ (1) Lee 53 señales activas
           ↓
┌─────────────────────────────┐
│  modulo_lectura_sheets.py   │
│  - Filtra señales activas   │
│  - Devuelve lista queries   │
└──────────┬──────────────────┘
           │
           │ (2) Por cada señal
           ↓
┌─────────────────────────────┐
│  modulo_busqueda_google.py  │
│  - Google Custom Search API │
│  - Max 10 resultados/query  │
└──────────┬──────────────────┘
           │
           │ (3) Resultados crudos
           ↓
┌─────────────────────────────┐
│  modulo_procesamiento.py    │
│  - Normaliza a JSON         │
│  - Extrae metadatos         │
│  - Genera IDs únicos        │
└──────────┬──────────────────┘
           │
           │ (4) Fichas normalizadas
           ↓
┌─────────────────────────────┐
│  modulo_guardado.py         │
│  - Verifica duplicados      │
│  - Inserta en PostgreSQL    │
└──────────┬──────────────────┘
           │
           │ (5) Datos persistidos
           ↓
┌─────────────────────────────┐
│  PostgreSQL LOCAL           │
│  Tabla: fichas              │
│  (Dentro del proyecto)      │
└──────────┬──────────────────┘
           │
           │ (6) Frontend consulta
           ↓
┌─────────────────────────────┐
│  Dashboard React            │
│  - Visualización            │
│  - Filtros                  │
│  - Gestión de estado        │
└─────────────────────────────┘
```

---

## 🔧 Componentes del Backend

### 1. `modulo_lectura_sheets.py`

**Función:** `obtener_senales(api_key)`

**Input:**
- `api_key` (str): Google API Key

**Output:**
- Lista de diccionarios:
  ```python
  [
    {
      'query': 'housing coordinator IE Madrid 2026',
      'origen': 'Signals_Sheet',
      'fila': 2
    },
    ...
  ]
  ```

**Configuración:**
- `SHEET_ID`: `1-6e0U1SATcgs2V8u2fOoDoKIrLjzwJi8GxJtUwy9t_U`
- `RANGE_NAME`: `Signals!A2:E`

**Lógica:**
- Lee columnas: [ID, Señal, Tipo, Activa, Notas]
- Filtra solo filas donde `Activa == 'SÍ'`
- Devuelve el texto de la columna "Señal"

---

### 2. `modulo_busqueda_google.py`

**Función:** `ejecutar_busqueda(query, num_resultados=10)`

**Input:**
- `query` (str): Término de búsqueda
- `num_resultados` (int): Cantidad deseada (máx 10)

**Output:**
- Lista de diccionarios:
  ```python
  [
    {
      'titulo': 'Student Housing | IE University',
      'url': 'https://www.ie.edu/housing',
      'snippet': 'We help international students...',
      'fecha_descubrimiento': '2024-12-22T10:30:00'
    },
    ...
  ]
  ```

**Credenciales:**
- `GOOGLE_API_KEY`: `AIzaSyBk5KghTy3GkOMbCdZDcduaeyrQaaP_KcA`
- `GOOGLE_CSE_ID`: `0679f1599bd26402e`

**Limitaciones:**
- Cuota gratuita: 100 búsquedas/día
- Máximo 10 resultados por búsqueda
- Rate limit: 1 segundo entre búsquedas (implementado en orquestador)

---

### 3. `modulo_procesamiento.py`

**Función:** `normalizar_resultados(resultados_crudos, query_origen, prioridad_origen='Media')`

**Input:**
- `resultados_crudos` (list): Salida de `ejecutar_busqueda()`
- `query_origen` (str): Query original
- `prioridad_origen` (str): Alta/Media/Baja

**Output:**
- Lista de fichas normalizadas (ver esquema completo abajo)

**Lógica interna:**
- `extraer_dominio(url)`: Limpia dominio (quita www.)
- `detectar_plataforma(url, dominio)`: Identifica Reddit, Facebook, LinkedIn, etc.
- `extraer_username(url, plataforma)`: Extrae usuario de redes sociales
- `extraer_subreddit(url, plataforma)`: Extrae subreddit si es Reddit
- Genera ID único: `SIG-YYYYMMDD-xxxxxxxx`
- Elimina duplicados dentro del mismo batch (por URL)

---

### 4. `modulo_guardado.py` (PENDIENTE DE MIGRACIÓN)

**Función:** `guardar_fichas(fichas)`

**Input:**
- `fichas` (list): Salida de `normalizar_resultados()`

**Output:**
- `int`: Número de fichas guardadas exitosamente

**Lógica:**
- `verificar_duplicado(conn, url)`: Consulta si URL ya existe en PostgreSQL local
- Si es duplicado → lo ignora
- Si es nuevo → lo inserta
- Devuelve estadísticas: guardadas, duplicadas, errores

**Estado actual:**
- ⚠️ **Archivo actual:** `modulo_guardado_supabase.py` (conecta a Supabase externa)
- ✅ **Migración pendiente:** Adaptar para conectar a PostgreSQL local usando variables de entorno del proyecto Manus

**Conexión PostgreSQL local:**
- Variables de entorno automáticas al activar `web-db-user`:
  - `DATABASE_URL`: Cadena de conexión completa
  - `PGHOST`, `PGPORT`, `PGDATABASE`, `PGUSER`, `PGPASSWORD`

---

### 5. `orquestador_maestro.py`

**Función:** `ejecutar_flujo_completo()`

**Flujo:**
1. Lee señales de Google Sheets
2. Por cada señal:
   - Ejecuta búsqueda en Google
   - Procesa resultados
   - Guarda en Supabase
   - Espera 1 segundo (rate limit)
3. Reporta estadísticas finales

**Última ejecución exitosa:**
- Fecha: 2024-12-22
- Señales procesadas: 53
- Fichas nuevas guardadas: 236
- Duplicados ignorados: ~30

---

## 📊 Esquema de Datos (24 campos)

### Tabla: `fichas`

| Campo | Tipo | Descripción | Origen |
|-------|------|-------------|--------|
| `id` | TEXT | ID único (SIG-YYYYMMDD-xxxxxxxx) | Generado |
| `tipo` | TEXT | Tipo de señal (ej: "búsqueda") | Fijo |
| `keyword` | TEXT | Query original de búsqueda | Input |
| `url` | TEXT | URL del resultado | Google API |
| `titulo` | TEXT | Título del resultado | Google API |
| `snippet` | TEXT | Fragmento de texto | Google API |
| `dominio` | TEXT | Dominio limpio (sin www) | Extraído |
| `institucion` | TEXT | Nombre institución | NULL (IA) |
| `email` | TEXT | Email de contacto | NULL (IA) |
| `telefono` | TEXT | Teléfono | NULL (IA) |
| `tiene_formulario` | BOOLEAN | Tiene formulario web | NULL (IA) |
| `plataforma_social` | TEXT | Reddit/Facebook/LinkedIn/Web | Detectado |
| `username` | TEXT | Usuario extraído | Extraído |
| `subreddit` | TEXT | Subreddit (si Reddit) | Extraído |
| `grupo_facebook` | TEXT | Grupo de Facebook | NULL |
| `fecha_detectada` | DATE | Fecha de detección (YYYY-MM-DD) | Generado |
| `prioridad` | TEXT | Alta/Media/Baja | Input |
| `propuesta_comunicativa` | TEXT | Mensaje sugerido | NULL (IA) |
| `canal_recomendado` | TEXT | Canal sugerido | NULL (IA) |
| `estado` | TEXT | pendiente/contactado/descartado | Fijo |
| `procesada` | TEXT | SI/NO (si pasó por IA) | Fijo |
| `fecha_contacto` | DATE | Fecha de contacto | NULL |
| `fecha_creacion` | TIMESTAMP | Timestamp creación (ISO) | Generado |
| `ultima_actualizacion` | TIMESTAMP | Timestamp modificación (ISO) | Generado |

**Campos NULL (a llenar por IA en futuras fases):**
- `institucion`, `email`, `telefono`, `tiene_formulario`
- `propuesta_comunicativa`, `canal_recomendado`
- `grupo_facebook`, `fecha_contacto`

---

## 🖥️ Componentes del Frontend

### Ubicación
`/home/ubuntu/dashboard-captacion/client/`

### Archivo Principal
`client/src/pages/Home.tsx`

### Funcionalidades

#### 1. Autenticación
- PIN de acceso: `MADRID2025`
- Almacenamiento en `localStorage`

#### 2. Visualización
- **Vista Grid**: Tarjetas expandidas con toda la información
- **Vista List**: Tabla compacta

#### 3. Filtros
- Búsqueda por texto (título, institución, canal)
- Filtro por estado (pendiente/contactado/descartado)
- Filtro por prioridad (alta/media/baja)

#### 4. Acciones
- **Contactar**: Abre URL/email/red social según canal recomendado
- **Marcar como Contactado**: Actualiza estado en BD
- **Marcar como Descartado**: Actualiza estado en BD
- **Buscar Nuevas Fichas**: Llama al endpoint `/api/run-search`

#### 5. Estadísticas
- Total de fichas
- Pendientes
- Contactados
- Descartados

### Estado Actual
- **Error de compilación** en línea 162 (sintaxis JSX)
- Conexión a Supabase configurada pero bloqueada por el error

---

## 🔐 Credenciales y Configuración

### Google Sheets API
- **API Key**: `AIzaSyBk5KghTy3GkOMbCdZDcduaeyrQaaP_KcA`
- **Sheet ID**: `1-6e0U1SATcgs2V8u2fOoDoKIrLjzwJi8GxJtUwy9t_U`
- **Pestaña**: `Signals`
- **Rango**: `A2:E` (salta encabezados)

### Google Custom Search
- **API Key**: `AIzaSyBk5KghTy3GkOMbCdZDcduaeyrQaaP_KcA` (misma)
- **CSE ID**: `0679f1599bd26402e`
- **Cuota**: 100 búsquedas/día (gratuita)

### PostgreSQL Local (Objetivo Final)
- **Proveedor**: Manus `web-db-user` feature
- **Conexión**: Variables de entorno automáticas (`DATABASE_URL`)
- **Tabla**: `fichas` (24 campos)
- **Estado**: Pendiente de activación y migración

### Supabase (Temporal - Solo para pruebas iniciales)
- **URL**: `https://imuhtilqwbqjuuvztfjp.supabase.co`
- **Anon Key**: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImltdWh0aWxxd2JxanV1dnp0ZmpwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjYwNzI5MzEsImV4cCI6MjA4MTY0ODkzMX0.aXHKbUUnzOXuiCbx3OalgHPXEQ2rbiw0eDG56y_MBU4`
- **Tabla**: `fichas`
- **Estado**: 236 registros de prueba (NO se usará en producción)
- **Razón de cambio**: Problemas de DNS en sandbox/Render → migración a PostgreSQL local

---

## ⚠️ Limitaciones Conocidas

### Backend
1. **Migración pendiente a PostgreSQL local**: El código actual conecta a Supabase externa, necesita adaptarse para usar PostgreSQL local del proyecto Manus
2. **DNS intermitente en sandbox**: Razón principal del cambio a PostgreSQL local (evitar dependencias externas)
3. **Cuota Google Search**: 100 búsquedas/día → con 53 señales, se pueden hacer ~1.8 ejecuciones completas por día
4. **Sin procesamiento IA**: Los campos `institucion`, `email`, `propuesta_comunicativa`, etc. quedan NULL

### Frontend
1. **Error de sintaxis**: Línea 162 de `Home.tsx` impide compilación
2. **Sin polling**: El botón "Buscar Nuevas Fichas" no actualiza automáticamente la lista (requiere refresh manual)
3. **Sin paginación**: Si hay >100 fichas, la carga puede ser lenta

### General
1. **Sin tests automatizados**: No hay cobertura de pruebas unitarias
2. **Sin CI/CD**: Despliegue manual
3. **Sin logs persistentes**: Los logs del orquestador solo están en consola

---

## 📝 Notas Finales

Este documento refleja el estado **real y verificado** del código al 22 de diciembre de 2024.

**Próximos pasos planificados (en orden):**
1. ✅ Activar PostgreSQL local (`web-db-user` feature)
2. ✅ Crear tabla `fichas` con esquema de 24 campos
3. ✅ Migrar `modulo_guardado_supabase.py` → `modulo_guardado.py` (PostgreSQL local)
4. ✅ Ejecutar orquestador para poblar BD local
5. ✅ Actualizar frontend para leer de PostgreSQL local
6. ✅ Mock de datos para validación rápida (opcional)
7. ✅ Dockerización completa (frontend + backend + PostgreSQL)
8. ✅ Despliegue en Render con imagen Docker

---

**Generado automáticamente desde el código fuente.**
