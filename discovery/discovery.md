# Discovery — Turnos Odontología

**Proyecto**: Sistema de gestión de turnos, pacientes y agenda para clínica odontológica
**Fecha**: 2026-10-04
**Fase**: Discovery (precedente a `kb-creator`)
**Fuentes investigadas**: 20 sistemas (10 argentinos odontológicos, 6 argentinos de medicina general, 1 latinoamericano, 3 internacionales)
**Criterio de evidencia**: se consultó la página oficial de cada proveedor el 2026-10-04. Se marca **[C]** lo que es **funcionalidad comprobada** (descrita con detalle funcional en la fuente oficial) y **[A]** lo que es **afirmación comercial** (metricas de resultado, cantidad de clientes, barreras de entrada) sin evidencia independiente verificable. **[NE]** = **No evidenciado**.

---

## 1. Problema que resuelve

Las clinicas odontologicas chico-medianas en Argentina coordinan la agenda por telefono, WhatsApp personal y papel. Eso produce tres danos concretos y medibles:

1. **Doble reserva y solapamiento**: no existe una unica fuente de verdad de disponibilidad, asi que el mismo slot se promete dos veces.
2. **Ausentismo**: sin recordatorio automatico, el paciente se olvida del turno, no vuelve, y el horario se pierde como ingreso.
3. **Dependencia de una sola persona**: si la secretaria falta, la agenda deja de entenderse y la clinica se frena.

**Formulacion en una frase**: *darle a una clinica odontologica una agenda unica, con disponibilidad real por profesional, que se pueda consultar y reservar desde el celular, y que avise al paciente antes del turno para que no se pierda el horario.*

Este problema es **el mismo que resuelven los competidores**, no uno distinto. La diferencia no esta en el problema sino en el **alcance**: los proveedores argentinos priorizan el componente clinico (odontograma, historia clinica, obras sociales) y compiten por productividad; el proyecto apunta a resolver **solo el nucleo de turnos**, que es un problema mas chico pero no resuelto en el mercado local sin pagar un suite completo.

---

## 2. Usuarios / roles

Con **verbo principal** por rol, segun `references/checklist.md`:

| Rol | Verbo principal | Que necesita del sistema |
|---|---|---|
| **Secretaria / recepcion** | agendar | Cargar y modificar turnos sin depender del odontologo; ver la agenda del dia completa; evitar solapamientos; buscar pacientes rapido |
| **Odontologo** | atender | Ver solo sus turnos del dia; ficha basica del paciente a mano al abrir el turno |
| **Administrador / dueno** | administrar | Ver la agenda de todos los profesionales; saber cuantos turnos hay y cuantos se cumplieron |

**Sobre el login por rol**: si. Tres roles, tres permisos. No es un requisito cosmetico — la secretaria necesita escribir turnos y el odontologo solo leer los suyos. Sin esta separacion, el odontologo termina cargando turnos que le corresponden a la secretaria, que es exactamente el problema que el sistema viene a resolver.

**Fuera del alcance de roles**: portal de autoservicio del paciente con usuario y contrasena **no** es necesario para el MVP. La reserva online es por enlace, sin cuenta. Ver punto 6.

---

## 3. Casos de uso

Cinco casos de uso, en formato "como [rol], quiero [accion] para [resultado]". Los tres primeros bloquean el MVP.

1. Como **secretaria**, quiero **cargar un turno** eligiendo profesional, fecha, hora y paciente, para **que el horario quede reservado y no se pueda sobreescribir por error**.
2. Como **secretaria**, quiero **ver la agenda del dia** de todos los profesionales en una sola pantalla, para **saber a quien atender y en que orden sin preguntar**.
3. Como **odontologo**, quiero **ver solo mis turnos del dia con la ficha basica del paciente**, para **atender sin buscar informacion en otro lado**.
4. Como **secretaria**, quiero **cancelar o reprogramar un turno** y **que el horario quede libre automaticamente**, para **poder ofrecerlo a otro paciente sin borrado manual**.
5. Como **paciente**, quiero **reservar un turno desde el celular sin llamar ni instalarme nada**, para **no perder tiempo en un turno telefonico**.

El caso 5 es el unico que toca al paciente, y es tambien el de mayor esfuerzo de construccion (pagina publica, slots calculados, conflictos). Ver seccion D para la justificacion de incluirlo o no.

---

## 4. Competidores / soluciones existentes

Se relevaron 20 sistemas. El detalle completo esta en la **Seccion A**; aca va la lectura sintetica.

**El hallazgo principal**: el competidor real del proyecto **no es otro software de odontologia**. El mercado argentino esta saturado de suites completos (DentalSoft, DenPro, DentalCore, OdontoClinIA, Dentiqa, Dentatools, FLAP, Sigo, IA Sistemas) que ya resuelven turnos **y** odontograma **y** obras sociales **y** facturacion. Competir contra ellos en funcionalidad es imposible para un TP.

**Como se compite entonces**: por **alcance deliberadamente acotado** y **transparencia**. Dos competidores directos de niche lo hacen bien y son el modelo a seguir:

- **Odontoly** (AR, USD 149,99/mes): 2 usuarios, 4 dispositivos, la informacion clinica **permanece en la computadora del consultorio**, instalador firmado y notarizado. El trade-off explicito y sin marketing de superlativos.
- **ixi** (AR): publica el **precio de lista desde el primer dia** ($11.000 + IVA por profesional/mes) aunque hoy cobre $0 por el plan fundador, y exporta datos al irse. La transparencia es el argumento de venta.

**Correccion importante sobre la lista original de competidores**: el prompt inicial mencionaba *Gestionix* como posible competidor. **Investiguado y descartado**: Gestionix era un ERP mexicano para pymes y contadores, adquirido por la fintech Konfio en diciembre de 2020 y **cerrado el 30 de octubre de 2023**. No tiene relacion con salud ni con Argentina. Se documenta en el punto 11 como supuesto que resulto falso.

Tampoco se pudo confirmar la existencia de **"SysTurno"** ni de un producto llamado **"Turnos Online"** como competidor dental argentino identificable (**[NE]**). **Calendly** es genérico de calendario, sin odontograma, sin ficha de paciente, sin obras sociales: sirve de referencia de UX de reserva, no de producto de salud.

---

## 5. Funcionalidades necesarias (MVP)

Innegociable para la primera version. Ordenada por prioridad de implementacion.

| # | Funcionalidad | Por que es innegociable |
|---|---|---|
| 1 | Ficha de paciente (nombre, apellido, DNI, telefono, mail, fecha de nacimiento) | Sin identificador de paciente no hay agenda: es el primero de los tres modulos |
| 2 | Gestion de profesionales (odontologos) | La agenda es **por profesional**. Sin profesionales no hay agenda |
| 3 | Agenda por dia y por profesional | Es la pantalla de la que vive la secretaria y el odontologo. Es el producto |
| 4 | Reserva de turno (fecha, hora, profesional, paciente, tratamiento breve) | La operacion central |
| 5 | Validacion anti-solapamiento | **Regla de negocio que no puede fallar**: doble reserva es el dano principal que se viene a eliminar. Va en la capa de datos, no solo en la interfaz |
| 6 | Cancelacion y reprogramacion | El turno se libera y vuelve a estar disponible sin edicion manual |
| 7 | Listado de turnos del dia | La consulta mas frecuente del odontologo |
| 8 | Busqueda basica de pacientes | Sin busqueda, la secretaria no encuentra al paciente y abandona el sistema |

**Ajuste al alcance propuesto en el prompt**: se agregan, porque sin ellos el MVP no cierra, tres items que no estaban explicitos en la lista original:

- **Roles y permisos basicos** (secretaria / odontologo / administrador). Ver punto 2.
- **Duracion variable por prestacion**: los turnos odontologicos no duran 30 minutos todos (una limpieza no es una endodoncia). Si se fija 30 minutos, el modelo de datos del turno es incorrecto desde el dia 1 y despues hay que migrar.
- **Bloqueos y feriados**: el odontologo tiene vacaciones, dias que no atiende y la clinica tiene feriados. Sin esto la agenda ofrece horarios que en realidad no existen - que es el riesgo mas caro del sistema.

---

## 6. Funcionalidades opcionales

Post-lanzamiento. Fuera del MVP, pero **consignadas con criterio** para que no se agranden por default a mitad de implementacion.

**Prioridad alta (altamente deseables, costo acotado)**
- **Recordatorio por WhatsApp al paciente**. Es la funcionalidad que mas impacto tiene en el problema real (ausentismo). Contra: costo por mensaje de la API de Meta, dependencia de un tercero y **no verificable sin probarla**.
- **Reserva online publica por enlace**, sin cuenta ni app: el paciente elige profesional, fecha y hora sobre disponibilidad real.
- **Lista de espera**: cuando alguien cancela, ofrecer el hueco a un paciente de espera. Mas complejo de lo que parece (hay que decidir quien y en que orden).

**Prioridad media**
- **Reporte de ocupacion** (cuantos turnos por profesional, por franja horaria, cuantos se cumplieron).
- **Impresion de agenda del dia** en formato lista para dejar en recepcion.
- **Turnos urgentes / sobreturnos** fuera de la agenda del dia.
- **Exportar la agenda del dia a CSV/Excel** para el docente o para el contador.

**Prioridad baja (post-MVP)**
- **Notificaciones por email** en lugar de WhatsApp.
- **Auditoria de cambios**: quien modifico que turno y cuando.
- **Multi-sucursal**: un solo consultorio con dos gabinetes no es multi-sucursal.

**Explicitamente fuera de alcance, y por que** (coherente con el prompt original): historia clinica electronica, odontograma, periodonto, prescripciones, facturacion, caja, obras sociales/prepagas, IA, chatbot, portal del paciente con usuario y contrasena, app movil nativa. La razon no es que sean malas ideas: es que cada una **multiplica el alcance por un factor de 3 a 5** y el proyecto es un TP de Metodologia de Sistemas donde el valor esta en que el nucleo este **bien resuelto y demonstrable**, no en la cantidad de modulos.

---

## 7. Reglas de negocio

Las reglas del dominio que el sistema tiene que respetar. Las marcadas como **[supuesto]** son las que **no fueron confirmadas por el usuario** y hay que validarlas antes de implementar.

| # | Regla | Estado |
|---|---|---|
| R1 | Un profesional no puede tener dos turnos superpuestos en el mismo horario | **Comprobada** (declarada de forma explicita por al menos 8 de los 20 proveedores relevados) |
| R2 | No se puede reservar en una fecha/hora pasada | **Comprobada** |
| R3 | No se puede reservar en un bloque de horario bloqueado (vacaciones, feriado, no atencion) | **Comprobada** |
| R4 | La duracion del turno depende de la prestacion, no es fija | **Supuesto** — a confirmar con el cliente/docente |
| R5 | Al cancelar, el horario queda automaticamente disponible para otro paciente | **Supuesto** — a confirmar |
| R6 | La clinica atiende en una franja horaria fija por dia de la semana (ej. 9-13 y 16-20) | **Supuesto** — a confirmar |
| R7 | El paciente no puede tener dos turnos simultaneos en profesionales distintos | **[NE]** — no se encontro ningun proveedor que la declare. Es una excepcion (cirugia en equipo, sedacion), pero conviene decidirla explicitamente |
| R8 | Los feriados se contrastan contra el calendario nacional argentino | **Supuesto** — solo IA Sistemas lo declara explicitamente entre los 10 argentinos; FLAP lo resuelve con "bloqueos" manuales |

**Sobre R7**: es la unica regla del listado que **ningun** proveedor declara. No significa que ninguno la implemente — significa que no es una funcion que los proveedores consideren destacable. Para el proyecto conviene **dejarla explicita en el modelo de datos** aunque la decision de negocio sea permitirla: documentar una excepcion es mas barato que descobrirla como bug.

**Sobre la anticipacion minima de cancelacion**: el prompt original la sugirio. **No se incluye como regla** - no hay evidencia en ningun proveedor argentino relevado de una politica de cancelacion con anticipacion minima, y en un contexto de consultorio chico imponerla sin dato real es inventar una politica. Queda como pregunta abierta (punto 11).

---

## 8. Integraciones

**Para el MVP: ninguna integracion externa obligatoria.** Esta es una decision consciente, no una casualidad.

Lo justifican dos hallazgos de la investigacion:

1. **Dos de los diez proveedores argentinos de odontologia cobran la automatizacion por separado**: DentalSoft cobra los recordatorios automaticos de WhatsApp aparte (USD 0.026 por mensaje, segun su propia tabla de planes); FLAP incluye email en la base y vende **WhatsApp en packs adicionales**; Odontoly declara que las funciones de IA **no estan ofrecidas** hasta completar una evaluacion tecnica, de privacidad y de uso profesional.
2. **WhatsApp tiene un costo variable que el proyecto no quiere asumir**: ixi traslada el costo de Meta tal cual (**$45 + IVA por mensaje entregado**) y lo declara explicitamente. Un TP que dependa de un costo variable por mensaje externo tiene un costo variable en su presupuesto.

**Integraciones declaradas como diferidas** (post-MVP, en orden):

| Integracion | Valor | Costo / riesgo |
|---|---|---|
| **WhatsApp Business API** | Es la que mas ataca el ausentismo, o sea el problema central | Costo por mensaje, dependencia de Meta, requiere cuenta empresarial verificada |
| **Mercado Pago** | Senas y cobros | Comision por transaccion, API de integracion acotada |
| **Google Calendar** | Sincronizacion con la agenda que el odontologo ya usa | Baja complejidad tecnica |
| **AFIP / ARCA (facturacion electronica)** | Solo si entra facturacion | Alta complejidad normativa; ademas **Dentatools declara explicitamente que NO emite factura AFIP** y opera igual |

**Ninguna de estas es necesaria para que el nucleo del sistema funcione.** El sistema debe ser completamente utilizable con la base de datos sola.

---

## 9. Restricciones

Restricciones reales (condicionan la arquitectura), diferenciadas de preferencias disfrazadas de restriccion:

| # | Restriccion | Tipo | Impacto |
|---|---|---|---|
| R-1 | Entregable de **Metodologia de Sistemas (TUP)** | **Real** | Define el criterio de exito: que se pueda explicar y defender, no que sea el mejor producto del mercado |
| R-2 | **Priorizar claridad sobre complejidad** | **Real** (explicita en el prompt) | Un solo camino para resolver cada cosa. Sin framework, sin sobreingenieria |
| R-3 | **Enfoque didactico pero usable** | **Real** | La interfaz tiene que poder operarse, no solo demonstrarse |
| R-4 | **Web, multiusuario, base de datos** | **[Supuesto]** — a confirmar | Es la eleccion tecnica que **mas condiciona** el diseno. Ver abajo |
| R-5 | Presupuesto acotado / sin costos de infraestructura | **[Supuesto]** — a confirmar | Si es real, descarta cualquier dependencia de un servicio de pago de terceros |

**La restriccion R-4 merece una decision explicita** porque es la que mas pesa:

- **Si es web + multiusuario + BD**: se elige un stack web, la validacion anti-solapamiento va con restricciones/indices unicos en la base (R1 es una invariante del modelo, no un `if` en el formulario), y el sistema **nunca tiene el problema de "dos secretarias editando el mismo turno"**.
- **Si fuera desktop local o Python + consola**: la validacion anti-solapamiento tiene que hacerla la aplicacion, y con dos copias de la base abierta el problema de la doble reserva **sigue existiendo a nivel de datos** — o sea, el sistema no resolveria el problema que dice resolver.

Este Discovery **no decide** R-4. La decision tecnica de stack le corresponde a `kb-creator`, que la va a preguntar explicitamente. Se documenta aca porque es la unica decision tecnica que este punto de la investigacion **si** condiciono.

---

## 10. Riesgos

Aplicando assumption-mapping sobre los puntos 1-9: los **supuestos sin probar** son los riesgos.

### Riesgos altos (supuestos sin probar, con impacto directo)

1. **Supuesto sin probar: que la clinica objetivo de verdad necesita digitalizar, y no seguir con WhatsApp + papel.** No hay ninguna validacion con una clinica real. Todo el proyecto descansa sobre este supuesto y nadie lo comprobo. **Es el riesgo #1 del proyecto**, no un riesgo de implementacion.
2. **Supuesto sin probar: que "solapamiento y doble reserva" es el dolor principal.** Es lo que dice el prompt, pero ningun proveedor argentino publica metricas de campo sobre que falla realmente en el consultorio. DentalSoft afirma "-82% ausencias" **[A]** e IA Sistemas cita una revision Cochrane y un analisis de 1,6 millones de turnos **[A]** — **ninguna de las dos es verificable independientemente**, y las dos venden lo que el proyecto quiere demostrar. No hay que tomar esas cifras como dato.
3. **Supuesto sin probar: que el usuario objetivo es una clinica chico-media con recepcion y varios profesionales.** Si el cliente real es un odontologo solo, el modulo de roles y la agenda multi-profesional sobran.
4. **Supuesto sin probar: que un sistema sin historia clinica ni odontograma es aceptable.** Es la apuesta central del proyecto y la mas discutible: **Los 10 de los 10 proveedores argentinos dedicados a odontologia incluyen odontograma**. Una clinica que ya tiene ficha en papel puede, pero tambien puede no volver a un sistema que le exija volver al papel sin folio digital. Este riesgo es el que define si el proyecto es viable.

### Riesgos tecnicos (derivados de la investigacion)

5. **El componente de envio de mensajes es el mas caro de construir y el menos controlable.** Los dos proveedores que publican un costo explicito coinciden en que el costo por mensaje de WhatsApp es variable y se traslada al cliente **[C]**. Si el MVP lo incluye, el proyecto hereda un costo variable.
6. **Reserva online publica = la parte mas difícil del MVP, no la mas facil.** Exige slots calculados en tiempo real, manejo de concurrencia (dos pacientes reservando el ultimo horario a la vez) y una pagina publica. El riesgo real es **subestimar la concurrencia**: es exactamente el escenario R1 y no se resuelve con un `if`.
7. **Datos sensibles de salud sin marco normativo resuelto.** Argentina aplica Ley 25.326 (Proteccion de Datos Personales) y la Ley 26.529 / Ley de Historia Clinica Electronica. Solo 4 de los 10 proveedores argentinos declaran cumplimiento normativo de forma explicita, y las declaraciones son **[A]** salvo cuando citan un registro verificable (OdontoClinIA cita ReNaPDiS #248, MedicAI cita ReNaPDiS #292 — esos si son verificables **[C]**). Un TP que guarde DNI y fecha de nacimiento sin una nota de privacidad es un riesgo academico y etico.
8. **Sobre-alcance por contaminacion del mercado.** Se vio en la investigacion como los proveedores arman bundles de 9 a 17 modulos. El riesgo real es copiar ese modelo y no terminar ninguno bien.

### Riesgos explicitamente descartados por Decision

- **Dependencia de un solo proveedor (lock-in)**: no aplica, el proyecto no depende de ningun SaaS externo en el MVP.
- **Gestionix como riesgo de competencia**: descartado, la empresa no existe (punto 11).

---

## 11. Preguntas abiertas

Lo que quedo sin resolver. Las primeras cuatro necesitan respuesta **antes** de que `kb-creator` arme la base de conocimiento.

**Bloqueantes (necesitan respuesta antes de avanzar)**

1. **¿Que se define como alcance del MVP: agenda interna o agenda publica?** El caso de uso 5 (el paciente reserva solo) esta en la lista, pero es la parte mas costosa y la que mas riesgo de concurrencia tiene. **Sin esta respuesta, el resto del MVP se puede construir pero no se cierra.**
2. **¿Se incluye recordatorio por WhatsApp?** Es la funcionalidad con mas impacto sobre el problema real y la que introduce costo variable y dependencia externa. Decision consciente, no un default.
3. **¿Se confirma web + multiusuario + BD relacional?** Es la decision que mas condiciona el modelo de datos, en particular R1. (Ver punto 9, R-4.)
4. **¿Acepta el cliente un sistema sin historia clinica ni odontograma?** Si la respuesta es no, el proyecto es otro proyecto.

**Importantes (para validar con el docente o el cliente, no bloquean el arranque)**

5. **¿Cual es la duracion por prestacion?** R4 quedo como supuesto. Sin tabla de duraciones, la agenda no se puede calcular bien. Necesita un conjunto real de practicas y tiempos.
6. **¿La clinica atiende obras sociales/prepagas?** Solo 3 de los 10 proveedores argentinos de odontologia lo manejan de forma explicita (DentalSoft, DentalCore y OdontoClinIA); los demas lo dejan en **[NE]** o lo declaran fuera (Dentatools). Dejarlo fuera es una decision consciente y valida para un TP, pero conviene que sea explicita y no un olvido.
7. **¿Hay una clinica real disponible para probar?** Sin usuario real, la validacion del riesgo 1 y del riesgo 3 no existe. Es el unico modo de convertir el supuesto 1 en dato.
8. **Se puede eliminar la regla de anticipacion minima de cancelacion?** No hay evidencia de que un consultorio chico la aplique.
9. **¿Un paciente puede tener dos turnos simultaneos?** (R7) Ningun proveedor lo declara; conviene decidirlo.
10. **¿Multi-sucursal entra en el MVP?** Se asumio que no.
11. **¿Que paso con "Gestionix"?** El prompt lo listaba como competidor. **Investigado: no es competidor.** Era un ERP mexicano para pymes y contadores, adquirido por la fintech Konfio en diciembre de 2020 y cerrado el 30 de octubre de 2023. Se documenta aca como supuesto **desmentido** — exactamente el tipo de cosa que queda dando vueltas si no se escribe. Lo mismo con "SysTurno": **no se pudo confirmar la existencia de un producto dental argentino con ese nombre** **[NE]**.

---

# Seccion A — Tabla comparativa de sistemas

**20 sistemas, ordenados por relevancia para Argentina.** Fecha de consulta de todas las fuentes: **2026-10-04**. Leyenda: **[C]** funcionalidad comprobada · **[A]** afirmacion comercial · **[NE]** No evidenciado.

| # | Sistema | Proveedor / Origen | Segmento | Modalidad | Agenda y turnos | Automatizacion | Odontologia clinica | Administracion | Integraciones | Seguridad / trazabilidad | Modelo comercial | URL |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **DentalSoft** | dentalsoft.com.ar · AR | Clinica / consultorio | Nube [C] | Agenda diaria/semanal/mensual, drag & drop, urgencias, sobreturnos **con deteccion automatica de solapamiento**, bloqueos, multi-sucursal, Google Calendar [C] | Recordatorios automaticos WhatsApp+email, campanas de recuperacion, cobro de deudas, pedido de reseñas Google [C] | Odontograma 18 estados, notacion FDI, modulo de ortodoncia, historias clinicas, presupuestos [C] | Caja, cobros, liquidaciones de comisiones y de obras sociales, presupuestos, reportes [C] | WhatsApp (Meta), Google Calendar, Mercado Pago, +20 obras sociales [C] | Egresos y anulaciones con trazabilidad [C]; exportacion de datos **[NE]**; auditoria **[NE]**; normativa AR **[NE]** | $0/mes 6 meses (≤50 turnos, 1 odontologo) · $30.000/mes Gestion · $60.000/mes Pro · +$10.000/profesional [C]. "300+ clinicas" **[A]** | https://dentalsoft.com.ar/ |
| 2 | **DentalCore** | dentalcore.app · AR | Clinica / consultorio / cadena | Nube [C] | Agenda drag & drop multi-doctor, auto-relleno de huecos cancelados, bloqueos, sala de espera virtual [C] | Bot de WhatsApp con 9 flujos: confirma, llena huecos, recall, leads, fotos [C] | Odontograma + periodontograma + deteccion de patologia, 17 motores CDSS, recetas, consentimientos, derivaciones, ordenes de laboratorio, teleodontologia [C] | Caja diaria, presupuestos con versionado, obras sociales y prepagas (PAMI, OSDE, IOMA, Swiss Medical, Galeno, Sancor +14), facturacion ARCA, dashboard de presupuestos no cobrados [C] | WhatsApp (sesion QR), facturacion ARCA, Mercado Pago, portal web de pacientes [C] | Cumplimiento normativo AR **[NE]**; exportacion **[NE]**; auditoria **[NE]**; dependencia de sesion WhatsApp personal = riesgo de disponibilidad **[C]** | Unico plan USD 50/mes con 2 usuarios + USD 10/usuario extra; 14 dias de reembolso [C] | https://dentalcore.app/ |
| 3 | **OdontoClinIA (ClinIA)** | clinia.com.ar · AR | Consultorio / clinica PyME / cadena / servicio publico | Nube [C] | Agenda por profesional, especialidad o sillon, agenda online 24/7, **reagendamiento automatico cuando el paciente cancela** [C] | Recordatorios por WhatsApp, confirmacion, asistente IA por WhatsApp que agenda sin intervencion humana [C] | Odontograma visual con historial por pieza, radiografias, fotos, consentimientos firmados, planes de tratamiento por etapas con presupuesto por pieza [C] | Facturacion electronica AFIP, recetas electronicas, seguimiento de avance de plan [C]; caja y cobros **[NE]** | WhatsApp, API PUCO, facturacion electronica AFIP, email, Google Calendar [C] | **ReNaPDiS #248 (recetario) — verificable en registro oficial** [C]; declara cumplimiento de la Ley de Historia Clinica Electronica ARG [C]; exportacion y auditoria **[NE]** | **Precios no publicados [NE]**; demo gratuita sin compromiso [C] | https://www.clinia.com.ar/odontologia |
| 4 | **FLAP** | flap.com.ar · AR (Tu WebMaster) | Consultorio / clinica / profesion | Nube + app web instalable [C] | Agenda multi-profesional con especialidades, **box y duracion propias**, bloqueos, **autoasignacion por carga diaria y semanal**, lista de espera [C] | Email recordatorio **incluido en la base**; **WhatsApp en packs adicionales** [C] | Odontograma FDI con **versiones** (anular sin borrar), historia clinica con versionado, ortodoncia, fotos [C] | Senas, finanzas y liquidaciones, inventario, presupuestos; facturacion fiscal AR **[NE]** | Google Calendar y Meet, **Mercado Pago**, check-in por QR o totem, DNI [C] | Roles y permisos con alcances y privacidad por integrante [C]; versionado de ficha clinica [C]; exportacion y auditoria **[NE]** | Plan Gratis **[C]**; resto **"Consultar" — precios no publicados [NE]**; demo en vivo con datos ficticios [C] | https://flap.com.ar/odontologos |
| 5 | **ixi** | ixi.ar · AR (ixi SAS, CABA) | Consultorio / clinica | Nube [C] | Agenda por profesional, turnos online, multiples sedes y profesionales en una cuenta [C] | Recordatorios por WhatsApp (opt-in por costo), agente de IA y asistente de voz [C] | Historia clinica con modulos por especialidad, **SNOMED CT y CIE-10** [C]; **odontograma [NE]** | **Reporte "A liquidar"**: aranceles por cobertura y profesional, codigo de practica, valor, copago [C] | Mercado Pago, WhatsApp, **verificacion de matricula SISA**, CUIR [C] | **Encuentros firmados e inmutables** [C]; CUIR con verificador publico [C]; **exportacion de datos al baja [C]**; app iOS/Android **[NE]** ("proximamente") | Plan fundador bonificado 100% primeros 500 consultorios [C]; **precio de lista publicado $11.000 + IVA/profesional/mes** [C]; WhatsApp $45 + IVA por mensaje entregado (traslado de costo de Meta) [C] | https://ixi.ar/ |
| 6 | **Dentiqa** | dentiqa.app · AR / Latam | Clinica pequena / mediana / grande | Nube [C] | Agenda multi-dentista con bloqueos por profesional, vistas dia/semana, drag & drop, validaciones de horario, "sin riesgo de doble-reserva" [C] | **Chatbot IA por WhatsApp 24/7** con 3 capas (reglas → Haiku → Sonnet), agenda citas, recordatorios 24h antes, campanas de marketing [C] | Odontograma + **periodontograma BOP/NIC**, historia clinica, firma electronica en evoluciones y recetas [C]; imagenes y presupuestos **[NE]** | Estadisticas basicas y avanzadas, facturacion por profesional, multi-clinica [C]; caja **[NE]**; obras sociales **[NE]** | **WhatsApp Business**, Mercado Pago [C]; Google Calendar, AFIP/ARCA, obras sociales **[NE]** | Cumplimiento normativo **[NE]**; exportacion **[NE]**; auditoria **[NE]** | USD 89 / 149 / 249 por mes, pagables en ARS via Mercado Pago, sin permanencia [C] | https://dentiqa.app/ar |
| 7 | **DenPro** | denpro.ar · marca de Elite Digital Services, LLC (**soporte +34 y +421**) | Consultorio / multisede / cadena / escuela | Nube [C] | Calendario de turnos, multi-sucursal, lista de espera (plan Team) [C]; duracion variable, bloqueos y sobreturnos **[NE]** | **Recordatorios por SMS unicamente — sin WhatsApp** [C] | Odontograma FDI, historias clinicas, recetas [C]; periodontograma, ortodoncia, imagen **[NE]** | Facturacion, inventario, exportaciones (plan Team) [C]; caja, obras sociales, ARCA **[NE]** | Integraciones genericas (plan Team) **[C]**; WhatsApp, Google Calendar, Mercado Pago, obras sociales **[NE]** | **AES-256, centros de datos ISO 27001 en la UE, permisos controlados, cumplimiento GDPR** [C]; norma argentina **[NE]** | Basic $19.900/mes (1 usuario) · Team $29.900/mes (usuarios ilimitados) · -15% anual · 30 dias gratis sin tarjeta [C]. "50+ consultorios" **[A]** | https://www.denpro.ar/ |
| 8 | **IA Sistemas** | iasistemas.com · AR | Clinica odontologica 1-10 profesionales | Nube [C] | Turnos online 24/7 multi-profesional, agenda diaria por doctor, directorio profesional [C] | **Doble recordatorio inteligente** (ultimo dia habil + mismo dia), **detecta feriados argentinos y reagenda el aviso** [C] | Odontograma FDI de 32 piezas × 5 caras, historia clinica, cuentas corrientes, planes de pago [C]; imagen **[NE]** | Reportes, dashboard de facturacion mensual y saldo, control de stock con alertas [C] | WhatsApp + email, Google Calendar [C]; Mercado Pago, obras sociales, ARCA **[NE]** | "Plataforma auditada y aprobada por el Ministerio de Salud", Legajo N° RL-2026-41992503-APN-SSVEIYES#MS — **afirmacion no verificable sin acceso al registro** **[A]** | USD 39 (1 prof) / 99 (hasta 5) / 149 (hasta 10) + USD 15/prof. adicional; sin contrato, sin instalacion; anual bonifica 2 meses [C] | https://iasistemas.com/sistema-para-clinicas-odontologicas |
| 9 | **Dentatools** | dentatools.co/ar · AR | Odontologo independiente / consultorio | Nube [C] | Agenda compartida, **auto-agendado por enlace**, el turno se bloquea al instante [C]; duracion variable y sobreturnos **[NE]** | Recordatorios por WhatsApp con confirmacion que **actualiza la agenda sola** [C]; campanas y recall **[NE]** | Historia clinica digital, odontograma interactivo, presupuestos en PDF [C]; periodonto, ortodoncia, imagen **[NE]** | Presupuestos en PDF, control de cuentas por cobrar [C]; caja **[NE]** | WhatsApp [C]; Mercado Pago, Google Calendar, obras sociales **[NE]**; **declara que NO gestiona obras sociales ni prepagas** [C] | Norma AR **[NE]**; **declara que NO emite factura electronica AFIP** [C]; exportacion y auditoria **[NE]** | $15.000/mes (1 profesional) · $30.000/mes (hasta 3) · +$8.000/profesional adicional · sin tarjeta de credito [C] | https://dentatools.co/ar/ |
| 10 | **Odontoly** | odontoly.com · AR | Consultorio chico | **Instalacion local / local-first** [C] | Agenda con turnos, tareas y reservas online en enlace propio [C]; bloqueos, sobreturnos, multi-sillon **[NE]** | **La reserva online entra al circuito y la confirma el equipo — no hay automatizacion declarada** [C] | Ficha, evoluciones, odontograma, **fotos y radiografias**, presupuestos con impresion, ordenes de laboratorio **[C]** | Caja en ARS y USD, cotizacion manual con registro historico, gastos, deudas, resumen del dia [C] | **Integraciones externas [NE]** | **Local-first: la informacion clinica permanece en la computadora del consultorio** [C]; instalador firmado y notarizado, 4 dispositivos autorizados [C]; **app movil nativa [NE]** ("todavia no disponible"); dependencia de la PC encendida = riesgo operativo [C] | USD 149,99/mes, sin permanencia; 2 usuarios con permisos, hasta 4 dispositivos [C] | https://odontoly.com/ |
| 11 | **MedicAI** | medicai.com.ar · AR (MEDICAI S.A.S) | Consultorio 1-15 prof / clinica | Nube [C] | Turnera publica online 24/7, sincronizacion con Google Calendar [C] | Recordatorios por email [C]; **WhatsApp [NE]** | Historia clinica electronica + IA clinica SENTINEL que lee hasta 50 documentos/prof/mes [C]; **odontograma [NE]** | Facturacion **ARCA** integrada, cobros con Mercado Pago, estadisticas [C] | Mercado Pago, ARCA, Google Calendar [C] | **ReNaPDiS #292 (recetario) — verificable** [C]; sello SHA-256, **2FA obligatorio**, QR verificable, **historial inmutable por 15 anos** [C]; exportacion **[NE]** | $25.900 + IVA/profesional/mes (-5%/-10%/-15% por volumen) · 30 dias gratis sin tarjeta · Enterprise a medida [C] | https://www.medicai.com.ar/precios |
| 12 | **Gestion Salud** | gestionsalud.com.ar · AR | Centro de salud / profesional | Nube (AWS) [C] | Agenda por profesional y puesto, turnos online 24/7, ocupacion de consultorios [C] | Recordatorios por email [C]; **WhatsApp [NE]** | **"Registro odontologico completo integrado a la HCE"** [C]; odontograma y periodonto **[NE]** | Caja por profesional, cuenta corriente con recibos, presupuestos, socios/membresias, estadisticas, gestion de camas, farmacia y stock [C] | **API REST (addon)** [C], lector de DNI por codigo de barras, pantalla TV de sala de espera [C]; Mercado Pago, Google Calendar **[NE]** | Backups automaticos cada 3 horas, hash de contrasenas, **Ley 25.326 y Ley 26.529** [C]; exportacion via API [C]; auditoria **[NE]** | Planes escalonados de $26.000 (5 usuarios) a $427.500 (155 usuarios); costo por usuario decreciente; pago via Mercado Pago; prueba gratuita [C] | https://www.gestionsalud.com.ar/ |
| 13 | **Sigo** | sigo.com.ar · AR | Consultorio / clinica | **[NE]** | Horarios personalizados por profesional con **duracion propia por turno**, rangos y dias [C]; multi-profesional **[NE]** | **Recordatorios por e-mail** [C]; WhatsApp **[NE]** | Odontogramas e historias clinicas [C]; periodonto, ortodoncia, imagen **[NE]** | **Facturacion electronica**, presupuestos, cuentas corrientes, tratamientos [C] | **[NE]** — ninguna integracion declarada | **[NE]** — sin declaracion de seguridad o normativa | $25.000/mes (1 profesional) · $250.000/ano · 30 dias gratis [C] | https://sigo.com.ar/ |
| 14 | **WorldSoft Systems (Medical)** | worldsoftsystems.com.ar · AR | Profesional / clinica / PAMI | Nube [C] | Agenda inteligente multi-profesional [C]; bloqueos, sobreturnos, duracion variable **[NE]** | Recordatorios por WhatsApp [C] | **[NE]** — sin funcionalidad odontologica declarada | Facturacion, liquidaciones, auditoria y reportes de liquidacion, metricas avanzadas [C] | **Validador online de afiliados PAMI**, WhatsApp, portal de pacientes, videollamadas [C] | **AES-256, backups diarios automaticos, roles de secretaria y administrador** [C]; **exportacion en archivo estandarizado antes de la baja** [C]; norma AR declarada en terminos generales **[A]** | Desde $40.000/mes con pago unico anual; precio congelado 3 meses para clientes nuevos [C] | https://worldsoftsystems.com.ar/software-gestion-medica/ |
| 15 | **Salvia** | salviagestion.ar · AR / Latam | Consultorio / clinica / centro medico / hospital | Nube [C] | Coordinacion de agendas, disponibilidad, **confirmaciones y reasignacion**, estados, admite [C] | Notificaciones [C]; WhatsApp **[NE]** | Historia clinica digital generalista [C]; **odontograma [NE]** | Caja, indicadores de gestion, **modulo de auditoria con registro de acciones** [C] | **[NE]** — ninguna integracion declarada | **Acceso por usuario con permisos por rol, cada accion relevante queda registrada en auditoria, HTTPS** [C]; exportacion **[NE]**; norma AR **[NE]** | **Precios no publicados [NE]** | https://salviagestion.ar/ |
| 16 | **MEDTECH GDC** | medtech.com.ar · AR | Ambulatorio / policonsultorio / centro medico / clinica con internacion | Nube [C] | Multiples agendas, reserva web para el paciente [C]; mas de 15 anos de evolucion **[A]** | **Recordatorios [NE]** | **[NE]** — nomencladores generales (IOMA, PAMI, IProSS, Nacional, NBU), no odontologicos | Internacion, farmacia y stock, valorizacion automatica, liquidacion a financiadores, unidades de honorarios [C] | Obras sociales pre-cargadas, nomencladores y planes de cobertura precargados [C] | **[NE]** — sin declaracion de seguridad o normativa | Ambulatorio $88.000/mes + IVA (1 profesional + 2 secretarias) · Policonsultorios desde $105.100/mes + IVA · >10 prof "a consultar" · 20 dias gratis [C] | https://medtech.com.ar/sistema-gdc/ |
| 17 | **AgendaPro** | agendapro.com · Colombia (**disponible en AR, CL, MX**) | Consultorio / centro medico / IPS | Nube + app movil [C] | Calendario inteligente, bloqueo de horarios/dias/profesionales, ocupacion en tiempo real, app para medicos, marketplace con geolocalizacion [C] | **Recordatorios por email, SMS o WhatsApp con confirmar/cancelar** que se reflejan al instante [C] | Historia clinica customizable con anexos, consentimiento, firma digital [C]; **odontograma — la propia tabla comparativa del proveedor lo marca como "No" frente a la competencia [C] (contradiccion interna)** | Caja, POS, inventarios, pagos online, control de ocupacion, reportes, calculo de comisiones [C] | WhatsApp, SMS, email, pagos online; **API solo en plan Pro** [C] | AWS, TLS forzado, sin permisos de conexion publica, niveles de acceso y permisos [C]; exportacion, auditoria y normativa AR **[NE]** | Desde US$19 **[C]** (pagina .cl muestra CLP: 15.900 / 34.900 / 54.900 / 249.900) | https://agendapro.com/co/dental/software-odontologico |
| 18 | **Doctoralia Pro** | pro.doctoralia.es · Espana (Docplanner Group, Varsovia) | Clinica / centro medico / hospital | Nube [C] | **Agenda Online 360**, agendamiento en grupo, control de cumplimiento de horarios del personal, **lista de espera inteligente que rellena cancelaciones**, programacion de citas en grupo [C] | Recordatorios por email, **WhatsApp** y SMS, recomposicion automatica de cancelaciones, campanas, **buzon de voz y SMS** [C] | HCE con **odontograma y periodontograma**, recetas electronicas, videoconsultas, notas clinicas con IA (Noa Notes) [C] | Facturacion electronica **Verifactu** (normativa espanola, no argentina), inventario, bonos digitales, panel financiero [C] | WhatsApp, SMS, email, pagos online; **integracion local argentina [NE]** | **RGPD y Ley 41/2002**, cifrado, copias de seguridad, control de accesos, servidores en la UE, **ISO/IEC 27001** [C]; exportacion **[NE]** | Especialistas: 89 / 109 / 129 EUR/mes + IVA · Clinicas: precio personalizado **[A]** | https://pro.doctoralia.es/precios/para-clinicas |
| 19 | **Curve Dental** | curvedental.com - EE.UU. (Orem, UT; adquirido por Constellation Software en 2022) | Consultorio pequeno a grupo mediano | **Cloud-nativa** [C] | Scheduler en navegador; **scheduler de solo lectura sin conexion** [C] | **Curve GRO incluido**: recordatorios, Message Builder, Campaign/Workflow Builder, Smart Action List [C] | Charting, period charting, Curve Imaging nativo a nube, Pearl AI, educacion al paciente [C] | **eClaims ilimitados incluidos**, sin clearinghouse de terceros; Business Analytics y Huddle Dashboards [C] | Bridges para DEXIS, Schick, Planmeca, Carestream, Gendex y 15+ marcas [C]; **integracion local argentina [NE]** | Continuous backup, intrusion detection, disaster recovery, balanceo dinamico; **uptime 99,99% [A]** | USD 299-500/mes todo incluido (segunda fuente: SuperHero USD 350-500); **sin prueba gratuita**; permanencia de 12 meses con preaviso de 90 dias [C] | https://www.curvedental.com/pricing |
| 20 | **Dentrix** | Henry Schein One · EE.UU. | Consultorio, DSO, grupo, multisede | **Servidor local + nube (Ascend)** [C] | Profundidad funcional de 30+ anos, multi-ubicacion, Jarvis Analytics [C] | **Detect AI con aprobacion FDA** (caries), dictado por voz [C]; **patient engagement como addon en local** [C] | **El mas completo**: chart, odontograma, periodonto, **integracion con 150+ dispositivos de imagen**, planificacion de tratamiento [C] | **1.300+ payors**, Eligibility Pro que consulta 40+ portales, analytics [C] | **Ecosistema de 50+ partners**, hardware Henry Schein (DEXIS, Schick) [C]; **integracion local argentina [NE]** | **Sin informacion publica verificable [NE]**; requiere servidor propio = carga de IT [C] | **Sin precio publicado [NE]** — licencia ~USD 400–700/mes mas soporte anual, servidor y addons (segunda fuente) **[A]**; 35.000+ consultorios **[A]** | https://www.capterra.es/software/2329/dentrix |

### A.1 Notas de la tabla

**Sobre precios**: todos los montos en pesos argentinos son **declarados por el proveedor el 2026-10-04** y ninguno incluye IVA salvo que se indique. Los precios internacionales aparecen en su moneda original. **No se normalizo a una moneda comun** a proposito: hacerlo sugeriria una comparabilidad que no existe entre un plan de 89 EUR con IVA y un plan de 25.000 ARS sin IVA.

**Contradicciones internas detectadas en los propios proveedores** (importante para no citarlas como dato):

- **DentalSoft** anuncia en su home "Recordatorios automaticos WhatsApp y e-mail" y "**sin costo de integracion extra**" y "-82% ausencias", pero su **propia tabla de planes** dice: el plan Gestion ($30.000) incluye **recordatorios manuales** por WhatsApp (se abre WhatsApp con el mensaje redactado y lo envia una persona) y el **recordatorio automatico** solo esta en el plan Pro ($60.000), con **Meta cobrando USD 0.026 por recordatorio**. Ademas la misma pagina usa "-82% ausencias" en un bloque y "reduccion promedio del 40%" en otro. **[C]** = la automaticidad es del plan Pro y tiene costo variable. **[A]** = el 82%/40% de reduccion.
- **AgendaPro** lista en su propia tabla comparativa que **no** tiene odontograma personalizable, mientras su pagina de odontologia vende el producto como software dental con historia clinica completa. **[C]** = hay contradiccion en la fuente.
- **DenPro** declara cifrado **AES-256, ISO 27001 y GDPR** — correcto y verificable en su FAQ — pero es una marca de una empresa de la UE (soporte +34 y +421) que vende en pesos argentinos sin declarar la normativa argentina aplicable.
- **Odontoly** se presenta como local-first pero **declara explicitamente** que "las funciones de IA necesitan completar su evaluacion tecnica, de privacidad y de uso profesional antes de ofrecerse". Honestidad a favor, y confirma el punto 10 (riesgo 7): el cumplimiento normativo no es un default del mercado.

**Lo que ningun proveedor argentino resuelve con evidencia publica**: exportacion de datos del paciente. Solo WorldSoft la declara **[C]** ("descargar toda tu informacion en un archivo estandarizado antes de irte") e ixi la declara **[C]** (exportacion al darse de baja). En los otros 8 la exportacion es **[NE]**. Para un sistema que guarda DNI y fecha de nacimiento, esto es una diferencia real y no un detalle.

---

# Seccion B — Matriz de puntuacion

## B.1 Criterio y pesos

Escala de **0 a 5** por criterio. **5** = comprovadamente completo en fuentes oficiales; **4** = solido con condiciones; **3** = parcial; **2** = minimo; **1** = tangencial; **0** = ausente; **[NE]** = no evidenciado, se puntua **1** (credito por existir la categoria, no por la funcionalidad). Los pesos son los indicados en la consigna de investigacion.

| Criterio | Peso | Que se puntua |
|---|---|---|
| **1. Gestion de turnos y automatizacion** | **25%** | Agenda multi-profesional, duracion variable, bloqueos, sobreturnos, deteccion de solapamiento, reserva online, recordatorios, cancelacion/reagendamiento |
| **2. Funcionalidad odontologica clinica** | **20%** | Ficha, odontograma, periodonto, ortodoncia, imagen/radiografia, planes de tratamiento |
| **3. Integraciones locales y WhatsApp** | **15%** | WhatsApp Business API, Google Calendar, Mercado Pago, AFIP/ARCA, obras sociales |
| **4. Administracion, cobros y facturacion** | **15%** | Caja, presupuestos, liquidaciones, facturacion electronica, obras sociales, reportes |
| **5. Experiencia del paciente** | **10%** | Reserva online 24/7, portal, recordatorios, pagos, accesibilidad desde el celular |
| **6. Seguridad, exportacion y trazabilidad** | **10%** | Cifrado, roles, auditoria, exportacion, backups, normativa declarada |
| **7. Precio y facilidad de adopcion** | **5%** | Precio publicado, prueba gratuita, sin permanencia, migracion, onboarding |

## B.2 Matriz

`Puntaje` = suma ponderada sobre 5. `Indice` = Puntaje × 20 (sobre 100).

| # | Sistema | C1 25% | C2 20% | C3 15% | C4 15% | C5 10% | C6 10% | C7 5% | Puntaje | Indice |
|---|---|---|---|---|---|---|---|---|---|---|
| 2 | **DentalCore** | 5 | 5 | 5 | 5 | 5 | 2 | 5 | **4,70** | **94** |
| 1 | **DentalSoft** | 5 | 5 | 5 | 5 | 5 | 2 | 4 | **4,65** | **93** |
| 3 | **OdontoClinIA** | 5 | 5 | 5 | 4 | 4 | 4 | 2 | **4,50** | **90** |
| 4 | **FLAP** | 5 | 5 | 4 | 3 | 5 | 4 | 3 | **4,35** | **87** |
| 18 | **Doctoralia Pro** | 5 | 5 | 2 | 3 | 5 | 5 | 3 | **4,15** | **83** |
| 5 | **ixi** | 4 | 3 | 4 | 5 | 4 | 5 | 5 | **4,10** | **82** |
| 6 | **Dentiqa** | 5 | 4 | 4 | 3 | 4 | 1 | 4 | **4,00** | **80** |
| 8 | **IA Sistemas** | 5 | 4 | 3 | 3 | 4 | 2 | 5 | **3,80** | **76** |
| 17 | **AgendaPro** | 5 | 3 | 2 | 4 | 5 | 3 | 5 | **3,80** | **76** |
| 10 | **Odontoly** | 4 | 5 | 1 | 4 | 3 | 4 | 3 | **3,60** | **72** |
| 11 | **MedicAI** | 4 | 2 | 4 | 4 | 3 | 5 | 4 | **3,60** | **72** |
| 9 | **Dentatools** | 4 | 4 | 3 | 3 | 4 | 1 | 4 | **3,40** | **68** |
| 12 | **Gestion Salud** | 4 | 2 | 3 | 4 | 3 | 4 | 4 | **3,35** | **67** |
| 19 | **Curve Dental** | 4 | 4 | 2 | 2 | 4 | 4 | 2 | **3,30** | **66** |
| 7 | **DenPro** | 4 | 4 | 2 | 2 | 3 | 5 | 5 | **3,20** | **64** |
| 14 | **WorldSoft (Medical)** | 4 | 0 | 4 | 4 | 4 | 4 | 3 | **3,15** | **63** |
| 15 | **Salvia** | 4 | 2 | 1 | 4 | 2 | 4 | 2 | **3,05** | **61** |
| 13 | **Sigo** | 4 | 4 | 1 | 4 | 1 | 1 | 4 | **2,95** | **59** |
| 16 | **MEDTECH GDC** | 4 | 1 | 3 | 5 | 2 | 1 | 2 | **2,80** | **56** |
| — | **Gestionix** | — | — | — | — | — | — | — | **descartado** | **—** |

## B.3 Como leer la matriz (y donde NO usarla)

**La matriz no es un ranking de Mercado.** Los tres primeros (DentalCore, DentalSoft, OdontoClinIA) su indice es alto porque hacen **todo lo del criterio 2** (odontograma) y **todo lo del criterio 4** (obra social y liquidaciones). Eso es exactamente lo que el proyecto **no va a hacer**.

**El criterio 2 (20%) esta penalizando a los competidores por tener mas funcionalidad de la que el proyecto necesita.** Un sistema sin odontograma no esta "peor" para nuestro proposito — esta **mejor orientado**. Si se recalculara la matriz **solo con los criterios que el MVP realmente necesita** (C1, C3, C5, C6, C7), el ordenamiento cambia de forma sustancial.

**Donde la matriz si es util**: para elegir a quien **mirar de cerca** en la Seccion D, y para identificar donde el mercado es debil (que es donde un proyecto de TP tiene mas chances). Los tres criterios donde **todos los proveedores estan flojos o en [NE]** son:

- **C6 (Seguridad, exportacion y trazabilidad)**: **ninguno de los 10 proveedores argentinos dedicados a odontologia declara exportacion de datos del paciente**. Fuera de ese grupo solo la declaran WorldSoft e ixi (y Gestion Salud expone una API REST que lo permite tecnicamente). **Este es el hueco mas grande del mercado.**
- **C7 (Precio y facilidad de adopcion)**: aca el mercado esta **mejor que en el resto**. **8 de los 10 argentinos dedicados a odontologia publican precio de lista**; los dos que no lo hacen son OdontoClinIA y FLAP ("Consultar"). El problema real es de otro tipo: DentalSoft y FLAP **cobran la funcion principal (recordatorio automatico) en el plan de mayor precio**, asi que el precio publicado no es el precio de la funcionalidad que se vende. Fuera de Argentina el problema si es total: Dentrix y Salvia no publican nada.
- **C3 (WhatsApp + integraciones locales)**: **7 de los 10 argentinos** tienen WhatsApp integrado de verdad (los otros tres son DenPro, que solo manda SMS; Odontoly y Sigo, que no lo declaran). De esos siete, **dos lo cobran aparte** (DentalSoft en el plan Pro, FLAP en packs adicionales).

**Conclusione de la matriz**: el mercado argentino esta **sobredimensionado en cubo clinico y subdimensionado en transparencia y en datos**. Ese es el espacio vacio donde el proyecto puede posicionarse sin intentar competir en lo que ya esta cubierto diez veces.

---

# Seccion C — Analisis competitivo

## C.1 Estructura del mercado

El mercado argentino de software de gestion odontologica se divide en **tres capas** que compiten por recursos distintos:

**Capa 1 — Suites odontologicas nativas (10 proveedores).** DentalSoft, DenPro, DentalCore, OdontoClinIA, Dentiqa, Dentatools, Odontoly, FLAP, Sigo, IA Sistemas. Compiten por ser "el sistema de la clinica" con 9 a 17 modulos. Precios del rango **$15.000 a $60.000 ARS/mes** para el plan de entrada, con usuario adicional entre $8.000 y $10.000.

**Capa 2 — Suites medicas generalistas con cobertura dental (6 proveedores).** ixi, MedicAI, Gestion Salud, Salvia, MEDTECH GDC, WorldSoft. Compiten por **obra social, prepagas, financiadores e internacion**, que es donde esta el dinero real del sistema de salud argentino. El odontologo aparece como un caso de uso mas.

**Capa 3 — Plataformas de reserva multi-vertical (2 proveedores).** AgendaPro (Latam) y Doctoralia Pro (internacional). Compiten por **atraer pacientes**, no por administrar la clinica. El calendario es el producto; la clinica es el cliente.

**Donde esta el proyecto**: entre Capa 1 y Capa 2, en el hueco de **agenda de turnos sin dependencia externa**. No existe ningun proveedor argentino que venda "solo la agenda, sin historia clinica, sin facturacion, sin costo variable por mensaje".

## C.2 Lo que la investigacion cambio del plan original

Cinco correcciones concretas, cada una con su fuente:

1. **Se descarto Gestionix** como competidor (punto 4 y punto 11). Un ERP mexicano cerrado en 2023. **El prompt original lo listaba con un signo de pregunta, y la pregunta resulto infundada.** Es exactamente el tipo de supuesto que, si no se investiga, se arrastra hasta la presentacion.

2. **"Turnos Online" y "SysTurno" no se pudieron confirmar** como productos dentales argentinos identificables (**[NE]**). Si existen, no tienen presencia publica verificable. Si el docente los menciono de oidas, conviene confirmarlo antes de citarlos.

3. **El mercado no tiene un competidor directo del MVP, pero si tiene 20 competidores funcionales.** El analisis inicial era "voy a hacer algo que nadie hace". El correcto es "voy a hacer el 30% del alcance que los demas hacen, y esa es la decision de diseno".

4. **WhatsApp es un costo, no un feature.** Los dos proveedores que publican el costo coinciden en que se traslada al cliente (ixi: $45 + IVA por mensaje; DentalSoft Pro: USD 0.026 por recordatorio). **Esto cambio la evaluacion del punto 8 (Integraciones)** de "integracion obligatoria" a "integracion diferida con costo".

5. **El odontograma no es un lujo, es la expectativa del mercado (los 10 de 10 lo tienen).** Pero **tampoco es necesario para gestionar turnos**. El proyecto tiene que asumir que esta en deficit funcional contra el mercado y **convertirlo en argumento**: menos modulos que mantener = menos lugares donde fallar.

## C.3 Cinco patrones de la competencia

| Patron | Quien lo usa | Lectura |
|---|---|---|
| **"Todo en uno"** — un plan, todo incluido, cero costo sorpresa | Curve Dental, ixi, Odontoly | El segmento que mas crece. La transparencia es el argumento y funciona |
| **"Suite completa + landing incluida"** | DentalSoft, Dentatools | Ganan por captacion de pacientes, no por gestion. La agenda es el anzuelo |
| **"Precio por profesional"** | MedicAI, ixi, Dentatools, DentalSoft | Alinea el costo con el ingreso. Es el modelo correcto para un consultorio chico |
| **"Local-first / privacidad"** | Odontoly | Contraargumento de nicho frente a la nube. Valido para datos de salud, y un diferenciador didactico fuerte |
| **"IA + WhatsApp como producto"** | DentalCore, Dentiqa, OdontoClinIA | Es donde va el mercado. Todos con afirmaciones de resultado, ninguna verificable **[A]** |

## C.4 Debilidades comunes (es el espacio disponible)

Cuatro debilidades se repiten en **todos** los proveedores argentinos, y una es tecnica:

1. **Cero exportacion de datos del paciente declarada**: ninguno de los **10 de 10** proveedores argentinos dedicados a odontologia la publica. El paciente queda atrapado en el proveedor.
2. **Precios opacos o ausentes** (OdontoClinIA "consultar", FLAP "consultar", Salvia sin precios, IA Sistemas con "promocion de agosto").
3. **WhatsApp cobrando sobre la funcion principal**: si la automatizacion de recordatorios - que es el argumento de venta - tiene costo variable, el cliente lo descubre al mes 2.
4. **Declaraciones de cumplimiento no verificables** (IA Sistemas con un legajo, DentalCore sin ninguna). Solo 2 sistemas citan un registro oficial verificable (ReNaPDiS #248 y #292).
5. **La concurrencia no se muestra.** Ningun proveedor publica como maneja el caso de dos pacientes reservando el ultimo horario a la vez. Es el problema tecnico mas dificil de la reserva online y **nadie lo muestra**. Es la oportunidad tecnica del proyecto.

---

# Seccion D — Recomendacion final

## D.1 Los 5 sistemas para demostracion

Para **desarmar en clase**. Todos son argentinos, todos tienen demo o trial accesible el 2026-10-04, y cada uno aporta una leccion distinta.

| Sistema | URL | Por que verlo | Que mirar primero | Cuidado |
|---|---|---|---|---|
| **1. DentalSoft** | https://dentalsoft.com.ar/ | El mas completo en lo clinico y en lo administrativo, y con **demo en vivo** sin tarjeta | El flujo de reserva en 4 pasos y la agenda con deteccion de solapamiento | Su propia tabla de planes **contradice** su home en los recordatorios. **Es el mejor ejemplo para enseñar a distinguir afirmacion comercial de funcionalidad comprobada** |
| **2. DentalCore** | https://dentalcore.app/ | El indice mas alto (94) y el unico con **CDSS clinico** | El bot de WhatsApp de 9 flujos y el dashboard de presupuestos no cobrados | Reclama ser el unico SIS/CDSS de Latam **[A]**. Y funciona sobre una **sesion de WhatsApp personal** — un riesgo de dependencia que vale la pena discutir |
| **3. OdontoClinIA** | https://www.clinia.com.ar/odontologia | El unico con **verificacion oficial** (ReNaPDiS #248) y el unico que declara el alcance de esa verificacion | El **reagendamiento automatico** al cancelar y el plan de tratamiento por etapas con presupuesto por pieza | Sin precios publicados. Hay que pedir demo |
| **4. FLAP** | https://flap.com.ar/odontologos | El mejor **modelo de datos** de agenda: box, duracion y versionado de ficha clinica | El **versionado de ficha clinica** (anular sin borrar) y la **autoasignacion por carga** | El WhatsApp esta en packs aparte: muestra como se esconde un costo |
| **5. ixi** | https://ixi.ar/ | El **modelo de negocio mas honesto**: precio de lista publicado, exportacion de datos, plan fundador explicito | El reporte "A liquidar" y el **encuentro firmado e inmutable** | Odontograma ausente. Y el precio de $0 actual no es el precio real: hay que explicar el de lista |

## D.2 Las 3 referencias de UX

Para copiar patrones de interaccion, no arquitectura.

| Referencia | URL | Patron a copiar | Por que |
|---|---|---|---|
| **1. AgendaPro** | https://agendapro.com/co/dental/software-odontologico | **Reserva en 4 pasos + ocupacion visible en tiempo real + marketplace** | El patron multi-vertical (una misma agenda para peluqueria, veterinaria, odontologia) es el mas simple de replicar y el que mejor escala el mismo software a otros rubros. Ademas muestra la contradiccion de su odontograma |
| **2. Doctoralia Pro** | https://pro.doctoralia.es/precios/para-clinicas | **Lista de espera inteligente** + **agendamiento en grupo** + **agenda 360** | El triangulo de "llenar huecos sin llamar a nadie" es la funcion que **si** ataca el ingreso perdido, y casi ningun proveedor argentino resuelve bien |
| **3. Curve Dental** | https://www.curvedental.com/pricing | **Todo en un plan vs add-ons** + formularios digitales y pagos online integrados | La leccion **negativa**: DentalCore y Dentiqa hacen exactamente lo contrario (todo en plan Pro de 60k/149 USD con add-ons). Comparar los dos enfoques es el mejor ejercicio de costo total de propiedad que se puede dar en un TP |

## D.3 MVP sugerido

**La propuesta: el nucleo de 8 items del prompt original, mas 4 items de cierre, sin integraciones externas.**

**Incluido (12 items):**

| Bloque | Items |
|---|---|
| **Datos** | Ficha de paciente (nombre, apellido, DNI, telefono, mail, fecha de nacimiento) · Catalogo de profesionales con horarios y duracion por prestacion |
| **Agenda** | Agenda por dia y por profesional · Listado de turnos del dia · Bloqueos y feriados · **Validacion anti-solapamiento en la capa de datos** |
| **Operacion** | Reserva de turno (fecha, hora, profesional, paciente, tratamiento) · Cancelacion y reprogramacion con liberacion automatica del horario · Busqueda basica de pacientes |
| **Cierre** | **Roles y permisos** (3 roles) · **Exportacion de la agenda y de pacientes a CSV** · **Nota de privacidad** (Ley 25.326) |

**Los 4 items de cierre, y por que estan dentro y no en el backlog:**

1. **Validacion anti-solapamiento en la capa de datos, no en el formulario.** R1 es la invariante que define el producto. Si se valida solo en la UI, con dos usuarios se rompe con dos pestanas abiertas. Es el item que diferencia un sistema que **realmente** evita la doble reserva de uno que solo avisa.
2. **Bloqueos y feriados.** Sin esto la agenda ofrece horarios que en realidad no existen, que es peor que no tener agenda: es el riesgo mas caro del sistema (punto 5).\n3. **Exportacion a CSV.** Es la **unica** funcionalidad donde la matriz B mostro un hueco de mercado total (seccion B.3) y tiene **costo de implementacion despreciable**. Es el diferencial honesto mas barato que puede tener el proyecto.
4. **Roles y permisos de 3 roles.** Es lo que separa "una agenda compartida" de "un sistema de clinica".

**Explicitamente fuera (con la razon):**

| Fuera | Razon |
|---|---|
| Historia clinica y odontograma | 10 de 10 competidores lo tienen: no es diferenciador. Multiplica el alcance x5. Es el limite de la apuesta (riesgo 4) |
| **Recordatorio por WhatsApp** | Es la funcion de mayor impacto, pero **introduce costo variable por mensaje** (ixi: $45 + IVA; DentalSoft Pro: USD 0.026) y dependencia de un tercero. **Va al backlog con el costo ya medido** |
| **Reserva online publica** | Es el caso de uso 5. Es la parte **mas cara y de mayor riesgo de concurrencia**. Si entra, entra **completa** (slots en tiempo real + manejo de dos reservas simultaneas del ultimo horario). Si no entra, el sistema sigue siendo util y el entregable es defendible. **Ver punto 11, pregunta 1 — esta decision es bloqueante** |
| Facturacion electronica / AFIP / ARCA | Alta complejidad normativa. **Dentatools demuestra que se puede operar sin ella** |
| Obras sociales y prepagas | Fuera del alcance del TP. **Decirlo explicitamente** es correcto; olvidarlo es un error |
| Caja, presupuestos, recetas, telemedicina, IA, chatbot, app movil | Cada uno multiplica el alcance por 3 a 5 |

**Criterio de exito, en una frase**: *que un odontologo y su secretaria puedan operar la agenda de un mes real completa, en multiusuario, sin solapamientos y sin depender de ningun servicio externo de pago.*

---

## Anexo — Trazabilidad de la investigacion

**Fecha de consulta de todas las fuentes**: 2026-10-04. Todas las fuentes consultadas son **sitios oficiales de cada proveedor** (landing, precios o FAQ). **No se uso ninguna fuente de opinion como base factual**: las referencias secundarias (Capterra, practicesignal, themolarreport, recepcionista.com) se usaron **unicamente para contrastar** precios no publicados, y cada uso esta marcado como tal ("segunda fuente") o **[A]**.

**Sistemas con fuente oficial unica (19 de 20)**: DentalSoft, DenPro, DentalCore, OdontoClinIA, Dentiqa, Dentatools, Odontoly, FLAP, Sigo, IA Sistemas, ixi, MedicAI, Gestion Salud, WorldSoft, Salvia, MEDTECH GDC, AgendaPro, Doctoralia Pro y Curve Dental. **El restante es Dentrix**, relevado unicamente a traves de fuentes secundarias (ver linea siguiente).

**Sistemas donde el precio proviene de una fuente secundaria y no del proveedor**: Dentrix (precio **[NE]** en Capterra; rango de USD 400–700/mes de practiquesignal, marcado **[A]**) · Curve Dental (USD 299–500 de practiquesignal; la pagina oficial publica dos tiers sin cifra, marcada **[C]** para la existencia de tiers y **[A]** para el monto) · AgendaPro (USD 19 de Capterra.co; la pagina oficial .cl publica CLP, marcada **[C]**).

**Verificaciones que un lector puede repetir**: los numeros de registro **ReNaPDiS #248** (OdontoClinIA) y **ReNaPDiS #292** (MedicAI) se contrastan contra el listado oficial del Ministerio de Salud. El **Legajo RL-2026-41992503-APN-SSVEIYES#MS** de IA Sistemas **no se pudo verificar** sin acceso al registro correspondiente, y por eso queda como **[A]**.

**Limites explicitos de esta investigacion**:
- No se realizo **entrevistas con clinicas reales** ni con odontologos. Los riesgos 1 y 3 del punto 10 **no estan mitigados**.
- No se **probaron los sistemas**. Todo lo relevado es documentacion del proveedor. Los conteos de clinicas y las reducciones de ausentismo son **[A]** en todos los casos, sin excepcion.
- No se verifico **precio real de renovacion** ni costos ocultos de implementacion en ningun proveedor.
- El **mercado local** (clientes que aun usan papel o WhatsApp, que es el publico objetivo real del proyecto) **no se dimensiono**. Es el gap de investigacion mas grande y el mas relevante para el proyecto.
