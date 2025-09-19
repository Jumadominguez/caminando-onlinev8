# Proceso Creativo y de Desarrollo

Este documento describe mi enfoque personal para el desarrollo de proyectos, enfocado en un proceso visual y creativo. Como no soy desarrollador profesional y soy una persona visual, priorizo la visualización antes de la implementación técnica. La IA debe seguir este proceso para guiar el desarrollo de manera alineada con mi estilo.

## Filosofía General

- **Enfoque Visual Primero**: Creo mockups y prototipos visuales con el esqueleto de la plataforma para conceptualizar la interfaz y la experiencia del usuario antes de escribir código.
- **Iteración Progresiva**: Desarrollo en fases: visualización → funcionalidad → estilos.
- **Integración Modular**: Mantengo archivos pequeños y modulares para facilitar cambios.
- **Uso de Sandbox**: Experimento en `Sandbox/Experiments/` y valido en `Sandbox/Prototypes/`.

## Pasos del Proceso

### 1. Conceptualización y Planificación Visual
- **Objetivo**: Definir la visión general del proyecto a través de elementos visuales.
- **Actividades**:
  - Crear wireframes o bocetos en papel/digital para la interfaz.
  - Identificar elementos clave: botones, formularios, navegación, layouts.
  - Definir relaciones entre elementos (e.g., flujo de navegación).
- **Herramientas**: Usar herramientas como Figma, Canva o incluso dibujos simples.
- **Rol de la IA**: Ayudar a generar descripciones detalladas de mockups basados en mis ideas, o sugerir mejoras visuales. No generar código aún.

### 2. Desarrollo del Mockup Visual del Frontend
- **Objetivo**: Crear un esqueleto funcional básico del frontend sin estilos finales.
- **Actividades**:
  - Diseñar layouts y posiciones de elementos (estructura básica).
  - Incluir placeholders para contenido dinámico (e.g., datos de backend).
  - Asegurar funcionalidad básica y navegación, sin colores o diseños avanzados.
- **Resultado**: Un mockup funcional que muestre la estructura y flujo, listo para integración con backend.
- **Rol de la IA**: Generar código HTML limpio sin estilos inline. Crear un archivo CSS separado básico para estructura mínima (e.g., layouts, posiciones), pero no colores o diseños avanzados. Asegurar modularidad para fácil reemplazo en el paso 5. Usar `Sandbox/Experiments/` para iteraciones.

### 3. Desarrollo del Backend
- **Objetivo**: Implementar la lógica y APIs para que el frontend funcione.
- **Actividades**:
  - Basado en el mockup, definir endpoints, bases de datos y lógica.
  - Crear archivos modulares para backend (e.g., rutas, modelos, utilidades).
  - Integrar con el mockup para probar funcionalidad.
- **Resultado**: Backend funcional que soporta el frontend.
- **Rol de la IA**: Generar código backend directamente, siguiendo estructura modular. Usar `Sandbox/Prototypes/` para integración.

### 4. Integración Frontend-Backend
- **Objetivo**: Conectar el frontend con el backend para funcionalidad completa.
- **Actividades**:
  - Reemplazar placeholders con datos reales.
  - Probar interacciones (e.g., formularios, navegación).
  - Validar en `Sandbox/Prototypes/`.
- **Resultado**: Aplicación funcional sin estilos finales.
- **Rol de la IA**: Ayudar en debugging y ajustes de integración. Documentar en `proceso.md`.

### 5. Desarrollo de Estilos y Pulido
- **Objetivo**: Aplicar estilos finales para una experiencia visual pulida.
- **Actividades**:
  - Diseñar CSS avanzado, animaciones y temas.
  - Asegurar consistencia y accesibilidad.
  - Optimizar para diferentes dispositivos.
- **Resultado**: Producto final listo.
- **Rol de la IA**: Generar estilos CSS/JS para UI, pero solo después de funcionalidad completa.

## Reglas para la IA

- **No Anticipar Fases**: No generar backend o estilos hasta que el mockup esté aprobado.
- **Mantener Modularidad**: Crear archivos pequeños y documentar en `registro-archivos.md`.
- **Usar Checkpoints**: Commit con `[CHECKPOINT-XXX]` en cada fase.
- **Preguntar si Necesario**: Si algo no está claro en el mockup, pedir aclaraciones visuales.
- **Referencias**: Consultar `sandbox.md` para experimentación, `puertos.md` para servidores.

## Ejemplo de Flujo

1. Idea: "Quiero una app de tareas."
2. Mockup: Crear wireframe con lista de tareas, botones de agregar/editar.
3. Backend: Implementar API para CRUD de tareas.
4. Integración: Conectar frontend a API.
5. Estilos: Aplicar colores, fuentes y animaciones.

Este proceso asegura que el desarrollo sea intuitivo y visualmente guiado. Actualiza este documento si cambian mis preferencias.
