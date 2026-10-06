# Turnos Odontología — Instrucciones para Agentes

> Este archivo (y su copia `CLAUDE.md`) es lo PRIMERO que todo agente lee al entrar al repo.
> Generado a partir de `knowledge-base/` y `CHANGES.md`. No editar a mano sin re-sincronizar ambos archivos.

---

## Stack Tecnológico

Stack **cerrado**: fue impuesto como condición de entrega (restricción **R-1**, DD-01). No sustituir componentes.

### Backend

| Capa | Tecnología | Versión mín. |
|------|------------|--------------|
| Lenguaje | Python | 3.12 |
| Web framework | FastAPI | 0.115 |
| Validación / schemas | Pydantic v2 | 2.9 |
| ORM | SQLAlchemy 2.0 (async) | 2.0 |
| Migraciones | Alembic | 1.13 |
| Auth | JWT (`python-jose` o `PyJWT`) + `passlib[bcrypt]` | — |
| Driver BD | asyncpg | 0.29 |
| Base de datos | **PostgreSQL 16** (fuente única de verdad) | 16 |
| Caché | Redis 7.2 — **declarado, sin uso funcional en el MVP** (DD-06) | 7.2 |
| Contenedores | Docker / Docker Compose v2 | — |

### Frontend

| Capa | Tecnología | Versión mín. |
|------|------------|--------------|
| UI | React | 18.3 |
| Lenguaje | TypeScript (tipado estricto) | 5.6 |
| Bundler / dev server | Vite | 6 |
| HTTP | `fetch` nativo envuelto en módulo propio (pieza didáctica: sin librería) | — |
| Estado global | React Context + `useReducer` (sin Redux) | — |
| Estilos | CSS Modules (sin framework de estilos) | — |

**Fuera del stack (y por qué)**: Next.js/SSR, Celery/RQ, Prisma/Drizzle, GraphQL, ORM de tipos compartido frontend↔backend. Motivos en [knowledge-base/02_descripcion_general.md](knowledge-base/02_descripcion_general.md).

**Integraciones externas en el MVP**: ninguna. WhatsApp, Mercado Pago, Google Calendar, AFIP/ARCA, SMTP y exportación están fuera de alcance (DD-07, DD-16).

Detalle completo: [knowledge-base/02_descripcion_general.md](knowledge-base/02_descripcion_general.md)

---

## Base de Conocimiento

La fuente de verdad del dominio vive en `knowledge-base/`. **Leé el archivo relevante ANTES de implementar.**

| Archivo | Cuándo leerlo |
|---------|---------------|
| [README.md](knowledge-base/README.md) | Índice, resumen ejecutivo, regla de oro y convenciones de códigos |
| [01_vision_y_objetivos.md](knowledge-base/01_vision_y_objetivos.md) | Propósito, alcance v1.0 y fuera de alcance (13 ítems) |
| [02_descripcion_general.md](knowledge-base/02_descripcion_general.md) | Stack, arquitectura, superficie de la API (43 endpoints) y códigos HTTP |
| [03_actores_y_roles.md](knowledge-base/03_actores_y_roles.md) | Auth, RBAC (3 roles), matriz de permisos y rutas públicas |
| [04_modelo_de_datos.md](knowledge-base/04_modelo_de_datos.md) | Entidades, ERD, constraints, índices y anti-solapamiento en la BD |
| [05_reglas_de_negocio.md](knowledge-base/05_reglas_de_negocio.md) | 67 reglas `RN-xx` y matriz endpoint → regla → HTTP |
| [06_funcionalidades.md](knowledge-base/06_funcionalidades.md) | 27 historias `US-xx` con criterios de aceptación |
| [07_flujos_principales.md](knowledge-base/07_flujos_principales.md) | 12 flujos E2E, incluidos los de concurrencia y error |
| [08_arquitectura_propuesta.md](knowledge-base/08_arquitectura_propuesta.md) | Patrones, estructura de las dos apps, Docker Compose, CORS, env vars |
| [09_decisiones_y_supuestos.md](knowledge-base/09_decisiones_y_supuestos.md) | 19 `DD-xx` con alternativas descartadas y 8 `SU-xx` |
| [10_preguntas_abiertas.md](knowledge-base/10_preguntas_abiertas.md) | ⚠️ `IN-xx` resueltas y `PA-xx` priorizadas (ver GATE abajo) |

> ⚠️ **GATE previo al primer change**: las `PA` de prioridad **Alta** deben estar respondidas. Por las decisiones vigentes ya están definidas: **PA-13** → clínica única, **sin** `clinica_id` en el modelo · **PA-01** → odontograma en el MVP **sin imágenes** (DD-04) · **PA-02** → agenda interna, **sin** reserva pública (DD-05) · **PA-06** → exportación fuera del MVP (DD-16) · **PA-07** → recordatorios/WhatsApp fuera del MVP (DD-07). Confirmar el cierre con el docente antes de `C-02`.

**Regla de oro**: si el código y la KB discrepan, **el código tiene un bug**. Ningún `docs/` ni comentario en el código redefine el alcance.

---

## Skills Disponibles

Fuente de verdad: `.atl/skill-registry.md` (generado por `skill-registry`).

| Agente | Rol | Skills que carga |
|--------|-----|------------------|
| **Backend Core** | FastAPI, dominio, modelo de datos, anti-solapamiento | `fastapi`, `postgresql-table-design`, `async-python-patterns`, `python-testing-patterns` |
| **Backend Aux** | Auth/RBAC, seguridad, contratos de API, tests | `auth-implementation-patterns`, `security-and-hardening`, `api-and-interface-design`, `tdd` |
| **Frontend** | React + TypeScript (Vite), performance de UI | `vercel-react-best-practices` |
| **Infra** | Docker / Docker Compose | `multi-stage-dockerfile` |
| **Orquestación** | Flujo de cambios OpenSpec | `openspec-propose`, `openspec-apply-change`, `openspec-archive-change` (`.opencode/skills/`, del orquestador) |

Cargá la skill correspondiente al contexto ANTES de escribir código.

> Los compact rules de cada skill los resuelve el orquestador desde `.atl/skill-registry.md` (generado por `skill-registry`; no versionado — no está en el repo). Esta tabla solo mapea skill→rol.

---

## Roadmap de Changes

El plan de implementación completo está en [CHANGES.md](CHANGES.md). Resumen:

- **Total**: **19 changes** (`C-01`…`C-19`) en **10 fases**, con **9 gates** de sincronización.
- **Camino crítico** (10 changes): `C-01 → C-02 → C-03 → C-05 → C-09 → C-10 → C-13 → C-14 → C-18 → C-19`.
- **Primer change**: `C-01` (`foundation-setup`) — después del GATE de preguntas de arriba.
- **Governance CRÍTICO**: `C-02` (modelo de datos + los 3 `EXCLUDE USING gist`), `C-03` (auth-rbac), `C-10` (reserva de turnos), `C-14` (auditoría).

**Antes de cualquier `/opsx:propose`**: leé [CHANGES.md](CHANGES.md), identificá las dependencias del change y los archivos de "Leer antes".

---

## Reglas Duras (específicas del proyecto)

> No existe un `~/.claude/CLAUDE.md` global en esta máquina: por eso las reglas universales de commit/build van acá hasta que se suban al global. Romper una regla de esta sección es un defecto. Formato `NUNCA X → hacer Y`.

### Dominio y alcance

- **NUNCA redefinir el alcance fuera de la KB** → si código y `knowledge-base/` discrepan, el código tiene el bug; los códigos `RN/US/DD/SU/PA/IN` son estables y los retirados (`RN-XP-*`, `RN-OD-10`) **nunca se reutilizan**.
- **NUNCA implementar fuera de alcance**: reserva pública, historia clínica, imágenes de odontograma, facturación, recordatorios/WhatsApp, exportación CSV, multi-sucursal (DD-04/05/07/12/16) → si una tarea lo pide, escalar como cambio de alcance vía `10_preguntas_abiertas.md`, no codear.
- **NUNCA usar Redis en el MVP** → está declarado sin uso funcional (DD-06); sin colas, workers ni tareas asíncronas.

### Arquitectura y stack

- **NUNCA unificar backend y frontend** (monolito, Next.js, BFF, código compartido) → dos aplicaciones separadas; la única interfaz es la API REST JSON bajo prefijo `/api/v1` (DD-01/DD-03).
- **NUNCA lógica de negocio en routers ni en el frontend** → routers declaran ruta + schema + dependencia de auth; las reglas `RN-xx` viven en servicios de dominio con estructura `app/{api,domain,infrastructure}` y dependencia `api → domain → infrastructure` (C-01).
- **NUNCA agregar tecnologías fuera del stack de `02_descripcion_general.md`** (Redux, Tailwind, GraphQL, ORM de TS, Prisma, Celery…) → frontend = React Context + `useReducer` + CSS Modules + `fetch` nativo envuelto.
- **NUNCA guardar sesión en cookies ni `localStorage`** → JWT stateless en `Authorization: Bearer` (RN-AU-06) y token en `sessionStorage` del cliente; no crear `POST /auth/logout` (RN-AU-07: no hay revocación).
- **NUNCA schema Pydantic de request sin `extra='forbid'`** → rechazar campos no declarados en el contrato.

### Datos y PostgreSQL

- **NUNCA garantizar el no-solapamiento sólo en código de aplicación** → la garantía son los 3 constraints `EXCLUDE USING gist` sobre `tstzrange(inicio, fin, '[)')` (`turno_no_solape_profesional/paciente/sillon`); cualquier conflicto de concurrencia es un caso de test obligatorio (métrica M-1).
- **NUNCA dejar pasar SQLSTATE `23P01` como `500`** → traducirlo a `409` con cuerpo legible (`SOLAPAMIENTO`).
- **NUNCA `DELETE` físico** → baja lógica con `activo BOOLEAN` (RN-GL-01); la auditoría y el historial del odontograma son **append-only** y sin endpoint de escritura.
- **NUNCA timestamps naive ni horas locales en la BD** → `TIMESTAMPTZ` en UTC; presentar en `America/Argentina/Buenos_Aires`; transmitir fechas en la API como ISO 8601 **con offset** (`2026-10-12T14:00:00-03:00`).
- **NUNCA enums con `CREATE TYPE`** → `VARCHAR` + `CHECK` (o tabla lookup); IDs `BIGINT GENERATED ALWAYS AS IDENTITY`, identificadores snake_case.

### Auth, RBAC y API

- **NUNCA devolver `403` por un recurso ajeno** → recurso inexistente, inactivo o de otro profesional responde `404` indistinguible (RN-GL-05); el `403` queda sólo para "rol sin esa operación" (RN-AU-02/04).
- **NUNCA query de agenda/pacientes sin el filtro de ownership para el rol odontólogo** → `profesional_id` obligatorio en las consultas (RN-AU-05); los guards del frontend son sólo UX, **la autoridad es el backend** (RN-AU-04).
- **NUNCA asumir que el rol viene sólo del token sin validación server-side** → `require_role(...)` en cada endpoint protegido; login público sólo en `POST /api/v1/auth/login` y `GET /api/v1/health`.

### Odontograma

- **NUNCA imágenes ni gráficos de piezas** → sólo estados por pieza con notación FDI y catálogo cerrado de estados (DD-04); `PUT /api/v1/pacientes/{id}/odontograma/{pieza}` es **idempotente** y el historial lo alimenta el servicio de dominio (RN-OD-07), sin endpoint de escritura propia.

### Flujo de trabajo y entorno

- **NUNCA proponer un change sin leer `CHANGES.md`** → respetar dependencias, gates y "Leer antes"; archivar con `/opsx:archive` y marcar `[x]` al terminar.
- **NUNCA invocar `openspec` desde el shim `.ps1`** → usar `openspec.cmd` (Execution Policy bloquea el `.ps1`); en PowerShell 5.1 no existen `grep/head/tail/wc` → usar `Select-String` / `Select-Object` / `Measure-Object`.
- **NUNCA buildear, commitear ni pushear sin pedido explícito** → commits convencionales, sin co-autoría de IA (reglas universales; el global aún no las cubre).

---

## Flujo de Trabajo

```
1. Leer la KB relevante (knowledge-base/)        → entender el dominio
2. Identificar el change en CHANGES.md           → respetar dependencias y gates
3. /opsx:propose C-NN-nombre                     → proposal + design + specs + tasks
4. Implementar las tasks (cargando skills)       → respetando las reglas duras
5. /opsx:archive C-NN-nombre + marcar [x]        → cerrar el change
```

Aplicar TODAS las reglas duras en cada paso. Ante conflicto entre la KB y este archivo, las reglas duras prevalecen.
