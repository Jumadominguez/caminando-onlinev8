# Guía de Seguridad Informática para Desarrollo

Este documento establece protocolos exhaustivos para prevenir vulnerabilidades de seguridad en el desarrollo de plataformas que manejan datos sensibles (personales, registros, pagos, bancarios, tarjetas de crédito). Como experto en ciberseguridad, detallo riesgos comunes, medidas preventivas y mejores prácticas para elevar la seguridad al máximo, con ejemplos prácticos y herramientas específicas. Basado en estándares como OWASP Top 10, NIST y PCI DSS.

## Introducción

La seguridad no es opcional; es fundamental. Una brecha puede exponer datos sensibles, causar pérdidas financieras y dañar la reputación. Esta guía cubre desarrollo seguro desde el inicio, integrando seguridad en cada fase del `proceso-creativo.md` y `instrucciones-globales.md`.

## Principios Generales de Seguridad

- **Defense in Depth**: Múltiples capas de protección (red, aplicación, datos).
- **Least Privilege**: Otorga solo permisos necesarios.
- **Fail-Safe Defaults**: Asume lo peor; deniega por defecto.
- **Zero Trust**: Verifica todo, siempre.
- **Principio de Responsabilidad Compartida**: Desarrollador, infraestructura y usuario contribuyen.

**Ejemplo Práctico en Node.js con Express**:
```javascript
const express = require('express');
const helmet = require('helmet');
const rateLimit = require('express-rate-limit');

const app = express();

// Aplicar headers de seguridad
app.use(helmet({
  contentSecurityPolicy: {
    directives: {
      defaultSrc: ["'self'"],
      scriptSrc: ["'self'", "'unsafe-inline'"],
      styleSrc: ["'self'", "'unsafe-inline'"],
    },
  },
}));

// Limitar tasa de solicitudes para prevenir ataques DDoS
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutos
  max: 100, // límite de 100 solicitudes por IP
});
app.use(limiter);

// Middleware de autenticación
app.use((req, res, next) => {
  // Verificar token JWT aquí
  next();
});
```

## Vulnerabilidades Comunes y Prevención

### 1. Inyección (Injection)
- **Descripción**: Ataques como NoSQL Injection en MongoDB, donde inputs maliciosos alteran queries.
- **Riesgo**: Exposición de datos sensibles.
- **Prevención**:
  - Usa prepared statements o ORM (e.g., Mongoose en Node.js).
  - Valida y sanitiza inputs con librerías como `validator.js`.
  - Evita concatenar strings en queries: `db.collection.find({$where: input})` → usa `db.collection.find({field: input})` con validación.

### 2. Cross-Site Scripting (XSS)
- **Descripción**: Código malicioso inyectado en páginas web.
- **Riesgo**: Robo de sesiones, datos.
- **Prevención**:
  - Escapa outputs: Usa `DOMPurify` o frameworks que auto-escapen (React, Vue).
  - Configura Content Security Policy (CSP): `<meta http-equiv="Content-Security-Policy" content="default-src 'self'">`.
  - Valida inputs en frontend y backend.

### 3. Cross-Site Request Forgery (CSRF)
- **Descripción**: Ataques que hacen requests no autorizados en nombre del usuario.
- **Riesgo**: Cambios no autorizados (e.g., transferencias).
- **Prevención**:
  - Usa tokens CSRF en formularios (e.g., `csurf` en Express).
  - Verifica origen de requests (SameSite cookies).
  - Implementa Same-Origin Policy estricta.

### 4. Broken Authentication
- **Descripción**: Sesiones débiles o credenciales expuestas.
- **Riesgo**: Acceso no autorizado a cuentas.
- **Prevención**:
  - Usa JWT con expiración corta y refresh tokens.
  - Implementa rate limiting (e.g., `express-rate-limit`).
  - Almacena hashes seguros (bcrypt, Argon2) para passwords.
  - Multi-factor authentication (MFA) para accesos sensibles.

**Ejemplo de Hashing Seguro en Node.js**:
```javascript
const bcrypt = require('bcrypt');

// Hashing de password al registrar usuario
async function hashPassword(password) {
  const saltRounds = 12; // Recomendado: 10-14
  const hashedPassword = await bcrypt.hash(password, saltRounds);
  return hashedPassword;
}

// Verificación de password al login
async function verifyPassword(password, hashedPassword) {
  const isValid = await bcrypt.compare(password, hashedPassword);
  return isValid;
}
```

### 5. Sensitive Data Exposure
- **Descripción**: Exposición de datos sensibles en tránsito o almacenamiento.
- **Riesgo**: Robo de tarjetas, datos personales.
- **Prevención**:
  - Encripta datos en reposo (MongoDB con encryption at rest).
  - Usa HTTPS/TLS 1.3 siempre.
  - Tokeniza datos sensibles (e.g., PCI DSS para tarjetas).
  - No logs datos sensibles; usa masking.

### 6. XML External Entity (XXE) / Deserialización Insegura
- **Descripción**: Procesamiento inseguro de XML/JSON.
- **Riesgo**: Ejecución remota de código.
- **Prevención**:
  - Deshabilita entidades externas en parsers XML.
  - Usa deserialización segura (e.g., limita tipos en JSON.parse).
  - Valida esquemas con Joi o similar.

### 7. Broken Access Control
- **Descripción**: Acceso a recursos sin autorización.
- **Riesgo**: Lectura/escritura no autorizada.
- **Prevención**:
  - Implementa RBAC (Role-Based Access Control).
  - Verifica permisos en cada endpoint (middleware).
  - Usa JWT con claims de roles.

### 8. Security Misconfiguration
- **Descripción**: Configuraciones por defecto o expuestas.
- **Riesgo**: Exposición de servicios.
- **Prevención**:
  - Deshabilita debug en producción.
  - Configura firewalls (e.g., MongoDB bind_ip).
  - Usa herramientas como `helmet` en Express para headers seguros.

### 9. Insufficient Logging & Monitoring
- **Descripción**: Falta de logs para detectar ataques.
- **Riesgo**: Ataques no detectados.
- **Prevención**:
  - Log eventos críticos (login, pagos) sin datos sensibles.
  - Usa herramientas como Winston o ELK stack.
  - Monitorea con alertas (e.g., fail2ban para brute force).

### 10. Using Components with Known Vulnerabilities
- **Descripción**: Dependencias obsoletas.
- **Riesgo**: Explotación de CVEs.
- **Prevención**:
  - Escanea con `npm audit`, `snyk` o `OWASP Dependency-Check`.
  - Actualiza regularmente; usa versiones LTS.
  - Audita supply chain.

## Seguridad por Capa

### Frontend
- Valida inputs en cliente y servidor.
- Usa HTTPS; evita mixed content.
- Implementa CSP y HSTS.

### Backend
- Autentica y autoriza requests.
- Limita rate; usa WAF (Web Application Firewall).
- Encripta comunicaciones.

### Base de Datos (MongoDB)
- Autentica conexiones.
- Encripta datos sensibles.
- Limita queries con aggregation pipelines seguros.
- Backup encriptado.

### Infraestructura
- Usa contenedores seguros (Docker con user no-root).
- Configura VPC, firewalls.
- Monitorea con SIEM (e.g., Splunk).

## Manejo de Datos Sensibles

- **Pagos y Tarjetas**: Cumple PCI DSS; usa gateways como Stripe con tokenización.
- **Datos Personales**: GDPR/CCPA compliance; minimiza colección.
- **Encriptación**: AES-256 para datos; TLS para tránsito.
- **Anonimización**: Para logs y analytics.

## Pruebas de Seguridad

- **Desarrollo**: Code reviews con checklists OWASP.
- **Testing**: Usa ZAP, Burp Suite para scans.
- **Penetration Testing**: Contrata expertos o usa herramientas automatizadas.
- **CI/CD**: Integra SAST/DAST en pipelines.

## Respuesta a Incidentes

- **Plan**: Define roles, comunicación, contención.
- **Herramientas**: Usa incident response frameworks (NIST).
- **Post-Mortem**: Analiza y mejora.

## Herramientas Recomendadas

- **OWASP ZAP**: Proxy de interceptación para testing de vulnerabilidades web. Escanea automáticamente XSS, SQLi, etc. Uso: `zap.sh` para iniciar, configura proxy en navegador.
- **Burp Suite**: Suite completa para pentesting. Community edition gratis; incluye scanner, repeater, intruder. Ideal para análisis manual de requests.
- **fail2ban**: Monitorea logs y bloquea IPs maliciosas. Configura jails para SSH, HTTP. Ejemplo: `sudo apt install fail2ban; sudo systemctl enable fail2ban`.
- **Wireshark**: Analiza tráfico de red para detectar fugas de datos. Filtra por protocolo (e.g., TLS).
- **SonarQube**: SAST para detectar vulnerabilidades en código. Integra en CI/CD.
- **Dependency-Check**: Escanea dependencias por CVEs conocidas (OWASP).
- **bcrypt/Argon2**: Librerías para hashing seguro de passwords.
- **Helmet**: Middleware para headers de seguridad en Express.
- **express-rate-limit**: Limita requests para prevenir DDoS.

## Integración con Vibe Coding

- En `Sandbox/Experiments/`, prueba vulnerabilidades.
- Registra en `registro-archivos.md` archivos de seguridad.
- Consulta `base-datos.md` para DB segura.
- La IA debe estar alerta a potenciales fallas de seguridad o datos sensibles no contemplados inicialmente, y los incorpore al documento de manera proactiva.

## Referencias

- OWASP Top 10.
- NIST Cybersecurity Framework.
- PCI DSS para pagos.

Esta guía es exhaustiva; revísala periódicamente. Seguridad es un proceso continuo.
