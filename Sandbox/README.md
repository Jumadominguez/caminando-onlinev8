# Sandbox - Entorno de Desarrollo Experimental

Este directorio contiene el entorno de desarrollo experimental (Sandbox) para el proyecto Caminando Online v8.

## Estructura

- **Experiments/**: Espacio para desarrollar, probar, romper y volver a intentar nuevas funcionalidades. Aquí se trabaja paso a paso en cada feature hasta que esté lista.
- **Debug/**: Ubicación para scripts, registros y herramientas de debugging. Mantén los scripts bien documentados y elimina los que ya no sean útiles.
- **prototypes/**: Etapa intermedia donde se prueba la integración de las nuevas funcionalidades con la plataforma, asegurando que no generen errores ni conflictos.
- **temps/**: Espacio para scripts de test, versiones simplificadas, alternativas y archivos temporales. Nada aquí es esencial para el funcionamiento a largo plazo.

## Flujo de Trabajo

1. **Desarrolla en Experiments/**: Crea y prueba nuevas funcionalidades aquí.
2. **Depura en Debug/**: Usa esta carpeta para resolver problemas específicos.
3. **Valida en prototypes/**: Prueba la integración antes de mover a producción.
4. **Archivos temporales en temps/**: Mantén limpio este directorio.

## Reglas Importantes

- Los archivos en `Debug/` y `temps/` están ignorados por Git.
- Los archivos en `Experiments/` y `prototypes/` se versionan para rastrear el progreso.
- Limpia periódicamente los archivos innecesarios.
- Documenta cada experimento importante.

## Referencias

Consulta `Library/instrucciones-globales.md` y `Library/sandbox.md` para más detalles sobre el flujo de trabajo.