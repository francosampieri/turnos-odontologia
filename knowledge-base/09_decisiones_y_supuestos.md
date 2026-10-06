# Decisiones y Supuestos

Registro de las decisiones de diseño del proyecto. Cada decisión tiene un código `DD-NN` estable y una sección de **alternativas rechazadas**: una decisión sin alternativas evaluadas no es una decisión, es una costumbre.

**Convención**: `DD` = decisión (elegida, con su por qué). `SU` = supuesto (creído cierto, todavía no verificado, con su riesgo y cómo validarlo).

> **Glosario de los códigos `R` ( Discovery).** El `discovery/discovery.md` usa **dos familias de códigos `R` distintos** que se confunden entre sí. Toda mención a un código `R` en esta base de conocimiento debe_NORMALIZARSE a la forma de esta tabla. Ver también la tabla equivalente en el apéndice de `05_reglas_de_negocio.md`.
>
> | Familia | Formato | Rango | Qué es | Dónde se define |
> |---|---|---|---|---|
> | **Reglas de negocio del Discovery** | `R1` … `R8` (**sin guion**) | §7 | Reglas que el sistema debe cumplir, derivadas del relevamiento de 20 proveedores. Casi todas terminan implementadas con un código `RN-` propio | `discovery/discovery.md` §7 |
> | **Restricciones de proyecto** | `R-1` … `R-5` (**con guion**) | §9 | Restricciones del enunciado y del proyecto: qué se entrega, con qué criterio, con qué stack y con qué presupuesto. **No** son reglas de negocio: no tienen código `RN-` | `discovery/discovery.md` §9 |
>
> **Las dos familias, código por código:**
>
> | Código | Familia | Significado | Dónde se usa en esta KB |
> |---|---|---|---|
> | **R1** | Regla de negocio | Un profesional no puede tener dos turnos solapados | RN-TU-05 · DD-08 · `04` § "El punto clave de diseño" · `08` |
> | **R2** | Regla de negocio | No se puede reservar en una fecha/hora pasada | RN-TU-02 |
> | **R3** | Regla de negocio | No se puede reservar sobre un bloque horario bloqueado | RN-HO-03, RN-FE-03, RN-FE-05 |
> | **R4** | Regla de negocio | La duración del turno depende de la prestación, no es fija *(supuesto)* | RN-PR-02/03 · DD-10 · SU-05 |
> | **R5** | Regla de negocio | Al cancelar, el horario queda automáticamente disponible *(supuesto)* | RN-CA-01, RN-TU-09 |
> | **R6** | Regla de negocio | La clínica atiende en una franja horaria fija por día de semana *(supuesto)* | RN-HO-01/05 · SU-06 |
> | **R7** | Regla de negocio | El paciente no puede tener dos turnos simultáneos **[NE]** | RN-TU-06 · DD-09 · PA-03 |
> | **R8** | Regla de negocio | Los feriados se contrastan contra el calendario nacional argentino *(supuesto)* | RN-FE-01…04 · DD-18 · IN-09 |
> | **R-1** | Restricción | Entregable de Metodología de Sistemas (TUP): el criterio de éxito es que se pueda explicar y defender | `01` · `02` · DD-19 |
> | **R-2** | Restricción | Priorizar claridad sobre complejidad | DD-01, DD-19 |
> | **R-3** | Restricción | Enfoque didáctico pero usable: la interfaz tiene que poder operarse, no sólo demostrarse | `01` § Presentación |
> | **R-4** | Restricción | Web, multiusuario, base de datos *(supuesto, luego confirmado)* | DD-01, DD-03 · IN-05 |
> | **R-5** | Restricción | Presupuesto acotado / sin costos de infraestructura *(supuesto)* | DD-06, DD-07 · SU-08 |
>
> **Regla de escritura**: en los documentos de la KB se escribe **"la regla R4"** para la familia de negocio y **"la restricción R-1"** para la familia de restricciones. **Nunca** se escribe un `R` suelto, y **nunca** se omite el guion cuando corresponde a `R-1…R-5`. Si un código no está en esta tabla, no existe.

| Decisión | Título | Dominio |
|---|---|---|
| [DD-01](#dd-01--backend-y-frontend-como-aplicaciones-separadas) | Backend y frontend como aplicaciones separadas | Arquitectura |
| [DD-02](#dd-02--rest-en-lugar-de-graphql) | REST en lugar de GraphQL | Arquitectura |
| [DD-03](#dd-03--postgresql-como-fuente-de-verdad) | PostgreSQL como fuente única de verdad | Datos |
| [DD-04](#dd-04--odontograma-de-piezas-y-estados-sin-imagenes) | Odontograma de piezas y estados, sin imágenes | Producto |
| [DD-05](#dd-05--agenda-interna-sin-reserva-online-pública) | Agenda interna solamente | Producto |
| [DD-06](#dd-06--redis-declarado-pero-sin-uso-en-el-mvp) | Redis declarado pero sin uso en el MVP | Arquitectura |
| [DD-07](#dd-07--recordatorios-por-whatsapp-fuera-del-mvp) | Recordatorios WhatsApp/SMS/email fuera del MVP | Producto |
| [DD-08](#dd-08--anti-solapamiento-en-la-capa-de-datos) | Anti-solapamiento en la capa de datos | Datos |
| [DD-09](#dd-09--anti-solapamiento-de-paciente-como-decisión-explícita) | Anti-solapamiento de paciente | Producto |
| [DD-10](#dd-10--duración-variable-por-servicio-y-por-profesional) | Duración variable por servicio y por profesional | Datos |
| [DD-11](#dd-11--sobreturno-como-única-excepción-controlada) | Sobreturno como única excepción controlada | Producto |
| [DD-12](#dd-12--una-sola-clínica-sin-multi-tenant) | Una sola clínica, sin multi-tenant | Alcance |
| [DD-13](#dd-13--tres-roles-fijos-sin-gestión-de-roles) | Tres roles fijos, sin gestión de roles | Seguridad |
| [DD-14](#dd-14--mínimo-2h-de-antelación-para-cancelar-o-reprogramar) | Mínimo 2 h de antelación | Producto |
| [DD-15](#dd-15--sillón-obligatorio-en-todo-turno) | Sillón obligatorio en todo turno | Modelo |
| [DD-16](#dd-16--exportación-de-datos-fuera-del-mvp) | Exportación de datos fuera del MVP | Alcance |
| [DD-17](#dd-17--auditoría-incluida-aunque-sea-prioridad-baja) | Auditoría incluida aunque sea prioridad baja | Seguridad |
| [DD-18](#dd-18--feriados-cargados-a-mano-sin-api-externa) | Feriados cargados a mano | Producto |
| [DD-19](#dd-19--el-criterio-de-éxito-es-la-defensa) | El criterio de éxito es la defensa | Proyecto |

---

## Decisiones documentadas

### DD-01 — Backend y frontend como aplicaciones separadas

**Decisión**: backend Python/FastAPI y frontend React/TypeScript/Vite son **dos aplicaciones distintas**, con procesos, puertos y artefactos de build separados. La única interfaz entre ambas es una API REST con JSON.

**Contexto**: el stack fue impuesto por el profesor como condición de entrega. La separación es un requisito, no una preferencia del equipo. Aun así había que elegir **cómo** materializar esa separación, porque hay al menos tres formas distintas de hacerla.

**Alternativas consideradas**:
1. **Monolito Next.js** (API routes + frontend en el mismo proyecto, un solo `npm run dev`). *Descartada por requisito*: el enunciado manda backend en Python. Además, un monolito resuelve la frontera entre capas en el mismo proceso, que es justamente lo que el proyecto quiere hacer visible y defender.
2. **Django + templates / HTMX**, o Flask con el frontend servido como estático por el propio backend. *Descartada*: FastAPI es el framework pedido, y además esta opción elimina la separación de procesos que da lugar a CORS y a la necesidad de manejar el token explícitamente — es decir, elimina parte del contenido didáctico del proyecto.
3. **Monolito modular en FastAPI** sirviendo además el bundle del frontend. *Descartada*: `npm run build` desde Python es una dependencia de Node en tiempo de build y complica el Compose sin ganar nada.
4. **Opción elegida**: SPA React servida por nginx + API FastAPI, con proxy `/api` en nginx.

**Justificación**: cumple el requisito y, además, hace explícita la frontera entre capas: el frontend no puede tocar la base de datos, la API no sabe qué hay renderizado, y cada una tiene su propio ciclo de despliegue. Es defendible punto por punto.

**Trade-offs aceptados**: dos procesos en lugar de uno; CORS obligatorio; doble manejo de errores (el backend devuelve códigos HTTP, el frontend los traduce); sin validación de tipos compartida salvo que se genere desde OpenAPI; el JWT viaja por cabecera porque no hay SSR.

---

### DD-02 — REST en lugar de GraphQL

**Decisión**: API REST con verbos HTTP, recursos nombrados y prefijo `/api/v1`. Schemas Pydantic como contrato único.

**Contexto**: el cliente del sistema es interno y conocido — la secretaria y el odontólogo. No hay terceros que necesiten descubrí la API.

**Alternativas consideradas**: GraphQL (buena para el caso de la agenda, donde cada pantalla pide un recorte distinto de la misma información); tRPC o generación de tipos compartida (atractiva en TypeScript, pero el backend es Python).

**Justificación**: un esquema de recursos con `GET /turnos?fecha=&profesional_id=` es autoexplicativo, se puede probar con curl a mano en la defensa y produce un `openapi.json` navegable. GraphQL agregaría una capa de resolución, un cliente generado y una decisión más que explicar sin ganar funcionalidad que el MVP necesite.

**Trade-offs aceptados**: el frontend puede traer más datos de los que necesita en algunas consultas; no hay tipado extremo a extremo automático.

---

### DD-03 — PostgreSQL como fuente única de verdad

**Decisión**: PostgreSQL 16 es la única fuente de verdad. El backend no guarda estado en memoria, ni en `sessionStorage`, ni en el navegador. Redis no se usa (DD-06).

**Contexto**: la clínica tiene varios usuarios simultáneos. Cualquier estado que viva fuera de la base puede desincronizarse.

**Alternativas consideradas**: SQLite (imposible: no soporta `EXCLUDE USING gist`, que es la base de DD-08); MongoDB (el modelo es altamente relacional y la invariante central es una restricción de rango); mantener el estado en el navegador con sincronización (multiplicaría los conflictos).

**Justificación**: la regla que define el producto (no-solapamiento) se expresa de manera nativa, declarativa e indexada en PostgreSQL. Usar otra base obligaría a simular esa restricción en el código, que es exactamente lo que el proyecto decidió no hacer.

**Trade-offs aceptados**: hay que operar un servidor de base de datos. El Compose lo resuelve y para un TP es una ventaja, no una carga.

---

### DD-04 — Odontograma de piezas y estados, sin imágenes

**Decisión**: el odontograma **entra en el MVP** con notación FDI, 32 piezas permanentes, un catálogo cerrado de 12 estados, cara opcional e historial de cambios por pieza. **No hay radiografías, ni fotos, ni imágenes, ni archivos adjuntos.**

**Contexto**: la investigación encontró que los **10 de 10** proveedores argentinos dedicados a odontología incluyen odontograma, y el propio Discovery lo había recomendado dejar fuera por ser "la expectativa del mercado" y multiplicar el alcance ×5. La decisión confirmada invierte ese punto: entra como diferenciador de nicho, pero acotado a su forma más simple.

**Alternativas consideradas**:
1. Odontograma **fuera** del MVP (propuesta del Discovery). *Descartada*: una clínica que debe volver al papel para registrar la pieza pierde el motivo por el que digitaliza.
2. Odontograma **completo** con imágenes y radiografías. *Descartada*: exige almacenamiento binario, un estándar de imagen, una revisión de privacidad adicional y una revisión de la Ley 26.529 — y es el ítem que más multiplica el esfuerzo dentro del módulo.
3. **Opción elegida**: piezas + estados + historial.

**Justificación**: el odontograma de piezas es barato de modelar (dos tablas) y de alto valor percibido para el odontólogo. Las imágenes son un proyecto aparte, con costos de almacenamiento y cumplimiento normativo propios.

**Trade-offs aceptados**:
- **Deuda de diseño consciente**: una fila por pieza y no por (pieza, cara). Si más adelante se necesita detalle por cara, se agrega `pieza_cara`; no afecta al modelo de turnos ni a las reglas de agenda.
- Se registra en `10_preguntas_abiertas.md` como **PA-01**, no como olvido.

---

### DD-05 — Agenda interna solamente

**Decisión**: la agenda es **interna a la clínica**. La reserva la realiza la secretaria. **No hay** reserva online pública, ni portal del paciente, ni autoservicio, ni confirmación en vivo por WebSocket.

**Contexto**: el caso de uso 5 del Discovery ("el paciente reserva desde el celular") es el más caro del proyecto y el de mayor riesgo de concurrencia. Era la pregunta bloqueante nº 1 de la investigación.

**Alternativas consideradas**:
1. **Reserva pública por enlace sin cuenta** (lo que proponía el Discovery). *Descartada*.
2. **Portal del paciente con usuario y contraseña**. *Descartada*.
3. **WebSocket para confirmación en vivo**. *Descartada*.
4. **Opción elegida**: agenda interna.

**Justificación — y por qué es defendible**: la reserva pública arrastra un subsistema de seguridad completo que el MVP no necesita: autenticación o verificación de un actor no confiable (el paciente), **rate limiting**, **anti-abuso**, manejo de concurrencia sobre el último horario disponible, y reconciliación de reservas abandonadas. Todo eso compite por el mismo tiempo que hace falta para que el núcleo esté bien resuelto. El Discovery lo formuló así: *"la reserva online pública es la parte más difícil del MVP, no la más fácil"* — y además *"si no entra, el sistema sigue siendo útil y el entregable es defendible"*.

**Trade-offs aceptados**: el sistema no ataca el ausentismo por sí solo (queda en manos de la secretaria y del canal que use la clínica), y no resuelve la fricción del paciente que quiere reservar sin llamar. Ambas cosas quedan registradas como **PA-02**.

> Lo que sí se conserva del problema original: **el anti-solapamiento de dos secretarias** es un problema de concurrencia real y está resuelto en la capa de datos (DD-08). El que queda fuera es el problema de concurrencia del paciente, que es un subcaso del mismo mecanismo ya implementado.

---

### DD-06 — Redis declarado pero sin uso en el MVP

**Decisión**: Redis está **declarado en `docker-compose.yml` y arranca**, pero **ninguna parte del MVP lo usa**. El backend no importa ninguna librería de Redis.

**Contexto**: Redis forma parte del stack requerido por el enunciado. Pero el MVP no tiene un solo proceso asíncrono: no se envían emails, no hay reportes programados, no hay cola de nada.

**Alternativas consideradas**:
1. **Usarlo para cachear la disponibilidad.** *Descartada*: una caché de disponibilidad se invalida justo en el momento en que importa (cuando alguien reserva), y convertirlo en un acierto o un fallo de consistencia. El cálculo de slots es barato sobre los volúmenes de una clínica.
2. **Usarlo para la cola de recordatorios.** *Descartada*: los recordatorios están fuera del MVP (DD-07), así que la cola no tendría consumidor.
3. **No declararlo.** *Descartada*: el enunciado lo pide; retirarlo del Compose sería defendible como una omisión.
4. **Opción elegida**: declarado, arrancando, sin uso, con la justificación escrita.

**Justificación**: dejar el servicio declarado hace que el entorno sea reproducible y que la decisión sea **explícita y defendible** en lugar de silenciosa. Un Redis arrancando y sin tráfico es una observación honesta; un Redis ausente sin explicación parece un olvido.

**Qué justificaría su uso real**: envío de recordatorios con reintentos, invalidación de caché de disponibilidad, rate limiting de un eventual endpoint público, o resultados de reportes pesados.

---

### DD-07 — Recordatorios por WhatsApp/SMS/email fuera del MVP

**Decisión**: no hay envío de mensajes en el MVP. Queda en el backlog con su costo ya medido.

**Contexto**: es la funcionalidad con más impacto sobre el problema real (el ausentismo), y simultáneamente la que más costo externo introduce. La investigación encontró dos cifras concretas: ixi traslada **$45 + IVA por mensaje entregado** y DentalSoft Pro cobra **USD 0,026 por recordatorio** de Meta. Ninguno de los dos es gratuito, y los dos lo cobran en el plan de mayor precio.

**Alternativas consideradas**: WhatsApp Business API (integración real y demostrada por 7 de 10 proveedores argentinos); email (sólo 1 lo incluye en la base); SMS (DenPro sólo manda SMS).

**Justificación**: meter un costo variable por mensaje en un TP elimina la propiedad más útil del sistema: **funciona completo sin depender de ningún servicio externo**. Además, la integración no es verificable sin probarla con una cuenta empresarial verificada, y el Discovery la marcó como *no verificable*.

**Trade-offs aceptados**: el enunciado de problema del Discovery incluía *"que avise al paciente antes del turno"*. Al sacar los recordatorios, **el problema que este proyecto resuelve es el núcleo de turnos más el odontograma**, no la automatización de avisos. Está escrito explícitamente en `01_vision_y_objetivos.md` y registrado como **IN-08** en `10_preguntas_abiertas.md`, porque es el punto que un jurado puede preguntar.

---

### DD-08 — Anti-solapamiento en la capa de datos

**Decisión**: la no-superposición de turnos se garantiza con **tres restricciones de exclusión GiST** en PostgreSQL (`EXCLUDE USING gist` sobre `tstzrange(inicio, fin, '[)')`, parciales), no con un `if` en el código de aplicación.

**Contexto**: la **regla R1** (no-solapamiento del profesional, §7 del Discovery) es la que el sistema promete cumplir. La alternativa obvia —validar en el endpoint— falla de dos maneras que sólo aparecen en producción: la carrera entre dos secretarias (entre el `SELECT` y el `INSERT` hay una ventana real) y el bypass por cualquier escritura que no pase por el servicio (un script de carga, una corrección manual, una migración).

**Alternativas consideradas**:
1. **Validación en el endpoint** (`if existe_turno_profesional(…): error`). *Descartada*: es exactamente la solución que el proyecto rechaza por no ser una invariante.
2. **`SELECT … FOR UPDATE` sobre el profesional.** *Descartada*: bloquea la fila del profesional, pero no el rango de tiempo, y no protege frente a escrituras por otras vías.
3. **`pg_advisory_xact_lock`.** *Considerada y descartada*: funciona y es más fácil de entender, pero serializa sólo mientras el lock está tomado. Cualquier escritura que no lo tome rompe la invariante igual. El `EXCLUDE` es una **declaración permanente** de la invariante.
4. **Opción elegida**: `EXCLUDE USING gist`.

**Justificación**: es la única forma de decir "estas filas no pueden coexistir" en SQL, es **indexable** (a diferencia de un predicado escrito a mano), PostgreSQL la soporta de forma nativa, y el conflicto se materializa como una excepción que la aplicación traduce a `409`. Requiere `CREATE EXTENSION btree_gist`, que es el error más común al implementarlo por primera vez.

**Trade-offs aceptados**: una extensión de PostgreSQL que hay que instalar; los constraints no son `DEFERRABLE` (no hacen falta: la reserva es transaccional e inmediata, y no hay edición en lote); el mensaje de error lo genera la base, así que hay que traducirlo bien.

---

### DD-09 — Anti-solapamiento de paciente como decisión explícita

**Decisión**: un paciente **no puede tener dos turnos simultáneos**, aunque sean con profesionales distintos.

**Contexto**: es la **única** de las **ocho reglas de negocio del Discovery (R1…R8)** que **ningún** proveedor de los 20 relevados declara. Existen excepciones clínicas legítimas: cirugía en equipo, sedación, un paciente con un tratamiento en curso y un control en otro sillón.

**Alternativas consideradas**: 1. No restricción alguna (permitirlo); 2. Restricción con excepción configurable (`motivo_excepcion`); 3. Restricción pura, como se eligió.

**Justificación**: para una clínica chica con agenda gestionada por recepción, el solapamiento del paciente es casi siempre un error de carga, no un caso de equipo. Se elige la restricción **pura y simple**, y se documenta el caso de equipo como limitación conocida en lugar de construir ahora un mecanismo de excepción que probablemente no se use.

**Trade-offs aceptados**: el sistema **no puede representar** un paciente en dos sillones a la vez. Si un caso real lo exige, hay que agregar la excepción (PA-03). Documentar una decisión límite es más barato que descubrirla como bug.

---

### DD-10 — Duración variable por servicio y por profesional

**Decisión**: 30 minutos por defecto; la duración es un atributo del `servicio` (valores 15/30/45/60) y admite un **override por profesional** (`profesional_servicio`). `fin` se calcula y **se desnormaliza** en `turno`.

**Contexto**: el Discovery marcó la **regla R4** (§7: *"la duración del turno depende de la prestación, no es fija"*) como supuesto sin dato real, y detectó que fijar 30 minutos hace que el modelo de datos sea incorrecto desde el día 1. La decisión confirmada fija 30 como default y lo hace configurable.

**Alternativas consideradas**: 1. Duración fija de 30 en el código; 2. Duración libre por servicio (cualquier entero); 3. Duración en minutos con override por profesional.

**Justificación**: el `CHECK (duracion_min IN (15,30,45,60))` mantiene el dominio acotado y deja la agenda legible. El override por profesional evita duplicar servicios ("Limpieza 30" / "Limpieza 45"), que es la clase de dato que se ensucia a los tres meses. Desnormalizar `fin` es lo que hace posible el índice de exclusión (DD-08).

**Trade-offs aceptados**: `fin` puede quedar desactualizado si alguien cambia la duración del servicio en el futuro. Se acepta porque los turnos existentes **no se recalculan**: un turno reservado conserva la duración con la que se agendó, que además es lo clínicamente correcto.

---

### DD-11 — Sobreturno como única excepción controlada

**Decisión**: el sobreturno es un estado propio (`sobreturno`), se crea por un **endpoint separado**, exige motivo, y es la **única** condición que excluye una fila de las tres restricciones GiST.

**Contexto**: la investigación lo listaba como funcionalidad opcional de prioridad media. Se decidió incluirlo porque una clínica real tiene urgencias, y excluirlo del modelo obligaría a "colar" un turno encima de otro sin registro.

**Alternativas consideradas**: 1. No soportarlo (la urgencia se carga pisando un horario, sin registro); 2. Permitir solapamientos "a pedido" con un flag libre; 3. Sobreturno como excepción acotada.

**Justificación**: un flag libre sería un agujero: cualquier `es_sobreturno = TRUE` mal puesto desactivaría el anti-solapamiento. Al atarlo a **un estado**, un motivo obligatorio, **un endpoint propio** y **un campo `es_sobreturno` que sólo ese endpoint escribe**, la excepción queda acotada, auditada y visible en la agenda.

**Trade-offs aceptados**: el sobreturno puede pisar cualquier horario sin verificación. A cambio, queda registrado quién lo hizo y por qué.

---

### DD-12 — Una sola clínica, sin multi-tenant

**Decisión**: el sistema sirve a **una única clínica**. No hay entidad `clinica`, ni `sucursal_id` en ninguna tabla, ni multi-tenant.

**Contexto**: el Discovery lo dejó como supuesto ("un solo consultorio con dos gabinetes **no** es multi-sucursal") y lo confirmó la decisión final.

**Alternativas consideradas**: multi-tenant por esquema; multi-tenant por fila con `clinica_id` en todas las tablas; una clínica pero con `clinica_id` "por si acaso".

**Justificación**: multi-tenant atraviesa **todas** las tablas, **todos** los endpoints y **todas** las pruebas de autorización. Es el multiplicador de alcance más grande después del SSR. La tercera opción —dejar la columna por si acaso— se descarta explícitamente: una columna que nunca se usa es sólo deuda.

**Trade-offs aceptados**: el sistema no se puede vender a dos clínicas sobre la misma instalación. Es una limitación **correcta** para el alcance: si aparece el segundo cliente, agregar `clinica_id` es una migración, no un rediseño.

---

### DD-13 — Tres roles fijos, sin gestión de roles

**Decisión**: existen exactamente tres roles (`secretaria`, `odontologo`, `admin`), cargados por seed. **No hay** interfaz de creación ni de edición de roles.

**Contexto**: el Discovery marcó la separación de roles como un ajuste obligatorio al alcance, no como un extra. La pregunta abierta era si conviene hacerlo extensible.

**Alternativas consideradas**: 1. Roles como `ENUM` en el código; 2. Roles como tabla con permisos configurables; 3. Roles como tabla, tres filas, permisos en código.

**Justificación**: los **permisos** de cada rol están escritos en el código (dependencias de FastAPI) y son la parte que hay que poder defender y probar. Una tabla de permisos configurable por interfaz haría que una prueba de RBAC dependiera de datos. Se elige el punto medio: el **rol es dato** (agregar un cuarto rol es un `INSERT`), los **permisos son código**.

**Trade-offs aceptados**: agregar un cuarto rol con permisos nuevos exige escribir código, no sólo cargar filas.

---

### DD-14 — Mínimo 2 h de antelación para cancelar o reprogramar

**Decisión**: cancelar o reprogramar un turno requiere **al menos 2 horas** de antelación respecto del inicio.

**Contexto**: el prompt original lo sugirió, y el Discovery lo **descartó**: ningún proveedor argentino relevado declara una política de cancelación con antelación mínima, e imponerla en un consultorio chico sin dato real sería inventar una política.

**Alternativas consideradas**: 1. Sin anticipación mínima (lo que decía la investigación); 2. 2 horas (decisión confirmada); 3. 24 horas (lo habitual en servicios con mail).

**Justificación**: se adopta la decisión confirmada de 2 h. Es una ventana **suficientemente corta para que casi nunca bloquee a la secretaria** (un paciente que avisa el mismo día por la mañana puede cancelarse si el turno es de la tarde) y lo bastante larga para que el horario liberado todavía tenga chances de ser reocupado. El Discovery ya había señalado que 24 h sería inviable sin un recordatorio que acompañe la política, y **no hay recordatorios en el MVP** (DD-07): una política dura sin aviso es una política que se incumple.

**Trade-offs aceptados**: la política es arbitraria en el sentido de que no viene de un dato de campo. Se documenta como **decisión de diseño** y no como hallazgo, y queda registrada como **IN-01** porque contradice explícitamente lo que decía la investigación.

---

### DD-15 — Sillón obligatorio en todo turno

**Decisión**: `turno.sillon_id` es **obligatorio**. No existen turnos sin gabinete.

**Contexto**: la clínica puede tener varios sillones y la cantidad es configurable. La decisión de exigirlo tiene un costo de entrada alto: sin sillón no se puede agendar.

**Alternativas consideradas**: 1. Sillón opcional (asume una clínica de un único gabinete); 2. Sillón obligatorio.

**Justificación**: modela lo que ocurre en el consultorio y habilita la restricción `turno_no_solape_sillon` (RN-SI/RN-TU-04), que es lo que impide que dos turnos del mismo profesional se pisen físicamente. Con el sillón opcional, esa restricción no se puede expresar y el sistema permite una operación imposible.

**Trade-offs aceptados**: la secretaria tiene que elegir sillón en cada reserva. Se compensa con un valor por defecto en el formulario (el primer sillón activo) y con el hecho de que el campo es visible en la agenda del día.

---

### DD-16 — Exportación de datos fuera del MVP

**Decisión**: la exportación a CSV/Excel **no** está en el MVP, pese a ser la funcionalidad de menor costo de implementación y el mayor hueco de mercado detectado.

**Contexto**: la investigación escribió que **0 de 10** proveedores argentinos dedicados a odontología declara exportación de datos del paciente — el hueco más grande del mercado — y que implementarla cuesta poco. El Discovery la había puesto explícitamente dentro del MVP, en los "4 items de cierre".

**Alternativas consideradas**: 1. Incluirla en el MVP (propuesta del Discovery); 2. Incluir sólo exportación de la agenda del día, no de pacientes; 3. Dejarla entera en el backlog.

**Justificación**: la decisión confirmada la deja afuera. La razón práctica es que la exportación de **pacientes** es exactamente la funcionalidad que más obliga a revisar permisos y privacy por campo (DNI, fecha de nacimiento), y eso es trabajo de Legal tanto como de código. Exportar la agenda del día es mucho más inocuo y podría reentrar por separado.

**Trade-offs aceptados**: se deja el hueco de mercado más grande del relevamiento sin explotar. Es una renuncia consciente: **la claridad del núcleo vale más que una función barata**, y queda como **PA-06** con la observación de que es la primera candidata a la v1.1.

---

### DD-17 — Auditoría incluida aunque sea prioridad baja

**Decisión**: se implementa auditoría append-only de acciones de agenda y de configuración, consultable sólo por `admin`.

**Contexto**: en el Discovery la auditoría figura como **prioridad baja** ("auditoría de cambios: quién modificó qué turno y cuándo") y ningún proveedor argentino la declara con evidencia pública.

**Alternativas consideradas**: 1. No auditarla; 2. Auditar todo, incluidos los `GET`; 3. Auditar sólo acciones sensibles.

**Justificación**: responde directamente al riesgo que el propio Discovery señaló en primer lugar: *"si la secretaria falta, la agenda deja de entenderse"*. Sin trazabilidad, un turno que desaparece de la agenda es indefendible. Es barato (una tabla append-only y un insert dentro de la transacción que ya existe) y es **la respuesta directa al problema de confianza** que el proyecto promete resolver.

**Trade-offs aceptados**: no se auditan las lecturas (una `GET` no genera registro), de modo que la auditoría no crece con el uso; a cambio, no se puede reconstruir **qué consultó** cada usuario. La auditoría no se puede corregir ni borrar, ni siquiera por el `admin`.

---

### DD-18 — Feriados cargados a mano, sin API externa

**Decisión**: el calendario de feriados se carga por seed (nacional argentino) y se administra a mano desde la configuración. **No** se consulta ninguna API de feriados.

**Contexto**: sólo 1 de los 10 proveedores argentinos (IA Sistemas) declara detectar feriados automáticamente; los demás resuelven con bloqueos manuales.

**Alternativas consideradas**: 1. API externa de feriados (siempre actualizada, pero agrega una dependencia y un punto de falla); 2. Carga manual.

**Justificación**: coherente con DD-06 y RN-GL-06 (el sistema opera con la base sola). Un sistema de una clínica que se queda sin internet un viernes tiene que poder seguir funcionando: un feriado mal cargado bloquea turnos; un servicio caído no debería **crear** feriados ni impedir ver la agenda.

**Trade-offs aceptados**: el `admin` tiene que cargar el calendario del año. Queda como **PA-09**.

---

### DD-19 — El criterio de éxito es la defensa

**Decisión**: el criterio de éxito del proyecto es que el sistema **se pueda explicar y defender**, no que sea el mejor producto del mercado.

**Contexto**: el Discovery la registró como la **restricción R-1** (§9): *"entregable de Metodología de Sistemas (TUP)"*. Además, no hay cliente real validado (riesgo nº 1 del Discovery).

**Alternativas consideradas**: 1. Criterio de adopción comercial (imposible: no hay cliente); 2. Criterio de completitud funcional (equivale a hacer todo lo que hacen 10 proveedores).

**Justificación**: define cómo se arbitran todas las decisiones de alcance de esta base. Cuando una funcionalidad es mutuamente excluyente con la claridad del núcleo, gana el núcleo.

**Consecuencia práctica**: cada decisión de "fuera de alcance" en `01_vision_y_objetivos.md` incluye **la razón**, y cada supuesto de la investigación se conserva documentado en vez de borrarse. La trazabilidad completa empieza en SU-01 (Supuesto: la clínica necesita digitalizar).

---

## Supuestos inferidos

Un supuesto es una creencia que el proyecto usa pero que **nadie verificó**. Cada uno tiene su riesgo y su forma de validación.

### SU-01 — La clínica objetivo necesita digitalizar de verdad

**Supuesto**: una clínica chico-mediana con recepción y varios profesionales quiere pasar de teléfono, WhatsApp y papel a un sistema formal.
**Origen**: `discovery/discovery.md` §10, riesgo nº 1. No hay ninguna validación con una clínica real.
**Riesgo si es falso**: el proyecto resuelve un problema que nadie tiene. **Es el riesgo nº 1 del proyecto y no se mitiga con código**: afecta la premisa, no la implementación.
**Cómo validar**: una entrevista con una clínica real; observación de media jornada en recepción.

### SU-02 — El solapamiento y la doble reserva son el dolor principal

**Supuesto**: el problema que más duele es la doble reserva, no otra cosa.
**Origen**: `discovery/discovery.md` §10, riesgo nº 2. Ningún proveedor argentino publica métricas de campo verificables; el "-82% de ausencias" de DentalSoft y la cita Cochrane de IA Sistemas son afirmaciones comerciales **[A]**.
**Riesgo si es falso**: el sistema resuelve un problema real pero secundario. Mitigación: el MVP también cubre búsqueda de pacientes, odontograma y configuración, que son necesidades de segunda línea.
**Cómo validar**: preguntar a la secretaria cuál es la molestia principal.

### SU-03 — El cliente tiene recepción y más de un profesional

**Supuesto**: la clínica tiene al menos una secretaria y dos o más odontólogos.
**Origen**: `discovery/discovery.md` §10, riesgo nº 3.
**Riesgo si es falso**: si el cliente es un odontólogo solo, sobran el módulo de roles y la agenda multiprofesional.
**Cómo validar**: la misma entrevista del SU-01. El seed ya provee 1 admin + 1 secretaria + 2 odontólogos, que es el escenario más exigente: si el sistema funciona ahí, funciona en el más simple.

### SU-04 — Un sistema sin historia clínica es aceptable

**Supuesto**: la clínica acepta que el sistema no registre historia clínica, evoluciones ni periodonto.
**Origen**: `discovery/discovery.md` §10, riesgo nº 4.
**Riesgo si es falso**: la clínica vuelve al papel para la ficha clínica y el sistema queda usado sólo para agendar.
**Mitigación parcial**: el **odontograma** entra al MVP (DD-04), que es el elemento clínico más consulteado del relevamiento y el más barato de modelar. Es la respuesta directa a este riesgo.
**Cómo validar**: preguntar qué parte de la ficha en papel es la que más costaría abandonar.

### SU-05 — La duración por servicio se resuelve con 15/30/45/60

**Supuesto**: las duraciones reales de las prácticas caen en ese conjunto de valores.
**Origen**: `discovery/discovery.md` §7, **regla R4** (*"la duración del turno depende de la prestación, no es fija"*, marcada como *Supuesto*) y §11, pregunta 5 ("¿cuál es la duración por prestación?"), que quedó sin dato real. Es la misma regla que RN-PR-02 enfrenta al decidir el conjunto `{15, 30, 45, 60}`.
**Riesgo si es falso**: hay que agregar valores al `CHECK`, lo que es una migración menor pero hay que hacerla.
**Cómo validar**: pedirle al cliente la tabla real de duraciones. El seed trae seis servicios con duraciones plausibles.

### SU-06 — El horario Lun–Vie 08:00–18:00 y sábado opcional sirve

**Supuesto**: ese es el horario por defecto razonable de una clínica.
**Origen**: `discovery/discovery.md` §7, **regla R6** (*"la clínica atiende en una franja horaria fija por día de semana"*, marcada como *Supuesto*) y §11, pregunta 5.
**Riesgo si es falso**: ninguno grave — el horario es 100 % configurable por profesional (US-011). El default sólo afecta la carga inicial.
**Cómo validar**: preguntarlo en la primera reunión de setup.

### SU-07 — No hay un segundo cliente sobre la misma instalación

**Supuesto**: el sistema se despliega para una sola clínica y no hace falta multi-tenancy.
**Origen**: `discovery/discovery.md` §11, pregunta 10 ("se asumió que no") y decisión confirmada (DD-12).
**Riesgo si es falso**: agregar `clinica_id` es una migración que atraviesa todas las tablas, todas las consultas y todas las pruebas de autorización.
**Cómo validar**: preguntar si el proyecto tiene un segundo cliente en mente antes de que exista la base instalada.

### SU-08 — Sin costes de infraestructura ni servicios pagos

**Supuesto**: no hay presupuesto para servicios de terceros.
**Origen**: `discovery/discovery.md` §9, **restricción R-5** (*"presupuesto acotado / sin costos de infraestructura"*, marcada como *Supuesto*, a confirmar). Nótese que es `R-5` (con guion, familia de restricciones), no `R5`: aqulla es la regla de negocio "al cancelar el horario queda disponible" (RN-CA-01).
**Riesgo si es falso**: el alcance crece (recordatorios, pagos, facturación) y el sistema deja de ser autónomo.
**Cómo validar**: confirmarlo con el docente antes de entregar. Mientras tanto, el sistema se despliega con Docker Compose en una máquina y no más.

---

## Reglas de decisión aplicadas en este proyecto

Para resolver los casos que no están cubiertos por ninguna `DD`:

1. **¿Se puede defender en quince minutos?** Si la respuesta es no, la funcionalidad entra al backlog.
2. **¿La regla se puede garantizar en la base de datos?** Si sí, va en la base; si sólo se puede garantizar en el código, hay que justificar por qué alcanza.
3. **¿Introduce un costo variable o una dependencia externa?** Si sí, fuera del MVP (DD-06, DD-07, DD-18).
4. **¿El enunciado lo pide?** Si sí, entra, aunque el mercado no lo tenga (odontograma, DD-04).
5. **En empate, gana el núcleo**: agenda, pacientes, configuración.