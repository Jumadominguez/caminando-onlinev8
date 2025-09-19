# Instrucciones de Inicio para Proyectos con Vibe Coding

Estas instrucciones permiten iniciar cualquier proyecto de manera ordenada y eficiente. Sigue estos pasos para configurar la estructura base. Una IA puede recrear esto leyendo este archivo.

## Pasos para Configurar la Estructura Base

1. **Crear Estructura de Carpetas Principal**:
   - Crear carpeta raíz del proyecto, e.g., `mi-proyecto/`.
   - Dentro, crear subcarpetas: `src/backend/`, `src/frontend/`, `Library/`, `tests/`.

2. **Configurar Entorno de Sandbox**:
   - Crear carpeta `Sandbox/` en la raíz.
   - Dentro de `Sandbox/`, crear: `Experiments/`, `Debug/`, `prototypes/`, `temps/`.
   - Copiar `sandbox.md` a `Sandbox/` para referencia.

3. **Cuestionario Inicial**:
   - Lee el `cuestionario-inicial.md` con respuestas detalladas.

4. **Configurar Entorno Virtual (Dependiendo del Lenguaje)**:
   - Basado en las respuestas del cuestionario, configurar el entorno adecuado.
   - **Para Python**: Ejecutar `python -m venv venv` en la raíz. Activar con `venv\Scripts\activate` (Windows).
   - **Para Node.js**: Ejecutar `npm init -y` en `src/frontend/`. Instalar dependencias globales si necesario.
   - **Para Otros Lenguajes**: Crear entorno virtual apropiado, e.g., `virtualenv` o contenedores.

5. **Iniciar Control de Versiones**:
   - Ejecutar `git init` en la raíz.
   - Crear `.gitignore` con:
     ```
     Sandbox/Debug/
     Sandbox/Temps/
     venv/
     node_modules/
     __pycache__/
     *.log
     tests/
     .env
     ```
   - Conectar a GitHub: Crear repositorio en GitHub, agregar remote con `git remote add origin <url>`, commit inicial.

6. **Instalar Dependencias Básicas**:
   - Basado en las respuestas del cuestionario, instalar frameworks y librerías.
   - Backend: Instalar frameworks como Flask/Django (Python), Express (Node.js).
   - Frontend: Instalar React/Vue/Angular.
   - Usar gestores de paquetes: `pip install` o `npm install`.

7. **Configurar Archivos Base**:
   - Basado en las respuestas del cuestionario, crear archivos iniciales.
   - Backend: Crear `src/backend/app.py` o equivalente con estructura básica.
   - Frontend: Crear `src/frontend/index.html`, `app.js`, etc.
   - Copiar `instrucciones-globales.md`, `glosario.md`, `puertos.md` a `Library/`.

8. **Verificar Setup**:
   - Ejecutar comandos básicos para confirmar funcionamiento, e.g., `python app.py` o `npm start`.
   - Verificar puertos asignados en `puertos.md` antes de iniciar servidores para evitar conflictos.

Siguiendo estos pasos, la estructura base estará lista para desarrollo. Consulta `cuestionario-inicial.md` para el cuestionario completo.
