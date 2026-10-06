# Actores y Roles

## Actores del sistema

| Actor | Descripción | Verbo principal | Cómo interactúa con el sistema |
|---|---|---|---|
| **Secretaria / recepción** | Personal administrativo de la clínica. Es quien atiende el teléfono y agenda. En el MVP es la **única persona que escribe turnos**. | **Agendar** | Accede con usuario y contraseña. Opera la agenda del día y de la semana, da de alta y da de baja pacientes, crea, reprograma y cancela turnos, y mantiene el padrón de profesionales y servicios. **No** toca la configuración de la clínica: horarios, feriados, duraciones, sillones y usuarios son del `admin`. |
| **Odontólogo (profesional)** | Profesional de la salud que atiende. Cada uno tiene su propio horario laboral y su propia agenda. | **Atender** | Accede con su propio usuario. Ve **únicamente** su propia agenda. Registra el estado de las piezas en el odontograma de los pacientes que tiene en turno. No puede crear, reprogramar ni cancelar turnos. |
| **Administrador / dueño** | Responsable de la clínica. Hace de superset de los otros dos roles. | **Administrar** | Accede con su propio usuario. Ve la agenda de **todos** los profesionales, administra usuarios, horarios, feriados, servicios, sillones y bloqueos, y consulta la auditoría. |
| **Paciente** *(indirecto)* | Persona que recibe la atención. | **Reservar** | **No es usuario del sistema en el MVP.** No hay cuenta, ni login, ni portal del paciente. La reserva la realiza la secretaria; el paciente recibe los datos del turno por el canal que use la clínica (teléfono, WhatsApp personal). Ver DD-05. |

### Por qué tres roles y no uno

La separación de roles no es cosmética. Si un solo rol hiciera todo, el odontólogo terminaría cargando los turnos de recepción — exactamente el problema que el sistema viene a resolver. El Discovery registró esto como un ajuste obligatorio al alcance original, no como un extra.

### Por qué el paciente no tiene usuario

Agregar al paciente como usuario introduce un problema que el MVP no necesita: **autenticación de un actor no confiable**. Un paciente que se autentica habilita reserva pública, que a su vez exige anti-abuso (rate limiting, verificación de teléfono, captcha) y manejo de concurrencia sobre el último horario disponible — el riesgo técnico que el Discovery identificó como *"la parte más difícil del MVP, no la más fácil"*. La decisión y sus consecuencias están en DD-05.

---

## RBAC — Matriz de permisos

**Roles:** exactamente tres, fijos, cargados por seed. No hay gestión de roles desde la interfaz (DD-13).

### Leyenda

- `C` = crear · `R` = leer · `U` = actualizar · `D` = eliminar (baja lógica) · `—` = sin permiso
- `*` = permiso condicionado: el alcance se restringe a los recursos propios

### Matriz por recurso

| Recurso | `secretaria` | `odontologo` | `admin` | Reglas |
|---|:---:|:---:|:---:|---|
| **Usuario** | R (sólo el propio) | R (sólo el propio) | C R U D | RN-AU-02 |
| **Rol** (catálogo) | R | R | R | Sólo lectura: los roles no se crean ni se editan (DD-13) |
| **Paciente** | C R U D | R\* | C R U D | RN-PC-07 |
| **Profesional** | C R U D | R | C R U D | RN-PR-05 |
| **Horario laboral** | R | R | C R U D | RN-HO-01 |
| **Servicio** | C R U D | R | C R U D | RN-PR-02/04 |
| **Override de duración por profesional** | R | R | C R U D | RN-PR-03 |
| **Sillón** | R | R | C R U D | RN-SI-01/04/05 |
| **Feriado** | R | R | C R U D | RN-FE-01/06 |
| **Bloqueo por profesional** | R | R | C R U D | RN-FE-05 |
| **Turno — crear** | **C** | — | **C** | RN-CA-04 |
| **Turno — reprogramar** | **U** | — | **U** | RN-CA-02/04 |
| **Turno — cancelar** | **U** | — | **U** | RN-CA-01/04 |
| **Turno — cambiar estado** | U | U\* (sólo `en_curso`, `completado`, `no_asistió` sobre turno propio) | U | RN-TU-07 |
| **Turno — sobreturno** | **C** | — | **C** | RN-TU-10 |
| **Turno — leer** | R (todos) | R\* (sólo propios) | R (todos) | RN-AU-05 |
| **Odontograma — leer** | R | R\* (sólo pacientes con turno propio) | R | RN-OD-05 |
| **Odontograma — escribir** | R (sólo lectura) | U\* (sólo pacientes con turno propio) | R (sólo lectura) | RN-OD-05 |
| **Odontograma — historial** | R | R\* | R | RN-OD-07 |
| **Auditoría** | — | — | R | RN-GL-04 |

### Detalle de los permisos condicionados (`*`)

| Regla | Comportamiento exacto | Por qué importa |
|---|---|---|
| **RN-AU-05** | El odontólogo **no puede ver turnos de otros profesionales**. El filtro por `profesional_id` se aplica **en la capa de datos** (en la consulta SQL y, además, en la dependencia de autorización), **no** en un `where` del frontend. Si sólo se filtrara en el cliente, cualquier `GET /api/v1/turnos` sin filtro devolvería la agenda completa. | Es la diferencia entre "el botón está oculto" y "el dato no sale del servidor". Verificable en la defensa con una petición directa sin `profesional_id`. |
| **RN-OD-05** | El odontólogo sólo puede escribir en el odontograma de un paciente si tiene algún turno no terminal con ese paciente. La condición se verifica en el servicio de dominio antes de escribir. | Evita que un profesional modifique la ficha de un paciente al que nunca atiende, y es coherente con la separación de responsabilidades entre recepción y clínica. |
| **RN-CA-04** | Sólo `secretaria` y `admin` pueden **cancelar y reprogramar**. El odontólogo no puede liberar un horario, ni aunque sea su propio turno. | La cancelación es una operación de recepción con consecuencia sobre el ingreso. El odontólogo, en cambio, sí puede registrar `no_asistió` o `completado` sobre su propio turno: son hechos clinicalos, no decisiones de agenda. |
| **RN-TU-07 (parcial)** | El odontólogo puede llevar su turno a `en_curso`, `completado` y `no_asistió`. **No** puede volver a `agendado` ni `confirmado`. | El odontólogo marca hechos; la secretaria gestiona el ciclo de vida del turno en la agenda. |

### Permisos sobre el usuario propio

Ningún rol puede editarse a sí mismo en los campos de rol ni de estado. Sólo un `admin` puede cambiar roles, y un usuario **no puede desactivar su propia cuenta** (evita dejar la clínica sin acceso).

---

## Rutas públicas

Tres rutas y ninguna más. **No hay ninguna ruta pública que escriba datos de negocio.**

| Ruta | Propósito | Por qué es pública |
|---|---|---|
| `GET /api/v1/health` | Health check. Reporta estado del servicio y de la conexión a PostgreSQL. | Los contenedores y cualquier monitorización necesitan consultar salud sin credenciales |
| `POST /api/v1/auth/login` | Autentica usuario y devuelve el JWT. | Es el punto de entrada inevitable; no expone datos del sistema más allá de "credenciales válidas / inválidas" |
| `GET /docs` · `GET /openapi.json` | Documentación interactiva de la API (Swagger UI + esquema OpenAPI). | Facilita la evaluación del proyecto. **Se deshabilita con `ENV=production`** |

### Lo que deliberadamente NO existe como ruta pública

| Ausente | Motivo |
|---|---|
| Reserva de turno por el paciente | DD-05. Requiere auth del paciente, rate limiting y anti-abuso |
| Consulta de disponibilidad pública | Expondría la agenda de la clínica sin autenticación alguna |
| Recuperación de contraseña | Fuera del alcance del MVP. El `admin` la resuelve directamente por la consola de usuarios |
| Registro de usuarios | El alta de usuarios es una operación del `admin`, no autoservicio |
| Cualquier endpoint que devuelva datos de pacientes sin token | El DNI, el teléfono y la fecha de nacimiento son **datos personales sensibles** bajo la Ley 25.326 |

> **Criterio de diseño**: cualquier ruta nueva que no devuelva datos de un paciente y no modifique el estado del sistema puede evaluarse como pública; cualquier otra cosa requiere sesión.

---

## Mapa de pantallas por rol

Cada rol ve un conjunto distinto de pantallas. El menú se construye a partir del rol del token; el backend sigue siendo la autoridad.

| Pantalla | Ruta frontend | `secretaria` | `odontologo` | `admin` |
|---|---|:---:|:---:|:---:|
| Login | `/login` | ✔ | ✔ | ✔ |
| Agenda del día | `/agenda` | ✔ (todos los profesionales) | ✔ (forzado a su id) | ✔ (todos) |
| Agenda de la semana | `/agenda/semana` | ✔ | ✔ (su id) | ✔ |
| Detalle de turno | `/turnos/:id` | ✔ | ✔ (sólo propios) | ✔ |
| Pacientes — lista y búsqueda | `/pacientes` | ✔ | — | ✔ |
| Pacientes — alta / edición | `/pacientes/nuevo`, `/pacientes/:id` | ✔ | — | ✔ |
| Ficha del paciente | `/pacientes/:id` | ✔ | ✔ (si tiene turno) | ✔ |
| Odontograma del paciente | `/pacientes/:id/odontograma` | R | ✔ (si tiene turno) | R |
| Servicios — padrón (CRUD) | `/servicios` | ✔ | R | ✔ |
| Profesionales — padrón (CRUD) | `/profesionales` | ✔ | R | ✔ |
| Configuración — Sillones | `/config/sillones` | — | — | ✔ |
| Configuración — Feriados | `/config/feriados` | — | — | ✔ |
| Configuración — Horarios | `/config/profesionales/:id/horarios` | — | — | ✔ |
| Configuración — Bloqueos | `/config/profesionales/:id/bloqueos` | — | — | ✔ |
| Usuarios | `/config/usuarios` | — | — | ✔ |
| Auditoría | `/auditoria` | — | — | ✔ |

> El `odontologo` **no ve** el listado global de pacientes (RN-OD-05): sólo llega a la ficha de un paciente a través de un turno propio. Esto reduce la exposición de datos personales sensibles y es coherente con su verbo principal.