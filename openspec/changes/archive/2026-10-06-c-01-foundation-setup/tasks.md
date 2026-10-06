# Tasks â€” C-01 `foundation-setup`

## 1. Esqueleto del backend: configuraciÃ³n y app base

- [x] 1.1 Crear `backend/requirements.txt` con las versiones pineadas del stack (Python 3.12, FastAPI â‰¥0.115, Pydantic v2, SQLAlchemy 2.0, Alembic, asyncpg, pydantic-settings, pytest, pytest-asyncio, httpx) y la estructura `backend/app/{api,domain,infrastructure}` con `__init__.py`; verificar que `pip install -r requirements.txt` completa sin errores en `python:3.12-slim` y que **no** aparece ningÃºn cliente Redis ni tecnologÃ­a fuera de stack (`Select-String -Path backend\requirements.txt -Pattern "redis|celery|prisma"` â†’ sin coincidencias)
- [x] 1.2 (TDD) Escribir el test rojo `backend/tests/test_config.py` para `Settings`: `CORS_ORIGINS="http://a, http://b"` se parsea a lista exacta de 2 orÃ­genes sin espacios; `ENV=development` y `ENV=production` se aceptan; ejecutar `pytest tests/test_config.py` y verlo fallar
- [x] 1.3 Implementar `backend/app/core/config.py` (pydantic-settings leyendo `os.environ`, sin `.env` propio) hasta que los tests de 1.2 pasen: `pytest tests/test_config.py` en verde
- [x] 1.4 (TDD) Test rojo: con `ENV=production` y `JWT_SECRET_KEY` vacÃ­a o en su valor de ejemplo, la creaciÃ³n de `Settings` lanza error explÃ­cito de arranque; con `ENV=development` no falla; verificar el fallo con `pytest`
- [x] 1.5 Implementar la guarda de startup de 1.4 en `app/core/config.py` hasta que `pytest tests/test_config.py` pase en verde
- [x] 1.6 (TDD) Test rojo `backend/tests/test_app_base.py`: la app no declara rutas fuera de `/api/v1`; `GET /api/v1/ruta-inexistente` devuelve `404` con cuerpo JSON; `GET /docs` responde con `ENV=development` y `404` con `ENV=production`; ejecutar `pytest tests/test_app_base.py` y verlo fallar
- [x] 1.7 Implementar `backend/app/main.py`: instancia FastAPI con `docs_url`/`openapi_url` anulados en producciÃ³n, rutas bajo `/api/v1`, handler 404 JSON; verificar verde con `pytest tests/test_app_base.py`
- [x] 1.8 (TDD) Test rojo de CORS: una peticiÃ³n con `Origin` incluido en `CORS_ORIGINS` recibe `Access-Control-Allow-Origin` exacto y `Access-Control-Allow-Credentials` **ausente/false**; un origen no listado no lo recibe; verificar fallo con `pytest`
- [x] 1.9 Implementar el middleware CORS en `app/main.py` con la lista exacta desde `Settings` y `allow_credentials=False`; verificar verde con `pytest tests/test_app_base.py`
- [x] 1.10 (TDD) Test rojo de exception handler global: un endpoint que lanza una excepciÃ³n no controlada responde `500` con cuerpo JSON genÃ©rico sin traza de stack; la trapea sÃ³lo el log; verificar fallo con `pytest`
- [x] 1.11 Implementar el handler global de `Exception` en `app/main.py`; verificar verde con `pytest tests/test_app_base.py`

## 2. Health check con verificaciÃ³n de conexiÃ³n

- [x] 2.1 (TDD) Test rojo `backend/tests/test_health.py`: `GET /api/v1/health` **sin token** (ruta pÃºblica) con el chequeo de conexiÃ³n mockeado OK â†’ `200` indicando servicio OK y base OK; con el chequeo mockeado fallando â†’ status no-`200` indicando fallo de conexiÃ³n; ejecutar `pytest tests/test_health.py` y verlo fallar
- [x] 2.2 Implementar `backend/app/infrastructure/db/check.py` (conexiÃ³n breve `asyncpg` + `SELECT 1`, cierre garantizado â€” D-02) y `backend/app/api/routers/health.py` montado en `main.py`; verificar verde con `pytest tests/test_health.py`

## 3. Alembic funcional y stub de seed

- [x] 3.1 Crear `backend/alembic.ini` y `backend/alembic/env.py` con template **async** (`async_engine_from_config` + `asyncpg`) que lee `DATABASE_URL` del entorno (D-3); verificar que `alembic history` responde sin error con `versions/` vacÃ­o (baseline sin revisiones)
- [x] 3.2 Crear `backend/app/seed.py` stub idempotente sin-op (D-1, la siembra real es C-19); verificar: `python -m app.seed` sale con cÃ³digo 0 y correrlo dos veces seguidas sigue saliendo con 0

## 4. Esqueleto del frontend

- [x] 4.1 Crear `frontend/package.json`, `tsconfig.json` (TypeScript estricto), `vite.config.ts`, `index.html`, `src/main.tsx` y `src/App.tsx` mÃ­nimo con React 18 + Vite 6; verificar: `npm ci && npx tsc --noEmit && npm run build` generan `dist/` sin errores
- [x] 4.2 Crear `frontend/nginx.conf` con proxy `location /api` â†’ `http://api:8000/api`, prefijo constante y **sin** `envsubst` (D-4); verificar la sintaxis con `nginx -t` dentro de la imagen (se valida de nuevo en la tarea 5.2)

## 5. Docker, Compose y variables de entorno

- [x] 5.1 Crear `backend/Dockerfile` multi-stage (builder `python:3.12-slim` con venv + runtime mÃ­nimo, `USER` no-root, `HEALTHCHECK` sobre `GET /api/v1/health`, `CMD` uvicorn `0.0.0.0:8000`) y `backend/.dockerignore`; verificar: `docker build -t turnos-api ./backend` termina OK
- [x] 5.2 Crear `frontend/Dockerfile` multi-stage (builder `node:22-alpine` con `ARG VITE_API_URL`/`ARG VITE_API_BASE` + `npm run build`, runtime `nginx:alpine` sÃ³lo con `dist/` y `nginx.conf`); verificar: `docker build --build-arg VITE_API_URL=http://localhost:8000/api/v1 --build-arg VITE_API_BASE=/api/v1 -t turnos-web ./frontend` termina OK y el `nginx -t` del stage final pasa
- [x] 5.3 Crear `docker-compose.yml` con los 5 servicios y el orden health-gated (`db` healthcheck `pg_isready` â†’ `migrate` `alembic upgrade head && python -m app.seed` â†’ `api` â†’ `web`), `redis:7-alpine` sin puertos ni cliente, `web` con `build.args` (nunca `environment:`) y `ports: ["5173:80"]`, `api` con `ports: ["8000:8000"]`; verificar: `docker compose config` valida sin errores y lista los 5 servicios
- [x] 5.4 Crear `.env.example` Ãºnico en la raÃ­z (DATABASE_URL, JWT_SECRET_KEY, JWT_ALGORITHM, JWT_EXPIRATION_MINUTES, CORS_ORIGINS, POSTGRES_*, TIMEZONE_CLINICA, ENV, REDIS_URL declarada-sin-uso, VITE_API_URL, VITE_API_BASE) y `.gitignore` con `.env`; verificar: `git check-ignore -q .env` sale con cÃ³digo 0 y todos los nombres del template aparecen en `.env.example`
- [x] 5.5 Correr la suite completa del backend y dejarla en verde: `pytest` dentro del contenedor o venv de `backend/` â†’ todos los tests de los grupos 1â€“2 en verde sin skips inesperados

## 6. VerificaciÃ³n integrada y documentaciÃ³n

- [x] 6.1 Crear `README.md` mÃ­nimo en la raÃ­z con el arranque exacto (`cp .env.example .env` + `docker compose up --build`) y la verificaciÃ³n de salud; verificar: los comandos escritos en el README ejecutan tal cual y producen el resultado descrito
- [x] 6.2 Verificar el stack E2E: `docker compose up --build` levanta los 5 servicios, `GET http://localhost:8000/api/v1/health` responde `200` con conexiÃ³n a BD OK, y `GET /docs` responde (ENV=development)
- [x] 6.3 Verificar el modo producciÃ³n: con `ENV=production` y `JWT_SECRET_KEY` de ejemplo el contenedor `api` **no arranca** (error explÃ­cito); con secreto real, `/docs` y `/openapi.json` responden `404`
- [x] 6.4 Verificar el frontend servido: `GET http://localhost:5173` devuelve el HTML de la SPA y `GET http://localhost:5173/api/v1/health` pasa por el proxy de nginx hacia `api:8000` y responde `200`
- [x] 6.5 Verificar el no-uso de Redis: `docker compose stop redis` y reiniciar `api` â†’ la API sigue operativa con `/health` en `200` (DD-06)






