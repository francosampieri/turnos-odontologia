# environment Specification

## Purpose

Garantiza que el sistema completo (base, API, SPA y job de migración) sea reproducible con un único `docker compose up` a partir de un `.env` raíz, sin secretos en el repo y sin uso funcional de Redis en el MVP.

## Requirements

### Requirement: Stack reproducible con un solo comando
El sistema SHALL levantar los cinco servicios (`db`, `redis`, `api`, `web`, `migrate`) con un único `docker compose up` desde la raíz del repositorio, sin pasos manuales adicionales.

#### Scenario: Levantamiento completo
- **WHEN** se ejecuta `docker compose up` con un `.env` válido en la raíz
- **THEN** los servicios `db`, `redis`, `migrate`, `api` y `web` quedan en ejecución y `GET /api/v1/health` responde desde el host

#### Scenario: Verificación de salud de la base
- **WHEN** el servicio `db` está corriendo
- **THEN** su healthcheck `pg_isready` lo marca sano antes de que los servicios dependientes arranquen

### Requirement: Orden de arranque health-gated
El sistema SHALL respetar el orden `db` (sano) → `migrate` (termina con éxito) → `api` → `web`; `api` no SHALL iniciar si la base no está sana o el job de migración falla.

#### Scenario: Base aún no disponible
- **WHEN** `db` todavía no pasa su healthcheck
- **THEN** `api` no arranca y espera a que `db` esté sano

#### Scenario: Migración fallida bloquea la API
- **WHEN** el job `migrate` termina con error
- **THEN** `api` no inicia (`service_completed_successfully`)

### Requirement: Configuración con fuente única en el `.env` de la raíz
El sistema SHALL leer todas las variables desde el `.env` de la raíz: runtime (`environment:`) para `db`, `redis`, `migrate` y `api`, y build-time (`build.args`) para `web`. No SHALL existir `backend/.env` ni `frontend/.env` con valores efectivos.

#### Scenario: Variables de la API en runtime
- **WHEN** se cambia una variable backend (p. ej. `DATABASE_URL`) en el `.env` raíz y se recrea `api`
- **THEN** el contenedor recibe el nuevo valor sin rebuild de imagen

#### Scenario: Variables `VITE_*` congeladas en build
- **WHEN** se cambia una `VITE_*` en el `.env` raíz sin rebuildear la imagen de `web`
- **THEN** el bundle servido conserva el valor compilado anterior; el nuevo valor sólo surte efecto tras `docker compose build web`

### Requirement: Secretos fuera del repositorio
El sistema SHALL ignorar `.env` en git y SHALL versionar un único `.env.example` en la raíz con las variables de ejemplo necesarias (incluidas `DATABASE_URL`, `JWT_SECRET_KEY`, `JWT_EXPIRATION_MINUTES`, `CORS_ORIGINS`, `POSTGRES_*`, `TIMEZONE_CLINICA`, `ENV` y `VITE_*`).

#### Scenario: `.env` no se commitea
- **WHEN** existe un `.env` local en la raíz
- **THEN** `git status` no lo muestra como archivo a commitear y `.env.example` sí está versionado

### Requirement: Redis declarado sin uso funcional
El sistema SHALL incluir el servicio `redis` en el Compose y el backend NO SHALL abrir ninguna conexión a Redis ni importar un cliente de Redis en el MVP (DD-06).

#### Scenario: Stack funcional sin Redis
- **WHEN** el servicio `redis` está detenido y se reinicia `api`
- **THEN** la API opera normalmente, incluido `GET /api/v1/health`
