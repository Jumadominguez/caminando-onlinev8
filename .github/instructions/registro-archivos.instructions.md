# Registro de Archivos y Dependencias

Este documento registra las descripciones de cada archivo en el proyecto, incluyendo su propósito, ubicación y relaciones/dependencias con otros archivos. Manténlo actualizado para facilitar la navegación y modificaciones.

## Tabla de Archivos

| Archivo | Ubicación | Descripción | Dependencias | Última Modificación |
|---------|-----------|-------------|--------------|---------------------|
| instrucciones-globales.md | Library/ | Define reglas globales para desarrollo con Vibe Coding. | glosario.md, sandbox.md | [Fecha] |
| instrucciones-inicio.md | Library/ | Guía paso a paso para iniciar proyectos. | cuestionario-inicial.md, puertos.md | [Fecha] |
| sandbox.md | Library/ | Explica el uso del entorno Sandbox. | instrucciones-globales.md | [Fecha] |
| glosario.md | Library/ | Definiciones de términos clave. | Ninguna | [Fecha] |
| cuestionario-inicial.md | Library/ | Cuestionario para recopilar info inicial. | instrucciones-inicio.md | [Fecha] |
| puertos.md | Library/ | Registro de puertos asignados. | instrucciones-globales.md | [Fecha] |
| guia-uso.md | Library/ | Guía para usar los documentos. | Todos los .md | [Fecha] |
| github-instrucciones.md | Library/ | Instrucciones para Git y GitHub. | instrucciones-globales.md | [Fecha] |
| seguridad.md | Library/ | Guía de seguridad informática para prevenir vulnerabilidades. | instrucciones-globales.md, base-datos.md | [Fecha] |
| base-datos.md | Library/ | Instructivo para manejo de bases de datos. | puertos.md, proceso-creativo.md | [Fecha] |
| proceso-creativo.md | Library/ | Describe el proceso visual y creativo de desarrollo. | sandbox.md, instrucciones-globales.md | [Fecha] |
| registro-archivos.md | Library/ | Registro de archivos y dependencias. | Todos los archivos del proyecto | [Fecha] |
| roles-ia.md | Library/ | Define los roles que la IA debe asumir en diferentes situaciones. | instrucciones-globales.md, proceso-creativo.md, seguridad.md | 2025-09-09 |

## Instrucciones de Uso

- **Actualización**: Agrega una fila por cada nuevo archivo creado. Incluye descripción breve, dependencias (archivos que usa o que lo usan) y fecha.
- **Dependencias**: Lista archivos relacionados, e.g., "Depende de utils.py para funciones auxiliares".
- **Búsqueda**: Usa esta tabla para identificar archivos rápidamente antes de modificaciones.
- **Mantenimiento**: Actualiza al crear, modificar o eliminar archivos. Registra en commits como `[DOC-XXX] Actualizar registro-archivos.md`.

Este registro asegura una estructura modular y clara, facilitando el trabajo con la IA.
