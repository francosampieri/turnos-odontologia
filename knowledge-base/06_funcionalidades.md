# Funcionalidades

Las funcionalidades se organizan por **épica** y, dentro de cada épica, por **historia de usuario** (`US-NNN`). Todas están en el alcance v1.0 del MVP salvo que se indique lo contrario.

**Formato de cada historia**

```
US-NNN — Título
Como [rol] · Quiero [acción] · Para [resultado]
Criterios de aceptación (CA) · Reglas relacionadas (RN)
```

**Convenciones**: una historia no puede cerrarse si al menos un criterio de aceptación no se cumple en el sistema corriendo. Los criterios marcados *(datos)* se verifican con el seed; los marcados *(concurrencia)* con un test de dos peticiones simultáneas.

---

## Épica 1: Identidad y acceso

### US-001 — Iniciar sesión
**Como** secretaria, odontólogo o admin · **Quiero** iniciar sesión con email y contraseña · **Para** operar el sistema con mi propia identidad y mis permisos.

**Criterios de aceptación**
- [ ] CA-1. Credenciales válidas devuelven `200`, el token JWT y los datos del usuario (id, nombre, rol).
- [ ] CA-2. Credenciales inválidas devuelven `401` con un mensaje genérico ("credenciales inválidas"), sin revelar si el email existe.
- [ ] CA-3. Un usuario con `activo = FALSE` recibe `403` aunque la contraseña sea correcta.
- [ ] CA-4. El rol viaja **dentro** del token (`claim rol`) y además se resuelve en el servidor contra la base en cada petición.
- [ ] CA-5. El token expira según la configuración (8 h por defecto) y a partir de ahí toda ruta protegida devuelve `401`.

**Reglas relacionadas**: RN-AU-01, RN-AU-02, RN-AU-03, RN-AU-07

### US-002 — Cerrar sesión
**Como** cualquier usuario · **Quiero** cerrar sesión · **Para** no dejar el token accesible en el equipo compartido.

**CA**
- [ ] CA-1. El frontend descarta el token de `sessionStorage` y vuelve a `/login`.
- [ ] CA-2. La acción es puramente cliente: el sistema documenta que no hay lista de revocación en el MVP.

**Reglas relacionadas**: RN-AU-06, RN-AU-07

### US-003 — Navegar según el rol
**Como** cualquier usuario · **Quiero** ver sólo las pantallas que me corresponden · **Para** no recorrer menús que no puedo usar.

**CA**
- [ ] CA-1. El menú se construye a partir del rol del token.
- [ ] CA-2. Un `odontologo` no ve "Pacientes" en el menú ni puede llegar a `/pacientes` por URL directa.
- [ ] CA-3. **Ocultar no es autorizar**: al llamar por HTTP directo a una ruta fuera de su rol, la respuesta es `403`.

**Reglas relacionadas**: RN-AU-04, RN-AU-05

### US-004 — Administrar usuarios *(admin)*
**Como** admin · **Quiero** crear, editar y desactivar usuarios · **Para** dar de alta a cada persona de la clínica con su rol.

**CA**
- [ ] CA-1. El alta exige email único, nombre y rol válido entre los tres.
- [ ] CA-2. La contraseña se guarda hasheada con bcrypt; el admin nunca ve una contraseña en texto plano después de crearla.
- [ ] CA-3. Al crear un usuario con rol `odontologo`, el alta ofrece crear el `profesional` asociado en el mismo formulario.
- [ ] CA-4. Un usuario no puede desactivar su propia cuenta.
- [ ] CA-5. Desactivar un profesional con turnos futuros no terminales devuelve `409`.

**Reglas relacionadas**: RN-AU-02, RN-AU-03, RN-PR-01, RN-PR-05, RN-CA-04

### US-005 — Consultar la auditoría *(admin)*
**Como** admin · **Quiero** ver quién creó, canceló o reconfiguró qué, y cuándo · **Para** reconstruir la historia de un turno que "desapareció" de la agenda.

**CA**
- [ ] CA-1. La auditoría es de sólo lectura y se filtra por entidad, usuario y rango de fechas.
- [ ] CA-2. Cada registro muestra: usuario, entidad, acción, fecha, estado anterior y estado posterior.
- [ ] CA-3. Los datos sensibles (DNI completo, fecha de nacimiento) **no** aparecen en la auditoría.
- [ ] CA-4. No existe ninguna operación de escritura ni de borrado sobre la auditoría.

**Reglas relacionadas**: RN-GL-03, RN-GL-04

---

## Épica 2: Datos maestros de la clínica

### US-010 — Administrar profesionales *(secretaria, admin)*
**Como** secretaria · **Quiero** dar de alta profesionales con especialidad y color de agenda · **Para** que la clínica pueda tener más de un odontólogo.

**CA**
- [ ] CA-1. El profesional se crea sin cuenta: `usuario_id` queda NULL hasta que el `admin` le crea un usuario con rol `odontologo` y lo vincula (RN-PR-01).
- [ ] CA-2. El color de agenda se valida como `#RRGGBB` y es opcional.
- [ ] CA-3. Se listan profesionales activos con su usuario asociado (o "sin cuenta") y su horario cargado.
- [ ] CA-4. Baja lógica: un profesional con historial de turnos no se borra, se desactiva.

**Reglas relacionadas**: RN-PR-01, RN-PR-05, RN-GL-01

### US-011 — Configurar el horario laboral *(admin)*
**Como** admin · **Quiero** definir las ventanas horarias de cada profesional por día de semana · **Para** que la agenda ofrezca solamente horarios que existen.

**CA**
- [ ] CA-1. El formulario se abre con el default: Lun–Vie `08:00–18:00`; sábado `08:00–12:00` **vacío**.
- [ ] CA-2. Un profesional puede tener más de una ventana por día (por ejemplo, mañana y tarde).
- [ ] CA-3. El sistema rechaza ventanas solapadas del mismo profesional y el mismo día.
- [ ] CA-4. No se pueden crear ventanas en domingo.
- [ ] CA-5. Guardar reemplaza el conjunto completo de ventanas del profesional, de forma atómica.
- [ ] CA-6. Los cambios de horario quedan auditados.

**Reglas relacionadas**: RN-HO-01, RN-HO-02, RN-HO-04, RN-HO-05, RN-GL-04

### US-012 — Administrar servicios y duraciones *(secretaria, admin)*
**Como** secretaria · **Quiero** mantener el catálogo de prácticas con su duración · **Para** que un turno tenga la duración real de cada práctica. El `admin` además puede definir overrides por profesional.

**CA**
- [ ] CA-1. La duración se elige entre 15, 30, 45 y 60 minutos; el default es 30.
- [ ] CA-2. El nombre del servicio es único entre los activos.
- [ ] CA-3. El `admin` puede definir un override de duración para un profesional concreto sobre un servicio; `secretaria` y `odontologo` no.
- [ ] CA-4. La interfaz muestra la duración efectiva que se va a usar (override si existe, si no la del servicio).
- [ ] CA-5. No se puede dar de baja un servicio que tenga turnos futuros no terminales.

**Reglas relacionadas**: RN-PR-02, RN-PR-03, RN-PR-04

### US-013 — Administrar sillones *(admin)*
**Como** admin · **Quiero** dar de alta y desactivar los sillones del consultorio · **Para** que el sistema sepa cuántos gabinetes hay y no agende sobre uno que no existe.

**CA**
- [ ] CA-1. La cantidad de sillones es libre (no hay número fijo en el código).
- [ ] CA-2. El nombre es único entre los activos.
- [ ] CA-3. Desactivar un sillón con turnos futuros no terminales devuelve `409`.
- [ ] CA-4. La disponibilidad por sillón se ve en la pantalla de agenda.

**Reglas relacionadas**: RN-SI-01, RN-SI-03, RN-SI-04, RN-SI-05

### US-014 — Administrar feriados *(admin)*
**Como** admin · **Quiero** cargar el calendario de feriados · **Para** que el sistema no ofrezca ni acepte turnos en días que la clínica está cerrada.

**CA**
- [ ] CA-1. Se cargan feriados `NACIONAL` y `LOCAL`, con fecha única.
- [ ] CA-2. El seed deja cargado el calendario nacional argentino del año en curso.
- [ ] CA-3. Cargar un feriado que tiene turnos futuros ya agendados devuelve `409` con la cantidad de turnos afectados.
- [ ] CA-4. Un feriado bloquea la disponibilidad **de todos** los profesionales a la vez.
- [ ] CA-5. El sistema **no** consulta ningún calendario externo: la carga es manual.
- [ ] CA-6. Un feriado cargado por error se puede **editar** (`PATCH /api/v1/feriados/{id}`: fecha, descripción, tipo) y **desactivar** (`DELETE /api/v1/feriados/{id}` → baja lógica). **No hay forma de dar de baja un feriado cargado por error.**
- [ ] CA-7. Editar la fecha de un feriado a una que ya pertenece a otro feriado activo devuelve `409`.
- [ ] CA-8. Desactivar un feriado con turnos futuros ya agendados **no** los cancela: los turnos quedan en la agenda y el sistema informa cuántos hay. El `admin` los reprograma uno por uno.
- [ ] CA-9. La baja es **lógica**: el feriado desaparece de la disponibilidad y de los listados, pero la fila queda en la base y auditada con quién la desactivó y cuándo.

**Reglas relacionadas**: RN-FE-01, RN-FE-02, RN-FE-03, RN-FE-04, RN-FE-06, RN-GL-01, RN-GL-04, RN-GL-06

### US-015 — Registrar bloqueos por profesional *(admin)*
**Como** admin · **Quiero** registrar vacaciones o congressos de un profesional con su rango de fechas · **Para** que no se agende sobre un profesional que no está.

**CA**
- [ ] CA-1. El rango es inclusivo (`desde` y `hasta`) y admite motivo libre.
- [ ] CA-2. El sistema rechaza `hasta < desde`.
- [ ] CA-3. La disponibilidad del profesional desaparece para todos los días del rango.
- [ ] CA-4. El bloqueo es **por profesional**: los demás siguen atendiendo en esos días.

**Reglas relacionadas**: RN-FE-05

---

## Épica 3: Pacientes

### US-020 — Dar de alta un paciente *(secretaria, admin)*
**Como** secretaria · **Quiero** cargar la ficha de un paciente · **Para** poder agendarle un turno.

**CA**
- [ ] CA-1. Los campos obligatorios son nombre, apellido, DNI, teléfono y fecha de nacimiento; el email es opcional.
- [ ] CA-2. El DNI se normaliza: se aceptan "12.345.678", "12345678" o con letras y se guarda siempre como dígitos.
- [ ] CA-3. Un DNI ya existente devuelve `409` con un mensaje que dice explícitamente "ya existe un paciente con ese DNI".
- [ ] CA-4. La fecha de nacimiento no puede ser futura.
- [ ] CA-5. *(datos)* El paciente queda activo y es inmediatamente buscable.

**Reglas relacionadas**: RN-PC-01, RN-PC-02, RN-PC-03, RN-PC-04, RN-PC-05

### US-021 — Buscar pacientes *(secretaria, admin)*
**Como** secretaria · **Quiero** buscar por DNI, apellido o teléfono · **Para** encontrar al paciente en segundos, incluso con el teléfono hecho un bollo de papel.

**CA**
- [ ] CA-1. Un solo campo de búsqueda devuelve resultados paginados; una búsqueda vacía devuelve el listado paginado.
- [ ] CA-2. La búsqueda ignora mayúsculas, acentos y guiones.
- [ ] CA-3. Los resultados sólo incluyen pacientes activos.
- [ ] CA-4. El listado enmascara el DNI salvo que el rol tenga autorización explícita para verlo completo.
- [ ] CA-5. Un `odontologo` no tiene acceso a esta pantalla ni al endpoint.

**Reglas relacionadas**: RN-PC-06, RN-AU-04, RN-AU-05

### US-022 — Editar y dar de baja un paciente *(secretaria, admin)*
**Como** secretaria · **Quiero** corregir los datos de un paciente y darlo de baja si deja de asistir · **Para** mantener la agenda confiable.

**CA**
- [ ] CA-1. Los campos editables son los mismos de la alta, con las mismas validaciones.
- [ ] CA-2. El DNI **no** se puede cambiar si el paciente ya tiene turnos: el historial quedaría desreferenciado. Se devuelve `409`.
- [ ] CA-3. La baja es lógica; el paciente desaparece de las búsquedas pero sus turnos y su odontograma se conservan.
- [ ] CA-4. La baja devuelve `409` si el paciente tiene turnos no terminales.

**Reglas relacionadas**: RN-PC-07, RN-PC-08, RN-GL-01

### US-023 — Ver la ficha del paciente
**Como** secretaria, odontólogo o admin · **Quiero** abrir la ficha con sus datos y sus próximos turnos · **Para** atender sin buscar información en otro lugar.

**CA**
- [ ] CA-1. La ficha muestra datos de contacto, próximos turnos e historial de turnos.
- [ ] CA-2. El `odontologo` llega a la ficha únicamente desde un turno propio, y no ve el listado global.
- [ ] CA-3. Desde la ficha se accede al odontograma del paciente.

**Reglas relacionadas**: RN-AU-05, RN-OD-05

---

## Épica 4: Agenda y turnos — el núcleo del sistema

### US-030 — Ver la agenda del día
**Como** secretaria · **Quiero** ver la agenda del día de todos los profesionales en una sola pantalla · **Para** saber a quién atender y en qué orden sin preguntar.

**CA**
- [ ] CA-1. La pantalla muestra una columna por profesional activo, ordenada por hora de inicio.
- [ ] CA-2. Cada turno muestra hora, paciente, servicio, sillón y estado con un color distinto.
- [ ] CA-3. Los estados terminales (`cancelado`, `no_asistió`) se distinguen visualmente y se pueden filtrar.
- [ ] CA-4. El `odontologo` ve la misma pantalla **forzada a su propia columna**.
- [ ] CA-5. Clic en un turno abre el detalle con acciones disponibles según el rol.
- [ ] CA-6. *(rendimiento)* Con 200 turnos del día la pantalla carga en menos de 1 segundo.

**Reglas relacionadas**: RN-AU-05, RN-TU-07, RN-TU-09

### US-031 — Ver la agenda de la semana
**Como** secretaria · **Quiero** ver la semana completa por profesional · **Para** detectar huecos y reprogramar con visión de conjunto.

**CA**
- [ ] CA-1. Vista de 7 días con la misma información que la agenda del día.
- [ ] CA-2. Permite filtrar por profesional.
- [ ] CA-3. No hay edición en lote: el Discovery evaluó esto como riesgo de corrupción de agenda y se descartó a propósito.

**Reglas relacionadas**: RN-AU-05, RN-CA-02

### US-032 — Consultar la disponibilidad
**Como** secretaria · **Quiero** ver los horarios libres de un profesional para una fecha y un servicio · **Para** ofrecerle al paciente una hora concreta sin arriesgar un conflicto.

**CA**
- [ ] CA-1. Los slots se calculan como `ventana horaria − feriados − bloqueos − turnos activos`, alineados a la duración efectiva del servicio.
- [ ] CA-2. Si el profesional no atiende ese día (domingo, sábado vacío, feriado, bloqueo), la respuesta es una lista vacía, **no** un error.
- [ ] CA-3. La respuesta indica el motivo de cada día sin disponibilidad, para que la interfaz pueda explicarlo.
- [ ] CA-4. La disponibilidad **no** es una reserva: no bloquea el slot.

**Reglas relacionadas**: RN-HO-01, RN-HO-03, RN-HO-05, RN-FE-02, RN-FE-03, RN-FE-05, RN-TU-03, RN-TU-09

### US-033 — Reservar un turno
**Como** secretaria · **Quiero** crear un turno eligiendo paciente, profesional, sillón, servicio, fecha y hora · **Para** que el horario quede reservado y no se pueda sobreescribir por error.

**CA**
- [ ] CA-1. Todos los campos son obligatorios; el motivo de consulta es opcional.
- [ ] CA-2. `fin` se calcula con la duración efectiva (override del profesional si existe).
- [ ] CA-3. El turno se crea con estado `agendado`.
- [ ] CA-4. Se rechazan las reservas en el pasado, fuera del horario laboral, en feriado, dentro de un bloqueo y sobre un sillón inactivo.
- [ ] CA-5. **Si el horario se solapa** con otro turno del mismo profesional, del mismo paciente o del mismo sillón, la respuesta es `409` con un mensaje legible y el frontend recarga la disponibilidad.
- [ ] CA-6. *(concurrencia)* Dos peticiones simultáneas sobre el mismo slot producen exactamente **una** `201` y **una** `409`.
- [ ] CA-7. La creación queda auditada con el usuario autor.

**Reglas relacionadas**: RN-TU-01, RN-TU-02, RN-TU-03, RN-TU-04, RN-TU-05, RN-TU-06, RN-TU-08, RN-HO-03, RN-FE-03, RN-SI-02, RN-SI-04, RN-AU-04, RN-GL-04

### US-034 — Cancelar un turno
**Como** secretaria · **Quiero** cancelar un turno con un motivo · **Para** liberar el horario y ofrecerlo a otro paciente.

**CA**
- [ ] CA-1. El estado pasa a `cancelado`; **no** se borra el registro.
- [ ] CA-2. El horario queda inmediatamente disponible para otro paciente, sin ninguna acción adicional.
- [ ] CA-3. Requiere al menos 2 horas de anticipación respecto del inicio del turno.
- [ ] CA-4. Un `odontologo` recibe `403` aunque el turno sea suyo.
- [ ] CA-5. Se registran quién canceló, cuándo y con qué motivo.

**Reglas relacionadas**: RN-CA-01, RN-CA-03, RN-CA-04, RN-TU-09, RN-GL-04

### US-035 — Reprogramar un turno
**Como** secretaria · **Quiero** mover un turno a otro horario · **Para** acomodar un cambio de pedido del paciente sin perder la reserva.

**CA**
- [ ] CA-1. La operación es **una única transacción**: o se crea el turno nuevo y se cancela el anterior, o no cambia nada.
- [ ] CA-2. El turno nuevo queda enlazado al anterior (`origen_turno_id`), de modo que el historial muestra la cadena.
- [ ] CA-3. El turno anterior pasa a `cancelado` con motivo "reprogramado".
- [ ] CA-4. Requiere 2 horas de anticipación.
- [ ] CA-5. Si el destino está ocupado, la respuesta es `409` y **el turno original sigue vigente**.

**Reglas relacionadas**: RN-CA-02, RN-CA-03, RN-CA-04, RN-CA-05, RN-TU-05, RN-TU-06

### US-036 — Cambiar el estado de un turno
**Como** secretaria o odontólogo · **Quiero** mover el turno por su ciclo de vida · **Para** que la agenda refleje lo que realmente pasó.

**CA**
- [ ] CA-1. Las transiciones permitidas son las de RN-TU-07; cualquier otra devuelve `422`.
- [ ] CA-2. El `odontologo` sólo puede llevar **su** turno a `en_curso`, `completado` o `no_asistió`.
- [ ] CA-3. Los estados `completado`, `cancelado` y `no_asistió` no tienen salida.
- [ ] CA-4. Cada cambio queda auditado.

**Reglas relacionadas**: RN-TU-07, RN-TU-08, RN-GL-04, RN-AU-04

### US-037 — Registrar un sobreturno
**Como** secretaria · **Quiero** registrar una urgencia fuera de la agenda del día · **Para** atender un caso sin subir ningún otro turno.

**CA**
- [ ] CA-1. El sobreturno exige **motivo** y se crea con estado `sobreturno`.
- [ ] CA-2. Es la **única** operación que puede solaparse con otro turno, y queda escrito así en el constraint de la base.
- [ ] CA-3. El endpoint es separado del de reserva: no se llega al sobreturno "por error" al agendar.
- [ ] CA-4. Queda auditado como acción sensible.

**Reglas relacionadas**: RN-TU-10, RN-TU-11, RN-AU-04, RN-GL-04

### US-038 — Ver el detalle de un turno
**Como** secretaria u odontólogo con turno propio · **Quiero** abrir un turno · **Para** ver todos sus datos y ejecutar la acción que corresponda.

**CA**
- [ ] CA-1. Muestra paciente, profesional, sillón, servicio, inicio, fin, estado y motivo.
- [ ] CA-2. Las acciones disponibles se calculan en el servidor según el rol, el estado actual y la anticipación.
- [ ] CA-3. Un `odontologo` que pide un turno ajeno recibe `404`, no `403`.

**Reglas relacionadas**: RN-AU-04, RN-AU-05, RN-CA-03, RN-TU-07

---

## Épica 5: Odontograma — diferenciador de nicho

> El odontograma entra en el MVP **sólo con piezas y estados**: sin radiografías, sin fotos, sin archivos (RN-OD-08, DD-04).

### US-040 — Ver el odontograma de un paciente
**Como** odontólogo, secretaria o admin · **Quiero** ver el esquema dentario del paciente · **Para** conocer su estado bucodental de un vistazo.

**CA**
- [ ] CA-1. Se muestran las 32 piezas permanentes (11–48) en el orden de la notación FDI, en arco superior e inferior.
- [ ] CA-2. Cada pieza muestra su estado con un color y una sigla; `sano` es el valor inicial.
- [ ] CA-3. La ficha del paciente y el detalle del turno enlazan al odontograma.
- [ ] CA-4. El `odontologo` entra al odontograma desde un turno propio; no desde el listado global de pacientes.

**Reglas relacionadas**: RN-OD-01, RN-OD-02, RN-OD-03, RN-OD-04, RN-OD-05

### US-041 — Registrar el estado de una pieza
**Como** odontólogo · **Quiero** actualizar el estado de una pieza · **Para** dejar registrado el tratamiento realizado.

**CA**
- [ ] CA-1. Se elige estado del catálogo de 12 valores y, opcionalmente, la cara afectada.
- [ ] CA-2. Sin cara, el estado aplica a la pieza completa.
- [ ] CA-3. La escritura es idempotente: repetirla con el mismo estado no duplica historial.
- [ ] CA-4. Las notas no superan 500 caracteres.
- [ ] CA-5. Sólo el `odontologo` con turno no terminal del paciente puede escribir; `secretaria` y `admin` reciben `403`.
- [ ] CA-6. Ninguna pantalla ofrece cargar imágenes.

**Reglas relacionadas**: RN-OD-03, RN-OD-04, RN-OD-05, RN-OD-06, RN-OD-08, RN-OD-09

### US-042 — Consultar el historial de una pieza
**Como** odontólogo o admin · **Quiero** ver los cambios sucesivos de una pieza · **Para** reconstruir su evolución.

**CA**
- [ ] CA-1. El historial se muestra en orden cronológico inverso con estado anterior, estado nuevo, autor y fecha.
- [ ] CA-2. El historial es inmutable: no hay forma de editarlo ni de borrarlo desde la interfaz.
- [ ] CA-3. El movimiento se genera automáticamente en la misma transacción que la actualización de la pieza.

**Reglas relacionadas**: RN-OD-07, RN-GL-03

---

## Mapa de historias por rol

| Épica | `secretaria` | `odontologo` | `admin` |
|---|---|---|---|
| 1 — Identidad y acceso | US-001, 002, 003 | US-001, 002, 003 | US-001, 002, 003, **004**, **005** |
| 2 — Datos maestros | US-010…015 *(lectura)* | — | US-010…015 *(escritura)* |
| 3 — Pacientes | US-020, **021**, **022**, 023 | US-023 *(desde turno propio)* | US-020, 021, 022, 023 |
| 4 — Agenda y turnos | US-030…**038** | US-030, 031, **036**, 038 *(propios)* | US-030…038 |
| 5 — Odontograma | US-040 *(lectura)* | US-040, **041**, 042 | US-040, 042 *(lectura)* |

## Trazabilidad hacia las historias del Discovery

| Caso de uso del Discovery | Historia | Estado |
|---|---|---|
| 1. Secretaria carga un turno | US-033 | En el MVP |
| 2. Secretaria ve la agenda del día | US-030 | En el MVP |
| 3. Odontólogo ve sus turnos con la ficha | US-030, US-023 | En el MVP |
| 4. Secretaria cancela o reprograma | US-034, US-035 | En el MVP |
| 5. Paciente reserva online desde el celular | — | **Fuera del MVP** (DD-05, PA-02) |

| Funcionalidad necesaria del Discovery | Historia |
|---|---|
| Ficha de paciente | US-020 |
| Gestión de profesionales | US-010 |
| Agenda por día y por profesional | US-030, US-031 |
| Reserva de turno | US-033 |
| Validación anti-solapamiento | US-033 CA-5/CA-6, US-037 |
| Cancelación y reprogramación | US-034, US-035 |
| Listado de turnos del día | US-030 |
| Búsqueda de pacientes | US-021 |
| Roles y permisos | US-003, US-004 |
| Duración variable por prestación | US-012 |
| Bloqueos y feriados | US-014, US-015 |
| Odontograma *(agregado por decisión de alcance)* | US-040, 041, 042 |