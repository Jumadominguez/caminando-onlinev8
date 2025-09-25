# Proceso de Extracción de Productos Carrefour - Análisis Detallado

## Fecha: 25 de septiembre de 2025
## Objetivo: Extraer información completa de productos incluyendo ofertas y promociones
## Alcance: Hasta 5000+ productos por categoría con enfoque en eficiencia

---

## 1. ANÁLISIS DEL SITIO WEB CARREFOUR

### 1.1 Arquitectura Técnica
- **Plataforma**: VTEX e-commerce
- **Frontend**: React + VTEX IO
- **API**: GraphQL + REST endpoints
- **Datos Estructurados**: JSON-LD schemas
- **Renderizado**: Server-side + Client-side hydration

### 1.2 Estructura de URLs
```
Categoría principal: https://www.carrefour.com.ar/{categoria}
Subcategoría: https://www.carrefour.com.ar/{categoria}/{subcategoria}
Producto: https://www.carrefour.com.ar/{nombre-producto}-{sku}/p
```

### 1.3 Paginación
- **Productos por página**: 20-50 productos
- **Parámetros**: `?page={numero}&PS=20`
- **Total de páginas**: Variable según categoría

---

## 2. ESTRATEGIAS DE SCRAPING EFICIENTE

### 2.1 Enfoque Multi-Nivel
```
Nivel 1: Categorías principales → URLs de subcategorías
Nivel 2: Subcategorías → URLs de productos
Nivel 3: Páginas de productos → Datos individuales
```

### 2.2 Optimizaciones de Rendimiento

#### 2.2.1 Paralelización Controlada
- **Máximo 5 requests simultáneos** por dominio
- **Delay de 1-2 segundos** entre requests
- **Rotación de User-Agents** para evitar bloqueos
- **Manejo de rate limiting** con exponential backoff

#### 2.2.2 Caching Inteligente
- **Cache de categorías**: 24 horas
- **Cache de productos**: 1 hora
- **Cache de imágenes**: 7 días
- **Invalidación automática** por cambios detectados

#### 2.2.3 Procesamiento Asíncrono
- **Queue system** para manejar grandes volúmenes
- **Batch processing** de 100 productos por vez
- **Background jobs** para actualizaciones masivas

### 2.3 Manejo de Errores
- **Retry logic** con backoff exponencial
- **Fallback a datos previos** si request falla
- **Logging detallado** de errores por categoría
- **Circuit breaker** para categorías problemáticas

---

## 3. ANÁLISIS DE DATOS DE PRODUCTOS

### 3.1 Fuentes de Datos Identificadas

#### 3.1.1 JSON-LD Schema (Principal)
```json
{
  "@context": "https://schema.org",
  "@type": "Product",
  "name": "Gaseosa cola Coca Cola Zero 2,25 lts",
  "sku": "11324",
  "brand": "Coca Cola",
  "offers": {
    "@type": "Offer",
    "price": "3450.00",
    "priceCurrency": "ARS",
    "availability": "https://schema.org/InStock"
  }
}
```

#### 3.1.2 Datos VTEX (JavaScript)
```javascript
window.__INITIAL_STATE__ = {
  product: {
    productId: "393964",
    productName: "Gaseosa cola Coca Cola Zero 2,25 lts",
    brand: "Coca Cola",
    // ... más datos
  }
}
```

#### 3.1.3 HTML Structured Data
- **Open Graph meta tags**
- **Product specifications tables**
- **Price components**
- **Promotion ribbons**

### 3.2 Información de Ofertas y Promociones

#### 3.2.1 Tipos de Promociones Identificadas

**A) Promociones por Cantidad:**
- `"2do al 50% Max 48 Unidades Iguales"`
- `"2do al 70% Mi Carrefour Crédito"`
- `"2do al 70% Mi Carrefour Prepaga"`

**B) Descuentos Directos:**
- `Hasta 35% off`
- `Promo Max 48`

**C) Códigos de Descuento:**
- `"5K-SEPTIEMBRE"` (5000% OFF primera compra)

#### 3.2.2 Estructura de Datos de Promociones
```javascript
{
  productClusters: [
    {
      id: "101",
      name: "2do al 50% Max 48 Unidades Iguales",
      __typename: "ProductClusters"
    }
  ],
  promotionalClusters: [
    {
      id: "101",
      name: "2do al 50% Max 48 Unidades Iguales",
      type: "2do_al_50"
    }
  ],
  isOnPromotion: true,
  discountCodes: ["5K-SEPTIEMBRE"]
}
```

#### 3.2.3 Información de Precios
```javascript
{
  sellingPrice: 3450.00,    // Precio actual
  listPrice: 4600.00,       // Precio tachado
  pricePerUnit: 1533.33,    // Precio por litro
  currency: "ARS",
  discountPercentage: 25    // 25% de descuento
}
```

---

## 4. IMPLEMENTACIÓN DEL PROCESO DE EXTRACCIÓN

### 4.1 ✅ CATEGORÍAS, SUBCATEGORÍAS Y PRODUCTTYPES YA CARGADOS

**IMPORTANTE**: Las colecciones `categories`, `subcategories` y `producttypes` ya están pobladas en la base de datos `carrefour`. No es necesario hacer scraping de estas estructuras.

#### 4.1.1 Estructura de Colecciones Existentes

**Colección `categories`:**
```javascript
{
  _id: ObjectId,
  url: "https://www.carrefour.com.ar/Almacen",
  name: "Almacén",
  name_simple: "almacen",
  scraped_at: "2025-09-24T07:40:15.411363"
}
```

**Colección `subcategories`:**
```javascript
{
  _id: ObjectId,
  category_url: "https://www.carrefour.com.ar/Almacen",
  name: "Gaseosas",
  category_name: "Almacén",
  name_simple: "gaseosas",
  scraped_at: "2025-09-23T06:31:17.923370"
}
```

**Colección `producttypes`:**
```javascript
{
  _id: ObjectId,
  category: "Almacén",
  subcategory: "Gaseosas",
  name: "Cola",
  category_url: "https://www.carrefour.com.ar/Almacen",
  extracted_at: "2025-09-24T16:35:17.658Z",
  simplified_name: "Cola"
}
```

### 4.2 Fase Única: Extracción de Productos Individuales

#### 4.2.1 Estrategia Simplificada
```
1. Leer producttypes de BD
2. Construir URLs de productos usando la info existente
3. Hacer scraping individual de cada producto
4. Vincular con categorías/subcategorías/producttypes existentes
5. Guardar en colección products
```

#### 4.2.2 Script Principal: `carrefour_product_scraper.py`
```python
# Estrategia simplificada:
# 1. Conectar a BD carrefour
# 2. Leer todos los producttypes
# 3. Para cada producttype, construir URLs de búsqueda
# 4. Extraer productos individuales
# 5. Vincular con jerarquía existente (category → subcategory → producttype)
```

---

## 5. ESTRUCTURA DE DATOS COMPLETA

### 5.1 Modelo de Producto (Product.js)

#### 5.1.1 Información Básica
```javascript
{
  name: "Gaseosa cola Coca Cola Zero 2,25 lts",
  sku: "11324",
  brand: "Coca Cola",
  description: "...",
  category: "Almacén",
  subcategory: "Gaseosas",
  productType: "Cola"
}
```

#### 5.1.2 Información de Precios y Promociones
```javascript
{
  price: 3450.00,
  originalPrice: 4600.00,
  currency: "ARS",
  pricePerUnit: 1533.33,
  unit: "litro",
  discountPercentage: 25,
  isOnSale: true,
  isOnPromotion: true
}
```

#### 5.1.3 Clusters Promocionales
```javascript
{
  productClusters: [...],
  promotionalClusters: [
    {
      id: "101",
      name: "2do al 50% Max 48 Unidades Iguales",
      type: "2do_al_50"
    }
  ],
  discountCodes: ["5K-SEPTIEMBRE"]
}
```

#### 5.1.4 Información Adicional
```javascript
{
  images: [...],
  availability: "instock",
  nutritionalInfo: {...},
  packageInfo: {...},
  scrapedAt: new Date(),
  sourceUrl: "..."
}
```

---

## 6. OPTIMIZACIONES PARA GRAN ESCALA

### 6.1 Estrategia de Procesamiento

#### 6.1.1 Paralelización por Categorías
```
Categoría A: Proceso 1 (5 threads)
Categoría B: Proceso 2 (5 threads)
Categoría C: Proceso 3 (5 threads)
```

#### 6.1.2 Queue System
- **Redis Queue** para URLs pendientes
- **Worker pools** especializados por tipo de tarea
- **Priority queues** para productos críticos

#### 6.1.3 Batch Processing
```javascript
const BATCH_SIZE = 100;
const products = await Product.find({})
  .limit(BATCH_SIZE)
  .sort({ scrapedAt: 1 });

// Procesar lote
for (const product of products) {
  await updateProductData(product);
}
```

### 6.2 Optimizaciones de Base de Datos

#### 6.2.1 Índices Estratégicos
```javascript
// Índices para consultas frecuentes
db.products.createIndex({ sku: 1 }, { unique: true });
db.products.createIndex({ category: 1, subcategory: 1 });
db.products.createIndex({ brand: 1 });
db.products.createIndex({ isOnPromotion: 1 });
db.products.createIndex({ scrapedAt: 1 });
```

#### 6.2.2 Bulk Operations
```javascript
// Insert masivo para mejor rendimiento
const bulkOps = products.map(product => ({
  insertOne: { document: product }
}));

await Product.bulkWrite(bulkOps, { ordered: false });
```

### 6.3 Monitoreo y Control de Calidad

#### 6.3.1 Métricas a Monitorear
- **Tasa de éxito de requests**: >95%
- **Tiempo promedio por producto**: <2 segundos
- **Productos procesados por hora**: >1000
- **Errores por categoría**: <5%

#### 6.3.2 Alertas Automáticas
- **Rate limiting detectado**: Pausar y retry con delay
- **Cambios en estructura HTML**: Notificar para actualización de parsers
- **Productos faltantes**: Re-queue para reintento

---

## 7. PLAN DE IMPLEMENTACIÓN ACTUALIZADO

### 7.1 ✅ Infraestructura Lista (Completado)
- [x] Modelo Product.js implementado
- [x] Configuración de scraping lista
- [x] Colecciones categories/subcategories/producttypes pobladas
- [x] Base de datos configurada

### 7.2 Fase Única: Scraper Principal (1-2 días)
- [ ] Implementar `carrefour_product_scraper.py`
- [ ] Leer producttypes de BD carrefour
- [ ] Construir URLs de búsqueda por producttype
- [ ] Implementar extracción individual de productos
- [ ] Vincular con jerarquía existente
- [ ] Guardar productos en colección products

### 7.3 Fase de Testing (1 día)
- [ ] Probar con un producttype pequeño
- [ ] Validar extracción de ofertas y promociones
- [ ] Verificar vinculación correcta con categorías
- [ ] Test con diferentes tipos de productos

### 7.4 Fase de Optimización (1-2 días)
- [ ] Implementar paralelización (5 requests simultáneos)
- [ ] Agregar sistema de cache para productos
- [ ] Implementar retry logic con backoff
- [ ] Testing con producttypes grandes (>1000 productos)

### 7.5 Fase de Monitoreo (1 día)
- [ ] Implementar métricas básicas
- [ ] Logging de progreso
- [ ] Alertas para errores
- [ ] Documentación final

---

## 8. RIESGOS Y MITIGACIONES

### 8.1 Riesgos Técnicos
- **Cambios en HTML**: Monitoreo continuo + parsers flexibles
- **Rate limiting**: Headers realistas + delays variables
- **Bloqueos de IP**: Rotación de proxies + VPN

### 8.2 Riesgos de Datos
- **Datos incompletos**: Validación post-extracción
- **Duplicados**: Control por SKU único
- **Datos obsoletos**: Timestamp de scraping

### 8.3 Riesgos Operativos
- **Tiempo de ejecución**: Procesamiento por lotes
- **Memoria**: Streaming para grandes categorías
- **Conectividad**: Retry logic robusto

---

## 9. MÉTRICAS DE ÉXITO

- **Cobertura**: >95% de productos extraídos correctamente
- **Velocidad**: 1000+ productos por hora
- **Confiabilidad**: <5% de errores
- **Actualización**: Datos frescos (<24 horas)
- **Escalabilidad**: Manejo de 5000+ productos por categoría

---

## 10. CONCLUSIONES

Este proceso permite extraer eficientemente información completa de productos Carrefour, incluyendo ofertas y promociones, manejando grandes volúmenes de manera escalable. La clave está en la paralelización controlada, el caching inteligente y el manejo robusto de errores.

**Próximo paso**: Implementar `carrefour_product_scraper.py` basado en este análisis.</content>
<parameter name="filePath">d:\dev\caminando-onlinev8\Sandbox\Experiments\carrefour_scraping_process.md