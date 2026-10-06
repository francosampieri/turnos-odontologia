# Descripción General

## Stack tecnológico

El stack **no es una preferencia**: fue impuesto desde arriba como condición de entrega (restricción **R-1** del Discovery, §9). Ver DD-01.

### Backend

| Capa | Tecnología | Versión mínima sugerida | Rol en el sistema |
|---|---|---|---|
| Lenguaje | **Python** | 3.12 | Lenguaje del backend |
| Framework web | **FastAPI** | 0.115 | Servidor REST, validación y documentación OpenAPI automática |
| Validación / serialización | **Pydantic v2** | 2.9 | Schemas de request/response y validación declarativa |
| ORM | **SQLAlchemy 2.0** | 2.0 | Mapeo objeto-relacional, sesiones, migraciones Alembic |
| Migraciones | **Alembic** | 1.13 | Versionado del esquema |
| Autenticación | **JWT** (`python-jose` o `PyJWT`) + `passlib[bcrypt]` | — | Tokens stateless + hashing de contraseñas |
| Driver de BD | **asyncpg** | 0.29 | Driver asíncrono nativo de PostgreSQL |
| Base de datos | **PostgreSQL** | 16 | **Fuente única de verdad**;Constraints de no-solapamiento |
| Caché (declarado, sin uso) | **Redis** | 7.2 | Presente en Docker Compose, sin uso funcional en el MVP (DD-06) |
| Contenedores | **Docker / Docker Compose** | Compose v2 | Entorno reproducible de desarrollo y evaluación |

### Frontend

| Capa | Tecnología | Versión mínima sugerida | Rol en el sistema |
|---|---|---|---|
| Librería de UI | **React** | 18.3 | Componentes de interfaz |
| Lenguaje | **TypeScript** | 5.6 | Tipado estricto |
| Bundler / dev server | **Vite** | 6 | Build y servidor de desarrollo |
| Cliente HTTP | **fetch** nativo (envuelto en un módulo propio) | — | Comunicación con la API REST. Sin librería adicional: la capa HTTP es una pieza didáctica del proyecto |
| Estado global | **React Context** + `useReducer` | — | Sesión, rol y datos compartidos. Sin Redux: sobreingeniería para el alcance |
| Estilos | **CSS Modules** | — | Estilos por componente. Sin framework de estilos |

> **Nota sobre versiones.** La tabla indica la **mínima sugerida**; las versiones exactas quedan pineadas en `backend/requirements.txt` y `frontend/package.json` en la etapa de implementación. Este documento es la fuente de verdad del contrato tecnológico, no del lockfile.

### Fuera del stack (y por qué)

| Tecnología no usada | Motivo |
|---|---|
| **Next.js / SSR** | El proyecto es una SPA administrativa detrás de un backend propio; el SSR no aporta valor y agrega una capa de renderizado que el enunciado no pide |
| **Celery / RQ / tareas asíncronas** | No hay ningún proceso asíncrono en el MVP (DD-06) |
| **Prisma / Drizzle** | El backend es Python/SQLAlchemy; un ORM de TypeScript sólo agregaría duplicación |
| **GraphQL** | El cliente es interno y conocido; REST con recursos bien definidos es más fácil de explicar y de defender (DD-02) |
| **ORM de tipos para el frontend** (compartido con el backend) | Generar tipos desde OpenAPI se considera opcional y no bloqueante |

---

## Arquitectura general

### Diagrama

```
                    ┌──────────────────────────────────────────────┐
                    │            NAVEGADOR (clínica)               │
                    │        React + TypeScript + Vite             │
                    │  SPA · sesión en memoria + sessionStorage    │
                    │                                              │
                    │  Login · Agenda · Pacientes · Configuración   │
                    │  Odontograma                                 │
                    └───────────────────┬──────────────────────────┘
                                        │  HTTPS / JSON
                                        │  Authorization: Bearer <JWT>
                                        ▼
        ┌───────────────────────────────────────────────────────────┐
        │                  API REST — FastAPI (Python)              │
        │                                                           │
        │  ┌─────────────┐  ┌──────────────┐  ┌──────────────────┐ │
        │  │ Routers     │  │ Servicios    │  │ Dependencias     │ │
        │  │ (recursos)  │─▶│ de dominio   │─▶│ (sesión SQLAlchemy)│
        │  └─────────────┘  └──────────────┘  └──────────────────┘ │
        │        │                 │                                │
        │  ┌─────────────┐  ┌──────────────┐  ┌──────────────────┐ │
        │  │ Pydantic    │  │ Reglas de    │  │ RBAC             │ │
        │  │ (schemas)   │  │ negocio      │  │ (dependencias)   │ │
        │  └─────────────┘  └──────────────┘  └──────────────────┘ │
        └───────┬─────────────────────────────────┬─────────────────┘
                │ SQLAlchemy 2.0 (async)          │  (declarado, sin uso)
                ▼                                 ▼
   ┌────────────────────────────┐     ┌──────────────────────────────┐
   │       PostgreSQL 16        │     │          Redis 7.2           │
   │  ────────────────────────  │     │  Arranca en Docker Compose.  │
   │  Fuente única de verdad    │     │  SIN uso funcional en el     │
   │  · EXCLUDE constraints     │     │  MVP (ver DD-06).            │
   │    (no-solapamiento)       │     └──────────────────────────────┘
   │  · CHECK, FKs, índices     │
   │  · timestamptz en UTC      │
   └────────────────────────────┘
```

### La decisión estructural: dos aplicaciones separadas

Backend y frontend son **aplicaciones distintas**, con procesos, puertos y artefactos de build distintos. La única interfaz entre ambas es **una API REST con JSON**. No hay renderizado en el servidor, no hay BFF, no hay código compartido.

**Consecuencias asumidas:**

| Consecuencia | Implicación práctica |
|---|---|
| Doble proceso en ejecución | En desarrollo hay que levantar `api` y `web`. Lo resuelve `docker compose up` |
| CORS obligatorio | El navegador llama a `localhost:8000` desde `localhost:5173`: hay que declarar el origen permitido |
| Doble manejo de errores | El backend devuelve códigos HTTP; el frontend los traduce a mensajes. Se define un mapa único (`08_arquitectura_propuesta.md`) |
| Sin validación compartida | Los schemas Pydantic son el contrato; el frontend valida sólo por experiencia de usuario |
| Autenticación sin cookies de sesión | Al no haber SSR, el JWT viaja explícito en `Authorization: Bearer` (RN-AU-06) |

**Por qué esto es una ventaja para el proyecto**: hace visible y defendible la separación de capas que exige el enunciado. Un monolito Next.js habría resuelto todo en un proceso, escondiendo justamente la frontera que se quiere demostrar (DD-01).

### Capas del backend

El backend se organiza en cuatro capas, sin framework de arquitectura adicional:

1. **API / Routers** — declaran la ruta, el schema de entrada y salida, y la dependencia de autorización. No contienen reglas de negocio.
2. **Servicios de dominio** — contienen las reglas de negocio (`RN-XX-NN`). Aquí vive la validación de disponibilidad, la máquina de estados, el cálculo de slots.
3. **Repositorios / Modelos SQLAlchemy** — acceso a datos. Los constraints de base de datos son la última línea de defensa (RN-TU-03/04/05).
4. **Schemas Pydantic** — el contrato de la API. Es también la documentación viva del proyecto.

---

## Integraciones externas

**Ninguna integración externa es obligatoria para el MVP.** Esto es una decisión consciente, no una casualidad: el sistema debe ser completamente utilizable con la base de datos sola. El Discovery lo fundamentó en que 2 de 10 proveedores argentinos cobran la automatización aparte y en que el costo por mensaje de WhatsApp se traslada al cliente.

| Servicio | Propósito | Tipo | Estado |
|---|---|---|---|
| **WhatsApp Business API** | Recordatorio y confirmación de turnos | REST (Cloud API de Meta) | **Fuera del MVP** — costo variable (ixi: USD $45 + IVA por mensaje entregado; DentalSoft Pro: USD 0,026 por recordatorio), cuenta empresarial verificada, dependencia de un tercero (DD-07) |
| **Mercado Pago** | Señas, cobros y pagos de turnos | REST + SDK | **Fuera del MVP** — comisión por transacción |
| **Google Calendar** | Sincronización con la agenda que el odontólogo ya usa | OAuth 2.0 + REST | **Fuera del MVP** — baja complejidad técnica, buen candidato a ser la primera integración post-MVP |
| **AFIP / ARCA** | Facturación electrónica | SOAP + certificados digitales | **Fuera del MVP** — alta complejidad normativa. Dentatools declara explícitamente que **no** emite factura AFIP y opera igual |
| **Mercado Libre / SMS gateways** | Mensajería alternativa | REST | **Fuera del MVP** — mismo problema de costo variable que WhatsApp |
| **Redis** | Caché / colas asíncronas | TCP | **Declarado en Docker Compose, sin uso funcional** — el MVP no tiene procesos asíncronos (DD-06) |
| **Proveedor de correo (SMTP)** | Notificaciones por email | SMTP | **Fuera del MVP** |

### Consecuencia arquitectónica de no tener integraciones

- Ninguna **cola de trabajos**: no hay reintentos, no hay `outbox pattern`, no hay idempotencia asíncrona que diseñar.
- Ningún **webhook entrante**.
- Ninguna **credencial de terceros** que proteger más allá del secreto JWT y la contraseña de la base de datos.
- Ningún **costo variable** en función del uso: el sistema se puede hostear sin costo mensual variable.

---

## API REST

Prefijo único: `/api/v1`. Todas las rutas requieren autenticación salvo las indicadas en `03_actores_y_roles.md`. Formato de request y response: `application/json`. Todas las fechas se transmiten en **ISO 8601 con offset** (`2026-10-12T14:00:00-03:00`).

### Autenticación

| Método | Ruta | Descripción | Rol |
|---|---|---|---|
| `POST` | `/api/v1/auth/login` | Autentica y devuelve el JWT | público |
| `GET` | `/api/v1/auth/me` | Devuelve el usuario del token (id, nombre, rol) | autenticado |
| `GET` | `/api/v1/health` | Health check del servicio y de la base de datos | público |

> **Por qué no existe `POST /auth/logout`**: el JWT es **stateless**, expira a las 8 h por defecto y **no hay lista de revocación** ni *refresh token* en el MVP (RN-AU-07). Un endpoint de logout no podría invalidar nada: sólo daría una respuesta `200` sin efecto. El cierre de sesión es **una operación del cliente** — el token se descarta de `sessionStorage`— y el riesgo se acepta y se documenta: un token robado es válido hasta su expiración (DD-19, US-002). Si en el futuro se agrega revocación, ese endpoint aparece con ella.

### Pacientes

| Método | Ruta | Rol | Reglas |
|---|---|---|---|
| `GET` | `/api/v1/pacientes?dni=&apellido=&telefono=` | secretaria, admin | RN-PC-06 |
| `GET` | `/api/v1/pacientes/{id}` | secretaria, odontologo (pacientes con turno propio), admin | RN-AU-05 |
| `POST` | `/api/v1/pacientes` | secretaria, admin | RN-PC-01…05 |
| `PATCH` | `/api/v1/pacientes/{id}` | secretaria, admin | RN-PC-01…05 |
| `DELETE` | `/api/v1/pacientes/{id}` | secretaria, admin | Baja lógica (RN-GL-01). Con turnos asociados → 409 |

> El odontograma de un paciente **no** se expone desde el grupo de Pacientes: vive únicamente en el grupo Odontograma, más abajo, en `/api/v1/pacientes/{id}/odontograma`. No existe `GET /api/v1/turnos/{id}/odontograma`: el odontograma es un recurso **del paciente**, no del turno, y se llega a él desde el turno (frontend `/pacientes/:id/odontograma`) o desde la ficha del paciente (US-040 CA-3/CA-4).

### Profesionales, horarios y configuración

| Método | Ruta | Rol | Reglas |
|---|---|---|---|
| `GET` | `/api/v1/profesionales` | todos | — |
| `POST` | `/api/v1/profesionales` | secretaria, admin | RN-PR-01 |
| `PATCH` | `/api/v1/profesionales/{id}` | secretaria, admin | — |
| `GET` | `/api/v1/profesionales/{id}/horarios` | todos | RN-HO-01 |
| `PUT` | `/api/v1/profesionales/{id}/horarios` | admin | Reemplaza el conjunto completo de ventanas (RN-HO-01/02) |
| `GET/POST/PATCH` | `/api/v1/servicios` | GET: todos · escritura: secretaria, admin | RN-PR-02 |
| `PUT` | `/api/v1/profesionales/{id}/servicios/{sid}` | admin | Override de duración (RN-PR-03) |
| `GET/POST/PATCH` | `/api/v1/sillones` | GET: todos · escritura: admin | RN-SI-01/04 |
| `GET` | `/api/v1/feriados` | todos | RN-FE-01 |
| `POST` | `/api/v1/feriados` | admin | RN-FE-01/04 |
| `PATCH` | `/api/v1/feriados/{id}` | admin | RN-FE-01/06 |
| `DELETE` | `/api/v1/feriados/{id}` | admin | Baja lógica (RN-FE-06, RN-GL-01) |
| `GET/POST/DELETE` | `/api/v1/profesionales/{id}/bloqueos` | GET: todos · escritura: admin | RN-FE-05 |

> **`feriado` también se puede desactivar.** Un feriado cargado por error es un error de configuración que hay que poder corregir sin borrar el histórico: por eso existe `PATCH` (editar fecha, descripción, tipo) y `DELETE` (baja lógica, `activo = FALSE`). Sin ellos, el único camino sería el `INSERT` de otra fila con la misma fecha, que viola `UNIQUE(fecha)` (RN-FE-01). Mismo criterio que el resto de los maestros: **soft delete, nunca borrado físico** (RN-GL-01, RN-FE-06).

### Agenda y turnos

| Método | Ruta | Rol | Reglas |
|---|---|---|---|
| `GET` | `/api/v1/turnos?fecha=&profesional_id=` | secretaria, admin (todos) · odontologo (forzado a su id) | RN-AU-05 |
| `GET` | `/api/v1/turnos/semana?desde=&hasta=&profesional_id=` | idem | — |
| `GET` | `/api/v1/turnos/{id}` | owner / secretaria / admin | — |
| `GET` | `/api/v1/disponibilidad?fecha=&profesional_id=&servicio_id=` | secretaria, admin | RN-HO-03, RN-FE-03, RN-TU-03 |
| `POST` | `/api/v1/turnos` | secretaria, admin | RN-TU-01…11, RN-HO-03, RN-CA-03 |
| `POST` | `/api/v1/turnos/{id}/cancelar` | secretaria, admin | RN-CA-01/03/04 |
| `POST` | `/api/v1/turnos/{id}/reprogramar` | secretaria, admin | RN-CA-02/03/05 |
| `PATCH` | `/api/v1/turnos/{id}/estado` | secretaria, admin; odontologo sólo → `en_curso`/`completado` sobre turno propio | RN-TU-07 |
| `POST` | `/api/v1/turnos/sobreturno` | secretaria, admin | RN-TU-10 |

### Odontograma

| Método | Ruta | Rol | Reglas |
|---|---|---|---|
| `GET` | `/api/v1/pacientes/{id}/odontograma` | odontologo (turno propio), secretaria, admin | RN-OD-01/02 |
| `PUT` | `/api/v1/pacientes/{id}/odontograma/{pieza}` | odontologo (turno propio) | RN-OD-03/04/06 |
| `GET` | `/api/v1/pacientes/{id}/odontograma/{pieza}/historial` | owner / secretaria / admin | RN-OD-07 |

> **Nota**: la ruta `PUT` del odontograma es **idempotente** por diseño: escribe el estado *actual* de una pieza. El **historial** es append-only y lo alimenta automáticamente el servicio de dominio (RN-OD-07), sin que exista un endpoint de escritura para el historial.

### Usuarios y auditoría

| Método | Ruta | Rol |
|---|---|---|
| `GET` | `/api/v1/usuarios` | admin |
| `POST` | `/api/v1/usuarios` | admin |
| `PATCH` | `/api/v1/usuarios/{id}` | admin |
| `GET` | `/api/v1/auditoria?entidad=&usuario_id=&desde=&hasta=` | admin |

### Recuento de la superficie de la API

Los grupos anteriores suman **43 endpoints** bajo el prefijo `/api/v1`:

| Grupo | Endpoints |
|---|---|
| Autenticación | 3 (login, auth/me, health) |
| Pacientes | 5 |
| Profesionales, horarios y configuración | 19 |
| Agenda y turnos | 9 |
| Odontograma | 3 |
| Usuarios y auditoría | 4 |
| **Total** | **43** |

Los 14 routers del backend (`auth`, `health`, `pacientes`, `profesionales`, `horarios`, `servicios`, `sillones`, `feriados`, `bloqueos`, `turnos`, `disponibilidad`, `odontograma`, `usuarios`, `auditoria`) distribuyen exactamente estas rutas; `03_actores_y_roles.md` lista cuáles de ellas son públicas (3: `POST /auth/login`, `GET /health` y la documentación OpenAPI).

---

## Códigos de error de la API

| HTTP | Situación | Uso principal |
|---|---|---|
| `200` / `201` / `204` | Éxito | — |
| `400` | Request malformado no detectable por schema | — |
| `401` | Sin token, token expirado o token inválido | RN-AU-01 |
| `403` | **Autenticado pero sin permiso para la OPERACIÓN**: el rol no tiene ese permiso sobre ese tipo de operación (RN-AU-02/04) | RN-AU-02/04 |
| `404` | El recurso **no existe**, o está **inactivo**, **o pertenece a otro profesional**. Los tres casos son **indistinguibles entre sí y devuelven la misma respuesta**, por diseño, para no filtrar la existencia de un recurso ajeno | RN-GL-05, RN-AU-05 |
| `409` | Conflicto de estado: solapamiento, DNI duplicado, entidad con turnos dependientes | RN-TU-03/04/05, RN-PC-01 |
| `422` | Regla de negocio violada (pasado, fuera de horario, anticipación mínima, transición ilegal) | RN-TU-02, RN-HO-03, RN-FE-03, RN-CA-03, RN-TU-07 |

> **`403` nunca reemplaza a `404` en un recurso ajeno.** Si un `odontologo` pide el turno de otro profesional, la respuesta es **`404`**, no `403` (RN-GL-05, US-038 CA-3). La distinción es deliberada: un `403` confirmaría que el recurso existe, y con eso ya leakaría información sobre la agenda de otros profesionales. El `403` queda reservado para el caso en que el **rol** no tiene la operación, sin importar de qué recurso se trate.

> El `409` derivado del constraint de exclusión de PostgreSQL (SQLSTATE `23P01`) se traduce en el backend a un cuerpo de error con detalle legible, nunca a un `500`. Es el punto más importante de la capa de traducción de errores y es verificable en la defensa.