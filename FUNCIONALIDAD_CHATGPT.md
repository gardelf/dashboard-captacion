# 🤖 FUNCIONALIDAD CHATGPT - RECUPERADA DEL HISTORIAL

## 📋 RESUMEN EJECUTIVO

ChatGPT se usaba para **enriquecer las fichas** después de guardarlas en la base de datos. El proceso era:

1. **Búsqueda en Google** → Guarda fichas con `procesada = 'NO'` y `propuesta_comunicativa = NULL`
2. **Análisis con ChatGPT** → Lee fichas no procesadas, llama a OpenAI, actualiza con datos extraídos
3. **Resultado** → Fichas con `procesada = 'SI'` y todos los campos NULL rellenados

---

## 🔄 FLUJO COMPLETO (Según `run_search_and_analysis.py`)

### FASE 1: BÚSQUEDA
- Lee señales de Google Sheets
- Busca en Google Custom Search
- Construye fichas con campos básicos:
  - `url`, `titulo`, `descripcion`, `institucion` (de la señal origen)
  - `prioridad`, `fecha_evento`, `estado = 'pendiente'`
  - **`procesada = False`** ← Marca para ChatGPT
  - **`propuesta_comunicativa = None`** ← ChatGPT lo llenará

### FASE 2: ANÁLISIS CON CHATGPT
- **Archivo:** `analizar_con_chatgpt.py`
- **Estado actual:** Solo tiene un placeholder (NO implementado)
- **Función:** `procesar_fichas()`

**Lo que DEBERÍA hacer (según el código del frontend):**
1. Leer fichas con `procesada = False`
2. Por cada ficha:
   - Enviar `snippet` + `url` + `titulo` a ChatGPT
   - Pedir que extraiga:
     - `institucion` (nombre completo de la universidad/organización)
     - `email` (si lo encuentra en el snippet o URL)
     - `telefono` (si lo encuentra)
     - `tiene_formulario` (boolean: si la URL parece ser un formulario)
     - **`propuesta_comunicativa`** ← **CAMPO CLAVE**
     - `canal_recomendado` (email/reddit/whatsapp/form)
   - Actualizar la ficha con `procesada = True`

---

## 💬 PROPUESTA COMUNICATIVA - USO EN EL FRONTEND

### Dónde se usa (según `Home.tsx`):

#### 1. **Vista de Tabla** (línea 358)
```tsx
<div className="truncate max-w-[250px] text-sm text-slate-500 font-mono">
  {ficha.propuesta_comunicativa}
</div>
```
- Se muestra truncada en la columna de la tabla
- Tiene botón de copiar al portapapeles

#### 2. **Vista de Tarjetas** (línea 478)
```tsx
<p className="whitespace-pre-wrap line-clamp-4 hover:line-clamp-none transition-all">
  {ficha.propuesta_comunicativa || "Sin propuesta comunicativa generada."}
</p>
```
- Se muestra en un recuadro gris
- Expandible al hacer hover
- Con botón de copiar

#### 3. **Acción "Contactar"** (líneas 293-306, 405-419)

**Para Email:**
```tsx
const subject = "Alojamiento para estudiantes internacionales en Madrid";
const body = encodeURIComponent(ficha.propuesta_comunicativa);
window.open(`https://mail.google.com/mail/?view=cm&fs=1&to=${ficha.email}&su=${subject}&body=${body}`, '_blank');
```
→ Abre Gmail con la propuesta como cuerpo del email

**Para Reddit:**
```tsx
copyToClipboard(ficha.propuesta_comunicativa);
window.open(ficha.url, '_blank');
toast.info("Propuesta copiada. Pegala en Reddit.");
```
→ Copia la propuesta y abre Reddit para que el usuario la pegue

**Para WhatsApp:**
```tsx
const text = encodeURIComponent(ficha.propuesta_comunicativa);
window.open(`https://wa.me/${ficha.telefono}?text=${text}`, '_blank');
```
→ Abre WhatsApp con la propuesta pre-escrita

**Para Formularios:**
```tsx
copyToClipboard(ficha.propuesta_comunicativa);
window.open(ficha.url, '_blank');
toast.info("Propuesta copiada. Pegala en el formulario.");
```
→ Copia la propuesta y abre la URL del formulario

---

## 🎯 QUÉ DEBE GENERAR CHATGPT

### Prompt Inferido (basado en el uso del frontend):

**Input a ChatGPT:**
- `titulo`: Título del resultado de Google
- `snippet`: Fragmento de texto de Google
- `url`: URL del resultado
- `plataforma_social`: Reddit/Facebook/LinkedIn/Web
- `keyword`: Query de búsqueda original

**Output esperado de ChatGPT:**

```json
{
  "institucion": "IE University",
  "email": "housing@ie.edu",
  "telefono": "+34912345678",
  "tiene_formulario": true,
  "canal_recomendado": "email",
  "propuesta_comunicativa": "Hola,\n\nSoy estudiante internacional que empezará en IE Madrid en septiembre de 2026 y estoy buscando alojamiento. Vi que ofrecen servicios de housing y me gustaría saber más sobre las opciones disponibles.\n\n¿Podrían ayudarme?\n\nGracias"
}
```

### Características de la `propuesta_comunicativa`:

1. **Personalizada** según el contexto (universidad, plataforma, tipo de señal)
2. **Breve pero educada** (2-4 líneas)
3. **Menciona el año 2026** (contexto de la búsqueda)
4. **Tono amigable** pero profesional
5. **Adaptada al canal**:
   - Email: más formal
   - Reddit: más casual, primera persona
   - WhatsApp: muy breve
   - Formulario: directo al grano

---

## 🚧 ESTADO ACTUAL

### ❌ NO Implementado:
- Llamada real a OpenAI API
- Prompt de ChatGPT
- Lógica de actualización de fichas procesadas

### ✅ SÍ Implementado:
- Frontend espera y usa `propuesta_comunicativa`
- Flujo de guardado marca `procesada = False`
- Estructura de datos preparada

---

## 📝 PROMPT SUGERIDO PARA CHATGPT

```
Eres un asistente que ayuda a estudiantes internacionales a encontrar alojamiento en Madrid.

Analiza el siguiente resultado de búsqueda y extrae:

1. **institucion**: Nombre completo de la universidad u organización (null si no es identificable)
2. **email**: Email de contacto si aparece en el snippet o puedes inferirlo (null si no)
3. **telefono**: Teléfono si aparece (null si no)
4. **tiene_formulario**: true si la URL parece ser un formulario de contacto, false si no
5. **canal_recomendado**: "email" si hay email, "reddit" si es Reddit, "whatsapp" si hay teléfono, "form" si tiene formulario, "web" por defecto
6. **propuesta_comunicativa**: Un mensaje breve (2-4 líneas) que un estudiante podría enviar para contactar. Debe:
   - Ser amigable y educado
   - Mencionar que es estudiante internacional que llegará en 2026
   - Preguntar por alojamiento
   - Adaptarse al canal (más formal para email, casual para Reddit)

**Input:**
- Título: {titulo}
- Snippet: {snippet}
- URL: {url}
- Plataforma: {plataforma_social}
- Keyword de búsqueda: {keyword}

Devuelve SOLO un JSON válido con los 6 campos.
```

---

## 🔧 IMPLEMENTACIÓN PENDIENTE

### Archivo a crear: `modulo_enriquecimiento_chatgpt.py`

**Función principal:** `enriquecer_fichas()`

**Pseudocódigo:**
```python
def enriquecer_fichas():
    # 1. Conectar a PostgreSQL local
    conn = conectar_bd_local()
    
    # 2. Leer fichas no procesadas
    fichas = conn.execute("SELECT * FROM fichas WHERE procesada = 'NO' LIMIT 10")
    
    # 3. Por cada ficha
    for ficha in fichas:
        # 4. Construir prompt
        prompt = construir_prompt(ficha)
        
        # 5. Llamar a OpenAI
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ]
        )
        
        # 6. Parsear JSON
        datos = json.loads(response.choices[0].message.content)
        
        # 7. Actualizar ficha
        conn.execute("""
            UPDATE fichas SET
                institucion = %s,
                email = %s,
                telefono = %s,
                tiene_formulario = %s,
                canal_recomendado = %s,
                propuesta_comunicativa = %s,
                procesada = 'SI'
            WHERE id = %s
        """, (datos['institucion'], datos['email'], ..., ficha['id']))
        
        # 8. Rate limit (evitar saturar OpenAI)
        time.sleep(1)
```

---

## 💰 COSTOS ESTIMADOS (OpenAI)

- **Modelo recomendado:** GPT-4o-mini (más barato, suficiente para esta tarea)
- **Tokens por ficha:** ~500 input + ~200 output = 700 tokens
- **Costo por ficha:** ~$0.0007 USD
- **Para 236 fichas:** ~$0.17 USD
- **Para 500 fichas/día:** ~$0.35 USD/día

---

## ✅ PRÓXIMOS PASOS

1. Activar PostgreSQL local
2. Migrar módulo de guardado
3. **Crear `modulo_enriquecimiento_chatgpt.py`**
4. Integrar en el orquestador (opcional: como paso separado o automático)
5. Configurar OpenAI API Key
6. Probar con 5-10 fichas
7. Ejecutar en batch completo

---

**Generado desde el análisis del código fuente y frontend.**
