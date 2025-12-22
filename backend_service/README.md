# Backend de Búsqueda - Dashboard Captación

Este es el motor de búsqueda que ejecuta los scripts de Python para encontrar nuevas fichas.

## Cómo desplegar en Render

1.  Sube todos estos archivos a un repositorio de GitHub.
2.  Ve a [Render.com](https://render.com) y crea un **New Web Service**.
3.  Conecta tu repositorio de GitHub.
4.  Render detectará automáticamente el archivo `Dockerfile`.
5.  Dale a **Deploy**.

## Configuración
No necesitas configurar variables de entorno porque las claves ya están incluidas en el script para asegurar que funcione sin errores.

## Endpoints
- `POST /api/run-search`: Inicia la búsqueda.
- `GET /api/status`: Consulta el estado de la búsqueda.
