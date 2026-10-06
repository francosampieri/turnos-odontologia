# Turnos Odontología

Sistema de gestión de turnos para clínica odontológica (FastAPI + React, PostgreSQL 16).

## Requisitos

- Docker Desktop (Docker Engine + Compose v2)
- PowerShell 5.1 o superior

## Arranque

Desde la raíz del repositorio:

```powershell
Copy-Item .env.example .env
docker compose up --build
```

El primer arranque descarga imágenes y construye `api` y `web`; el orden es health-gated: `db` (sano) → `migrate` (termina OK) → `api` → `web`.

## Verificación de salud

En otra terminal (o con la pila corriendo en background: `docker compose up -d`):

```powershell
Invoke-WebRequest -Uri http://localhost:8000/api/v1/health -UseBasicParsing
```

Debe responder `200` con cuerpo `{"status":"ok","database":"ok"}`.

También:

- `http://localhost:8000/docs` → UI de documentación (sólo con `ENV=development`).
- `http://localhost:5173` → SPA (React servida por nginx).
- `http://localhost:5173/api/v1/health` → proxy de nginx hacia `api:8000` → `200`.

## Detener

```powershell
docker compose down
```

Para resetear la base (borra el volumen `pgdata`): `docker compose down -v`.

## Notas

- `.env` nunca se commitea (está en `.gitignore`); `.env.example` es la plantilla versionada.
- Redis está declarado en el Compose pero **no se usa** en el MVP (DD-06).
- Con `ENV=production` la API exige un `JWT_SECRET_KEY` real y deshabilita `/docs` y `/openapi.json`.
- Si recreás el contenedor `api`, reiniciá `web` (`docker compose restart web`): nginx resuelve `api:8000` al arrancar y si no se reinicia responde `502`.
