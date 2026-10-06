# Visión y Objetivos

## Propósito del sistema

**Turnos Odontología** es el sistema de gestión de agenda, pacientes y odontograma de una clínica odontológica de una sola sede. Su propósito es **darle a la clínica una agenda única, con disponibilidad real por profesional, que se pueda consultar y reservar desde el navegador, y en la que sea imposible que un horario quede reservado dos veces.**

La clínica objetivo coordina hoy la agenda por teléfono, WhatsApp personal y papel. De ahí provienen los tres daños concretos que el sistema ataca:

| Daño | Causa actual | Cómo lo ataca el sistema |
|---|---|---|
| **Doble reserva y solapamiento** | No hay una única fuente de verdad de disponibilidad | Regla de no-solapamiento garantizada **por la base de datos**, no por el formulario (RN-TU-03/04/05) |
| **Dependencia de una sola persona** | Si la secretaria falta, la agenda deja de entenderse | Agenda persistida en base de datos, con permisos por rol (RN-AU-02) |
| **Desorden de la ficha clínica mínima** | La pieza y su estado se anotan en papel y se pierden | Odontograma por paciente con piezas, estados y caras (RN-OD-01…09) |

> **Nota de encuadre (importante para la defensa).** El problema declarado en el Discovery incluía *"que avise al paciente antes del turno"* como parte de la solución. Los recordatorios (WhatsApp/SMS/email) están **fuera del MVP** (ver *Fuera de alcance* y DD-07). El enunciado de problema que este proyecto resuelve es, por lo tanto, **el núcleo de turnos + ficha mínima**, no la automatización de avisos. Ver `10_preguntas_abiertas.md` → IN-08.

---

## Objetivos por actor

| Actor | Objetivo principal | Objetivos secundarios |
|---|---|---|
| **Secretaria / recepción** | Cargar, reprogramar y cancelar turnos sin depender del odontólogo | Ver la agenda del día de todos los profesionales en una pantalla; saber a quién atender y en qué orden; encontrar un paciente rápido por DNI, apellido o teléfono; no volver a producir una doble reserva |
| **Odontólogo** | Ver sus turnos del día con la ficha básica del paciente a mano | Registrar el estado de las piezas de sus pacientes en el odontograma; no cargar turnos (esa es la tarea de recepción); no ver la agenda de otros profesionales |
| **Administrador / dueño** | Ver y configurar toda la operación de la clínica | Ver la agenda de todos los profesionales; configurar horarios, feriados, duraciones, sillones y usuarios; auditar quién modificó qué |
| **Paciente** *(indirecto, sin login)* | No depender de una persona específica para reservar | No es un usuario del sistema en el MVP: **no hay portal, ni cuenta, ni contraseña** (DD-05) |

---

## Alcance v1.0

### Datos maestros

- **Alta, edición, baja lógica y búsqueda de pacientes** — nombre, apellido, DNI (único), teléfono, email, fecha de nacimiento (RN-PC-01…07).
- **Catálogo de profesionales** (odontólogos), cada uno vinculado a un usuario del sistema, con specialty/especialidad y **horario laboral propio y configurable** (RN-PR-01, RN-HO-01…05).
- **Catálogo de servicios** con **duración propia** (15 / 30 / 45 / 60 minutos), con posibilidad de override por profesional (RN-PR-02/03).
- **Catálogo de sillones** (configurable, en cantidad variable) para una única clínica (RN-SI-01…05).
- **Calendario de feriados** (nacional argentino + locales) y **bloqueos por profesional** (vacaciones, congressos) (RN-FE-01…05).

### Agenda y turnos

- **Agenda del día** por profesional y **agenda de la semana** — es la pantalla principal del producto (US-030, US-031).
- **Cálculo de disponibilidad** en slots a partir de horario laboral − feriados − bloqueos − turnos existentes (US-032).
- **Reserva de turno** eligiendo paciente, profesional, sillón, servicio, fecha y hora (US-033).
- **Cancelación** y **reprogramación** con liberación automática del horario, en transacción única (RN-CA-01/02).
- **Antelación mínima de 2 horas** para cancelar o reprogramar (RN-CA-03).
- **Máquina de estados de 7 estados**: `agendado`, `confirmado`, `en_curso`, `completado`, `cancelado`, `no_asistió`, `sobreturno` (RN-TU-07).
- **Sobreturno** como excepción controlada y explícita a la regla de no-solapamiento (RN-TU-10).

### Odontograma

- **Odontograma por paciente**, notación FDI, **32 piezas permanentes (11–48)**, una fila por pieza.
- **Estados de pieza** (12 estados) y **cara** afectada (5 caras o la pieza completa).
- **Historial de cambios** de estado de cada pieza, con autor y fecha (RN-OD-07).
- **Sin imágenes, sin radiografías, sin fotos.** Ver DD-04.

### Seguridad y trazabilidad

- **Autenticación JWT** con tres roles fijos: `secretaria`, `odontologo`, `admin` (RN-AU-01…07).
- **RBAC aplicado en la capa de datos**, no sólo ocultando botones en el frontend (RN-AU-05).
- **Auditoría** append-only de acciones sensibles (RN-GL-04).
- **Nota de privacidad y consentimiento** conforme a la Ley 25.326 de Protección de Datos Personales.

### Presentación

- Backend y frontend como **aplicaciones separadas** (REST API entre ambas) (DD-01).
- **Docker Compose** para orquestar backend, frontend, PostgreSQL y Redis (DD-06).
- Interfaz **operable**, no sólo demostrable: tiene que poder cargarse un mes real de agenda.

---

## Fuera de alcance

Todo lo siguiente está **explícitamente** afuera del MVP. No es un olvido: cada ítem está consignado con su razón.

| Fuera de alcance | Razón | Dónde queda |
|---|---|---|
| **Reserva online pública / autoservicio del paciente** | Exige autenticación del paciente (o verificación de teléfono), cálculo de slots públicos en tiempo real, **rate limiting y anti-abuso** — es decir, todo un subsistema de seguridad adicional. El Discovery lo señaló como *"la parte más difícil del MVP, no la más fácil"* (riesgo técnico 6) | Backlog — DD-05, PA-02 |
| **Confirmación en vivo por WebSocket** | Requiere WebSockets + reconexión + estado distribuido. La confirmación en el MVP es un cambio de estado explícito por la secretaria | Backlog — DD-05 |
| **Recordatorios por WhatsApp / SMS / email** | Costo variable por mensaje (ixi declara USD $45 + IVA por mensaje entregado; DentalSoft Pro, USD 0,026 por recordatorio), dependencia de Meta y cuenta empresarial verificada | Backlog — DD-07 |
| **Radiografías, fotos e imágenes del odontograma** | Requiere almacenamiento binario (o integración con un PACS), estándar de imágenes y una revisión de privacidad adicional. Es una fase completa del módulo | Fase 2 — DD-04, PA-01 |
| **Historia clínica electrónica, evoluciones, periodonto, ortodoncia** | Fuera de alcance por definición del proyecto. Multiplica el alcance ×5 | Fuera — `10_preguntas_abiertas.md` |
| **Prescripciones / recetas electrónicas** | Alta complejidad normativa; el Discovery verificó que sólo 2 de 20 proveedores citan un registro oficial (ReNaPDiS #248, #292) | Fuera |
| **Facturación electrónica, AFIP/ARCA, caja, presupuestos** | Alta complejidad normativa. Dentatools opera **declarando explícitamente que no emite factura AFIP** | Fuera |
| **Obras sociales / prepagas** | Sólo 3 de 10 proveedores argentinos lo manejan de forma explícita. Fuera es una decisión consciente; olvidarlo sería el error | Fuera — PA-04 |
| **Reportes avanzados y dashboard** | El MVP entrega la agenda y el odontograma; el análisis de ocupación es post-MVP | Backlog |
| **Exportación de datos (CSV / Excel)** | Es **el hueco de mercado más grande** que encontró el Discovery (0 de 10 proveedores argentinos la declara) y tiene costo de implementación despreciable, pero queda en el backlog por alcance | Backlog — DD-16, PA-06 |
| **Multi-sucursal / multi-tenant** | Una clínica con dos gabinetes **no** es multi-sucursal. El modelo de datos no lo contempla (DD-12) | Fuera |
| **App móvil nativa** | La interfaz web es responsive; una app nativa duplica el alcance | Fuera |
| **IA, chatbot, teleodontología** | Es donde va el mercado, y donde las afirmaciones de los proveedores no son verificables | Fuera |

### Sobre el uso de Redis

Redis **está declarado y arranca** en `docker-compose.yml`, y **no se usa para nada funcional en el MVP**. No hay jobs asíncronos: no se envían emails, no se generan reportes, no hay cola de tareas. Se documenta con su justificación completa en `08_arquitectura_propuesta.md` y DD-06, incluyendo qué tendría que justifies su uso real.

---

## Métricas de éxito

El criterio de éxito **no** es la cuota de mercado ni el número de funcionalidades: es **que el sistema se pueda explicar y defender** (restricción **R-1** del Discovery, §9) y que **resuelva sin ambigüedad el problema que dice resolver**.

### Métricas técnicas (verificables, con evidencia propia)

| # | Métrica | Objetivo | Cómo se verifica |
|---|---|---|---|
| M-1 | **Dobles reservas** producidas por el sistema | **0** | Test de concurrencia: dos peticiones simultáneas de reserva sobre el mismo slot → exactamente una responde 201 y la otra 409 |
| M-2 | Solapamientos existentes en la base | **0** | Consulta directa sobre `turno` contando pares que se solapen |
| M-3 | Tiempo de carga de la agenda del día | < 1 s con 200 turnos | Medición en el navegador |
| M-4 | Tiempo para agendar un turno con paciente existente | < 30 s | Prueba manual cronometrada |
| M-5 | Peticiones al endpoint de reserva que llegan a la capa de aplicación y son rechazadas por conflicto | Medible y > 0 cuando hay concurrencia | Log de respuestas 409 |

### Métricas funcionales (verificables por observación)

| # | Métrica | Objetivo |
|---|---|---|
| M-6 | Un mes real de agenda cargado por la secretaria sin intervención del odontólogo | **Completo y sin doble reserva** |
| M-7 | El odontólogo puede abrir el sistema y ver *sólo* sus turnos del día, con la ficha del paciente, sin pedirle nada a nadie | **Sí** |
| M-8 | Al cancelar un turno, el horario queda disponible para otro paciente sin ninguna edición manual | **Sí** |
| M-9 | El sistema funciona completo **sin ninguna integración externa pagada** | **Sí** |
| M-10 | Un usuario ajeno puede explicar qué problema resuelve el sistema y por qué el odontograma es parte de él | **Sí** (métrica de defensa) |

### Métricas explícitamente **no** objetivo

- Número de módulos (el Discovery identificó el riesgo de sobre-alcance por contaminación del mercado: los proveedores arman bundles de 9 a 17 módulos).
- Porcentaje de ausentismo reducido (ningún proveedor argentino publica métricas de campo verificables; las cifras de DentalSoft e IA Sistemas son afirmaciones comerciales **[A]**).
- Cualquier métrica de adopción comercial: **no hay cliente real validado**.

---

## Criterio de éxito, en una frase

> Que una secretaria y un odontólogo puedan operar la agenda de un mes real, en multiusuario, sin solapamientos y sin depender de ningún servicio externo de pago — y que eso se pueda explicar en quince minutos.