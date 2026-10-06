# Design — C-01 `foundation-setup`

## Context

El repo está verde: sólo existen `knowledge-base/`, `CHANGES.md`, la configuración de OpenSpec y las carpetas de tooling; no hay `backend/`, `frontend/`, `docker-compose.yml` ni `.env`. La motivación y el alcance están en `proposal.md`; los contratos de comportamiento en `specs/environment/spec.md` y `specs/api-foundation/spec.md`. Las restricciones que moldean este diseño son el stack cerrado (R-1 / DD-01), la regla de capas `api → domain → infrastructure`, la fuente única de configuración en el `.env` raíz (KB `08_arquitectura_propuesta.md` §Variables de entorno) y el contrato exacto de servicios del Compose definido en `CHANGES.md` §[C-01].

## Goals / Non-Goals

**Goals:**

- `docker compose up` levanta las 5 aplicaciones descritas en la KB con el orden health-gated.
- Esqueleto de backend por capas, con `GET /api/v1/health` real (verifica conexión a PostgreSQL) y configuración por `pydantic-settings`.
- Esqueleto de frontend Vite + React + TypeScript compilado a imagen nginx con proxy `/api`.
- Alembic instalado y funcional (aún sin versiones) para que C-02 sólo agregue `versions/001`.
- Verificación por tests desde el primer change (patrón TDD que los cambios siguientes heredan).

**Non-Goals:**

- Modelos SQLAlchemy, tablas, migraciones con DDL ni los 3 `EXCLUDE USING gist` (C-02).
- Auth, `require_role`, catálogo de errores de dominio completo (C-03).
- Seed real de datos (C-19) — sólo el stub descrito en Decisión D-1.
- Cualquier pantalla de frontend más allá de `App.tsx` mínimo, ni `api/client.ts` (C-15).
- Uso funcional de Redis (prohibido por AGENTS.md / DD-06).

## Decisions

### D-1 — Stub de `app/seed.py` en C-01 (conflicto CHANGES ↔ KB)

`CHANGES.md` §[C-01] exige que el servicio `migrate` ejecute `alembic upgrade head && python -m app.seed`, pero `app/seed.py` con datos reales se crea recién en C-19. Sin el módulo, el job falla y bloquea el arranque de `api` (`service_completed_successfully`).

- **Decisión**: crear en C-01 un `backend/app/seed.py` idempotente **sin-op** (docstring que explica que la siembra real llega en C-19 y ejecuta sin error). El contrato del Compose se cumple desde el día 1 y C-19 sólo reemplaza el cuerpo.
- **Alternativa descartada**: quitar `python -m app.seed` del comando hasta C-19 — rompe el contrato literal de `CHANGES.md` y de la tabla de servicios de la KB, y obliga a retocar el Compose dos veces.
- ⚠️ **Flag para revisión**: es una extrapolación mínima del scope de C-01; si el docente prefiere el Compose literal sin el stub, la variante es sacar `&& python -m app.seed` del comando hasta C-19.

### D-2 — Health check de BD sin pisar el alcance de C-02

`GET /api/v1/health` debe verificar la conexión a PostgreSQL, pero `infrastructure/db/base.py` + `session.py` (engine, `get_db`) son alcance de C-02.

- **Decisión**: en C-01, `app/infrastructure/db/check.py` abre una conexión breve con `asyncpg` directo (`SELECT 1`) usando `DATABASE_URL` y la cierra; el router `health` la invoca. Es una pieza mínima, sin sessionmaker ni modelos.
- **Alternativa descartada**: crear ya el engine/sessionmaker de C-02 en C-01 (duplica alcance del change CRÍTICO siguiente).
- **Consecuencia**: en C-02 el refactor unificará este chequeo sobre el engine compartido — queda anotado como punto de fusión, no como deuda.

### D-3 — Alembic funcional sin versiones

- `alembic.ini` + `alembic/env.py` (template **async**: `async_engine_from_config` + `asyncpg`) leyendo `sqlalchemy.url` desde `DATABASE_URL` en el entorno, sin `.env` propio.
- `alembic upgrade head` con `versions/` vacío es no-op → el job `migrate` pasa limpio en C-01.
- **Alternativa descartada**: template sync con driver `psycopg` — introduciría un segundo driver fuera del stack (asyncpg es el driver único, `02_descripcion_general.md`).

### D-4 — Compose: contrato de servicios y puertos

- `db`: `postgres:16-alpine`, healthcheck `pg_isready`, volumen `pgdata`, puerto `5432` **publicado en host sólo si** hace falta para el desarrollo del TP (la KB recomienda no publicarlo en despliegue real; se publica `5432:5432` para depuración local desde el host, documentado como decisión de desarrollo).
- `redis`: `redis:7-alpine` con `--save "" --appendonly no`, sin puertos publicados, sin cliente en el backend.
- `web`: `ports: ["5173:80"]` (fragmento de la KB) — nginx de producción atiende en el 5173 del host. El dev server de Vite (`npm run dev`) queda fuera del Compose como opción opcional.
- `VITE_API_URL=http://localhost:8000/api/v1` (el navegador hablando directo con 8000 en dev de bundle) y `VITE_API_BASE=/api/v1` (prefijo constante del proxy nginx) — ambas por `build.args`, nunca `environment:`.
- ⚠️ **Flag menor**: la tabla de servicios de la KB dice "5173 en desarrollo, 80 en producción" mientras su propio fragmento YAML usa `5173:80`; se adopta el fragmento (`5173:80`).

### D-5 — CORS y exception handlers en `main.py`

- `CORS_ORIGINS` llega como lista separada por comas desde el env; se parsea en `Settings` a `list[str]`, se aplica `allow_origins=` exacto (sin comodín) y `allow_credentials=False`.
- Dos exception handlers globales en C-01: `Exception` → `500` JSON genérico (detalle al log, nunca al cliente) y `HTTPException` 404 → cuerpo JSON. El catálogo de errores de dominio (401/403/409/422 con códigos `RN-xx`) entra en C-03 (`app/core/errors.py`).
- `docs_url`/`openapi_url` se anulan cuando `ENV=production`; `JWT_SECRET_KEY` valida en startup en producción (valor de ejemplo → `RuntimeError` al arrancar).

### D-6 — Dockerfiles multi-stage

- **Backend**: stage `builder` (`python:3.12-slim`) con `pip install --no-cache-dir -r requirements.txt` a venv; stage runtime final copia sólo el venv + `app/`, `USER` no-root, `HEALTHCHECK` contra `GET /api/v1/health`, `.dockerignore` para `.git`, tests y `__pycache__`. `CMD` uvicorn con `--host 0.0.0.0 --port 8000`.
- **Frontend**: stage `builder` (`node:22-alpine`, `npm ci` + `npm run build` con `ARG VITE_*`) y runtime `nginx:alpine` sólo con `dist/` + `nginx.conf` (proxy `/api` → `http://api:8000/api`, sin `envsubst`).
- Ambos con `COPY --chown`, `RUN` combinados con `&&` y tags exactos de imagen (nunca `python` pelado).

### D-7 — Estrategia de pruebas de C-01 (patrón para el resto)

- `backend/tests/` con `pytest` + `pytest-asyncio` + `httpx.AsyncClient` sobre la app (sin red).
- Suites: parsing de `Settings` (lista CORS, producción sin secreto → error de arranque), `GET /api/v1/health` (mockeando el check de conexión: OK → 200, caída → 503), gating de `/docs` por `ENV`, respuesta 404 JSON, y que la app no declare rutas fuera de `/api/v1`.
- Cada task de `tasks.md` sigue TDD: test rojo → implementación mínima → verde. No se testea la capa interna, sólo comportamiento observable (seams públicos: HTTP y `Settings`).

## Risks / Trade-offs

- [El stub de seed (D-1) se sale literalmente del scope de C-01] → mínimo y reversible; se marca en la revisión del change; alternativa documentada en D-1.
- [El health check con `asyncpg` crudo (D-02) diverge del engine de C-02] → es una sola pieza aislada en `infrastructure/db/check.py`; C-02 la sustituye por el engine compartido en su propio change.
- [`web` en `5173` sirve bundle de producción, no el dev server de Vite] → comportamiento idéntico al usuario (mismo puerto); el dev server queda documentado como opcional fuera de Compose.
- [Puerto `5432` publicado en host] → sólo superficie local de desarrollo; se documenta que en despliegue real no se publica (KB §Seguridad).
- [C-01 no tiene dependencias pero `CHANGES.md` línea 540 dice "primer change… después de cerrar PA-13"] → la tabla GATE y el árbol de dependencias indican que PA-13 bloquea **C-02**; el scope de C-01 no toca el modelo, así que PA-13 no afecta este change. **Flag abierto para el docente** (no resuelto acá).

## Migration Plan

No hay datos previos: es el change inicial. Despliegue = `cp .env.example .env && docker compose up --build`. Rollback = `git revert` del commit; ninguna migración ni volumen de datos que revertir (el volumen `pgdata` se descarta con `docker compose down -v` si hace falta volver a cero).

## Open Questions

- **PA-13 y el GATE**: confirmar con el docente si `CHANGES.md` línea 540 ("C-01… después de cerrar PA-13") es un residuo editorial o una restricción real; el árbol de dependencias y la tabla GATE dicen que PA-13 sólo bloquea C-02.
- **Publicación del puerto 5432**: si el entorno de evaluación exige Compose sin puertos de BD expuestos, cambiar a sólo-red-interna (afecta desarrollo local, no specs).
