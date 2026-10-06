# Flujos Principales

Cada flujo se documenta extremo a extremo, mostrando las interacciones entre frontend, API y base de datos. Los flujos marcados con ⚠️ son los que se presentan en la defensa, porque concentran la dificultad técnica del proyecto.

---

## Flujo 1: Autenticación y sesión

**Disparador**: la secretaria abre la aplicación.
**Actor**: `secretaria` (o cualquier rol).

**Pasos**
1. El frontend detecta que no hay token en `sessionStorage` y redirige a `/login`.
2. La secretaria envía email y contraseña con `POST /api/v1/auth/login`.
3. El backend busca el usuario, verifica `activo = TRUE` y compara el hash con **bcrypt**.
4. Si las credenciales no coinciden, devuelve `401` con un mensaje genérico.
5. Si coinciden, genera el JWT con los claims `sub` (id), `rol`, `exp` y actualiza `ultimo_acceso`.
6. El frontend guarda el token en `sessionStorage` y guarda el usuario en el estado de React.
7. El menú se construye a partir del rol; el frontend pide `GET /api/v1/auth/me` para confirmar la sesión al recargar.

```
Usuario          Frontend (React)        API (FastAPI)          PostgreSQL
  │                   │                      │                       │
  │ credenciales      │                      │                       │
  ├──────────────────▶│                      │                       │
  │                   │ POST /auth/login     │                       │
  │                   ├─────────────────────▶│ SELECT usuario, rol   │
  │                   │                      ├──────────────────────▶│
  │                   │                      │◀─────── fila + hash ───┤
  │                   │                      │ bcrypt.verify()       │
  │                   │                      │ UPDATE ultimo_acceso │
  │                   │                      ├──────────────────────▶│
  │                   │◀─── 200 { token } ───┤                       │
  │                   │ sessionStorage.set   │                       │
  │◀── pantalla ──────┤                      │                       │
```

**Casos de error**
- Credenciales incorrectas → `401`, mensaje genérico, sin revelar qué parte falló.
- Usuario inactivo → `403` con mensaje explícito (es un caso de administración, no de seguridad).
- Token expirado → `401`; el frontend limpia `sessionStorage` y vuelve a `/login`.
- Token de un rol que no alcanza el recurso → `403`.

**Reglas**: RN-AU-01, RN-AU-02, RN-AU-03, RN-AU-06, RN-AU-07.

---

## Flujo 2: Alta de paciente

**Disparador**: la secretaria necesita agendar a un paciente que no está cargado.
**Actor**: `secretaria`.

**Pasos**
1. Desde `/pacientes/nuevo` completa nombre, apellido, DNI, teléfono, fecha de nacimiento y, opcionalmente, email.
2. El frontend normaliza el DNI a dígitos y valida el formato como ayuda de uso.
3. `POST /api/v1/pacientes`.
4. El servicio de dominio normaliza el DNI de nuevo (**la validación real es del lado del servidor**).
5. Se inserta el paciente; la base aplica `UNIQUE(dni)`.
6. Si el DNI ya existe, PostgreSQL devuelve SQLSTATE `23505`, el backend lo traduce a `409` y el frontend ofrece abrir la ficha existente.
7. Se escribe el registro de auditoría y se responde `201` con la ficha creada.

**Casos de error**
- DNI duplicado → `409` "ya existe un paciente con ese DNI".
- Fecha de nacimiento futura → `422`.
- Teléfono vacío → `422`.
- Token de `odontologo` → `403`.

**Reglas**: RN-PC-01…RN-PC-05, RN-GL-03, RN-GL-04.

---

## Flujo 3: ⚠️ Cálculo de disponibilidad

**Disparador**: la secretaria elige profesional, fecha y servicio para agendar.
**Actor**: `secretaria`.
**Por qué importa**: es el primer lugar donde se aplica el modelo de horarios. Si este cálculo acepta un horario que la base después rechaza, la secretaria pierde la confianza en el sistema.

**Pasos**
1. `GET /api/v1/disponibilidad?fecha=…&profesional_id=…&servicio_id=…`
2. El servicio resuelve la **duración efectiva**: override del profesional si existe, si no la del servicio.
3. Verifica que la fecha no sea feriado y no esté dentro de un bloqueo del profesional; si lo está, devuelve lista vacía con el motivo.
4. Toma las ventanas de `horario_laboral` del día de semana correspondiente.
5. Genera los slots alineados a la duración efectiva dentro de cada ventana.
6. Resta los turnos activos (`activo = TRUE` y estado no terminal) del rango `[inicio, fin)` de ese profesional.
7. Devuelve los slots libres con hora de inicio y fin.

```
                    ventana 08:00 ─────────────────── 18:00
                    │ 08:00 │ 08:30 │ 09:00 │ 09:30 │ 10:00 │
    generados  →    │   ○   │   ○   │   ○   │   ○   │   ○   │   (5 slots de 30 min)
    turno existente │       │       │   █   │   █   │   █   │
    disponibles  →  │   ○   │   ○   │   —   │   —   │   —   │
                                    ↑ 09:00–10:30 ocupado
```

**Casos de error**
- Sábado sin ventanas → lista vacía con motivo `"el profesional no atiende ese día"`.
- Feriado → lista vacía con motivo `"feriado"`.
- Servicio de 45 minutos sobre una ventana de 30 minutos → ningún slot, con explicación.
- El último slot termina exactamente en el fin de ventana → **sí** se incluye, porque el rango es semiabierto `[inicio, fin)`.

**Reglas**: RN-HO-01, RN-HO-03, RN-HO-05, RN-FE-02, RN-FE-03, RN-FE-05, RN-PR-02, RN-PR-03, RN-TU-03, RN-TU-09.

---

## Flujo 4: Reserva de turno (camino feliz)

**Disparador**: la secretaria confirma los datos del turno en el formulario.
**Actor**: `secretaria`.

**Pasos**
1. El frontend envía `POST /api/v1/turnos` con paciente, profesional, sillón, servicio, `inicio` y motivo opcional.
2. El servicio de dominio, **en una única transacción**:
   - resuelve la duración efectiva y calcula `fin = inicio + duración`;
   - valida que `inicio` no esté en el pasado;
   - valida que el turno entre completo en una ventana horaria;
   - valida que la fecha no sea feriado ni esté bloqueada para ese profesional;
   - valida que el sillón esté activo y que el paciente esté activo.
3. Se ejecuta el `INSERT`.
4. La base evalúa las tres restricciones de exclusión GiST (profesional, paciente, sillón). Como no hay conflicto, acepta la fila.
5. Se escribe la auditoría en la **misma transacción**.
6. Se responde `201` con el turno completo.

**Casos de error**: ver flujo 5 y flujo 6.

**Reglas**: RN-TU-01, RN-TU-02, RN-TU-03, RN-TU-07, RN-TU-08, RN-TU-11, RN-HO-03, RN-FE-03, RN-SI-04, RN-GL-04.

---

## Flujo 5: ⚠️ Reserva con conflicto — el núcleo técnico del proyecto

**Disparador**: la secretaria intenta reservar un horario ya ocupado, o dos secretarias presionan "Agendar" sobre el mismo slot en el mismo segundo.
**Actor**: `secretaria`.
**Por qué importa**: es el daño que el sistema promete eliminar (doble reserva). Si la validación viviera sólo en la aplicación, este flujo terminaría en doble reserva.

### 5.1 Conflicto detectado de forma explícita

1. El `INSERT` es rechazado por la restricción `turno_no_solape_profesional` (o `..._paciente`, o `..._sillon`).
2. PostgreSQL aborta la sentencia con `ExclusionViolation`, **SQLSTATE `23P01`**.
3. La transacción hace rollback: **no queda nada escrito a medias**, ni el turno ni la auditoría.
4. El servicio de dominio captura la excepción y la traduce:

```json
{
  "detail": "El horario ya está reservado para el profesional seleccionado.",
  "codigo": "SOLAPAMIENTO",
  "recurso": "profesional",
  "conflicto": { "inicio": "2026-10-12T14:00:00Z", "fin": "2026-10-12T14:30:00Z" }
}
```

5. El frontend muestra el mensaje y **recarga la disponibilidad** del día.

### 5.2 Carrera entre dos secretarias

```
Secretaria A                API                        PostgreSQL              Secretaria B
    │  POST 14:00            │                            │                          │
    ├───────────────────────▶│                            │                          │
    │                        │ BEGIN                     │                          │
    │                        ├───────────────────────────▶│                          │
    │                        │ INSERT turno (A)          │                          │
    │                        ├───────────────────────────▶│ GiST: sin choque        │
    │                        │ INSERT auditoria          │                          │
    │                        ├───────────────────────────▶│                          │
    │                        │ COMMIT ── bloquea ────────▶│                          │
    │◀──── 201 Created ──────┤                            │                          │
    │                        │◀──── POST 14:00 ───────────────────────────────────────────┤
    │                        │ BEGIN                     │                          │
    │                        ├───────────────────────────▶│                          │
    │                        │ INSERT turno (B)          │                          │
    │                        ├───────────────────────────▶│ GiST: conflicto         │
    │                        │ ROLLBACK (23P01)          │                          │
    │                        │                            │                          │
    │                        │── 409 SOLAPAMIENTO ────────────────────────────────────────▶│
    │                        │                            │   (frontend recarga      │
    │                        │                            │    la disponibilidad)    │
```

**Punto clave**: no hay ventana de carrera posible porque la comprobación y la inserción son **la misma operación**. El `409` lo produce la base de datos, no un `if` del código de aplicación.

**Casos de error**
- Solapamiento con otro profesional, mismo horario → `409`.
- Solapamiento del mismo paciente con otro profesional → `409` (RN-TU-06, decisión explícita del proyecto).
- Solapamiento por sillón con otro profesional → `409`.
- Todo lo anterior **deja la base en el mismo estado** que antes del intento.

**Reglas**: RN-TU-04, RN-TU-05, RN-TU-06, RN-GL-04.

---

## Flujo 6: Reglas de negocio rechazan la reserva

**Disparador**: la secretaria reserva un horario inválido por regla de negocio (no por colisión).
**Actor**: `secretaria`.

| Situación | Validación | Respuesta |
|---|---|---|
| Turno en el pasado | `inicio < now()`, contra el reloj del servidor | `422` |
| Fuera del horario laboral | El turno no cabe entero en una ventana | `422` con la ventana válida más cercana |
| En feriado | Coincidencia con `feriado` activa | `422` |
| En bloqueo del profesional | El turno cae en `[desde, hasta]` | `422` |
| Sillón inactivo | `sillon.activo = FALSE` | `422` |
| Paciente inactivo | `paciente.activo = FALSE` | `404` |
| Falta la anticipación mínima (2 h) | `inicio - now() < 2h` en cancelación/reprogramación | `422` |
| Transición de estado ilegal | Máquina de estados | `422` |
| Rol sin permiso | `odontologo` intenta reservar | `403` |

> **Distinción importante**: las validaciones de regla de negocio son `422` y ocurren **antes** del `INSERT`; el solapamiento es `409` y lo detecta la base. No es un detalle cosmético: `422` significa "tu pedido fue mal formado", `409` significa "el mundo cambió mientras lo hacías".

**Reglas**: RN-TU-02, RN-HO-03, RN-FE-03, RN-FE-05, RN-SI-04, RN-CA-03, RN-TU-07, RN-AU-04, RN-GL-05.

---

## Flujo 7: Cancelación y liberación automática del horario

**Disparador**: el paciente no puede asistir; la secretaria lo cancela.
**Actor**: `secretaria`.

**Pasos**
1. `POST /api/v1/turnos/{id}/cancelar` con motivo.
2. El servicio valida rol (`RN-CA-04`), estado actual (no terminal) y anticipación (`RN-CA-03`).
3. En una transacción: `UPDATE turno SET estado='CANCELADO', cancelado_por=…, motivo_cancelacion=… WHERE id=… AND activo=TRUE`.
4. Se inserta la auditoría.
5. **No hay nada más que hacer**: la fila sigue ocupando la tabla, pero la restricción GiST es **parcial** y su predicado es `estado NOT IN ('CANCELADO','NO_ASISTIO')`. Al cambiar el estado, la fila sale del índice de exclusión y el horario vuelve a estar libre.
6. Se responde `200` con el turno cancelado.

**Casos de error**
- Anticipación menor a 2 h → `422`, el turno sigue vigente.
- `odontologo` → `403`.
- Turno ya `completado` → `422` (estado final).
- Cancelación doble → `422`, idempotencia no garantizada a propósito: el segundo intento debe fallar, no "borrar" nada.

**Reglas**: RN-CA-01, RN-CA-03, RN-CA-04, RN-TU-07, RN-TU-09, RN-GL-04.

---

## Flujo 8: Reprogramación transaccional

**Disparador**: el paciente pide mover su turno.
**Actor**: `secretaria`.

**Pasos**
1. `POST /api/v1/turnos/{id}/reprogramar` con el nuevo `inicio` y el sillón destino opcional.
2. Validaciones: rol, anticipación, horario, feriado, sillón.
3. En **una sola transacción**:
   - `INSERT` del turno nuevo con la duración efectiva recalculada, `estado='AGENDADO'` y `origen_turno_id` apuntando al anterior;
   - `UPDATE` del turno anterior a `estado='CANCELADO'` con motivo "reprogramado";
   - auditoría de ambas operaciones.
4. `COMMIT`. Las restricciones GiST evaluan las dos filas en el mismo commit.

**Casos de error**
- Destino ocupado → `409` y **ROLLBACK completo**: el turno original sigue `AGENDADO`. Es la propiedad transaccional de RN-CA-05.
- Destino en pasado → `422`, nada cambia.
- Anticipación insuficiente → `422`, nada cambia.

**Por qué no se edita el turno en el lugar**: si se actualizara el `inicio` del mismo registro, se perdería el horario original y no habría forma de responder "¿este paciente vino el martes o el jueves?". La cadena `origen_turno_id` permite reconstruir la historia.

**Reglas**: RN-CA-02, RN-CA-03, RN-CA-04, RN-CA-05, RN-TU-05, RN-TU-06.

---

## Flujo 9: Ciclo de vida del turno

**Disparador**: se confirma la llegada del paciente.
**Actor**: `secretaria` (agenda) u `odontologo` (hecho clínico).

```
   agendado ──▶ confirmado ──▶ en_curso ──▶ completado     (final)
      │             │             │
      │             │             └──────▶ no_asistió        (final)
      ├──────┬──────┴────────────────────▶ cancelado        (final)
      ▼
  sobreturno  (estado propio, exento de no-solapamiento)
```

**Pasos**
1. `PATCH /api/v1/turnos/{id}/estado` con el estado destino.
2. El servicio valida la transición contra la tabla de RN-TU-07.
3. `UPDATE turno SET estado=…` y auditoría. Al cambiar a `cancelado` o `no_asistió`, la fila sale del índice de exclusión y el horario queda libre.
4. Se responde `200`.

**Casos de error**
- Transición ilegal (`completado` → `en_curso`) → `422`.
- Odontólogo que mueve un turno ajeno → `404`.
- Odontólogo que mueve su turno a `confirmado` → `403` (sólo se le permiten `en_curso`, `completado`, `no_asistió`).

**Reglas**: RN-TU-07, RN-TU-08, RN-TU-09, RN-GL-04.

---

## Flujo 10: Registro en el odontograma

**Disparador**: durante la atención, el odontólogo actualiza el estado de una pieza.
**Actor**: `odontologo`.

**Pasos**
1. Abre el odontograma desde el turno (`/pacientes/:id/odontograma`).
2. Selecciona la pieza (por ejemplo, la 16) y elige estado y, opcionalmente, cara.
3. `PUT /api/v1/pacientes/{id}/odontograma/16`.
4. El servicio verifica: paciente activo, odontólogo con turno no terminal de ese paciente, pieza en 11–48, estado del catálogo, cara del catálogo.
5. En una transacción:
   - `INSERT` en `odontograma` si la fila no existe, o `UPDATE` si existe;
   - `INSERT` en `odontograma_movimiento` con estado anterior (o `NULL` en la primera registración) y estado nuevo.
6. Se responde `200` con el estado actual y el historial.

**Casos de error**
- Odontólogo sin turno de ese paciente → `403`.
- Estado fuera del catálogo → `422`.
- Pieza 55 (decidua) → `422`, el MVP es sólo dentición permanente.
- Cualquier intento de subir una imagen → no hay endpoint; la interfaz ni siquiera ofrece la acción.

**Reglas**: RN-OD-01…RN-OD-09.

---

## Flujo 11: Cambio de configuración y su efecto en la agenda

**Disparador**: el admin define el horario del próximo mes.
**Actor**: `admin`.

**Pasos**
1. `PUT /api/v1/profesionales/{id}/horarios` con el conjunto completo de ventanas.
2. El servicio reemplaza todas las ventanas del profesional en una transacción (borra las anteriores e inserta las nuevas) y valida que no haya solapamientos ni domingo.
3. Auditoría.
4. **No se toca ningún turno existente**: cambiar el horario no reprograma la agenda pasada ni futura. Si un turno queda fuera del horario nuevo, sigue existiendo y la interfaz lo marca como fuera de horario.

**Por qué es una decisión y no una falta de implementación**: reprogramar en cascada los turnos que quedan fuera sería una operación en lote sobre la agenda — precisamente lo que `US-031` CA-3 descarta. Obligar a la secretaria a resolver los casos uno por uno es más lento, pero nunca destruye reservas silenciosamente.

**Casos de error**
- Ventanas solapadas del mismo día → `422`.
- Ventana en domingo → `422`.
- `hasta < desde` en un bloqueo → `422`.

**Reglas**: RN-HO-02, RN-HO-04, RN-GL-04.

---

## Flujo 12: Baja lógica y sus consecuencias

**Disparador**: la secretaria da de baja un paciente que deja de asistir, o el admin desactiva un sillón o un servicio.
**Actor**: `secretaria` (sólo paciente) o `admin`.

**Pasos**
1. `DELETE /api/v1/pacientes/{id}` o `PATCH` con `activo = FALSE` en los maestros.
2. El servicio verifica si existen turnos **no terminales**: si existen, devuelve `409` con el detalle.
3. Si no existen, `UPDATE ... SET activo = FALSE`. **No hay `DELETE`.**
4. Auditoría.
5. Los registros quedan en la base: los turnos históricos, el odontograma y el historial se conservan y se pueden consultar con fines de trazabilidad.

**Por qué no se borra nunca**: un turno borrado no se puede explicar ni auditar. La baja lógica es lo que permite responder "el mes pasado ¿este paciente tuvo tratamiento?" meses después.

**Reglas**: RN-GL-01, RN-GL-05, RN-PC-07, RN-PC-08, RN-SI-05, RN-PR-05.

---

## Mapa de flujos por riesgo técnico

| Flujo | Riesgo que concentra | Dónde se demuestra |
|---|---|---|
| 5 — Conflicto de reserva | Carrera entre dos escrituras | Test de concurrencia: una `201`, una `409` |
| 3 — Disponibilidad | Cálculo de slots sobre modelo de horarios | Agenda de un sábado vacío y de un feriado |
| 7 — Cancelación | Liberación automática sin edición manual | Cancelar y ver el slot disponible otra vez |
| 8 — Reprogramación | Atomicidad de una operación de dos filas | Reprogramar a un horario ocupado: nada cambia |
| 10 — Odontograma | Escritura con historial automático | Historial de una pieza tras dos cambios |
| 12 — Baja lógica | Conservación del histórico | Dar de baja un paciente y seguir viendo sus turnos |