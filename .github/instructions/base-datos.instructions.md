# Instructivo para Manejo de Base de Datos con MongoDB

Este documento proporciona guías detalladas para el manejo correcto de MongoDB en proyectos con Vibe Coding. Enfocado en conexiones seguras, arquitectura evolutiva y registro de cambios para evitar conflictos y mantener escalabilidad.

## Introducción

MongoDB es la base de datos NoSQL predeterminada para persistencia flexible de datos. Este instructivo asegura conexiones específicas, arquitectura adaptable y documentación de evoluciones. La arquitectura puede mutar durante el desarrollo, por lo que se registra cada cambio.

## Conexiones a MongoDB

### Creación de Conexiones Específicas
- **Evitar Conflictos**: Usa nombres únicos para bases de datos y conexiones. No uses nombres genéricos como "db".
- **Variables de Entorno**: Almacena credenciales en archivos `.env` (ignorados en Git). Ejemplo:
  ```
  MONGO_URI=mongodb://localhost:27017/my_project_db
  MONGO_USER=my_project_user
  MONGO_PASSWORD=secure_password
  ```
- **Conexión por Proyecto**: Crea una base de datos específica para cada proyecto. En MongoDB, las bases se crean automáticamente al insertar datos, pero configura usuarios:
  ```javascript
  // En MongoDB shell
  use admin;
  db.createUser({
    user: "my_project_user",
    pwd: "secure_password",
    roles: ["readWrite"]
  });
  ```
- **Manejo de Conexiones**: Usa drivers como `mongoose` (Node.js) o `pymongo` (Python) con pools de conexiones. Limita conexiones para evitar sobrecarga.
- **Verificación**: Antes de conectar, verifica que el puerto (default 27017) esté libre (consulta `puertos.md`).

### Seguridad
- Nunca hardcodea credenciales en código.
- Usa autenticación y SSL/TLS.
- Rota contraseñas periódicamente.

## Arquitectura de MongoDB

### Diseño Inicial
- **Análisis de Requisitos**: Basado en el mockup y funcionalidades del `proceso-creativo.md`, identifica colecciones, documentos y campos necesarios.
- **Modelado**: Crea diagramas de colecciones y relaciones embebidas/referenciadas. Define esquemas flexibles.
- **Colecciones y Documentos**: Usa colecciones en lugar de tablas. Documentos JSON-like para datos flexibles.
- **Índices**: Crea índices en campos frecuentemente consultados para rendimiento.

### Evolución y Mutaciones
- **Arquitectura Evolutiva**: La arquitectura puede cambiar durante el desarrollo. No asumas diseño final desde el inicio.
- **Iteraciones**: En `Sandbox/Experiments/`, prueba esquemas alternativos. Migra a `Sandbox/Prototypes/` para validación.
- **Registro de Cambios**: Documenta cada mutación en `Library/archivos/db-cambios.md`. Formato:
  ```
  # Cambios en Arquitectura MongoDB

  ## Fecha: [Fecha]
  ## Cambio: [Descripción, e.g., Agregar colección 'users']
  ## Razón: [Por qué se cambió]
  ## Impacto: [Colecciones afectadas, migraciones]
  ## Commit: [Número de commit]
  ```
- **Migraciones**: Usa herramientas como `migrate-mongo` (Node.js) o scripts manuales para aplicar cambios en esquemas.

### Mejores Prácticas
- **Versionado**: Incluye DB en Git, pero ignora datos sensibles.
- **Backup**: Realiza backups con `mongodump` antes de cambios.
- **Testing**: Crea DB de test separadas (e.g., `my_project_test`).
- **Escalabilidad**: Diseña para crecimiento (e.g., sharding, agregaciones).

## Flujo de Trabajo

1. **Planificación**: Basado en `cuestionario-inicial.md`, define requisitos iniciales.
2. **Diseño**: Crea esquema inicial en `Sandbox/Experiments/`.
3. **Implementación**: Genera código de conexión y modelos con Mongoose/PyMongo.
4. **Evolución**: Registra cambios en `db-cambios.md` y aplica migraciones.
5. **Validación**: Prueba en `Sandbox/Prototypes/`.
6. **Integración**: Mueve a producción, actualizando `puertos.md` si es necesario.

## Referencias

- Consulta `puertos.md` para asignación de puertos DB.
- Integra con `proceso-creativo.md` para alineación con frontend.
- Registra en `registro-archivos.md` archivos relacionados con DB.

Este instructivo asegura un manejo seguro y adaptable de MongoDB. Actualiza según evolucione el proyecto.
