# Arquitectura Propuesta

Backend y frontend son **dos aplicaciones separadas** que se comunican por una API REST. No hay monorepo de build, no hay renderizado en el servidor y no hay código compartido entre ambos.

---

## Patrones aplicados

| Patrón | Dónde se usa | Por qué |
|---|---|---|
| **Separación API / SPA** | `backend/` y `frontend/` | Requisito del enunciado. Hace visible la frontera entre capas (DD-01) |
| **Repository / Service / Router en 3 capas** | `backend/app/{api,domain,infrastructure}` | Cada capa tiene una responsabilidad y un grano distintos. Sin framework de arquitectura adicional |
| **Inyección de dependencias** | Dependencias de FastAPI (`get_db`, `get_current_user`, `require_role`) | Los servicios no conocen al framework: se prueban sin HTTP ni base real |
| **DTO / Schema (Pydantic)** | `backend/app/schemas/` | El schema **es** el contrato de la API y la documentación viva. El frontend no redefin reglas |
| **Anti-solapamiento declarativo (constraint de exclusión)** | PostgreSQL, tabla `turno` | La invariante **R1** no puede depender del código de aplicación (RN-TU-04/05/06) |
| **Unidad de trabajo transaccional** | `get_db()` con `commit` / `rollback` por petición | Operaciones de varias filas (reprogramación) son atómicas (RN-CA-02/05) |
| **Maquina de estados explícita** | `domain/turnos/estados.py` | Las transiciones válidas están en un solo lugar y son legibles (RN-TU-07) |
| **RBAC como dependencia, no como decorador** | `Depends(require_role(...))` + filtro en la consulta | Ocultar botones no es autorizar (RN-AU-04/05) |
| **Soft delete** | `activo BOOLEAN` en todas las entidades | Un registro borrado no se puede auditar (RN-GL-01) |
| **Auditoría append-only** | `domain/auditoria/` | Trazabilidad de cambios de agenda y configuración (RN-GL-04) |
| **Global exception handlers** | `main.py` | Traduce SQLSTATE y errores de dominio a un cuerpo de error único y legible |
| **Sembrado idempotente (seed)** | `backend/app/seed.py` | El sistema debe ser demostrable sin carga manual, y el seed se puede correr N veces |
| **Health check** | `GET /api/v1/health` | Verifica servicio y conexión a la base. Necesario para los contenedores |

### Lo que deliberadamente **no** se usa

| Patrón / librería no usado | Motivo |
|---|---|
| GraphQL | El cliente es interno y conocido; REST se explica y se defiende mejor (DD-02) |
| Celery / RQ / `asyncio.Queue` | No hay ningún proceso asíncrono en el MVP (DD-06) |
| Redis para caché | No hay consultas caras que justifiquen invalidación; y una caché de disponibilidad sería **incorrecta** justo cuando importa |
| Redux / Zustand | React Context + `useReducer` alcanza para el estado de sesión y de agenda |
| Tailwind / MUI / Ant Design | CSS Modules: menos dependencias, menos superficie de configuración, más control del resultado visual |
| DDD estricto / agregados / repositorios con interfaces por entidad | Sobreingeniería para 14 tablas. Las tres capas por *caso de uso* (turnos, pacientes, odontograma) alcanzan |
| Migraciones automáticas en el arranque | El esquema se versiona con Alembic de forma explícita, no implícita |

---

## Estructura de directorios

```
turnos-odontologia/
├── docker-compose.yml
├── .env.example                     ← ÚNICO archivo de variables (ver § Variables de entorno)
├── .gitignore
├── README.md
├── discovery/
│   ├── discovery.md                     ← investigación de mercado (20 sistemas)
│   └── sources/
├── knowledge-base/                      ← esta base de conocimiento
├── openspec/                            ← artefactos de especificación
├── .active-orchestrator-state.json
│
├── backend/                             ═══ APLICACIÓN 1 ═══
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── alembic.ini
│   └── app/                              (sin .env propio: lee os.environ)
│       ├── main.py                      ← instancia FastAPI, CORS, exception handlers, health
│       ├── core/
│       │   ├── config.py                ← Settings (pydantic-settings), lee el entorno
│       │   ├── security.py              ← hash de contraseñas, creación y verificación de JWT
│       │   ├── deps.py                  ← get_db, get_current_user, require_role, get_current_profesional
│       │   └── errors.py                ← catálogo de errores de dominio y su mapeo a HTTP
│       │
│       ├── domain/                      ← REGLAS DE NEGOCIO (sin FastAPI, sin SQLAlchemy)
│       │   ├── turnos/
│       │   │   ├── servicio.py          ← crear, cancelar, reprogramar, cambiar estado, sobreturno
│       │   │   ├── disponibilidad.py    ← cálculo de slots (RN-HO-03, RN-FE-05, RN-TU-09)
│       │   │   ├── estados.py           ← máquina de 7 estados y tabla de transiciones (RN-TU-07)
│       │   │   └── solapamiento.py      ← traducción de SQLSTATE 23P01 → 409
│       │   ├── pacientes/
│       │   │   ├── servicio.py
│       │   │   └── normalizacion.py     ← DNI, teléfono (RN-PC-02)
│       │   ├── profesionales/           ← profesionales, horarios, servicios, sillones
│       │   │   ├── servicio.py
│       │   │   └── duracion.py          ← duración efectiva (RN-PR-03)
│       │   ├── feriados/
│       │   │   └── servicio.py
│       │   ├── odontograma/
│       │   │   ├── servicio.py          ← estado de pieza + historial (RN-OD-03…07)
│       │   │   └── catalogos.py         ← 12 estados, 6 caras
│       │   └── auditoria/
│       │       └── servicio.py          ← registro append-only (RN-GL-04)
│       │
│       ├── infrastructure/              ← PERSISTENCIA Y ACCESO A DATOS
│       │   ├── db/
│       │   │   ├── base.py              ← DeclarativeBase, sessionmaker async, engine
│       │   │   └── session.py           ← dependencia get_db con commit/rollback
│       │   ├── models/                  ← modelos SQLAlchemy (mapeo de 04_modelo_de_datos.md)
│       │   │   ├── rol.py  usuario.py  profesional.py  servicio.py
│       │   │   ├── profesional_servicio.py  sillon.py
│       │   │   ├── horario_laboral.py  feriado.py  bloqueo_profesional.py
│       │   │   ├── paciente.py  turno.py
│       │   │   ├── odontograma.py  odontograma_movimiento.py
│       │   │   └── auditoria.py
│       │   └── repositories/            ← acceso a datos por entidad (consultas, filtros)
│       │       ├── turno_repo.py  paciente_repo.py  profesional_repo.py …
│       │
│       ├── api/                         ← HTTP PURO: rutas, schemas de entrada/salida, auth
│       │   ├── routers/
│       │   │   ├── auth.py  health.py  pacientes.py
│       │   │   ├── profesionales.py  horarios.py  servicios.py  sillones.py
│       │   │   ├── feriados.py  bloqueos.py
│       │   │   ├── turnos.py  disponibilidad.py
│       │   │   ├── odontograma.py
│       │   │   └── usuarios.py  auditoria.py
│       │   └── schemas/
│       │       ├── auth.py  paciente.py  turno.py
│       │       ├── profesional.py  horario.py  servicio.py  sillon.py
│       │       └── odontograma.py
│       │
│       ├── seed.py                      ← datos iniciales idempotentes
│       └── scripts/
│           ├── crear_admin.py           ← alta del primer usuario
│           └── test_concurrencia.py     ← dos reservas simultáneas sobre el mismo slot
│
├── frontend/                            ═══ APLICACIÓN 2 ═══
│   ├── Dockerfile
│   ├── nginx.conf
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   ├── index.html
│   └── src/
│       ├── main.tsx
│       ├── App.tsx                      ← rutas y guards por rol
│       ├── api/
│       │   ├── client.ts                ← fetch + Authorization + manejo de errores
│       │   ├── auth.ts  pacientes.ts  turnos.ts
│       │   ├── profesionales.ts  horarios.ts  servicios.ts
│       │   ├── sillones.ts  feriados.ts
│       │   └── odontograma.ts
│       ├── auth/
│       │   ├── AuthContext.tsx          ← usuario, rol, login, logout
│       │   └── RequireRole.tsx          ← guard de rutas (UX, no seguridad)
│       ├── features/                    ← una carpeta por épica de 06_funcionalidades.md
│       │   ├── agenda/
│       │   │   ├── AgendaDia.tsx        ← US-030
│       │   │   ├── AgendaSemana.tsx     ← US-031
│       │   │   ├── TurnoDetalle.tsx     ← US-038
│       │   │   ├── TurnoForm.tsx        ← US-033
│       │   │   ├── Disponibilidad.tsx   ← US-032
│       │   │   └── components/ColumnaProfesional.tsx, SlotTurno.tsx
│       │   ├── pacientes/
│       │   │   ├── PacienteLista.tsx    ← US-021
│       │   │   ├── PacienteForm.tsx     ← US-020
│       │   │   ├── PacienteDetalle.tsx  ← US-023
│       │   │   └── PacienteBusqueda.ts
│       │   ├── odontograma/
│       │   │   ├── Odontograma.tsx      ← US-040
│       │   │   ├── PiezaCelda.tsx       ← US-041
│       │   │   ├── PiezaHistorial.tsx   ← US-042
│       │   │   └── catalogo.ts          ← colores y siglas de los 12 estados
│       │   └── config/
│       │       ├── Servicios.tsx        ← US-012
│       │       ├── Sillones.tsx         ← US-013
│       │       ├── Feriados.tsx         ← US-014
│       │       ├── Horarios.tsx         ← US-011
│       │       ├── Bloqueos.tsx         ← US-015
│       │       ├── Usuarios.tsx         ← US-004
│       │       └── Auditoria.tsx        ← US-005
│       ├── pages/
│       │   ├── LoginPage.tsx
│       │   └── NotFoundPage.tsx
│       ├── shared/
│       │   ├── components/  (Boton, Modal, Tabla, Badge, ConfirmDialog, Toast)
│       │   ├── hooks/       (useApi, useDebounce, useFeriados)
│       │   ├── utils/       (fecha.ts, zonaHoraria.ts, dni.ts, errores.ts)
│       │   └── styles/      (variables.css, global.css)
│       └── types/                       ← tipos TS de los schemas de la API
│
└── docs/
    └── diagrama-arquitectura.png        ← opcional, para la entrega
```

**Regla de dependencia**: `api → domain → infrastructure`. El `domain` no importa nada de FastAPI ni de la capa HTTP. Por eso los servicios de negocio se pueden probar como funciones puras y por eso el mismo servicio sirve tanto a la API como a un eventual script.

---

## Docker Compose — servicios

| Servicio | Imagen | Puerto | Función | Variables que lee |
|---|---|---|---|---|
| `db` | `postgres:16-alpine` | `5432` | Base de datos. Fuente única de verdad. Contiene los `EXCLUDE` de no-solapamiento | `POSTGRES_*` |
| `redis` | `redis:7-alpine` | `6379` | **Declarado y sin uso funcional en el MVP** (DD-06) | — |
| `api` | construir `backend/Dockerfile` | `8000` | API REST FastAPI | `DATABASE_URL`, `JWT_SECRET_KEY`, `JWT_EXPIRATION_MINUTES`, `CORS_ORIGINS`, `ENV` |
| `web` | construir `frontend/Dockerfile` (build Vite + nginx) | `5173` en desarrollo, `80` en producción | SPA servida por nginx, con proxy `/api` hacia `api` | **build-time**: `VITE_API_URL`, `VITE_API_BASE` vía `build.args` (no `environment`) |
| `migrate` | misma imagen que `api` | — | Job de una sola ejecución: `alembic upgrade head` + `seed`. Corre **antes** que `api` (`depends_on: service_completed_successfully`) | las del backend |

### Sobre Redis en el Compose

Redis **arranca** con el Compose y **no se conecta desde el backend**. Es una decisión consciente y documentada, no un descuido: el MVP no tiene ningún proceso asíncrono (no hay emails, no hay reportes, no hay cola). Se deja declarado para que el entorno sea reproducible y para que la decisión sea visible y defendible. El backend **no** importa ninguna librería de Redis.

**Qué justificaría su uso real**: envío de recordatorios (cola + reintentos), invalidación de la caché de disponibilidad cuando hay alta de turnos, rate limiting en un eventual endpoint público, o resultados de reportes pesados.

```yaml
# Fragmento del docker-compose.yml
services:
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER}"]
      interval: 5s
      retries: 10

  redis:
    image: redis:7-alpine
    # Sin consumidores en el MVP. Ver DD-06.
    command: ["redis-server", "--save", "", "--appendonly", "no"]

  migrate:
    build: ./backend
    command: sh -c "alembic upgrade head && python -m app.seed"
    depends_on:
      db: { condition: service_healthy }

  api:
    build: ./backend
    environment:            # RUNTIME: llega desde el .env de la raíz
      DATABASE_URL: ${DATABASE_URL}
      JWT_SECRET_KEY: ${JWT_SECRET_KEY}
      JWT_ALGORITHM: ${JWT_ALGORITHM}
      JWT_EXPIRATION_MINUTES: ${JWT_EXPIRATION_MINUTES}
      CORS_ORIGINS: ${CORS_ORIGINS}
      ENV: ${ENV}
    depends_on:
      db: { condition: service_healthy }
      migrate: { condition: service_completed_successfully }
    ports: ["8000:8000"]

  web:
    build:
      context: ./frontend
      args:                          # BUILD-time: se compilan dentro del bundle
        VITE_API_URL: ${VITE_API_URL}
        VITE_API_BASE: ${VITE_API_BASE}
    depends_on: [api]
    ports: ["5173:80"]
    # Sin `environment:` a propósito: las VITE_* ya quedaron congeladas en el
    # bundle. Cambiar una VITE_* exige rebuildear la imagen, no reiniciar.
    # nginx NO necesita sustitución de plantillas en runtime porque el prefijo
    # de la API es una constante del bundle (/api/v1), igual en todos los entornos.

volumes:
  pgdata:
```

---

## Seguridad

### Autenticación

- **Esquema**: **JWT stateless** firmado con **HS256**. Payload mínimo: `sub` (id del usuario), `rol`, `iat`, `exp`. Sin datos personales en el token.
- **Transporte**: `Authorization: Bearer <token>` en cada petición (RN-AU-06). No hay cookies, porque no hay SSR.
- **Almacenamiento en el cliente**: `sessionStorage`. Se elige deliberadamente sobre `localStorage` (que persiste entre sesiones y es legible por cualquier XSS) y sobre una cookie `httpOnly` (que requeriría un flujo con cookies y CSRF, innecesario en una API con token explícito).
- **Expiración**: 8 h por defecto, configurable.
- **Revocación**: no hay lista de revocación ni *refresh token* en el MVP. `logout` es cliente (RN-AU-07). El riesgo se acepta y se documenta: un token robado es válido hasta 8 h.
- **Contraseñas**: **bcrypt** con cost factor ≥ 12 (RN-AU-03). Nunca en texto plano en la base, ni en el seed, ni en los logs.

### Autorización

- **Tres roles fijos**: `secretaria`, `odontologo`, `admin` (RN-AU-02).
- El permiso se verifica **en el servidor**, en la dependencia de la ruta y **dentro de la consulta SQL** (RN-AU-04/05). Ocultar botones es sólo ergonomía.
- El `odontologo` tiene un filtro obligatorio por `profesional_id` en toda consulta de turnos. Un `GET /api/v1/turnos` sin filtro, con su token, devuelve **sólo** sus turnos.
- Para recursos fuera de su alcance se responde `404`, no `403`, cuando responder `403` revelaría la existencia del recurso (RN-GL-05).

### Validación de input

- **Dos capas**: Pydantic v2 valida forma, tipo y rango en el borde HTTP; el servicio de dominio valida las reglas de negocio. **La validación de forma no reemplaza a la de negocio** — el frontend valida para dar buena experiencia, el backend valida porque es la autoridad.
- Consultas siempre parametrizadas por SQLAlchemy; **ninguna** concatenación de strings en SQL.
- Límites de paginación obligatorios en los listados (RN-PC-06): sin paginación, la agenda del día no escala.

### Datos sensibles de salud — Ley 25.326

El sistema guarda DNI, teléfono, fecha de nacimiento y estado dentario. Son **datos personales** bajo la Ley 25.326 de Protección de Datos Personales, y el odontograma es información de salud.

| Medida | Implementación |
|---|---|
| Minimización | Se guarda exactamente lo declarado en `04_modelo_de_datos.md`, ni un campo más. No hay domicilio, ni cobertura médica, ni obra social |
| Enmascarado por defecto | El listado de pacientes devuelve el DNI enmascarado (`****5678`). Verlo completo requiere autorización explícita |
| Logs | **Nunca** se registran DNI, teléfono, email ni fecha de nacimiento. Los identificadores de log son los `id` internos |
| Auditoría | Los campos sensibles no aparecen en `datos_antes` / `datos_despues` (RN-GL-04) |
| Base de datos | Accesible sólo por la red interna de Docker; puerto `5432` **no** publicado en el host en un despliegue real |
| HTTPS | Obligatorio fuera del entorno de desarrollo. El Compose de desarrollo sirve en HTTP y eso está documentado |
| Acceso del odontólogo | No ve el listado global de pacientes: llega a la ficha sólo desde un turno propio. Es una reducción real de exposición (RN-AU-05) |
| Consentimiento | La pantalla de login declara el tratamiento de datos y el responsable. Es la medida mínima exigible en un TP; una clínica real necesita además contrato con el titular y registro ante la autoridad de aplicación (AAIP) |

> **Límite explícito**: el MVP **no** implementa la Ley 26.529 de Historia Clínica Electrónica porque **no hay historia clínica**: hay un odontograma por paciente. Es un registro odontológico, no una historia clínica. Si se agrega historia clínica, esa obligación entra con ella (PA-08).

### Secrets management

- **Ninguna credencial real en el repositorio.** `.env` está en `.gitignore`; existe **un solo** `.env.example`, en la raíz del repositorio, con valores de ejemplo.
- `JWT_SECRET_KEY` es obligatoria en `ENV=production`: la aplicación **no arranca** si está en el valor de ejemplo. En desarrollo se puede dejar el valor por defecto documentado.
- **Ubicación única**: el Compose toma **todos** sus valores del `.env` de la **raíz** por interpolación `${VAR}`. No hay `backend/.env` ni `frontend/.env`: las variables llegan al contenedor por `environment:` (backend, en runtime) o por `build.args` (frontend, en build time), siempre desde el `.env` de la raíz. Ver § "Variables de entorno".

### CORS

El frontend corre en `http://localhost:5173` y la API en `http://localhost:8000`: son orígenes distintos, hace falta CORS. Se declara el origen exacto en `CORS_ORIGINS` (lista, no comodín). Cookies: `allow_credentials` en `False`, porque la autenticación va por cabecera, no por cookie.

---

## Variables de entorno

> **Ubicación única y autoritativa: el `.env` de la raíz del repositorio.** Es el **único** archivo de variables del proyecto: existe un solo `.env.example`, en la raíz. El Compose lo lee e interpola `${VAR}` en dos momentos distintos: **en runtime** para los servicios `db`, `redis`, `migrate` y `api`, y **en build time** para los `build.args` del servicio `web`. **No hay un `backend/.env` ni un `frontend/.env`**: el backend lee `os.environ` (que el Compose ya le inyectó desde la raíz) y el frontend lee `import.meta.env` (que Vite le congeló en el bundle). Si alguien copia un `.env` dentro de `backend/`, el Compose lo ignora y la configuración real sigue siendo la de la raíz.

### Backend (runtime, inyectadas por el Compose desde el `.env` de la raíz)

| Variable | Descripción | Ejemplo | Sensible |
|---|---|---|---|
| `ENV` | Modo de ejecución. `production` desactiva `/docs` | `development` | N |
| `DEBUG` | Trazas y reload | `true` | N |
| `APP_NAME` | Nombre de la aplicación (aparece en OpenAPI) | `Turnos Odontología API` | N |
| `DATABASE_URL` | Cadena de conexión async a PostgreSQL | `postgresql+asyncpg://app:app@db:5432/turnos` | **S** |
| `JWT_SECRET_KEY` | Clave de firma HS256. **Obligatoria en producción** | `cambiar-en-produccion` | **S** |
| `JWT_ALGORITHM` | Algoritmo de firma | `HS256` | N |
| `JWT_EXPIRATION_MINUTES` | Vigencia del token | `480` | N |
| `CORS_ORIGINS` | Orígenes permitidos, separados por coma | `http://localhost:5173` | N |
| `POSTGRES_DB` | Nombre de la base (usada por el Compose) | `turnos` | N |
| `POSTGRES_USER` | Usuario de la base | `app` | **S** |
| `POSTGRES_PASSWORD` | Contraseña de la base | `app` | **S** |
| `TIMEZONE_CLINICA` | Zona usada para la conversión a hora de pared en el frontend | `America/Argentina/Buenos_Aires` | N |
| `REDIS_URL` | **Declarada, no usada** en el MVP | `redis://redis:6379/0` | N |

### Frontend (build time, prefijo `VITE_`, vía `build.args`)

| Variable | Momento | Descripción | Ejemplo | Sensible |
|---|---|---|---|---|
| `VITE_API_URL` | **build time** (`build.args`) | URL base de la API en desarrollo, cuando el frontend corre en el dev server de Vite (`5173`) y el navegador habla directo con `8000` | `http://localhost:8000/api/v1` | N |
| `VITE_API_BASE` | **build time** (`build.args`) | Prefijo de la API que el bundle usa en producción, donde nginx hace proxy de `/api` hacia el servicio `api` | `/api/v1` | N |

> **Por qué `build.args` y no `environment`.** Vite **reemplaza** los `import.meta.env.VITE_*` literalmente durante `npm run build`: el valor queda escrito dentro del bundle JavaScript que se sirve. Un `environment:` del Compose llega al contenedor **después** de compilar, así que no tendría ningún efecto sobre el bundle — es la trampa clásica de esta configuración. Por lo tanto **cambiar una `VITE_*` exige rebuildear la imagen** (`docker compose build web`), no reiniciar el contenedor.
>
> **nginx no necesita sustitución en runtime.** El `nginx.conf` no usa `envsubst` ni plantillas: hace proxy de un prefijo **constante** (`/api` → `http://api:8000/api`), que es idéntico en todos los entornos. Si en el futuro el prefijo tuviera que cambiar por entorno, la alternativa sería un `entrypoint` con `envsubst` sobre `/etc/nginx/templates/*.conf`, pero con un valor constante eso sería complejidad agregada sin beneficio.
>
> `VITE_*` se compila dentro del bundle del navegador: **sólo** se pueden poner ahí valores públicos. Ninguna clave, ningún secreto — y no es sólo una limitación de Vite: tampoco habría dónde guardarlo, porque el frontend no habla con ningún tercero.

---

## Migraciones, seed y verificación

| Aspecto | Decisión |
|---|---|
| Esquema | Alembic. La primera migración incluye `CREATE EXTENSION btree_gist` y los tres `EXCLUDE USING gist` de `04_modelo_de_datos.md` |
| Orden de arranque | `db` sano → `migrate` (`alembic upgrade head` + seed) → `api` → `web` |
| Seed | Idempotente (upsert por clave natural). Contraseñas hasheadas **antes** de insertar. Datos de pacientes ficticios, nunca reales. Siembra **los defaults que declaran las reglas**, no excepciones: `horario_laboral` con **10 filas** (Lun–Vie `08:00–18:00` por profesional, **sábado vacío** — RN-HO-01 y US-011 CA-1), `duracion_min = 30` (RN-PR-02), `estado = 'AGENDADO'` (RN-TU-08). Detalle de filas y contenido en `04_modelo_de_datos.md` § "Seed data inicial" |
| Health check | `GET /api/v1/health` devuelve estado del servicio y de la conexión a la base |
| Documentación interactiva | `/docs` y `/openapi.json`, **deshabilitadas** en `ENV=production` |
| Verificación de la invariante central | `python -m app.scripts.test_concurrencia` lanza dos reservas simultáneas sobre el mismo slot y exige exactamente una `201` y una `409` |

### Estrategia de pruebas

| Nivel | Qué se prueba | Herramienta |
|---|---|---|
| Unitario | Normalización de DNI/teléfono, duración efectiva, cálculo de slots, tabla de transiciones de estado | `pytest` |
| Integración | Endpoints contra una base de prueba real en contenedor, incluidos los casos `409` | `pytest` + `httpx.AsyncClient` |
| Concurrencia | Dos escrituras simultáneas sobre el mismo slot | `pytest` + `asyncio.gather` o el script mencionado |
| E2E manual | Recorrido de defensa: login, agenda del día, reserva, conflicto, cancelación, odontograma | Manual, cronometrado |

No se usa Selenium ni Playwright: para un TP, la prueba de concurrencia y la prueba de integración cubren el riesgo técnico real, y el recorrido de defensa se hace a mano con más control narrativo.