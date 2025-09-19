# Registro de Puertos para Desarrollo

Este documento registra el uso correcto de puertos en el proyecto para evitar interferencias durante el desarrollo. Cada aplicación que requiera un puerto debe tener uno asignado de manera organizada. Antes de asignar o usar un puerto, verifica que no esté en uso en el sistema (e.g., usando `netstat` o herramientas similares).

## 🚀 Puertos Activos

| Puerto | Servicio | Ubicación | Estado | Descripción |
|--------|----------|-----------|--------|-------------|
| 3000 | Frontend Producción | `frontend/` | ✅ Activo | Interfaz de usuario principal (React con TypeScript/SCSS) |
| 5000 | Backend Producción | `backend/` | ✅ Activo | API REST principal (Express.js con MongoDB) |
| 27017 | MongoDB | Local | ✅ Activo | Base de datos MongoDB local |
| 3100 | Frontend Prototypes | `Sandbox/prototypes/` | 📋 Pendiente | Interfaz para prototipos y pruebas de integración |
| 3800 | Frontend Experiments | `Sandbox/experiments/` | 📋 Pendiente | Interfaz para experimentos y desarrollo inicial |
| 5010 | Backend Experiments | `Sandbox/experiments/` | 📋 Pendiente | API para pruebas en experiments |
| 9000 | Debugging Temporal | `Sandbox/debug/` | ⚠️ Temporal | Puerto para debugging y resolución de errores |

*Nota: Puertos asignados basados en estándares y disponibilidad. Actualiza esta tabla a medida que se agreguen nuevos servicios.*

## 📝 Notas de Uso

- **Puerto 3000**: Frontend de producción (principal y fijo para React).
- **Puerto 5000**: Backend de producción (principal y fijo para API Express.js).
- **Puerto 27017**: MongoDB local (default, verificar si está libre).
- **Puerto 3100**: Frontend en `Sandbox/prototypes` (para pruebas de integración).
- **Rango 3800-3899**: Reservado para desarrollos en `Sandbox/experiments` (frontend y servicios relacionados).
- **Rango 3900-3999**: Reservado para desarrollos en `Sandbox/prototypes` (adicionales si es necesario).
- **Rango 3000-3799**: Reservado para servicios frontend (excepto 3000 que es principal).
- **Rango 5000-5099**: Reservado para servicios backend/API (excepto 5000 que es principal).
- **Rango 9000-9200**: Reservado para tests y debugging temporal.

### Reglas Generales
- **Asignación**: Puertos asignados siguiendo convenciones estándar (3000 para React, 5000 para APIs).
- **Verificación**: Antes de usar un puerto, ejecuta `lsof -i :PUERTO` (en macOS) o `netstat -ano | findstr :PUERTO` (en Windows) para confirmar que no esté ocupado.
- **Debugging**: Si necesitas un puerto alternativo para solucionar errores, usa uno en el rango 9000-9200. Una vez resuelto, libera el puerto de debugging y regresa al asignado.
- **Actualización**: Mantén esta tabla actualizada con cada nuevo servicio o cambio. Registra en `proceso.md` cualquier modificación.
- **Conflictos**: Si hay un conflicto, elige un puerto libre dentro del rango correspondiente y documenta el cambio.

Este sistema asegura un desarrollo ordenado y sin interferencias. Consulta este archivo antes de iniciar cualquier servidor o servicio.
