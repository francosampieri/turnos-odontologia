# Preguntas Abiertas

Este archivo tiene dos secciones con propósitos distintos:

- **Inconsistencias detectadas (`IN-xx`)**: contradicciones entre lo que dice la investigación de mercado (`discovery/discovery.md`) y lo que el proyecto decidió. Están resueltas —cada una dice cuál es la resolución— pero se conservan porque **ocultarlas sería el error**: son exactamente lo que un jurado puede preguntar.
- **Preguntas abiertas (`PA-xx`)**: lo que sigue **sin respuesta**. No se inventan respuestas: se priorizan y se les asigna un decisor.

---

## Inconsistencias detectadas

### IN-01 — La anticipación mínima de cancelación: la investigación la descartó, el proyecto la adoptó

**Documento A dice**: `discovery/discovery.md` §7 — *"Sobre la anticipación mínima de cancelación: el prompt original la sugirió. **No se incluye como regla** — no hay evidencia en ningún proveedor argentino relevado de una política de cancelación con anticipación mínima, y en un contexto de consultorio chico imponerla sin dato real es inventar una política."*

**Documento B dice**: decisión confirmada — cancelar o reprogramar exige **al menos 2 horas** de antelación (`RN-CA-03`, DD-14).

**Impacto**: si no se explicita, la diferencia es invisible para quien lee sólo uno de los dos documentos. Y el riesgo real es de cumplimiento: una política de cancelación sin aviso al paciente es una política que se incumple, sobre todo sin recordatorios automáticos (PA-07).

**Resolución propuesta — adoptada**: la regla de 2 h entra como **decisión de diseño**, no como hallazgo de mercado. Se documenta como tal en DD-14, con la observación explícita de que el Discovery la descartó. 2 h es una ventana que rara vez bloquea a la secretaria y que todavía deja el horario liberado con chances de ser reocupado.

---

### IN-02 — La exportación de datos: el Discovery la puso **dentro** del MVP

**Documento A dice**: `discovery/discovery.md` §D.3 — *"Los 4 items de cierre"* del MVP incluyen *"**Exportación a CSV.** Es la única funcionalidad donde la matriz B mostró un hueco de mercado total y tiene costo de implementación despreciable. Es el diferencial honesto más barato que puede tener el proyecto."*

**Documento B dice**: decisión confirmada — la exportación **queda en el backlog** (DD-16, PA-06), pese a ser el hueco de mercado más grande del relevamiento (**0 de 10** proveedores argentinos la declara).

**Impacto**: el alcance del MVP cambia en un ítem. La sección D.3 del Discovery deja de ser la definición del MVP.

**Resolución propuesta — adoptada**: la exportación sale del MVP. El argumento es de privacidad por campo: exportar pacientes obliga a revisar permisos y tratamiento de DNI y fecha de nacimiento, que es trabajo tanto de Legal como de código. La exportación **de la agenda del día** (sin datos de pacientes) es mucho más inocua y queda como candidata de v1.1.

---

### IN-03 — El odontograma: la investigación lo sacó, el proyecto lo mete

**Documento A dice**: `discovery/discovery.md` §6 y §D.3 — *"Explicitamente fuera de alcance: historia clínica, odontograma, periodonto…"* y *"Historia clínica y odontograma | 10 de 10 competidores lo tienen: no es diferenciador. Multiplica el alcance ×5. Es el límite de la apuesta (riesgo 4)"*.

**Documento B dice**: decisión confirmada — el **odontograma entra en el MVP** con piezas y estados, sin imágenes (DD-04, RN-OD-01…09, US-040…042).

**Impacto**: es la inversión más grande de alcance respecto de la investigación, y **invierte también el riesgo nº 4** del Discovery ("¿acepta el cliente un sistema sin odontograma?"): esa pregunta pasa de ser bloqueante a estar resuelta en la dirección contraria.

**Resolución propuesta — adoptada**: entra acotado a su forma más simple (dos tablas, notación FDI, catálogo cerrado de estados, historial). Las imágenes quedan diferidas a una fase 2 del módulo (PA-01). Esto es lo que permite que el sistema sea defendible frente a un mercado donde los 10 proveedores tienen odontograma.

---

### IN-04 — El caso de uso 5 (reserva online del paciente) sigue listado como caso de uso

**Documento A dice**: `discovery/discovery.md` §3 y §2 — el caso de uso 5 ("como **paciente**, quiero reservar un turno desde el celular…") está en la lista de los cinco casos de uso, y §2 afirma que *"la reserva online es por enlace, sin cuenta"*.

**Documento B dice**: decisión confirmada — **agenda interna solamente**. No hay reserva pública, ni portal del paciente, ni WebSocket (DD-05).

**Impacto**: el Discovery dejó este caso marcado como *"la parte más costosa y de mayor riesgo de concurrencia"* y lo señaló como pregunta bloqueante nº 1. Mantenerlo listado sin marcarlo como descartado hace que el alcance parezca mayor de lo que es.

**Resolución propuesta — adoptada**: el caso de uso 5 se marca explícitamente como **fuera del MVP** en `06_funcionalidades.md` (tabla de trazabilidad) y en `01_vision_y_objetivos.md` (fuera de alcance), con la razón completa: autenticación de actor no confiable, rate limiting, anti-abuso y concurrencia sobre el último horario. Regresa como PA-02.

---

### IN-05 — La restricción R-4 (web, multiusuario, base de datos) era un supuesto sin confirmar

**Documento A dice**: `discovery/discovery.md` §9 — *"**R-4 Web, multiusuario, base de datos** — **[Supuesto]**, a confirmar. Es la elección técnica que más condiciona el diseño… Este Discovery **no decide** R-4. La decisión técnica de stack le corresponde a `kb-creator`."*

**Documento B dice**: la restricción se resuelve por decisión del profesor: backend Python/FastAPI + frontend React/TypeScript/Vite como **aplicaciones separadas**, PostgreSQL como base (DD-01, DD-03).

**Impacto**: era **la** decisión que más condicionaba el modelo de datos, porque de ella depende que la regla R1 (no-solapamiento) pueda garantizarse en la capa de datos. Con una aplicación local, el problema de la doble reserva seguiría existiendo a nivel de datos.

**Resolución propuesta — adoptada y resuelta**: web + multiusuario + base relacional, confirmada. El modelo de datos de `04_modelo_de_datos.md` incluye `EXCLUDE USING gist`, que sólo es posible en PostgreSQL. El supuesto queda cerrado.

---

### IN-06 — El sobreturno era "funcionalidad opcional de prioridad media", hoy es parte del MVP

**Documento A dice**: `discovery/discovery.md` §6 — *"**Prioridad media**: turnos urgentes / sobreturnos fuera de la agenda del día."*

**Documento B dice**: el sobreturno es un **estado de la máquina**, un **endpoint propio** y la **única excepción** a las restricciones de no-solapamiento (`RN-TU-10/11`, DD-11, US-037).

**Impacto**: si se implementa sólo "como funcionalidad opcional", sin estado propio y sin excepción acotada en el modelo, aparece el problema que la decisión evita: para cargar una urgencia hay que pisar un turno sin registro, o hay que agregar un flag libre que desactiva silenciosamente el anti-solapamiento.

**Resolución propuesta — adoptada**: sobreturno en el MVP como excepción acotada. Si la urgencia **no** se necesita en la demostración, la funcionalidad queda sin uso pero **la excepción del modelo sigue siendo correcta**: el `EXCLUDE` parcial tiene que excluir algo, y el sobreturno es lo único que tiene sentido excluir.

---

### IN-07 — La auditoría era "prioridad baja", y la impresión de agenda desapareció

**Documento A dice**: `discovery/discovery.md` §6 — *"**Prioridad baja**: auditoría de cambios: quién modificó qué turno y cuando."* y *"**Prioridad media**: impresión de la agenda del día en formato lista."*

**Documento B dice**: la **auditoría entra en el MVP** (DD-17, US-005, RN-GL-04); la impresión de agenda del día **no está** en ninguna historia de `06_funcionalidades.md`.

**Impacto**: si el alcance se define por las historias de usuario, la impresión de agenda no existe; y si la auditoría se trata como opcional, el proyecto pierde la respuesta directa a su propio riesgo nº 1 ("dependencia de una sola persona").

**Resolución propuesta — adoptada**: auditoría dentro, impresión de agenda fuera. La auditoría es barata (una tabla append-only y un `INSERT` dentro de la transacción que ya existe) y responde al problema central. La impresión es una función de conveniencia, no una necesidad.

---

### IN-08 — El enunciado de problema incluye "que avise al paciente" y el MVP no avisa a nadie

**Documento A dice**: `discovery/discovery.md` §1 — la formulación en una frase del problema incluye *"y que **avise al paciente antes del turno** para que no se pierda el horario"*, y el riesgo nº 2 habla de que "sin recordatorio automático… el horario se pierde como ingreso".

**Documento B dice**: los recordatorios por WhatsApp, SMS y email están **fuera del MVP** (DD-07, RN-XP-02, PA-07).

**Impacto**: es la inconsistencia más visible para un jurado. El proyecto promete resolver un problema cuya cuarta mitad no toca.

**Resolución propuesta — adoptada**: **enunciar el problema que el proyecto efectivamente resuelve**: el núcleo de turnos más la ficha clínica mínima (odontograma). El texto de `01_vision_y_objetivos.md` lo dice de entrada, con una nota de encuadre. La mitigación de frente es reconocer que la automatización de avisos es exactamente lo que hacen los proveedores grandes con un costo variable por mensaje, y que el proyecto apuesta por **el control de la agenda** en lugar de **la automatización de avisos**.

---

### IN-09 — Los feriados: la regla R8 quedó como supuesto y se resolvió sin fuente

**Documento A dice**: `discovery/discovery.md` §7 — *"**R8** Los feriados se contrastan contra el calendario nacional argentino — **Supuesto**, a confirmar. Solo IA Sistemas lo declara explícitamente entre los 10 argentinos; FLAP lo resuelve con 'bloqueos' manuales."*

**Documento B dice**: los feriados se cargan por seed con el calendario nacional y se administran a mano; **no** hay ninguna API de feriados (DD-18, `RN-FE-01…04`).

**Impacto**: si se implementa una sincronización automática, el sistema queda con una dependencia externa que contradice el principio "funciona con la base sola" (RN-GL-06). Si no se implementa, hay que asumir explícitamente la carga manual.

**Resolución propuesta — adoptada**: carga manual, sin API externa. Un sistema de una clínica que se queda sin internet un viernes tiene que poder seguir funcionando. Queda el trabajo de cargar el calendario del año como **PA-09**.

---

### IN-10 — Redis forma parte del stack requerido, pero el MVP no lo usa

**Documento A dice**: el stack impuesto por el enunciado incluye Redis; la integración en Docker Compose se da por descontada.

**Documento B dice**: Redis **arranca** en el Compose y **ninguna parte del MVP lo usa**. No hay procesos asíncronos: no hay emails, no hay reportes, no hay cola (DD-06).

**Impacto**: si Redis aparece en el Compose sin explicación, parece un resto de plantilla. Si no aparece, se ve como un incumplimiento del stack pedido.

**Resolución propuesta — adoptada**: declarado, arrancando y sin uso, **con la justificación escrita y el listado de lo que sí lo justificaría** (recordatorios con reintentos, invalidación de caché de disponibilidad, rate limiting de un endpoint público, reportes pesados). Es más honesto y más defendible que un Redis silencioso.

---

### IN-11 — La regla de simultaneidad del paciente: se corrige una premisa de la instrucción original

**Instrucción A dice**: al armar el modelo de datos se pidió *"un `EXCLUDE` constraint con `btree_gist` y `tstzrange` para la ocupación del profesional, más una comprobación transaccional a nivel de aplicación para la regla de simultaneidad del paciente, ya que un `EXCLUDE` no puede abarcar dos filas distintas del eje del profesional"*.

**Documento B dice**: `04_modelo_de_datos.md` define **tres** `EXCLUDE USING gist` parciales e independientes — `turno_no_solape_profesional`, `turno_no_solape_paciente` y `turno_no_solape_sillon` — y trata la simultaneidad del paciente (RN-TU-06) como **garantizada por la base**, no por la aplicación.

**Por qué la instrucción A es técnicamente incorrecta**: un constraint de exclusión no está atado a un único eje de identidad, y **no** necesita abarcar las dos filas que compiten. `profesional_id WITH =` y `paciente_id WITH =` son **dos invariantes distintas**, cada una en su propio constraint, y PostgreSQL las evalúa de forma autónoma. No hay ninguna limitación técnica que obligue a degradar la regla del paciente a un chequeo de aplicación. Lo que sí exigiría un chequeo transaccional en la aplicación es una invariante **entre tablas distintas** (por ejemplo, "el paciente no puede tener dos filas en `odontograma` con una cita simultánea"), que no es el caso.

**Impacto**: si la regla del paciente quedara apoyada sólo en la aplicación, la invariante central del proyecto quedaría partida en dos capas de fiabilidad distintas — y la parte más débil sería exactamente la que el Discovery marcó como **[NE] en los 20 proveedores relevados**, es decir, la que nadie va a auditar en la defensa. Es el peor lugar para dejar una excepción al modelo.

**Resolución propuesta — adoptada**: los tres solapamientos se garantizan en la capa de datos con la misma mecánica. La comprobación previa en la aplicación **se mantiene y se documenta** (`04_modelo_de_datos.md` § "Comprobación previa en la aplicación"), pero con su rol real y correctamente limitado: elegir qué mensaje de `409` devolver, **asignar automáticamente un sillón libre**, y evitar el viaje hasta la excepción. Se documenta explícitamente por qué **una comprobación sólo de aplicación sería insuficiente** (condición de carrera TOCTOU bajo `READ COMMITTED`, que se cierra con `SERIALIZABLE` al costo de obligar a la aplicación a reintentar la transacción completa). Ver DD-08, DD-09 y RN-TU-04/05/06.

---

## Preguntas abiertas (priorizadas)

**Definición de prioridad**: *Alta* = cambia el modelo de datos o el alcance del MVP; *Media* = agrega funcionalidad sobre el modelo actual; *Baja* = mejora sin impacto estructural.

| # | Prioridad | Pregunta | Qué implica decidirlo | Bloquea | Decisor |
|---|---|---|---|---|---|
| **PA-01** | Alta | ¿Entra la imagen del odontograma (radiografías y fotos) en una segunda fase del módulo? | Almacenamiento binario, estándar de imágenes, revisión de privacidad y mayor alcance de la Ley 26.529. El MVP está escrito para que esta agregación **no** requiera cambiar el modelo de turnos ni las reglas de agenda | Fase 2 del módulo | Alumnos + docente |
| **PA-02** | Alta | ¿Se implementa reserva online pública, y bajo qué esquema de identidad del paciente? | Un subsistema completo: autenticación o verificación del paciente, rate limiting, anti-abuso, concurrencia sobre el último horario y reconciliación de reservas abandonadas | Cierre del alcance del producto | Alumnos + docente |
| **PA-03** | Media | ¿El anti-solapamiento de paciente necesita una excepción para casos de equipo (cirugía en equipo, sedación)? | Un campo `motivo_excepcion` y una cuarta restricción GiST parcial. Hoy el sistema **no puede** representar a un paciente en dos sillones a la vez | Casos clínicos reales | Odontólogo consultada |
| **PA-04** | Media | ¿La clínica atiende obras sociales o prepagas? | Si sí: entidad de cobertura, nomencladores, coseguros, liquidación. Sólo 3 de 10 proveedores argentinos lo manejan de forma explícita; hoy el sistema lo excluye y eso hay que decirlo | Módulo de cobertura | Alumnos + cliente |
| **PA-05** | Media | ¿Entra facturación electrónica, caja o presupuestos? | AFIP/ARCA es de alta complejidad normativa. Dentatools opera **declarando** que no emite factura AFIP, así que hay precedente para dejarlo afuera | Módulo administrativo | Alumnos + docente |
| **PA-06** | Alta | ¿Cuándo entra la exportación de datos (CSV/Excel)? | Es el **hueco de mercado más grande** del relevamiento (0 de 10 proveedores) y la funcionalidad más barata de implementar. Choca con el criterio de privacidad por campo sobre DNI y fecha de nacimiento | Versión v1.1 | Alumnos |
| **PA-07** | Alta | ¿Entra el recordatorio por WhatsApp y quién paga el costo por mensaje? | Requiere cuenta empresarial verificada de Meta, costo variable (ixi: $45 + IVA por mensaje; DentalSoft Pro: USD 0,026) y **el uso real de Redis** como cola con reintentos | Automatización de avisos | Alumnos + docente |
| **PA-08** | Media | ¿El registro odontográfico pasa a ser historia clínica electrónica? | Mientras no haya historia clínica, el MVP no está alcanzado por la Ley 26.529. Si se agrega historia clínica, esa obligación entra **con ella** | Cumplimiento normativo | Alumnos + docente |
| **PA-09** | Baja | ¿Los feriados se sincronizan con una fuente externa o siguen siendo carga manual? | Hoy son carga manual (DD-18). Una fuente externa agrega dependencia y punto de falla | Operación anual | Admin de la clínica |
| **PA-10** | Baja | ¿Se integra Google Calendar con la agenda? | Baja complejidad técnica (OAuth + REST) y es la primera integración de bajo riesgo | Alcance post-MVP | Alumnos |
| **PA-11** | Media | ¿Entra lista de espera para rellenar huecos producidos por cancelaciones? | Exige decidir quién entra a la lista y en qué orden, y **cómo** se le avisa (mismo problema de costo que PA-07) | Agregado a agenda | Alumnos |
| **PA-12** | Baja | ¿El odontograma incluye dentición decidua (piezas 51–85)? | Agrega 20 filas por paciente y un flag de dentición; hoy el modelo es sólo permanente | Fase 2 del módulo | Odontólogo consultada |
| **PA-13** | Baja | ¿Aparece un segundo cliente sobre la misma instalación? | `clinica_id` atraviesa todas las tablas, todas las consultas y todas las pruebas de autorización | Arquitectura | Alumnos |
| **PA-14** | Baja | ¿Se agrega reporte de ocupación e impresión de la agenda del día? | Son consultas agregadas y una vista de impresión. Es la forma más barata de "análisis de gestión" | Reporting | Alumnos |
| **PA-15** | Baja | ¿Cómo se resuelve la recuperación de contraseña y la renovación de sesión? | Hoy el `admin` la resuelve por consola y no hay `refresh token` (RN-AU-07). Es una brecha de usabilidad, no de seguridad | Autenticación | Alumnos |

### Supuestos que siguen abiertos (sin respuesta, y no son funcionalidades)

Estos no son preguntas de producto: son creencias que el proyecto usa y que nadie verificó. Están desarrolladas en detalle en `09_decisiones_y_supuestos.md` (SU-01…SU-08).

| Supuesto | Cómo se validaría | Impacto si es falso |
|---|---|---|
| **SU-01** — la clínica necesita digitalizar de verdad | Una entrevista con una clínica real | Es el **riesgo nº 1 del proyecto**: afecta la premisa, no la implementación |
| **SU-02** — el solapamiento es el dolor principal | Preguntar a la secretaria cuál es su molestia principal | El sistema resolvería un problema real pero secundario |
| **SU-03** — el cliente tiene recepción y más de un profesional | La misma entrevista de SU-01 | Sobrarían el módulo de roles y la agenda multiprofesional |
| **SU-04** — un sistema sin historia clínica es aceptable | Preguntar qué parte de la ficha en papel costaría más abandonar | Mitigado parcialmente: el odontograma entra al MVP (DD-04) |
| **SU-05** — las duraciones reales caen en {15, 30, 45, 60} | Pedir la tabla real de duraciones al cliente | Agregar valores al `CHECK` (migración menor) |
| **SU-06** — el horario Lun–Vie 08:00–18:00 sirve | Preguntarlo en la primera reunión de setup | Ninguno: el horario es 100 % configurable |
| **SU-07** — no habrá un segundo cliente | Preguntar antes de que exista la base instalada | `clinica_id` atraviesa todo el modelo |
| **SU-08** — no hay presupuesto para servicios pagos | Confirmarlo con el docente | El alcance crece y el sistema deja de ser autónomo |

---

## Cómo se cierran estas preguntas

No hay que responderlas todas para entregar. El orden honesto es:

1. **Antes de escribir código**: PA-01, PA-02, PA-06, PA-07 (definen el alcance del MVP) y PA-13 (define si el modelo lleva `clinica_id`).
2. **Antes de la entrega**: PA-04, PA-05, PA-08 (son declaraciones de alcance: decir que no entran es correcto; olvidarlas es el error).
3. **Después de la entrega**: PA-09, PA-10, PA-11, PA-12, PA-14, PA-15.
4. **En cualquier momento, pero idealmente temprano**: SU-01 y SU-03, que son los únicos supuestos cuya falsedad cambiaría el proyecto entero.

Una respuesta que llega tarde y es anotada acá vale más que una respuesta inventada y no anotada.