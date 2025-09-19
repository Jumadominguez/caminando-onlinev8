# Guía de Uso del Sandbox

El entorno `Sandbox` es nuestra mesa de trabajo principal para el desarrollo de la plataforma web. Aquí se organiza el flujo de trabajo y la experimentación de nuevas funcionalidades, herramientas y secciones antes de su integración final. La estructura recomendada es la siguiente:

## Estructura de Carpetas

- **Experiments**: Espacio para desarrollar, probar, romper y volver a intentar. Aquí se trabaja paso a paso en cada feature, sección o herramienta hasta que esté lista. Documenta los intentos, errores y aprendizajes para futuras referencias.

- **Debug**: Ubicación para scripts, registros y tareas de debugging. Utiliza esta carpeta para aislar y resolver problemas, registrar logs y crear herramientas de diagnóstico. Mantén los scripts bien documentados y elimina los que ya no sean útiles.

- **prototypes**: Etapa intermedia entre experiments y el entorno final. Aquí se prueba la integración de las nuevas funcionalidades con la plataforma, asegurando que no generen errores ni conflictos. Solo lo que esté aprobado y validado pasa a la plataforma final.

- **temps**: Espacio para scripts de test, versiones simplificadas, alternativas y archivos temporales como reportes de debug. Nada en esta carpeta es esencial para el funcionamiento a largo plazo; limpia periódicamente los archivos innecesarios.

## Buenas Prácticas

- Mantén una documentación clara de cada experimento, prototipo y script de debugging.
- Utiliza nombres descriptivos para los archivos y carpetas.
- Elimina archivos temporales y obsoletos regularmente.
- Documenta los resultados y aprendizajes en `Library` para mantener un registro ordenado.
- Antes de mover una feature a `prototypes`, asegúrate de que esté bien probada en `experiments`.
- Solo tras la validación en `prototypes`, integra la feature en la plataforma final.

## Proceso de Trabajo

1. Desarrolla y prueba en `Experiments`.
2. Si la solución funciona, trasládala a `prototypes` para pruebas de integración.
3. Usa siempre `Debug` para resolver problemas y registrar logs.
4. Utiliza `temps` para archivos temporales y pruebas rápidas.
5. Documenta cada paso relevante en la carpeta `docs`.

Esta estructura permite mantener el desarrollo ordenado, facilitar la colaboración y asegurar la calidad antes de la integración final. Si tienes dudas o necesitas agregar nuevas reglas, actualiza este documento.

## Integración con Instrucciones Globales

- Después de validar en `prototypes`, sigue las instrucciones en `instrucciones-globales.md` para documentar archivos y actualizar `proceso.md`.
- Usa `Library/` para almacenar documentación relacionada con experiments y prototypes.
- Mantén sincronizado con el glosario en `glosario.md` para términos clave.
