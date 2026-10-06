# Turnos Odontología — Base de Conocimiento

Base de conocimiento canónica del proyecto, generada a partir del enunciado del TP, de la investigación de mercado (`discovery/discovery.md`) y de las decisiones de producto ya confirmadas.

**Regla de oro**: si el código y este directorio discrepan, el código tiene un bug. Ningún documento de `docs/`, ni un comentario en el código, redefine el alcance.

---

## Índice de Archivos

| Archivo | Contenido |
|---------|-----------|
| [01_vision_y_objetivos.md](01_vision_y_objetivos.md) | Propósito, objetivos por actor, alcance v1.0, fuera de alcance y métricas de éxito |
| [02_descripcion_general.md](02_descripcion_general.md) | Descripción en prosa, stack tecnológico, arquitectura general, integraciones y superficie de la API REST |
| [03_actores_y_roles.md](03_actores_y_roles.md) | Los tres roles, matriz RBAC por recurso, rutas públicas y permisos condicionados |
| [04_modelo_de_datos.md](04_modelo_de_datos.md) | Dominios, ERD, entidades con columnas y constraints, índices, seed y cómo la base impide el solapamiento |
| [05_reglas_de_negocio.md](05_reglas_de_negocio.md) | 67 reglas `RN-xx` activas en 10 dominios, más el dominio `RN-XP` (4 reglas retiradas), y matriz endpoint → regla → estado HTTP |
| [06_funcionalidades.md](06_funcionalidades.md) | 27 historias `US-xx` con criterios de aceptación y reglas asociadas, agrupadas por épica |
| [07_flujos_principales.md](07_flujos_principales.md) | Doce flujos extremo a extremo, incluidos los que fallan por concurrencia, con diagramas de secuencia y casos de error |
| [08_arquitectura_propuesta.md](08_arquitectura_propuesta.md) | Patrones, estructura de las dos aplicaciones, Docker Compose, seguridad, CORS y variables de entorno |
| [09_decisiones_y_supuestos.md](09_decisiones_y_supuestos.md) | 19 decisiones `DD-xx` con alternativas descartadas y 8 supuestos `SU-xx` con su validación |
| [10_preguntas_abiertas.md](10_preguntas_abiertas.md) | 11 inconsistencias `IN-xx` detectadas contra la investigación y 15 preguntas abiertas `PA-xx` priorizadas |

---

## Quick Start para Desarrolladores

1. **Entender el dominio** → [01](01_vision_y_objetivos.md), [03](03_actores_y_roles.md)
2. **Entender los datos** → [04](04_modelo_de_datos.md)
3. **Entender las reglas** → [05](05_reglas_de_negocio.md)
4. **Entender la arquitectura** → [02](02_descripcion_general.md), [08](08_arquitectura_propuesta.md)
5. **Implementar** → [07](07_flujos_principales.md), [06](06_funcionalidades.md)
6. **Antes de codificar** → [10](10_preguntas_abiertas.md)

Si sólo tenés 10 minutos para entender el proyecto: leé `01`, después el resumen de decisiones de `09`, y por último la tabla de `10`.

---

## Resumen Ejecutivo

Sistema web interno para gestionar los turnos de una clínica odontológica de **una sola sede**: agenda diaria y semanal, pacientes, profesionales, servicios, configuración de horarios y feriados, y un **odontograma mínimo** (estado de cada pieza, sin imágenes). El backend es **FastAPI con PostgreSQL** y el frontend **React + TypeScript**, como aplicaciones separadas que se comunican por una API REST con JWT. El diferencial técnico es que **el no-solapamiento de turnos se garantiza en la base de datos** (`EXCLUDE USING gist` sobre `tstzrange`), no en el código de aplicación: por eso, si dos secretarias intentan reservar el último horario disponible en el mismo segundo, exactamente una obtiene `201` y la otra `409`.

---

## Propósito

Esta KB responde, en orden de dependencia, cinco preguntas que el resto del proyecto no puede responder solo:

1. **Qué** se construye y para qué (01, 02).
2. **Quién** lo usa y con qué permisos (03).
3. **Cómo** se guarda (04).
4. **Qué** reglas cumple el sistema y **qué** pantallas existen (05, 06).
5. **Cómo** se ejecuta el día a día, con qué stack y bajo qué decisiones (07, 08, 09) — y **qué** sigue sin respuesta (10).

---

## Alcance en una línea

Agenda interna de turnos para una clínica de una sola sede, con pacientes, profesionales, servicios, configuración de horarios y odontograma mínimo (piezas y estados, sin imágenes), sobre **FastAPI + React** con PostgreSQL como garantía de no-solapamiento.

## Fuera de alcance en una línea

Reserva pública, historia clínica, imágenes, obras sociales, facturación, recordatorios automáticos, multi-sucursal y exportación de datos.

Los **trece ítems** y la razón de cada uno están en la tabla *Fuera de alcance* de `01_vision_y_objetivos.md`. Las decisiones que los sostienen están en `09_decisiones_y_supuestos.md` (**DD-04** odontograma sin imágenes · **DD-05** agenda interna sin reserva pública · **DD-07** recordatorios fuera · **DD-12** una sola clínica · **DD-16** exportación fuera) y las preguntas que los dejan abiertos, en `10_preguntas_abiertas.md` (PA-01, PA-02, PA-04, PA-06).

---

## Convenciones

| Prefijo | Significado | Dónde se define | Dónde se usa |
|---------|-------------|-----------------|--------------|
| `RN-xx` | Regla de negocio | `05_reglas_de_negocio.md` | 06, 07, 08, 09 |
| `US-xx` | Historia de usuario | `06_funcionalidades.md` | 07, 09 |
| `DD-xx` | Decisión de diseño | `09_decisiones_y_supuestos.md` | todos |
| `SU-xx` | Supuesto sin verificar | `09_decisiones_y_supuestos.md` | 01, 10 |
| `PA-xx` | Pregunta abierta priorizada | `10_preguntas_abiertas.md` | 01, 05, 09 |
| `IN-xx` | Inconsistencia detectada | `10_preguntas_abiertas.md` | 09 |

Los códigos son estables: si una regla cambia de comportamiento, conserva su `RN` y se le agrega otra. No se reutiliza un código retirado — queda en la tabla de reglas retiradas de `05`.

**Dominios de reglas**: `GL` general · `AU` autenticación y autorización · `PC` pacientes · `PR` profesionales y servicios · `HO` horarios laborales · `SI` sillones · `FE` feriados y bloqueos · `TU` turnos · `CA` cancelación y reprogramación · `OD` odontograma · `XP` retiradas o fuera del MVP.

**Conteos**: **11 dominios** en total (10 activos + `XP`, que sólo tiene reglas retiradas) · **67 reglas activas** (`7`+`8`+`5`+`5`+`5`+`6`+`11`+`5`+`9`+`6`) · **5 códigos retirados** (`RN-XP-01…04` + `RN-OD-10`), listados en el apéndice de `05_reglas_de_negocio.md` y **nunca reutilizados**.

> **Los códigos `R` del Discovery son dos familias distintas** —`R1`…`R8` (reglas de negocio, §7) y `R-1`…`R-5` (restricciones de proyecto, §9)— y se confunden con facilidad. La glosario que las desambigua está al principio de `09_decisiones_y_supuestos.md`.

---

## Reglas de mantenimiento

1. **Una decisión, un lugar.** Si algo es una decisión de diseño, va en `09` con sus alternativas. Si es una regla que el sistema cumple, va en `05`. Si es una tabla, va en `04`.
2. **Toda regla es verificable.** Si no se puede escribir un test que la compruebe, no es una regla: es una intención.
3. **Toda exclusión lleva su razón.** "No está" no es una decisión; "no está porque X" sí.
4. **Ningún supuesto se borra.** Si un supuesto queda invalidado, se marca como invalidado en `09` y se agrega el `DD` que lo reemplaza.
5. **Los cambios de alcance se anotan en `10`.** Un ítem que entra o sale del MVP actualiza su `PA` en el mismo commit.

---

## Origen de los datos

| Origen | Qué aporta | Cómo se usó |
|--------|------------|-------------|
| Enunciado del TP | Alcance obligatorio: roles, entidades, reglas y stack | Fuente primaria. Cuando contradice al Discovery, gana el enunciado |
| `discovery/discovery.md` | 20 sistemas analizados, matriz de funcionalidades, riesgos | Fuente de contexto y de preguntas abiertas. **No** define alcance |
| Decisiones de producto confirmadas | Los 19 `DD` y los 8 `SU` | Definidas con el cliente durante la creación de la KB |
| `openspec/` (a futuro) | Cambios de implementación | No cambia el alcance: se expresa como diferencia sobre esta KB |