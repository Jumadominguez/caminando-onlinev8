# Jumbo Scraper Scripts

Este directorio contiene los scripts de scraping para el supermercado Jumbo Argentina, adaptados para su sistema de navegación basado en hover menus.

## 📋 Descripción General

Los scripts replican la funcionalidad del scraper de Carrefour pero están adaptados para las particularidades de Jumbo:

- **Navegación por hover**: Jumbo usa menús desplegables que aparecen al pasar el mouse, en lugar de clics como Carrefour
- **Base de datos separada**: Usa la base de datos `jumbo` en MongoDB
- **URLs específicas**: Apunta a `jumbo.com.ar`
- **Estructura similar**: Mantiene la arquitectura de 4 pasos del scraper original

## 🗂️ Estructura de Archivos

```
jumbo/
├── jumbo_step1_supermarket.py      # Extrae información del supermercado
├── jumbo_step2_categories.py       # Extrae categorías usando hover
├── jumbo_step3_subcategory.py      # Extrae subcategorías de páginas de categorías
├── jumbo_step4_producttypes.py     # Extrae tipos de productos de subcategorías
├── jumbo_master_scraper.py         # Script maestro para ejecutar todos los pasos
├── proceso-desarrollo-jumbo.md     # Documentación del proceso de desarrollo
└── README.md                       # Este archivo
```

## 🚀 Uso

### Requisitos Previos

1. **Python 3.8+**
2. **MongoDB** corriendo en localhost:27017
3. **Firefox** instalado
4. **GeckoDriver** (se incluye en el directorio raíz del proyecto)
5. **Dependencias Python**:
   ```bash
   pip install selenium pymongo beautifulsoup4 requests
   ```

### Ejecutar Todos los Pasos

```bash
# Ejecutar todos los pasos en secuencia
python jumbo_master_scraper.py --all

# Ejecutar en modo background (headless, para pasos 2-4)
python jumbo_master_scraper.py --all --background
```

### Ejecutar Paso Individual

```bash
# Ejecutar solo el paso 1
python jumbo_master_scraper.py --step=1

# Ejecutar el paso 2 en background
python jumbo_master_scraper.py --step=2 --background
```

## 📊 Pasos del Proceso

### Paso 1: Información del Supermercado (`jumbo_step1_supermarket.py`)
- **Objetivo**: Extraer información básica del supermercado
- **URL**: https://www.jumbo.com.ar
- **Datos extraídos**:
  - Nombre: "Jumbo Argentina"
  - URL principal
  - País: Argentina
  - Información de contacto (si disponible)
- **Base de datos**: Guarda en colección `supermarket`

### Paso 2: Categorías (`jumbo_step2_categories.py`)
- **Objetivo**: Extraer categorías principales usando navegación por hover
- **Método**: ActionChains para simular movimiento del mouse
- **Datos extraídos**:
  - Nombre de categoría
  - URL de categoría
  - Slug para identificadores
  - Subcategorías (si están disponibles en el hover menu)
- **Base de datos**: Guarda en colección `categories`

### Paso 3: Subcategorías (`jumbo_step3_subcategory.py`)
- **Objetivo**: Navegar a cada página de categoría y extraer subcategorías
- **Método**: Visita cada URL de categoría y busca elementos de filtro/subcategoría
- **Datos extraídos**:
  - Nombre de subcategoría
  - URL de subcategoría
  - Relación con categoría padre
- **Base de datos**: Guarda en colección `subcategories`

### Paso 4: Tipos de Productos (`jumbo_step4_producttypes.py`)
- **Objetivo**: Extraer tipos de productos disponibles en cada subcategoría
- **Método**: Visita páginas de subcategorías y busca filtros de tipo de producto
- **Datos extraídos**:
  - Nombre del tipo de producto
  - URL con filtros aplicados
  - Relación con subcategoría y categoría
- **Base de datos**: Guarda en colección `product_types`

## 🔧 Configuración

### Modo Background
- Los pasos 2-4 pueden ejecutarse en modo background (headless)
- Útil para procesamiento automático sin interfaz visual
- Se activa con el flag `--background`

### Logging
- Cada script genera su propio archivo de log:
  - `jumbo_scraper_step1.log`
  - `jumbo_scraper_step2.log`
  - `jumbo_scraper_step3.log`
  - `jumbo_scraper_step4.log`
  - `jumbo_master_scraper.log`

### Timeouts y Esperas
- Los scripts incluyen esperas inteligentes para cargar páginas
- Timeouts configurables para elementos web
- Reintentos automáticos para operaciones fallidas

## 🗄️ Estructura de Base de Datos

### Base de Datos: `jumbo`

#### Colección: `supermarket`
```json
{
  "name": "Jumbo Argentina",
  "url": "https://www.jumbo.com.ar",
  "country": "Argentina",
  "phone": "...",
  "email": "...",
  "scraped_at": "2024-01-01T00:00:00"
}
```

#### Colección: `categories`
```json
{
  "name": "Alimentos",
  "url": "https://www.jumbo.com.ar/alimentos",
  "slug": "alimentos",
  "supermarket": "jumbo",
  "subcategories": [...],
  "scraped_at": "2024-01-01T00:00:00"
}
```

#### Colección: `subcategories`
```json
{
  "name": "Lácteos",
  "url": "https://www.jumbo.com.ar/lacteos",
  "slug": "lacteos",
  "category_name": "Alimentos",
  "category_slug": "alimentos",
  "supermarket": "jumbo",
  "scraped_at": "2024-01-01T00:00:00"
}
```

#### Colección: `product_types`
```json
{
  "name": "Leche Entera",
  "url": "https://www.jumbo.com.ar/lacteos?tipo=leche-entera",
  "slug": "leche-entera",
  "subcategory_name": "Lácteos",
  "subcategory_slug": "lacteos",
  "category_name": "Alimentos",
  "category_slug": "alimentos",
  "supermarket": "jumbo",
  "scraped_at": "2024-01-01T00:00:00"
}
```

## 🐛 Troubleshooting

### Problemas Comunes

1. **WebDriver no encontrado**
   - Asegurarse de que `geckodriver.exe` esté en el directorio raíz
   - Verificar que Firefox esté instalado

2. **MongoDB connection error**
   - Verificar que MongoDB esté corriendo en localhost:27017
   - Crear la base de datos `jumbo` si no existe

3. **Elementos no encontrados**
   - Los selectores CSS pueden cambiar; revisar la estructura HTML de Jumbo
   - Los scripts incluyen múltiples selectores alternativos

4. **Timeouts**
   - Aumentar timeouts si la conexión es lenta
   - Verificar conectividad a internet

### Debug Mode
- Ejecutar sin `--background` para ver el navegador en acción
- Revisar logs detallados en los archivos `.log`
- Usar herramientas de desarrollo de Firefox para inspeccionar elementos

## 📈 Monitoreo y Logs

- **Progreso**: Los logs muestran el progreso de cada paso
- **Errores**: Detalles de errores con timestamps
- **Estadísticas**: Conteo de elementos extraídos por paso

## 🔄 Mantenimiento

- **Actualización de selectores**: Revisar periódicamente si cambian los selectores CSS
- **Versiones**: Actualizar dependencias Python regularmente
- **Limpieza**: Eliminar logs antiguos y datos temporales

## 📚 Referencias

- `proceso-desarrollo-jumbo.md`: Documentación detallada del proceso de desarrollo
- Scripts de Carrefour: Base para la adaptación a Jumbo
- Documentación de Selenium: Para mantenimiento de WebDriver

---

**Nota**: Estos scripts están diseñados para uso educativo y de investigación. Respetar los términos de servicio de Jumbo y no sobrecargar sus servidores.