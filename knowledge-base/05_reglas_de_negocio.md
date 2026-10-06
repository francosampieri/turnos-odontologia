# Reglas de Negocio

Cada regla tiene un código único `RN-{DOMINIO}-{NN}` para trazabilidad: las historias de usuario de `06_funcionalidades.md`, los endpoints de `02_descripcion_general.md` y las restricciones de `04_modelo_de_datos.md` referencian estos códigos.

**Convención de numeración**: los códigos son estables. Una regla que se agrega al final no renumera las anteriores; una regla que se elimina deja su código marcado como *retirada* en lugar de reutilizarse.

**Leyenda de la columna "Origen"**:

- **[D]** = Decisión confirmada por el usuario/profesor. No se abre a discusión en el MVP.
- **[C]** = Comprobada en la investigación de mercado (declarada por al menos un proveedor relevado).
- **[S]** = Supuesto del Discovery, confirmado por decisión posterior.

| Dominio | Prefijo | Nº de reglas | Estado |
|---|---|---|---|
| Autenticación y acceso | `RN-AU` | 7 | en el MVP |
| Pacientes | `RN-PC` | 8 | en el MVP |
| Profesionales y servicios | `RN-PR` | 5 | en el MVP |
| Horarios laborales | `RN-HO` | 5 | en el MVP |
| Sillones | `RN-SI` | 5 | en el MVP |
| Feriados y bloqueos | `RN-FE` | 6 | en el MVP |
| Turnos | `RN-TU` | 11 | en el MVP |
| Cancelación y reprogramación | `RN-CA` | 5 | en el MVP |
| Odontograma | `RN-OD` | 9 | en el MVP (+1 retirada) |
| Globales | `RN-GL` | 6 | en el MVP |
| **Experiencia del paciente** | `RN-XP` | **0** | **retiradas**: 4 códigos (RN-XP-01…04) |
| **Total en el MVP** | — | **67** | 10 dominios activos (7+8+5+5+5+6+11+5+9+6) + 1 dominio retirado |

---

## Dominio: Autenticación y acceso (RN-AU)

- **RN-AU-01**: Toda ruta salvo las públicas (`03_actores_y_roles.md`) exige un JWT válido. Sin token, con token expirado o con firma inválida la respuesta es `401`. Origen: **[D]**.
- **RN-AU-02**: Todo usuario tiene **exactamente un rol**, y sólo existen tres: `secretaria`, `odontologo`, `admin`. No hay alta de roles desde la interfaz (DD-13). Origen: **[D]**.
- **RN-AU-03**: Las contraseñas se almacenan con **bcrypt** (cost factor ≥ 12) y nunca en texto plano, ni en la base, ni en el archivo de seed, ni en los logs. Longitud mínima 8 caracteres. Origen: **[D]**.
- **RN-AU-04**: El permiso por rol se aplica en la **capa de aplicación y de datos**, no ocultando botones en el frontend. Un endpoint que requiera un rol inexistente devuelve `403`, no `404`. Origen: **[D]**.
- **RN-AU-05**: El `odontologo` **sólo** accede a los turnos de su propia agenda, y sólo a los pacientes con los que tenga un turno no terminal. El filtro se aplica en la consulta SQL y en la dependencia de autorización. Origen: **[D]**.
- **RN-AU-06**: El JWT viaja en la cabecera `Authorization: Bearer <token>`. **No** se usa cookie de sesión, porque no hay renderizado en el servidor (DD-01). El frontend lo guarda en `sessionStorage`, nunca en `localStorage` ni en una cookie legible por JavaScript. Origen: **[D]**.
- **RN-AU-07**: La duración del token es configurable (por defecto 8 h). Un usuario con `activo = FALSE` no puede autenticarse aunque tenga credenciales válidas. El `logout` es una operación del cliente: el token se descarta, no existe lista de revocación en el MVP. Origen: **[D]**.

> **Por qué RN-AU-05 es una regla y no una función del frontend**: es la diferencia entre "el botón no está" y "el dato no sale del servidor". Verificable en la defensa con una petición directa a `GET /api/v1/turnos` sin `profesional_id` usando el token de un odontólogo.

---

## Dominio: Pacientes (RN-PC)

- **RN-PC-01**: El **DNI es único** entre los pacientes activos, con 7 u 8 dígitos, almacenado sin guiones ni letras. Un DNI repetido devuelve `409`. Origen: **[C]** — es la clave natural del paciente en todo el mercado relevado.
- **RN-PC-02**: El DNI se **normaliza** en el borde (se quitan guiones, espacios y letras) antes de persistir y antes de comparar. Origen: **[S]**.
- **RN-PC-03**: `nombre` y `apellido` son obligatorios y no pueden ser cadenas vacías ni sólo espacios. Origen: **[C]**.
- **RN-PC-04**: `telefono` es **obligatorio** (es el canal de contacto real de una clínica chica); el formato es libre pero se normaliza a dígitos para la búsqueda. `email` es **opcional** y se valida como correo si se completa. Origen: **[S]** — el Discovery planteó el email como dato del paciente; se decide que el teléfono es el contacto confiable.
- **RN-PC-05**: `fecha_nacimiento` es obligatoria y no puede ser futura. Es **dato personal sensible** bajo la Ley 25.326: no se expone en logs ni en la auditoría. Origen: **[C]**.
- **RN-PC-06**: La búsqueda de pacientes acepta `dni`, `apellido` y `telefono`, **siempre paginada** y **sólo sobre pacientes activos**. Origen: **[C]** — sin búsqueda, la secretaria abandona el sistema.
- **RN-PC-07**: El paciente se da de **baja lógica** (`activo = FALSE`), nunca física. Si tiene turnos no terminales, la baja devuelve `409`. Origen: **[D]**.
- **RN-PC-08**: Un paciente dado de baja **conserva** sus turnos, su odontograma y su historial: el registro es histórico- clínico. Origen: **[S]**.

---

## Dominio: Profesionales y servicios (RN-PR)

- **RN-PR-01**: Cada profesional está asociado a **exactamente un** usuario con rol `ODONTOLOGO` (`profesional.usuario_id` es UNIQUE). Un odontólogo sin usuario no puede tener agenda. Origen: **[D]**.
- **RN-PR-02**: La duración de un servicio es una de `{15, 30, 45, 60}` minutos. El **valor por defecto es 30**. No hay duraciones arbitrarias: el `CHECK` de la base lo impide. Origen: **[D]** — decisión explícita frente al supuesto **R4** del Discovery (*"la duración del turno depende de la prestación, no es fija"*, §7 de `discovery/discovery.md`, que quedó sin dato real). **No confundir R4 con R-4**: R-4 es la restricción de stack del §9 (*"web, multiusuario, base de datos"*), que es otra cosa. Ver la glosario de códigos `R` en `09_decisiones_y_supuestos.md` y el supuesto abierto SU-05.
- **RN-PR-03**: Un profesional puede tener un **override** de duración para un servicio (`profesional_servicio.duracion_min`). Si el override es `NULL`, manda la duración del servicio. Origen: **[D]**.
- **RN-PR-04**: El nombre del servicio es único entre los activos. No se modelan submarcas del tipo "Limpieza 30" / "Limpieza 45": para eso está el override de RN-PR-03. Origen: **[S]**.
- **RN-PR-05**: No se puede desactivar un profesional que tenga turnos futuros en estados no terminales. Origen: **[D]**.

> **RN-PR-02 es la regla que decide si el modelo de datos es correcto desde el día 1**. Fijar 30 minutos como constante en el código obliga a migrar la agenda en cuanto aparezca una endodoncia de 60. Se resuelve en el esquema, no en el formulario.

---

## Dominio: Horarios laborales (RN-HO)

- **RN-HO-01**: Valores por defecto: **lunes a viernes 08:00–18:00**; **sábado 08:00–12:00 opcional**, es decir, **vacío por defecto** y a criterio del `admin`. Origen: **[D]**.
- **RN-HO-02**: Para un mismo profesional y día de semana, dos ventanas horarias **no pueden solaparse**, y `hora_fin > hora_inicio` siempre. Se valida en el servicio de dominio al reemplazar el conjunto de ventanas. Origen: **[S]** — corolario de la regla general de no-solapamiento.
- **RN-HO-03**: **Todo** turno debe caber **completamente** dentro de una ventana horaria del profesional (ventana del día de la semana correspondiente). Un turno que empieza dentro de la ventana y termina fuera es inválido. Origen: **[C]**.
- **RN-HO-04**: El domingo **no** es día de atención: no se pueden crear ventanas para `dia_semana = 0`. Origen: **[S]** — decisión de alcance de la clínica; no es una limitación técnica.
- **RN-HO-05**: El `admin` puede dejar un día sin ventanas (por ejemplo, vaciar el sábado) sin desactivar al profesional. Origen: **[D]**.

---

## Dominio: Sillones (RN-SI)

- **RN-SI-01**: La cantidad de sillones es **configurable**: se dan de alta y se desactivan. No están hardcodeados en el código. Origen: **[D]**.
- **RN-SI-02**: **Todo** turno tiene sillón **obligatorio**. El modelo no admite turnos sin gabinete asignado. Origen: **[S]** — decisión de diseño que evita el caso "turno reservado sobre una clínica de un solo sillón" y hace explícita la ocupación física.
- **RN-SI-03**: El nombre del sillón es único entre los activos. Origen: **[S]**.
- **RN-SI-04**: No se puede agendar sobre un sillón inactivo. Origen: **[D]**.
- **RN-SI-05**: No se puede desactivar un sillón con turnos futuros no terminales (`409`). Origen: **[D]**.

> **Por qué el sillón importa en el modelo y no sólo como etiqueta**: es lo que impide que dos turnos del mismo profesional se pisen físicamente. La restricción `turno_no_solape_sillon` de `04_modelo_de_datos.md` es la expresión en la base de esta regla.

---

## Dominio: Feriados y bloqueos (RN-FE)

- **RN-FE-01**: La fecha de feriado es **única** en el calendario y lleva un tipo: `NACIONAL` o `LOCAL`. Un feriado es un **día completo**, sin horario ni zona horaria. Origen: **[D]**.
- **RN-FE-02**: Un feriado bloquea a **toda la clínica**, no a un profesional: es transversal. Origen: **[C]**.
- **RN-FE-03**: **No se puede reservar ni reprogramar un turno a un feriado** (`422`). Origen: **[C]**.
- **RN-FE-04**: Cargar un feriado con turnos futuros ya agendados **no** los borra: la operación se rechaza con `409` y se informa cuántos turnos quedan afectados, para que el `admin` los reprograme uno por uno. Origen: **[S]** — evita la corrupción silenciosa, que es el peor resultado posible en una clínica.
- **RN-FE-05**: El **bloqueo por profesional** es un rango de fechas **inclusivo** (`desde` y `hasta`) con motivo (vacaciones, congreso, curso). Un turno no puede caer dentro de un bloqueo. Origen: **[C]** — FLAP e IA Sistemas resuelven esto con bloqueos manuales; el Discovery lo marcó como "el riesgo más caro del sistema".
- **RN-FE-06**: Un feriado se **edita** (`PATCH`) y se **da de baja lógicamente** (`DELETE` → `activo = FALSE`), nunca se borra físicamente. Editar la fecha a una que ya pertenece a otro feriado activo devuelve `409` por `UNIQUE(fecha)`. Origen: **[S]** — corolario de RN-GL-01 aplicado a `feriado`: un feriado cargado por error es un error de configuración corregible, y sin esta ruta el único remedio sería imposible por el `UNIQUE(fecha)`.

---

## Dominio: Turnos (RN-TU)

- **RN-TU-01**: Un turno tiene paciente, profesional, sillón, servicio, `inicio`, `fin`, estado y motivo de consulta opcional. Todos son obligatorios salvo el motivo. Origen: **[C]**.
- **RN-TU-02**: **No se puede crear ni reprogramar un turno en el pasado** (`422`). Se evalúa contra la hora actual del servidor, no contra la del navegador. Origen: **[C]**.
- **RN-TU-03**: `fin = inicio + duración efectiva`, con `CHECK (fin > inicio)`. `fin` se **desnormaliza a propósito**: la exclusión de solapamiento necesita un rango consultable e indexable. Origen: **[D]**.
- **RN-TU-04**: **Anti-solapamiento de sillón**: un sillón no puede estar ocupado por dos turnos solapados. Origen: **[S]**.
- **RN-TU-05**: **Anti-solapamiento de profesional**: un profesional **no puede tener dos turnos solapados**. Es la **regla R1** del Discovery (§7, *"un profesional no puede tener dos turnos superpuestos en el mismo horario"*), declarada explícitamente por al menos 8 de los 20 proveedores relevados. Origen: **[C]**.
- **RN-TU-06**: **Anti-solapamiento de paciente**: un paciente **no puede tener dos turnos simultáneos, aunque sean con profesionales distintos**. Origen: **[D]** — decisión explícita del proyecto. Ningún proveedor de los 20 relevados declara esta regla, y existen excepciones clínicas reales (cirugía en equipo, sedación). Se adopta igual y se documenta como decisión, no como hallazgo de mercado. Ver `09_decisiones_y_supuestos.md` → DD-09 y `10_preguntas_abiertas.md` → PA-03.
- **RN-TU-07**: La máquina de estados tiene **7 estados**: `agendado`, `confirmado`, `en_curso`, `completado`, `cancelado`, `no_asistió`, `sobreturno`. Transiciones permitidas:

  ```
  agendado ──▶ confirmado ──▶ en_curso ──▶ completado
     │             │             │
     │             │             └──▶ no_asistió
     ├──▶ en_curso ├──▶ no_asistió
     ├──▶ cancelado ├──▶ no_asistió
     └──▶ sobreturno (RN-TU-11)
  ```
  Todo estado no terminal (`agendado`, `confirmado`, `en_curso`) puede pasar a `cancelado` o a `no_asistió`. **No hay retorno desde `completado`, `cancelado` ni `no_asistió`**: son estados finales. Origen: **[D]**.
- **RN-TU-08**: El estado inicial de todo turno creado es `agendado`. Origen: **[S]**.
- **RN-TU-09**: Los turnos en estado `cancelado` o `no_asistió` **no ocupan agenda**: no bloquean el horario para otros pacientes. Es lo que hace verdadero el RN-CA-01 en la capa de datos (exclusión parcial del constraint GiST). Origen: **[S]**.
- **RN-TU-10**: El **sobreturno es la única excepción controlada** al anti-solapamiento: puede solaparse y requiere estado `sobreturno` + motivo obligatorio. Un sobreturno nunca se crea por la interfaz de reserva normal, sino por un endpoint específico y auditado. Origen: **[D]**.
- **RN-TU-11**: El sobreturno se registra con `es_sobreturno = TRUE`, lo que **excluye la fila de las tres restricciones GiST**. Ninguna otra vía puede marcar un turno como sobreturno. Origen: **[D]**.

> **Dónde vive cada anti-solapamiento**: RN-TU-04 (sillón), RN-TU-05 (profesional) y RN-TU-06 (paciente) están **los tres** garantizados por la base de datos — un `EXCLUDE USING gist` parcial e independiente por eje —, y no por un `if`. La aplicación hace una comprobación previa *dentro de la misma transacción* sólo para elegir el mensaje de `409` y para asignar sillón automáticamente; si esa comprobación fuera la única, la carrera entre dos secretarias produciría doble reserva (TOCTOU bajo `READ COMMITTED`). La aplicación traduce `SQLSTATE 23P01` a `409`. Ver `04_modelo_de_datos.md` § "El punto clave de diseño" y `10_preguntas_abiertas.md` → IN-11.

---

## Dominio: Cancelación y reprogramación (RN-CA)

- **RN-CA-01**: **Cancelar** cambia el estado a `cancelado` y **libera el horario automáticamente**, sin borrado manual y sin tocar el resto de los datos. No hay `DELETE` sobre turnos. Origen: **[S]** — supuesto **R5** del Discovery (§7, *"al cancelar, el horario queda automáticamente disponible para otro paciente"*), confirmado como decisión.
- **RN-CA-02**: **Reprogramar** crea un turno **nuevo** y marca el anterior como `cancelado` (motivo: "reprogramado") **en una única transacción**. El turno nuevo apunta al anterior con `origen_turno_id`. No se edita el turno original: el historial queda intacto. Origen: **[D]**.
- **RN-CA-03**: **Antelación mínima de 2 horas** para cancelar o reprogramar un turno ya agendado (`422` si falta). No aplica a `no_asistió` ni a `completado`, porque son hechos y no decisiones. Origen: **[D]** — decisión explícita; el Discovery no encontró evidencia en el mercado (ver `10_preguntas_abiertas.md` → IN-01).
- **RN-CA-04**: Sólo `secretaria` y `admin` pueden cancelar y reprogramar. El `odontologo` **no**, ni siquiera sobre su propio turno. Origen: **[D]**.
- **RN-CA-05**: Si el horario destino de una reprogramación está ocupado, la operación **falla completa** (`409`) y **no se modifica nada**: no queda el turno original cancelado. Origen: **[D]** — es la propiedad transaccional de la regla.

---

## Dominio: Odontograma (RN-OD)

- **RN-OD-01**: Notación **FDI**. El MVP cubre la dentición **permanente**: 32 piezas, `numero` entre 11 y 48. La dentición decidua (51–85) queda fuera. Origen: **[D]**.
- **RN-OD-02**: **Una fila por paciente y pieza**: `UNIQUE(paciente_id, numero)`. Origen: **[D]** — el enunciado pide estado por pieza, no por cara.
- **RN-OD-03**: El estado de una pieza pertenece a un **catálogo cerrado** de 12 valores: `sano`, `ausente`, `caries`, `obturado`, `endodoncia`, `corona`, `implante`, `protesis`, `sellante`, `fracturado`, `extraído`, `requiere_tratamiento`. El valor inicial de toda pieza registrada es `sano`. Origen: **[D]**.
- **RN-OD-04**: La cara afectada es opcional y pertenece al catálogo `mesial`, `distal`, `vestibular`, `lingual`, `oclusal`, `completa`. `cara = NULL` significa que el estado aplica a la pieza completa. Origen: **[D]**.
- **RN-OD-05**: Sólo el `odontologo` **escribe** el odontograma, y sólo de pacientes con los que tenga un turno no terminal. `secretaria` y `admin` **leen**. Origen: **[D]**.
- **RN-OD-06**: La escritura de una pieza es **idempotente** (`PUT`): define el estado actual de esa pieza. Las notas no superan 500 caracteres. Origen: **[D]**.
- **RN-OD-07**: **Todo** cambio de estado de una pieza genera un registro en el historial append-only con estado anterior, estado nuevo, profesional autor y fecha. No existe endpoint de escritura ni de borrado del historial. Origen: **[D]**.
- **RN-OD-08**: El odontograma del MVP es **sólo piezas y estados**: **sin radiografías, sin fotos, sin imágenes, sin archivos adjuntos**. Origen: **[D]** — es la frontera de alcance de la fase 2 del módulo (DD-04, PA-01).
- **RN-OD-09**: El odontograma de un paciente inactivo queda **congelado**: se puede leer, no se puede escribir. Origen: **[S]**.

---

## Dominio: Excepciones globales (RN-GL)

- **RN-GL-01**: **Soft delete** en toda entidad maestra: campo `activo BOOLEAN` y **nunca** `DELETE` físico. Un registro que se borró no se puede auditar ni explicar. Origen: **[D]**.
- **RN-GL-02**: Los **instantes** se guardan en `TIMESTAMPTZ` (UTC). Las **horas de pared** del horario laboral se guardan en `TIME` sin zona. La conversión a la zona de la clínica (`America/Argentina/Buenos_Aires`) ocurre en el frontend. Separar "instante" de "hora de reloj local" es lo que hace correcto el cálculo de slots en el cambio de horario de verano. Origen: **[D]**.
- **RN-GL-03**: Toda entidad mutable lleva `created_at`, `updated_at`, `created_by`, `updated_by`. Origen: **[D]**.
- **RN-GL-04**: Las acciones que **modifican la agenda** (crear, reprogramar, cancelar, cambiar estado) y los **cambios de configuración** generan un registro de auditoría **append-only**. Sólo el `admin` lo consulta. Los `GET` no se auditan. Origen: **[D]**.
- **RN-GL-05**: Un recurso inactivo responde **`404`**, igual que uno inexistente. No se distingue entre "no existe" y "existe pero está dado de baja", para no filtrar existencia. Origen: **[S]**.
- **RN-GL-06**: El sistema es **completamente funcional con la base de datos sola**. Ninguna función del MVP depende de un servicio externo, de una clave de API de terceros o de un costo variable. Origen: **[D]**.

---

## Matriz de reglas por endpoint crítico

Verificable en la defensa: cada fila indica qué reglas bloquean la operación.

| Operación | Reglas aplicadas | Rechazo esperado |
|---|---|---|
| `POST /api/v1/auth/login` | RN-AU-01/03/07 | `401` credenciales inválidas · `403` usuario inactivo |
| `POST /api/v1/pacientes` | RN-PC-01…05 | `409` DNI duplicado · `422` campos inválidos |
| `GET /api/v1/turnos` (como odontólogo) | RN-AU-04/05 | Sin filtro obligatorio: la consulta ya viene acotada |
| `GET /api/v1/disponibilidad` | RN-HO-01/03/05, RN-FE-02/05, RN-TU-03/09 | Lista vacía (no error) si el día no atiende |
| `POST /api/v1/turnos` | RN-TU-01…11, RN-HO-03, RN-FE-03, RN-SI-04, RN-AU-04 | `409` solapamiento · `422` pasado / fuera de horario / feriado |
| `POST /api/v1/turnos/{id}/cancelar` | RN-CA-01/03/04 | `422` faltan 2 h · `403` rol odontólogo |
| `POST /api/v1/turnos/{id}/reprogramar` | RN-CA-02/03/05 | `409` destino ocupado (y nada cambia) |
| `PATCH /api/v1/turnos/{id}/estado` | RN-TU-07/08 | `422` transición ilegal |
| `POST /api/v1/turnos/sobreturno` | RN-TU-10/11, RN-AU-04 | `422` falta motivo |
| `PUT /api/v1/pacientes/{id}/odontograma/{pieza}` | RN-OD-01…09, RN-AU-04 | `403` sin turno propio · `422` pieza/cara/estado inválido |
| `DELETE /api/v1/pacientes/{id}` | RN-PC-07, RN-GL-01 | `409` tiene turnos no terminales |
| `PUT /api/v1/profesionales/{id}/horarios` | RN-HO-01…05 | `422` ventanas solapadas o domingo |
| `POST /api/v1/feriados` | RN-FE-01/04 | `409` ya existe · `409` hay turnos futuros afectados |
| `PATCH /api/v1/feriados/{id}` | RN-FE-01/06 | `409` la fecha editada ya la usa otro feriado activo |
| `DELETE /api/v1/feriados/{id}` | RN-FE-06, RN-GL-01 | Baja lógica. `404` si ya estaba inactivo |

---

## Apéndice: reglas retiradas o pendientes de confirmar

> Los códigos de esta tabla **no se implementan**: existen para que ninguna referencia histórica quede colgando y para que un código retirado **no se reutilice nunca** (convención de numeración, arriba). El dominio `RN-XP` tiene **4 códigos retirados y 0 activos**; `RN-OD-10` es un quinto código retirado, dentro de un dominio activo.

| Dominio | Prefijo | Códigos | Nº |
|---|---|---|---|
| Experiencia del paciente (reserva pública, recordatorios, exportación, obras sociales) | `RN-XP` | RN-XP-01, RN-XP-02, RN-XP-03, RN-XP-04 | **4 retiradas** |
| Odontograma (pieza decidua) | `RN-OD` | RN-OD-10 | 1 retirada |

| Código retirado | Regla | Motivo |
|---|---|---|
| `RN-XP-01` | Reserva online pública por enlace, sin cuenta | Fuera del MVP (DD-05). Vuelve como PA-02 |
| `RN-XP-02` | Notificación automática de recordatorio | Fuera del MVP (DD-07). Vuelve como PA-07 |
| `RN-XP-03` | Exportación de agenda y pacientes a CSV/Excel | Fuera del MVP (DD-16). Vuelve como PA-06 |
| `RN-XP-04` | Gestión de obras sociales y prepagas | Fuera del alcance del proyecto (PA-04) |
| `RN-OD-10` *(retirada)* | Piezas deciduas 51–85 en el odontograma | No solicitado; el enunciado pide piezas permanentes (PA-12) |

**Ninguna regla del MVP quedó sin confirmar.** Las que el Discovery marcó como supuesto (reglas de negocio **R1…R8**, §7 de `discovery/discovery.md`) están todas resueltas por decisión confirmada, con el código RN que las implementa:

| Regla del Discovery | Contenido | Resuelta por |
|---|---|---|
| **R1** | Un profesional no puede tener dos turnos solapados | RN-TU-05 (y DD-08) |
| **R2** | No se puede reservar en una fecha/hora pasada | RN-TU-02 |
| **R3** | No se puede reservar en un bloque horario bloqueado | RN-HO-03, RN-FE-03, RN-FE-05 |
| **R4** | La duración depende de la prestación, no es fija | RN-PR-02/03 (y DD-10, SU-05) |
| **R5** | Al cancelar, el horario queda automáticamente disponible | RN-CA-01, RN-TU-09 |
| **R6** | La clínica atiende en una franja horaria fija por día de semana | RN-HO-01/05 (y SU-06) |
| **R7** | El paciente no puede tener dos turnos simultáneos | RN-TU-06 (y DD-09, PA-03) |
| **R8** | Los feriados se contrastan contra el calendario nacional argentino | RN-FE-01…04 (y DD-18) |
| (sin código en el Discovery) | Antelación mínima de cancelación | RN-CA-03 (y DD-14) |

> Esta tabla **no** incluye las **restricciones `R-1…R-5`** del §9 del Discovery (criterio de éxito, claridad sobre complejidad, enfoque didáctico, stack web y presupuesto acotado): ésas no son reglas de negocio del sistema, son restricciones de proyecto. La glosario completa de los dos grupos de códigos `R` está en `09_decisiones_y_supuestos.md`.