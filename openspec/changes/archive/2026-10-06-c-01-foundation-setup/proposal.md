# Proposal — C-01 `foundation-setup`

## Why

El proyecto no tiene todavía ningún código ni entorno ejecutable: no existe `docker-compose.yml`, `backend/`, `frontend/` ni `.env`. Todos los changes posteriores (empezando por C-02, que necesita la base corriendo y Alembic configurado) dependen de un entorno reproducible y de los esqueletos de las dos aplicaciones. C-01 es la raíz del árbol de dependencias de `CHANGES.md` y el GATE 0: sin él no hay dónde escribir ni cómo verificar nada.

## What Changes

- Se crea `docker-compose.yml` con los 5 servicios definidos en `knowledge-base/08_arquitectura_propuesta.md`: `db` (postgres:16-alpine + healthcheck `pg_isready`), `redis` (7-alpine, declarado **sin uso funcional** — DD-06), `api` (build `./backend`, puerto 8000), `web` (build `./frontend` con `build.args: VITE_API_URL`, `VITE_API_BASE` — sin `environment:`) y `migrate` (job `alembic upgrade head && python -m app.seed`, `depends_on: service_completed_successfully`), con orden de arranque `db` sano → `migrate` → `api` → `web`.
- Se crea `.env.example` **único en la raíz** (fuente única de variables: `DATABASE_URL`, `JWT_SECRET_KEY`, `JWT_ALGORITHM`, `JWT_EXPIRATION_MINUTES`, `CORS_ORIGINS`, `POSTGRES_*`, `TIMEZONE_CLINICA`, `ENV`, `VITE_*`, etc.) y `.gitignore` que excluye `.env`. No hay `backend/.env` ni `frontend/.env`.
- Se crea `backend/`: `Dockerfile` multi-stage, `requirements.txt` pineado (Python 3.12, FastAPI, Pydantic v2, SQLAlchemy 2.0 async, Alembic, asyncpg, pydantic-settings), `alembic.ini` + env de Alembic, y la estructura por capas `app/{api,domain,infrastructure}` con la regla de dependencia `api → domain → infrastructure` (sin lógica de negocio en routers).
- `backend/app/main.py`: instancia FastAPI, CORS con la **lista exacta** desde `CORS_ORIGINS` y `allow_credentials=False`, exception handlers globales, y `GET /api/v1/health` **público** con chequeo de conexión a la base.
- `backend/app/core/config.py`: `Settings` con pydantic-settings leyendo `os.environ` (sin `.env` propio); `JWT_SECRET_KEY` obligatoria cuando `ENV=production`.
- Se crea `frontend/`: `Dockerfile` multi-stage (build Vite + nginx en runtime), `nginx.conf` con proxy `/api` → `http://api:8000/api` **sin envsubst** (prefijo constante), proyecto Vite + React 18 + TypeScript estricto con `src/main.tsx` y `App.tsx` mínimos.
- Se crea `README.md` mínimo con el arranque por `docker compose up`.
- **No** se implementa ningún endpoint además de `health`, ninguna tabla, migración con tablas, auth, seed real ni funcionalidad de dominio (eso es C-02 en adelante).

## Capabilities

### New Capabilities

- `environment`: entorno reproducible con Docker Compose — servicios, orden de arranque health-gated, configuración desde el `.env` raíz (`build.args` para `VITE_*`, `environment:` para runtime), Redis declarado sin uso, y `.env.example`/`.gitignore` como única superficie de secretos.
- `api-foundation`: comportamiento base de la API bajo `/api/v1` — prefijo único, `GET /api/v1/health` público con verificación de conexión a PostgreSQL, CORS con lista explícita de orígenes y `allow_credentials=False`, `/docs` y `/openapi.json` deshabilitados en `ENV=production`, y cuerpo de error consistente para fallos no controlados.

### Modified Capabilities

(ninguna — `openspec list --specs` está vacío; este change introduce la primera spec)

## Impact

- **Archivos nuevos en la raíz**: `docker-compose.yml`, `.env.example`, `.gitignore`, `README.md`.
- **Código nuevo**: `backend/` (Dockerfile, requirements, alembic, `app/main.py`, `app/core/config.py`, esqueleto `app/{api,domain,infrastructure}`) y `frontend/` (Dockerfile, nginx.conf, proyecto Vite/React/TS).
- **API**: expone únicamente `GET /api/v1/health` (público). No modifica ninguna API existente (no hay ninguna).
- **Dependencias**: crea la base sobre la que trabajan los 18 changes restantes; GATE 1 desbloquea C-02.
- **Fuera de alcance deliberado**: modelos y migraciones con tablas (C-02), auth/RBAC (C-03), seed de datos (C-19; en C-01 sólo un stub idempotente vacío para que el job `migrate` del Compose no falle), tests de concurrencia, feature de frontend más allá del shell.
