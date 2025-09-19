# Glosario de Términos

Este documento define términos clave utilizados en el proceso de desarrollo para evitar confusiones y asegurar una comunicación clara con la IA o colaboradores.

- **Sandbox**: Entorno de desarrollo principal donde se experimenta, prueba y valida nuevas funcionalidades antes de integrarlas al proyecto final. Incluye subcarpetas como Experiments, Debug, prototypes y temps.

- **Experiments**: Carpeta dentro de Sandbox para desarrollar y probar features paso a paso, documentando intentos, errores y aprendizajes.

- **Debug**: Carpeta para scripts, registros y herramientas de diagnóstico para resolver problemas específicos.

- **Prototypes**: Etapa intermedia donde se prueba la integración de features con la plataforma, asegurando compatibilidad antes de la aprobación final.

- **Temps**: Carpeta para archivos temporales, scripts de test y versiones simplificadas que no son esenciales a largo plazo.

- **Vibe Coding**: Enfoque de desarrollo intuitivo y creativo, utilizando IA para prototipar, iterar y refinar código de manera fluida, priorizando el flujo y la experimentación sobre procesos rígidos.

- **Feature**: Una funcionalidad o componente específico del proyecto, como una nueva sección, herramienta o mejora.

- **Backend**: Parte del proyecto que maneja la lógica del servidor, bases de datos y APIs.

- **Frontend**: Parte del proyecto que maneja la interfaz de usuario, diseño y experiencia del cliente.

- **Entorno Virtual**: Ambiente aislado para dependencias de un proyecto, como virtualenv en Python o node_modules en Node.js, para evitar conflictos.

- **Gitignore**: Archivo que especifica qué archivos o carpetas deben ignorarse en el control de versiones Git, como entornos virtuales, archivos temporales y Sandbox.

- **Proceso.md**: Documento que registra el paso a paso de las fases y tareas desarrolladas después de aprobar una feature en prototypes.

- **Desglose de Archivos**: Documentación individual en markdown para cada archivo incorporado, detallando su propósito, relaciones con otros archivos y cómo recrear el desarrollo.

## Regla de Nombres en Inglés

Para mantener coherencia y facilitar la colaboración internacional, todos los nombres de archivos, variables, funciones, clases, colecciones de bases de datos, rutas de API, etc., deben estar en inglés. Los mensajes de commit pueden permanecer en español para comodidad personal. Esto incluye:

- Nombres de archivos: `user_model.py` en lugar de `modelo_usuario.py`.
- Variables: `user_name` en lugar de `nombre_usuario`.
- Colecciones DB: `users` en lugar de `usuarios`.
- Funciones: `get_user_data()` en lugar de `obtener_datos_usuario()`.
- Clases: `UserManager` en lugar de `GestorUsuario`.
- Comentarios y documentación: Preferiblemente en inglés, salvo excepciones justificadas.

Si el usuario se refiere a algo en español, la IA debe traducirlo automáticamente al inglés para el código o archivos. Registrar aquí cualquier traducción necesaria para referencia futura.

Ejemplos de traducciones comunes:
- Usuario → User
- Producto → Product
- Pedido → Order
- Carrito → Cart
- Pago → Payment
- Configuración → Settings
- Autenticación → Authentication
- Base de Datos → Database
