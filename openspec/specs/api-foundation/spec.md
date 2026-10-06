# api-foundation Specification

## Purpose

Define el comportamiento base de la API FastAPI bajo el prefijo `/api/v1`: health check público con verificación de base, CORS con lista explícita de orígenes, documentación deshabilitada en producción y cuerpo de error consistente ante fallos no controlados.

## Requirements

### Requirement: Prefijo único de la API
Todas las rutas públicas del sistema SHALL vivir bajo el prefijo `/api/v1`; una ruta fuera de ese prefijo o inexistente SHALL responder `404`.

#### Scenario: Ruta inexistente
- **WHEN** se hace `GET /api/v1/no-existe`
- **THEN** la respuesta es `404` con cuerpo JSON

### Requirement: Health check público con chequeo de conexión
El sistema SHALL exponer `GET /api/v1/health` sin autenticación, devolviendo el estado del servicio y el resultado de la conexión a PostgreSQL.

#### Scenario: Base accesible
- **WHEN** se hace `GET /api/v1/health` con la base corriendo
- **THEN** la respuesta es `200` e indica servicio OK y conexión a la base OK

#### Scenario: Base inaccesible
- **WHEN** se hace `GET /api/v1/health` con la base caída o inalcanzable
- **THEN** la respuesta no es `200` y el cuerpo indica que la conexión a la base falló

### Requirement: CORS con lista explícita de orígenes
El sistema SHALL aceptar CORS sólo para los orígenes listados en `CORS_ORIGINS` (sin comodines) y SHALL declarar `allow_credentials=False` (la auth va por cabecera, no por cookie).

#### Scenario: Origen permitido
- **WHEN** una petición llega desde un origen incluido en `CORS_ORIGINS`
- **THEN** la respuesta incluye ese origen en `Access-Control-Allow-Origin`

#### Scenario: Origen no permitido
- **WHEN** una petición llega desde un origen distinto a los listados
- **THEN** la respuesta no otorga `Access-Control-Allow-Origin` para ese origen

### Requirement: Documentación interactiva sólo fuera de producción
El sistema SHALL servir `/docs` y `/openapi.json` cuando `ENV` distinto de `production`, y SHALL deshabilitarlos cuando `ENV=production`.

#### Scenario: Desarrollo
- **WHEN** `ENV=development`
- **THEN** `GET /docs` responde la UI de documentación

#### Scenario: Producción
- **WHEN** `ENV=production`
- **THEN** `GET /docs` y `GET /openapi.json` responden `404`

### Requirement: Clave JWT obligatoria en producción
El sistema SHALL negarse a iniciar cuando `ENV=production` y `JWT_SECRET_KEY` esté vacía o sea el valor de ejemplo documentado.

#### Scenario: Producción sin secreto real
- **WHEN** la API se inicia con `ENV=production` y `JWT_SECRET_KEY` en su valor de ejemplo
- **THEN** el arranque falla con un error explícito antes de servir peticiones

### Requirement: Fallo no controlado con cuerpo de error consistente
El sistema SHALL registrar el detalle del error en el servidor y SHALL responder ante excepciones no controladas con un cuerpo JSON con un mensaje genérico, sin exponer trazas de stack al cliente.

#### Scenario: Excepción inesperada
- **WHEN** un endpoint lanza una excepción no manejada
- **THEN** la respuesta es `500` con cuerpo JSON genérico y la traza aparece sólo en el log del servidor
