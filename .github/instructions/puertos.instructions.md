# Registro de Puertos para Desarrollo

Este documento registra el uso correcto de puertos en el proyecto para evitar interferencias durante el desarrollo. Cada aplicación que requiera un puerto debe tener uno asignado de manera organizada. Antes de asignar o usar un puerto, verifica que no esté en uso en el sistema (e.g., usando `netstat` o herramientas similares).

## 🚀 Puertos Activos

| Puerto | Servicio | Ubicación | Estado | Descripción |
|--------|----------|-----------|--------|-------------|
| X000 | Frontend Producción | `src/frontend/` | ✅ Activo | Interfaz de usuario principal (e.g., Next.js, React) |
| Y000 | Backend Producción | `src/backend/` | ✅ Activo | API REST principal (e.g., Express.js, Flask) |
| X100 | Frontend Prototypes | `Sandbox/prototypes/` | ✅ Activo | Interfaz para prototipos y pruebas de integración |
| X800 | Frontend Experiments | `Sandbox/experiments/` | ✅ Activo | Interfaz para experimentos y desarrollo inicial |
| Y010 | Backend Experiments | `Sandbox/experiments/` | ✅ Activo | API para pruebas en experiments |
| Z000 | Debugging Temporal | `Sandbox/debug/` | ⚠️ Temporal | Puerto para debugging y resolución de errores |

*Nota: Reemplaza X, Y, Z con números asignados por la IA al configurar el proyecto (e.g., X=3 para 3000, Y=5 para 5000). Actualiza esta tabla a medida que se agreguen nuevos servicios.*

## 📝 Notas de Uso

- **Puerto X000**: Frontend de producción (principal y fijo, e.g., 3000 para Next.js).
- **Puerto Y000**: Backend de producción (principal y fijo, e.g., 5000 para API Express.js).
- **Puerto X100**: Frontend en `Sandbox/prototypes` (para pruebas de integración).
- **Rango X800-X899**: Reservado para desarrollos en `Sandbox/experiments` (frontend y servicios relacionados).
- **Rango X900-X999**: Reservado para desarrollos en `Sandbox/prototypes` (adicionales si es necesario).
- **Rango X000-X799**: Reservado para servicios frontend (excepto X000 que es principal).
- **Rango Y000-Y099**: Reservado para servicios backend/API (excepto Y000 que es principal).
- **Rango Z000-Z200**: Reservado para tests y debugging temporal.

### Reglas Generales
- **Asignación**: La IA asignará números específicos a X, Y, Z al crear la estructura del proyecto, basándose en disponibilidad.
- **Verificación**: Antes de usar un puerto, ejecuta `netstat -ano | findstr :PUERTO` (en Windows) para confirmar que no esté ocupado.
- **Debugging**: Si necesitas un puerto alternativo para solucionar errores, usa uno en el rango Z000-Z200. Una vez resuelto, libera el puerto de debugging y regresa al asignado.
- **Actualización**: Mantén esta tabla actualizada con cada nuevo servicio o cambio. Registra en `proceso.md` cualquier modificación.
- **Conflictos**: Si hay un conflicto, elige un puerto libre dentro del rango correspondiente y documenta el cambio.

Este sistema asegura un desarrollo ordenado y sin interferencias. Consulta este archivo antes de iniciar cualquier servidor o servicio.
