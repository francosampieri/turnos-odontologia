# CHANGES — Secuencia de Implementación

> Índice canónico de todos los changes del proyecto **Turnos Odontología**.
> Cada change es atómico: un agente puede implementarlo en una sesión (~4-6 horas).
> **Leer este archivo antes de ejecutar cualquier `/opsx:propose`.**

---

## Cómo usar este documento

1. Identificar el change a implementar (verificar que sus dependencias están en `openspec/changes/archive/`).
2. Leer los docs de la knowledge-base indicados en "Leer antes".
3. Ejecutar `/opsx:propose <nombre-del-change>`.
4. Al terminar el change, archivarlo con `/opsx:archive <nombre-del-change>`.
5. Marcar el checkbox `[x]` en este archivo.

### GATE previo — Preguntas bloqueantes (cerrar ANTES de escribir código)

`knowledge-base/10_preguntas_abiertas.md` § "Cómo se cierran estas preguntas" exige cerrar 5 preguntas antes del primer cambio. Ningún change las implementa: **las afectan** si la respuesta cambia el alcance o el modelo.

| PA | Pregunta | Cambios que toca si cambia la respuesta | Efecto |
|---|---|---|---|
| **PA-13** | ¿Segundo cliente / `clinica_id` en el modelo? | **C-02** (y todo lo demás) | Si es "sí", `clinica_id` atraviesa las 14 tablas, todos los endpoints y las pruebas de autorización. **Es la más cara de cerrar tarde.** |
| **PA-01** | ¿Imágenes del odontograma en fase 2? | C-13 | Fase 2 del módulo: almacenamiento binario + Ley 26.529. El MVP (DD-04) no la necesita. |
| **PA-02** | ¿Reserva online pública? | C-10, C-16 (futuro v1.x) | Subsistema completo (auth del paciente, rate limiting, anti-abuso). Hoy el MVP es agenda interna (DD-05). |
| **PA-06** | ¿Exportación CSV/Excel? | C-16, C-18 (futuro v1.1) | Privacidad por campo sobre DNI/fecha de nacimiento (DD-16). |
| **PA-07** | ¿Recordatorio WhatsApp? ¿Quién paga? | C-19 y futuro módulo de avisos | Activaría Redis como cola real (hoy declarado sin uso, DD-06) y un costo variable por mensaje (DD-07). |

> Mientras PA-13 no esté cerrada, **C-02 no se implementa**: es la única de las cinco que cambia código del MVP.

---

## Árbol de dependencias

```
C-01 foundation-setup
  └── C-02 core-data-model                     ← incluye los 3 EXCLUDE USING gist
        └── C-03 auth-rbac                     ← desbloquea TODO lo demás
              ├── C-04 usuarios-admin ────────────────────────────────────────┐
              ├── C-05 profesionales-horarios ──┬── C-07 feriados-bloqueos    │
              ├── C-06 servicios-sillones ──────┤                            │
              ├── C-08 pacientes ───────────────┤                            │
              └── C-15 frontend-shell           ▼                            │
                    │                    C-09 disponibilidad                 │
                    │                            │                           │
                    │                            ▼                           │
                    │                    C-10 reserva-turnos (C-08 + C-09)   │
                    │                       ├── C-11 ciclo-vida-turnos ──┐   │
                    │                       ├── C-12 sobreturno          │   │
                    │                       └── C-13 odontograma (+C-08) │   │
                    │                                   └───────┬─────────┘   │
                    │                                           ▼             │
                    │                              C-14 auditoria (C-04, C-11, C-13)
                    │                                           │             │
                    ├── C-16 frontend-agenda (C-10 + C-11 + C-12)            │
                    ├── C-17 frontend-pacientes-odontograma (C-08 + C-13)     │
                    └── C-18 frontend-config-auditoria (C-04..C-07 + C-14) ◄──┘
                                  └── C-19 seed-tests-docs (C-16 + C-17 + C-18)
```

### Paralelismo por fase

> Cada "gate" es un punto de sincronización. Los changes dentro de un grupo pueden ejecutarse en paralelo.

```
GATE 0: ninguna
  → C-01 foundation-setup                     [Agente A]

GATE 1: C-01 ✓
  → C-02 core-data-model                      [Agente A]

GATE 2: C-02 ✓
  → C-03 auth-rbac                            [Agente A]

GATE 3: C-03 ✓                                            ← PRIMER FORK (6 paralelos)
  → C-05 profesionales-horarios               [Agente A]
  → C-04 usuarios-admin                       [Agente B]
  → C-15 frontend-shell                       [Agente C]
  → C-06 servicios-sillones                   [Agente B — si C-04 ✓]
  → C-08 pacientes                            [Agente A — si C-05 ✓]
  → C-07 feriados-bloqueos                    [Agente B — si C-05 ✓]

GATE 4: C-05 ✓ + C-06 ✓ + C-07 ✓
  → C-09 disponibilidad                       [Agente A]

GATE 5: C-08 ✓ + C-09 ✓
  → C-10 reserva-turnos                       [Agente A]

GATE 6: C-10 ✓                                            ← FORK (3 paralelos)
  → C-11 ciclo-vida-turnos                    [Agente A]
  → C-13 odontograma                          [Agente B — si C-08 ✓]
  → C-12 sobreturno                           [Agente C]

GATE 7: C-11 ✓ + C-12 ✓ + C-13 ✓
  → C-14 auditoria                            [Agente A]

GATE 8: C-14 ✓ + C-15 ✓                                 ← FORK frontend (3 paralelos)
  → C-16 frontend-agenda                      [Agente C — si C-11 ✓ y C-12 ✓]
  → C-17 frontend-pacientes-odontograma       [Agente B — si C-13 ✓]
  → C-18 frontend-config-auditoria            [Agente A — si C-14 ✓]

GATE 9: C-16 ✓ + C-17 ✓ + C-18 ✓
  → C-19 seed-tests-docs                      [Todos]
```

### Camino crítico (10 changes — mínimo irreducible)

```
C-01 → C-02 → C-03 → C-05 → C-09 → C-10 → C-13 → C-14 → C-18 → C-19
```

> `C-06` y `C-07` corren en paralelo con `C-05` y cierran en el mismo gate (GATE 4): el camino pasa por el más largo de los tres. `C-05` es el eslabón representativo.

### Plan óptimo con 3 agentes

```
Paso │ Agente A (Backend Core)      │ Agente B (Backend Aux)       │ Agente C (Frontend)
─────┼──────────────────────────────┼──────────────────────────────┼─────────────────────────
  1  │ C-01 foundation-setup        │           —                  │           —
  2  │ C-02 core-data-model         │           —                  │           —
  3  │ C-03 auth-rbac               │           —                  │           —
  4  │ C-05 profesionales-horarios  │ C-04 usuarios-admin          │ C-15 frontend-shell
  5  │ C-08 pacientes               │ C-06 servicios-sillones      │           —
  6  │ C-09 disponibilidad          │ C-07 feriados-bloqueos       │           —
  7  │ C-10 reserva-turnos          │           —                  │           —
  8  │ C-11 ciclo-vida-turnos       │ C-13 odontograma             │ C-12 sobreturno
  9  │ C-14 auditoria               │           —                  │ C-16 frontend-agenda
 10  │           —                  │ C-17 frontend-pac.-odontogr. │ C-18 frontend-config
 11  │ C-19 seed-tests-docs         │ C-19 (suite pytest)          │ C-19 (README/recorrido)
```

---

## FASE 0 — Cimientos

### [C-01] `foundation-setup`
- **Estado**: `[ ]` pendiente
- **Scope**: Entorno reproducible completo + esqueleto de las dos aplicaciones
  - `docker-compose.yml` con 5 servicios: `db` (postgres:16-alpine + healthcheck `pg_isready`), `redis` (7-alpine, declarado **sin uso funcional** — DD-06), `api` (build `./backend`, puerto 8000), `web` (build `./frontend` con `build.args: VITE_API_URL`, `VITE_API_BASE` — no `environment`), `migrate` (`alembic upgrade head && python -m app.seed`, `depends_on: service_completed_successfully`)
  - `.env.example` **único en la raíz** (DATABASE_URL, JWT_SECRET_KEY, JWT_EXPIRATION_MINUTES, CORS_ORIGINS, POSTGRES_*, TIMEZONE_CLINICA, ENV) + `.gitignore` con `.env`
  - `backend/`: Dockerfile, `requirements.txt`, `alembic.ini` + env, `app/main.py` (FastAPI, CORS lista exacta desde `CORS_ORIGINS`, `allow_credentials=False`, exception handlers globales, `GET /api/v1/health` con chequeo de conexión), `app/core/config.py` (pydantic-settings), estructura `app/{api,domain,infrastructure}` según la regla `api → domain → infrastructure`
  - `frontend/`: Dockerfile (build Vite + nginx), `nginx.conf` (proxy `/api` → `http://api:8000/api`, sin envsubst), Vite + React + TypeScript, `src/main.tsx`, `App.tsx` mínimo
  - README.md mínimo con `docker compose up`
- **Dependencias**: ninguna
- **Governance**: BAJO
- **Leer antes**:
  - `knowledge-base/01_vision_y_objetivos.md` (qué es el sistema)
  - `knowledge-base/02_descripcion_general.md` §Stack
  - `knowledge-base/08_arquitectura_propuesta.md` §Estructura de directorios
  - `knowledge-base/08_arquitectura_propuesta.md` §Docker Compose — servicios

---

## FASE 1 — Modelo de datos y anti-solapamiento

### [C-02] `core-data-model`
- **Estado**: `[ ]` pendiente
- **Scope**: Las 14 tablas + la invariante central garantizada en la base
  - Modelos SQLAlchemy de las 14 entidades: `Rol`, `Usuario`, `Profesional`, `Servicio`, `ProfesionalServicio`, `Sillon`, `HorarioLaboral`, `Feriado`, `BloqueoProfesional`, `Paciente`, `Turno`, `Odontograma`, `OdontogramaMovimiento`, `Auditoria`
  - Migración Alembic 001: `BIGINT GENERATED ALWAYS AS IDENTITY`, enums como `VARCHAR` + `CHECK`, `TIMESTAMPTZ` en UTC, `activo BOOLEAN` (soft delete), `created_at/updated_at/created_by/updated_by`, FK `ON DELETE RESTRICT` hacia `turno`
  - `CREATE EXTENSION IF NOT EXISTS btree_gist`; `CHECK turno_fin_positivo (fin > inicio)`; los **3 `EXCLUDE USING gist` parciales** (`turno_no_solape_profesional`, `turno_no_solape_paciente`, `turno_no_solape_sillon`) sobre `tstzrange(inicio, fin, '[)')` con predicado `activo AND NOT es_sobreturno AND estado NOT IN ('CANCELADO','NO_ASISTIO')`
  - Índices: parcial `ix_turno_activos`, `UNIQUE(dni)`, `UNIQUE(paciente_id, numero)`, `INDEX(profesional_id, inicio)`, `INDEX(apellido, nombre)`
  - `infrastructure/db/base.py` + `session.py`: engine asyncpg, `get_db()` con commit/rollback por petición
  - `domain/auditoria/servicio.py` **mínimo**: `INSERT` append-only dentro de la transacción del llamador — los CA de auditoría de C-10 en adelante se cumplen desde su primer cambio; C-14 completa hooks y consulta
  - `app/scripts/test_concurrencia.py` (nivel base): dos `INSERT` concurrentes sobre el mismo slot → **exactamente un commit y un `ExclusionViolation` 23P01** (prueba de datos de la métrica M-1). La modalidad HTTP (una `201`, una `409`) se cierra en C-10
  - Tests: violación de cada constraint, turno cancelado **no** ocupa, sobreturno **sí** solapa
- **Dependencias**: C-01 *(requisito previo absoluto: PA-13 debe estar cerrada antes de arrancar)*
- **Governance**: CRITICO
- **Leer antes**:
  - `knowledge-base/04_modelo_de_datos.md` §El punto clave de diseño
  - `knowledge-base/04_modelo_de_datos.md` §Entidades
  - `knowledge-base/09_decisiones_y_supuestos.md` DD-03, DD-08, DD-09
  - `knowledge-base/10_preguntas_abiertas.md` IN-11
  - `knowledge-base/08_arquitectura_propuesta.md` §Migraciones, seed y verificación

---

## FASE 2 — Identidad y acceso

### [C-03] `auth-rbac`
- **Estado**: `[ ]` pendiente
- **Scope**: JWT stateless + bcrypt + RBAC en servidor (US-001, US-002, US-003)
  - `app/core/security.py`: hash bcrypt cost ≥ 12 (RN-AU-03), JWT HS256 con claims `sub`, `rol`, `iat`, `exp` (480 min por defecto), sin datos personales en el payload
  - `app/core/deps.py`: `get_current_user`, `require_role(...)`, `get_current_profesional` — filtro obligatorio por `profesional_id` en la consulta (RN-AU-05, base del RBAC de datos)
  - `POST /api/v1/auth/login` → `200` token + usuario · `401` genérico ("credenciales inválidas") · `403` si `activo = FALSE` · actualiza `ultimo_acceso`
  - `GET /api/v1/auth/me` → id, nombre, rol
  - `app/scripts/crear_admin.py` (primer usuario, para desbloquear el resto)
  - Ficheros `app/core/errors.py`: catálogo de errores de dominio + mapeo a HTTP (401/403/404/409/422)
  - Tests: login válido, `401`, `403` inactivo, token expirado, `403` por rol, `404` por recurso ajeno
- **Dependencias**: C-02
- **Governance**: CRITICO
- **Leer antes**:
  - `knowledge-base/03_actores_y_roles.md` (RBAC + matriz + rutas públicas)
  - `knowledge-base/05_reglas_de_negocio.md` §RN-AU
  - `knowledge-base/07_flujos_principales.md` §Flujo 1
  - `knowledge-base/08_arquitectura_propuesta.md` §Seguridad

---

### [C-04] `usuarios-admin`
- **Estado**: `[ ]` pendiente
- **Scope**: Administración de usuarios por el admin (US-004)
  - `GET/POST/PATCH /api/v1/usuarios` (admin): email único, nombre, rol válido entre los 3 (RN-AU-02), contraseña hasheada nunca visible (CA-2)
  - Alta de usuario con rol `odontologo` ofrece crear el `profesional` asociado en la misma operación (RN-PR-01)
  - Validación: no auto-desactivación (CA-4); desactivar profesional con turnos futuros no terminales → `409` (RN-PR-05)
  - Baja lógica de usuario (`activo = FALSE`), nunca `DELETE` (RN-GL-01)
  - Tests: CRUD, `403` a no-admin, no auto-desactivación, `409` con turnos futuros
- **Dependencias**: C-03
- **Governance**: MEDIO
- **Leer antes**:
  - `knowledge-base/06_funcionalidades.md` US-004
  - `knowledge-base/03_actores_y_roles.md` §Matriz de permisos
  - `knowledge-base/04_modelo_de_datos.md` §usuario, §profesional
  - `knowledge-base/09_decisiones_y_supuestos.md` DD-13

---

## FASE 3 — Datos maestros de la clínica

> Los tres changes son paralelos tras GATE 3. C-07 depende además de C-05 (los bloqueos cuelgan de un profesional).

### [C-05] `profesionales-horarios`
- **Estado**: `[ ]` pendiente
- **Scope**: Alta de profesionales y ventanas horarias (US-010, US-011)
  - `GET/POST/PATCH /api/v1/profesionales`: alta **sin cuenta** (`usuario_id = NULL` hasta que el admin la cree — RN-PR-01), `CHECK color_agenda ~ '^#[0-9A-Fa-f]{6}$'`, baja lógica con `409` si tiene turnos (RN-PR-05)
  - `GET/PUT /api/v1/profesionales/{id}/horarios`: **reemplazo atómico** del conjunto completo de ventanas (borra e inserta en una transacción — Flujo 11)
  - Validaciones: solapes de ventanas del mismo día → `422` (RN-HO-02), domingo → `422` (RN-HO-04), `hora_fin > hora_inicio`
  - Defaults: Lun–Vie `08:00–18:00`, **sábado vacío** (RN-HO-01, US-011 CA-1)
  - Tests: reemplazo atómico, ventana en domingo, ventanas solapadas, `403` a secretaria en escritura de horarios
- **Dependencias**: C-03
- **Governance**: MEDIO
- **Leer antes**:
  - `knowledge-base/04_modelo_de_datos.md` §profesional, §horario_laboral
  - `knowledge-base/06_funcionalidades.md` US-010, US-011
  - `knowledge-base/05_reglas_de_negocio.md` §RN-HO, §RN-PR
  - `knowledge-base/07_flujos_principales.md` §Flujo 11

---

### [C-06] `servicios-sillones`
- **Estado**: `[ ]` pendiente
- **Scope**: Catálogo de prácticas con duración y gabinete (US-012, US-013)
  - `GET/POST/PATCH /api/v1/servicios`: `duracion_min IN (15, 30, 45, 60)` default 30 (RN-PR-02), nombre único entre activos, `409` si tiene turnos futuros no terminales (CA-5)
  - `PUT /api/v1/profesionales/{id}/servicios/{sid}`: override de duración, **sólo admin** (RN-PR-03); helper `domain/profesionales/duracion.py` con `duracion_efectiva(profesional, servicio)`
  - `GET/POST/PATCH /api/v1/sillones`: cantidad configurable (RN-SI-01), nombre único entre activos, `409` con turnos futuros (RN-SI-05)
  - Tests: `CHECK` de duración, resolución de duración efectiva, `409`s, `403` a secretaria en override
- **Dependencias**: C-03
- **Governance**: BAJO
- **Leer antes**:
  - `knowledge-base/04_modelo_de_datos.md` §servicio, §profesional_servicio, §sillon
  - `knowledge-base/06_funcionalidades.md` US-012, US-013
  - `knowledge-base/05_reglas_de_negocio.md` §RN-PR, §RN-SI
  - `knowledge-base/09_decisiones_y_supuestos.md` DD-10, DD-15

---

### [C-07] `feriados-bloqueos`
- **Estado**: `[ ]` pendiente
- **Scope**: Días no atendidos (US-014, US-015)
  - `GET/POST/PATCH/DELETE /api/v1/feriados`: `UNIQUE(fecha)`, tipos `NACIONAL|LOCAL`; `POST` con turnos futuros → `409` con **cantidad de turnos afectados** (RN-FE-04); `PATCH` editar (fecha duplicada → `409`), `DELETE` = baja lógica auditada (RN-FE-06); **sin API externa** (DD-18)
  - `GET/POST/DELETE /api/v1/profesionales/{id}/bloqueos`: rango inclusivo `[desde, hasta]`, `CHECK (hasta >= desde)` → `422` (RN-FE-05)
  - Feriado transversal a toda la clínica vs bloqueo por profesional (RN-FE-02)
  - Tests: feriado duplicado, `409` con turnos, baja lógica, bloqueo invertido, `403` a no-admin
- **Dependencias**: C-03, C-05
- **Governance**: BAJO
- **Leer antes**:
  - `knowledge-base/04_modelo_de_datos.md` §feriado, §bloqueo_profesional
  - `knowledge-base/06_funcionalidades.md` US-014, US-015
  - `knowledge-base/05_reglas_de_negocio.md` §RN-FE
  - `knowledge-base/09_decisiones_y_supuestos.md` DD-18

---

## FASE 4 — Pacientes

### [C-08] `pacientes`
- **Estado**: `[ ]` pendiente
- **Scope**: Ficha, búsqueda y baja lógica (US-020, US-021, US-022, US-023)
  - `POST /api/v1/pacientes`: normalización de DNI a dígitos (`domain/pacientes/normalizacion.py`, RN-PC-02), `UNIQUE(dni)` → `23505` traducido a `409` "ya existe un paciente con ese DNI", `fecha_nacimiento <= CURRENT_DATE` → `422`, teléfono obligatorio, email opcional validado
  - `GET /api/v1/pacientes?dni=&apellido=&telefono=`: **paginado**, ignora mayúsculas/acentos/guiones, sólo activos, **DNI enmascarado `****5678`** por defecto (Ley 25.326)
  - `GET /api/v1/pacientes/{id}`: ficha con próximos turnos e historial; el odontologo sólo desde un turno propio, `404` si no (RN-AU-05)
  - `PATCH` + `DELETE` (baja lógica): DNI inmutable si tiene turnos → `409`; turnos no terminales → `409`; turnos/odontograma se conservan (RN-PC-08)
  - Tests: 409 duplicado, normalización, enmascaramiento, 404 inactivo, 403 a odontologo en listado
- **Dependencias**: C-03
- **Governance**: MEDIO
- **Leer antes**:
  - `knowledge-base/04_modelo_de_datos.md` §paciente
  - `knowledge-base/06_funcionalidades.md` US-020 a US-023
  - `knowledge-base/05_reglas_de_negocio.md` §RN-PC
  - `knowledge-base/07_flujos_principales.md` §Flujo 2, §Flujo 12
  - `knowledge-base/08_arquitectura_propuesta.md` §Datos sensibles de salud — Ley 25.326

---

## FASE 5 — Agenda y turnos (el núcleo)

### [C-09] `disponibilidad`
- **Estado**: `[ ]` pendiente
- **Scope**: Cálculo de slots libres (US-032)
  - `domain/turnos/disponibilidad.py`: `ventana horaria − feriados − bloqueos − turnos activos`, alineado a la **duración efectiva** (override → servicio), rangos semiabiertos `[inicio, fin)`
  - `GET /api/v1/disponibilidad?fecha=&profesional_id=&servicio_id=`
  - Sin disponibilidad → **lista vacía con motivo** (`"feriado"`, `"el profesional no atiende ese día"`, `"bloqueo"`), nunca error (CA-2/CA-3)
  - No reserva el slot (CA-4)
  - Tests unitarios: sábado vacío, domingo, feriado, bloqueo, servicio de 45 sobre ventana de 30, último slot que termina exacto en el fin de ventana
- **Dependencias**: C-05, C-06, C-07
- **Governance**: ALTO
- **Leer antes**:
  - `knowledge-base/07_flujos_principales.md` §Flujo 3
  - `knowledge-base/04_modelo_de_datos.md` §horario_laboral
  - `knowledge-base/05_reglas_de_negocio.md` §RN-HO (RN-HO-03, RN-HO-05), §RN-FE-03/05
  - `knowledge-base/06_funcionalidades.md` US-032
  - `knowledge-base/09_decisiones_y_supuestos.md` DD-10

---

### [C-10] `reserva-turnos`
- **Estado**: `[ ]` pendiente
- **Scope**: La operación central del sistema (US-033) + lectura de agenda
  - `POST /api/v1/turnos`: en **una transacción** — duración efectiva → `fin = inicio + duración`; validaciones `422` (pasado, fuera de ventana, feriado, bloqueo, sillón inactivo, paciente inactivo); comprobación previa para elegir mensaje y **asignar sillón libre**; `INSERT` → evaluación GiST → `201`
  - `domain/turnos/solapamiento.py`: captura `SQLSTATE 23P01` → `409` con `{detail, codigo: "SOLAPAMIENTO", recurso: "profesional|paciente|sillon", conflicto}` (Flujo 5)
  - Auditoría en la misma transacción (servicio de C-02) — US-033 CA-7
  - `GET /api/v1/turnos?fecha=&profesional_id=`, `GET /api/v1/turnos/semana?desde=&hasta=`, `GET /api/v1/turnos/{id}` con filtro obligatorio del odontologo y `404` para turno ajeno (RN-AU-05, RN-GL-05)
  - `app/scripts/test_concurrencia.py` **modalidad HTTP**: dos `POST` simultáneos sobre el mismo slot → exactamente **una `201` y una `409`** — métrica **M-1**
  - Tests: `409` en cada uno de los 3 ejes, `422` de cada regla, concurrencia CA-6
- **Dependencias**: C-08, C-09
- **Governance**: CRITICO
- **Leer antes**:
  - `knowledge-base/04_modelo_de_datos.md` §turno, §El punto clave de diseño
  - `knowledge-base/07_flujos_principales.md` §Flujo 4, §Flujo 5, §Flujo 6
  - `knowledge-base/05_reglas_de_negocio.md` §RN-TU
  - `knowledge-base/06_funcionalidades.md` US-033
  - `knowledge-base/09_decisiones_y_supuestos.md` DD-08

---

### [C-11] `ciclo-vida-turnos`
- **Estado**: `[ ]` pendiente
- **Scope**: Cancelar, reprogramar y máquina de estados (US-034, US-035, US-036, US-038)
  - `domain/turnos/estados.py`: máquina de **7 estados** + tabla de transiciones (RN-TU-07), estados finales sin salida
  - `POST /api/v1/turnos/{id}/cancelar`: estado → `cancelado`, **liberación automática** por exclusión parcial del GiST (US-034 CA-2), anticipación ≥ 2 h → `422` (RN-CA-03), odontologo → `403` (RN-CA-04), registra `cancelado_por` + motivo
  - `POST /api/v1/turnos/{id}/reprogramar`: **una sola transacción** — `INSERT` del nuevo con `origen_turno_id` + `UPDATE` del anterior a `cancelado` (motivo "reprogramado"); destino ocupado → `409` y **rollback total** (RN-CA-05)
  - `PATCH /api/v1/turnos/{id}/estado`: transición válida → `200`, ilegal → `422`; odontologo sólo `en_curso|completado|no_asistio` sobre turno propio
  - `GET /api/v1/turnos/{id}` con **acciones calculadas en servidor** según rol, estado y anticipación (US-038 CA-2)
  - Tests: transición ilegal, 2 h de anticipación, reprogramación atómica, slot liberado tras cancelar
- **Dependencias**: C-10
- **Governance**: MEDIO
- **Leer antes**:
  - `knowledge-base/07_flujos_principales.md` §Flujo 7, §Flujo 8, §Flujo 9
  - `knowledge-base/05_reglas_de_negocio.md` §RN-CA, §RN-TU-07
  - `knowledge-base/06_funcionalidades.md` US-034, US-035, US-036, US-038
  - `knowledge-base/09_decisiones_y_supuestos.md` DD-14

---

### [C-12] `sobreturno`
- **Estado**: `[ ]` pendiente
- **Scope**: La única excepción controlada al anti-solapamiento (US-037)
  - `POST /api/v1/turnos/sobreturno`: **endpoint separado** del de reserva (CA-3), motivo obligatorio → `422` si falta, estado `sobreturno`, `es_sobreturno = TRUE`
  - Único escritor del flag `es_sobreturno` (RN-TU-11); respeta `CHECK (es_sobreturno = FALSE OR estado = 'SOBRETURNO')`
  - Auditoría de la acción sensible (RN-GL-04)
  - Tests: se solapa sobre un slot ocupado → `201`; `POST /turnos` normal no puede marcar sobreturno; sin motivo → `422`; `403` a odontologo
- **Dependencias**: C-10
- **Governance**: ALTO
- **Leer antes**:
  - `knowledge-base/04_modelo_de_datos.md` §turno
  - `knowledge-base/05_reglas_de_negocio.md` §RN-TU-10, §RN-TU-11
  - `knowledge-base/09_decisiones_y_supuestos.md` DD-11
  - `knowledge-base/10_preguntas_abiertas.md` IN-06
  - `knowledge-base/06_funcionalidades.md` US-037

---

## FASE 6 — Odontograma

### [C-13] `odontograma`
- **Estado**: `[ ]` pendiente
- **Scope**: Piezas y estados con historial append-only, **sin imágenes** (US-040, US-041, US-042)
  - `domain/odontograma/catalogos.py`: 12 estados (RN-OD-03) y 6 caras (RN-OD-04)
  - `GET /api/v1/pacientes/{id}/odontograma` — 32 piezas FDI 11..48
  - `PUT /api/v1/pacientes/{id}/odontograma/{pieza}`: **idempotente** (RN-OD-06); sólo odontologo con **turno no terminal** con el paciente → `403` (RN-OD-05); `422` fuera de catálogo o pieza 55; en una transacción: upsert en `odontograma` + `INSERT` en `odontograma_movimiento` (estado anterior/nuevo, autor, fecha)
  - `GET .../{pieza}/historial`: orden cronológico inverso, inmutable — **sin endpoint de escritura ni borrado** (RN-OD-07)
  - Sin `bytea`, sin rutas de archivo, sin adjuntos (DD-04, RN-OD-08); odontograma de paciente inactivo congelado (RN-OD-09)
  - Tests: idempotencia (no duplica historial), `403` sin turno propio, `422` pieza/cara/estado inválido, inmutabilidad del historial
- **Dependencias**: C-08, C-10
- **Governance**: ALTO
- **Leer antes**:
  - `knowledge-base/04_modelo_de_datos.md` §odontograma, §odontograma_movimiento
  - `knowledge-base/05_reglas_de_negocio.md` §RN-OD
  - `knowledge-base/06_funcionalidades.md` US-040, US-041, US-042
  - `knowledge-base/07_flujos_principales.md` §Flujo 10
  - `knowledge-base/09_decisiones_y_supuestos.md` DD-04

---

## FASE 7 — Auditoría

### [C-14] `auditoria`
- **Estado**: `[ ]` pendiente
- **Scope**: Trazabilidad completa append-only (US-005) — DD-17 la incluye pese a la "prioridad baja" del Discovery
  - Completa `domain/auditoria/servicio.py`: registro desde **todos** los flujos que modifican agenda (crear, reprogramar, cancelar, cambiar estado, sobreturno) y **configuración** (usuarios, profesionales, horarios, servicios, sillones, feriados, bloqueos) — RN-GL-04
  - `GET /api/v1/auditoria?entidad=&usuario_id=&desde=&hasta=` (sólo admin): filtros por entidad, usuario y rango; muestra usuario, entidad, acción, fecha, estado anterior/posterior (CA-1/CA-2)
  - **Sin datos sensibles completos** en `datos_antes/datos_despues` (DNI completo, fecha de nacimiento) — CA-3, Ley 25.326
  - Sin ninguna operación de escritura ni borrado: la tabla no tiene `updated_at` ni `activo` — CA-4
  - Nota: la tabla y el servicio mínimo de escritura nacieron en **C-02** para que US-033 CA-7 se cumpla desde C-10; este change agrega los hooks de configuración y el endpoint de consulta
  - Tests: `403` a no-admin, sin endpoints de escritura, `GET` no genera registro, redacción de sensibles
- **Dependencias**: C-04, C-11, C-13
- **Governance**: CRITICO
- **Leer antes**:
  - `knowledge-base/04_modelo_de_datos.md` §auditoria
  - `knowledge-base/05_reglas_de_negocio.md` §RN-GL-03, §RN-GL-04
  - `knowledge-base/06_funcionalidades.md` US-005
  - `knowledge-base/09_decisiones_y_supuestos.md` DD-17
  - `knowledge-base/03_actores_y_roles.md` §Matriz de permisos

---

## FASE 8 — Frontend

> GATE 8 abre tres ramas de UI en paralelo. Los guards por rol son UX, no seguridad: la autoridad sigue siendo el backend (RN-AU-04).

### [C-15] `frontend-shell`
- **Estado**: `[ ]` pendiente
- **Scope**: Base de la SPA + sesión + guards (US-001, US-002, US-003)
  - `src/api/client.ts`: fetch envuelto con `Authorization: Bearer`, manejo unificado de `401` (→ `/login`), `403`, `404`, `409`, `422`
  - `auth/AuthContext.tsx` (usuario, rol, login, logout) + token en `sessionStorage` (RN-AU-06), logout cliente (US-002)
  - `auth/RequireRole.tsx` + rutas/guards en `App.tsx`; menú construido desde el rol del token (US-003 CA-1)
  - `pages/LoginPage.tsx` con declaración de tratamiento de datos (Ley 25.326)
  - `shared/`: components (Boton, Modal, Tabla, Badge, ConfirmDialog, Toast), hooks (`useApi`, `useDebounce`), utils (`fecha.ts`, `zonaHoraria.ts` con `America/Argentina/Buenos_Aires`, `dni.ts`, `errores.ts`), CSS Modules
  - Verificación: odontologo no llega a `/pacientes` por URL y el backend responde `403` al HTTP directo
- **Dependencias**: C-01, C-03
- **Governance**: MEDIO
- **Leer antes**:
  - `knowledge-base/08_arquitectura_propuesta.md` §Estructura de directorios (frontend)
  - `knowledge-base/03_actores_y_roles.md` §Mapa de pantallas por rol
  - `knowledge-base/06_funcionalidades.md` US-001, US-002, US-003
  - `knowledge-base/05_reglas_de_negocio.md` §RN-AU (RN-AU-06)

---

### [C-16] `frontend-agenda`
- **Estado**: `[ ]` pendiente
- **Scope**: Las pantallas de las que viven secretaria y odontólogo (US-030 a US-038)
  - `features/agenda/AgendaDia.tsx` (US-030): columna por profesional activo, turno con hora/paciente/servicio/sillón/estado con color, terminales filtrables, odontologo **forzado a su columna**, detalle con acciones por rol, 200 turnos < 1 s
  - `AgendaSemana.tsx` (US-031): 7 días, filtro por profesional, **sin edición en lote**
  - `Disponibilidad.tsx` (US-032): slots libres con motivo de no disponibilidad
  - `TurnoForm.tsx` (US-033): en `409` muestra mensaje y **recarga la disponibilidad** (Flujo 5.1)
  - `TurnoDetalle.tsx` (US-038) + acciones cancelar/reprogramar/cambiar estado/sobreturno (US-034…US-037) con confirmación
  - Validación en cliente sólo para UX; el backend es la autoridad
- **Dependencias**: C-10, C-11, C-12, C-15
- **Governance**: ALTO
- **Leer antes**:
  - `knowledge-base/08_arquitectura_propuesta.md` §features/agenda
  - `knowledge-base/06_funcionalidades.md` Épica 4 (US-030 a US-038)
  - `knowledge-base/03_actores_y_roles.md` §Mapa de pantallas
  - `knowledge-base/07_flujos_principales.md` §Flujo 5 (recarga tras 409)

---

### [C-17] `frontend-pacientes-odontograma`
- **Estado**: `[ ]` pendiente
- **Scope**: Ficha de pacientes y odontograma (US-020 a US-023, US-040 a US-042)
  - `features/pacientes/`: `PacienteLista.tsx` (búsqueda paginada de un campo, DNI enmascarado), `PacienteForm.tsx` (alta/edición con normalización de DNI en cliente), `PacienteDetalle.tsx` (datos, próximos turnos, historial, enlace al odontograma)
  - `features/odontograma/Odontograma.tsx` (US-040): 32 piezas FDI en arco superior e inferior, estado con color y sigla, `sano` inicial
  - `PiezaCelda.tsx` (US-041): selector de los 12 estados + cara opcional; **ninguna pantalla ofrece cargar imágenes** (CA-6)
  - `PiezaHistorial.tsx` (US-042): cronológico inverso, inmutable
  - `odontograma/catalogo.ts`: colores y siglas de los 12 estados
  - El odontologo entra desde un turno propio, no desde el listado global
- **Dependencias**: C-08, C-13, C-15
- **Governance**: MEDIO
- **Leer antes**:
  - `knowledge-base/06_funcionalidades.md` Épica 3, Épica 5
  - `knowledge-base/04_modelo_de_datos.md` §odontograma
  - `knowledge-base/08_arquitectura_propuesta.md` §features/pacientes, §features/odontograma
  - `knowledge-base/03_actores_y_roles.md` §Mapa de pantallas

---

### [C-18] `frontend-config-auditoria`
- **Estado**: `[ ]` pendiente
- **Scope**: Pantallas de configuración del admin y de auditoría (US-004, US-005, US-010 a US-015)
  - `features/config/`: `Usuarios.tsx`, `Profesionales.tsx`, `Horarios.tsx` (ventanas por día con default y sábado vacío), `Servicios.tsx` (duracion efectiva visible), `Sillones.tsx`, `Feriados.tsx`, `Bloqueos.tsx`
  - `Auditoria.tsx` (US-005): **sólo lectura**, filtros por entidad, usuario y rango de fechas; muestra estado anterior/posterior
  - Errores `409` traducidos a mensajes accionables (ej. feriado con turnos afectados: mostrar la cantidad)
  - Guards de ruta por rol (`admin` para configuración/auditoría, `secretaria` para profesionales/servicios)
- **Dependencias**: C-04, C-05, C-06, C-07, C-14, C-15
- **Governance**: BAJO
- **Leer antes**:
  - `knowledge-base/03_actores_y_roles.md` §Mapa de pantallas
  - `knowledge-base/06_funcionalidades.md` Épica 2, US-004, US-005
  - `knowledge-base/08_arquitectura_propuesta.md` §features/config
  - `knowledge-base/07_flujos_principales.md` §Flujo 11, §Flujo 12

---

## FASE 9 — Cierre: seed, tests y documentación

### [C-19] `seed-tests-docs`
- **Estado**: `[ ]` pendiente
- **Scope**: Demostrabilidad y verificación de todo el sistema
  - `app/seed.py` **idempotente** (upsert por clave natural, transacción propia, bcrypt **antes** de insertar): 3 roles · 4 usuarios (admin, secretaria, 2 odontólogos) · 2 profesionales · 2 sillones · 6 servicios + 1 override de duración · 10 filas de `horario_laboral` (**sábado vacío**) · 8–12 feriados nacionales del año en curso · 5 pacientes ficticios · 8–12 turnos de la semana en curso en varios estados · 3–6 piezas de odontograma + sus movimientos · **auditoría sin sembrar**
  - Suite pytest: **unitarios** (normalización DNI/teléfono, duración efectiva, cálculo de slots, máquina de estados), **integración** (`httpx.AsyncClient` contra base en contenedor, incluidos `409`), **concurrencia** (una `201` / una `409` — M-1)
  - Verificación: `GET /api/v1/health`, `/docs` deshabilitado con `ENV=production`, `JWT_SECRET_KEY` obligatoria en producción
  - README.md completo: arranque con `docker compose up`, credenciales del seed, **recorrido de defensa cronometrado** (login → agenda del día → reserva → conflicto → cancelación → odontograma), métricas del proyecto (M-1)
- **Dependencias**: C-16, C-17, C-18
- **Governance**: ALTO
- **Leer antes**:
  - `knowledge-base/04_modelo_de_datos.md` §Seed data inicial, §Reglas del seed
  - `knowledge-base/08_arquitectura_propuesta.md` §Migraciones, seed y verificación, §Estrategia de pruebas
  - `knowledge-base/01_vision_y_objetivos.md` (métrica M-1)
  - `knowledge-base/09_decisiones_y_supuestos.md` DD-19 (el criterio de éxito es la defensa)

---

## Resumen

| Change | Nombre | FASE | Dependencias | Governance |
|---|---|---|---|---|
| C-01 | foundation-setup | 0 | — | BAJO |
| C-02 | core-data-model | 1 | C-01 | CRITICO |
| C-03 | auth-rbac | 2 | C-02 | CRITICO |
| C-04 | usuarios-admin | 2 | C-03 | MEDIO |
| C-05 | profesionales-horarios | 3 | C-03 | MEDIO |
| C-06 | servicios-sillones | 3 | C-03 | BAJO |
| C-07 | feriados-bloqueos | 3 | C-03, C-05 | BAJO |
| C-08 | pacientes | 4 | C-03 | MEDIO |
| C-09 | disponibilidad | 5 | C-05, C-06, C-07 | ALTO |
| C-10 | reserva-turnos | 5 | C-08, C-09 | CRITICO |
| C-11 | ciclo-vida-turnos | 5 | C-10 | MEDIO |
| C-12 | sobreturno | 5 | C-10 | ALTO |
| C-13 | odontograma | 6 | C-08, C-10 | ALTO |
| C-14 | auditoria | 7 | C-04, C-11, C-13 | CRITICO |
| C-15 | frontend-shell | 8 | C-01, C-03 | MEDIO |
| C-16 | frontend-agenda | 8 | C-10, C-11, C-12, C-15 | ALTO |
| C-17 | frontend-pacientes-odontograma | 8 | C-08, C-13, C-15 | MEDIO |
| C-18 | frontend-config-auditoria | 8 | C-04, C-05, C-06, C-07, C-14, C-15 | BAJO |
| C-19 | seed-tests-docs | 9 | C-16, C-17, C-18 | ALTO |

**19 changes · 10 fases · 9 gates · camino crítico de 10 changes.**

**Primer change recomendado**: `C-01` (`foundation-setup`) — después de cerrar **PA-13**.

Para arrancar: `/opsx:propose C-01-foundation-setup`
