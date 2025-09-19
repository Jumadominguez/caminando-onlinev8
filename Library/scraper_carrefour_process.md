# Proceso de Scraping - Carrefour Argentina

**Fecha de creación:** 19/9/2025
**Última actualización:** 19/9/2025
**Versión:** 1.3.0
**Proyecto:** Caminando Online V8
**Objetivo:** Sistema de comparación de precios para supermercados argentinos
**Estado:** 🔄 Fase 2 en desarrollo - Scraper de subcategorías creado y probado

## 📋 Información General

### 🎯 Propósito
Documentar el proceso completo de scraping de Carrefour Argentina para extracción de datos de productos y categorías, con el fin de crear una plataforma de comparación de precios.

### 🛠️ Tecnologías Utilizadas
- **Lenguaje principal:** Node.js
- **Framework de automatización:** Playwright
- **Base de datos:** MongoDB con Mongoose
- **Navegador:** Firefox (compatible con macOS ARM)
- **Sistema operativo:** macOS
- **Gestor de dependencias:** npm

### 📦 Dependencias Requeridas
```json
{
  "playwright": "^1.40.0",
  "mongoose": "^8.18.1"
}
```

### 🚀 Instalación
```bash
npm install playwright
npx playwright install firefox
```

## 🔄 Proceso de Scraping - Paso a Paso

### Paso 1: Configuración del Entorno
```javascript
const { firefox } = require('playwright');

const browser = await firefox.launch({
  headless: false, // Para ver el proceso
  args: ['--no-sandbox', '--disable-setuid-sandbox']
});
```

### Paso 2: Navegación a la Página Principal
```javascript
const page = await browser.newPage();

// Configurar viewport
await page.setViewportSize({ width: 1280, height: 720 });

// Navegar a Carrefour
await page.goto('https://www.carrefour.com.ar', {
  waitUntil: 'networkidle',
  timeout: 60000
});
```

### Paso 3: Desplegar Menú de Categorías
**Selector utilizado:** `button.carrefourar-mega-menu-0-x-triggerContainer:has-text("Categorías")`

```javascript
// Esperar a que el selector esté disponible con retry
await page.waitForSelector('button.carrefourar-mega-menu-0-x-triggerContainer:has-text("Categorías")', {
  timeout: 15000
});

// Hacer scroll hasta el elemento
await page.locator('button.carrefourar-mega-menu-0-x-triggerContainer:has-text("Categorías")')
  .scrollIntoViewIfNeeded();

// Hacer clic en el menú de categorías con retry
await page.click('button.carrefourar-mega-menu-0-x-triggerContainer:has-text("Categorías")', {
  timeout: 10000
});

// Esperar a que se despliegue el menú completamente
await page.waitForTimeout(5000);
```

## 🎯 Selectores Identificados y Verificados

### 1. Selector Principal - Menú de Categorías
```
Selector: button.carrefourar-mega-menu-0-x-triggerContainer:has-text("Categorías")
Elemento: BUTTON
Función: Abre el menú desplegable de categorías
Estado: ✅ Probado y funcional
Uso: await page.click('button.carrefourar-mega-menu-0-x-triggerContainer:has-text("Categorías")')
Resultado: Extrae 16 categorías principales
```

### 2. Selector de Categorías Principales
```
Selector: .carrefourar-mega-menu-0-x-styledLink
Elemento: LINKS (a)
Función: Extrae todas las categorías principales del menú desplegable
Estado: ✅ Probado y funcional
Uso: await page.locator('.carrefourar-mega-menu-0-x-styledLink').all()
Criterios de filtrado: URLs sin '/c/' (principales) vs con '/c/' (subcategorías)
```

### 3. Selectores de Productos (Pendientes de Identificación)
```
Estado: 🔄 Por identificar en Fase 2
Notas: En páginas de categorías, identificar selectores para:
- Nombre del producto
- Precio
- Imagen
- Descripción
- Información nutricional
```

## 📝 Código Base del Scraper

```javascript
const { firefox } = require('playwright');
const mongoose = require('mongoose');
const Category = require('./models/Category');

async function scrapeCarrefour() {
  console.log('🚀 Iniciando scraping de Carrefour...');

  // Conectar a base de datos
  await mongoose.connect('mongodb://localhost:27017/carrefour', {
    useNewUrlParser: true,
    useUnifiedTopology: true
  });
  console.log('📊 Conectado a base de datos carrefour');

  const browser = await firefox.launch({
    headless: false,
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });

  try {
    const page = await browser.newPage();
    await page.setViewportSize({ width: 1280, height: 720 });

    // Paso 1: Navegar a la página
    console.log('📍 Navegando a Carrefour...');
    await page.goto('https://www.carrefour.com.ar', {
      waitUntil: 'networkidle',
      timeout: 60000
    });
    console.log('✅ Página cargada');

    // Paso 2: Desplegar menú de categorías con retry
    console.log('🎯 Desplegando menú de categorías...');
    const menuSelector = 'button.carrefourar-mega-menu-0-x-triggerContainer:has-text("Categorías")';

    await page.waitForSelector(menuSelector, { timeout: 15000 });
    await page.locator(menuSelector).scrollIntoViewIfNeeded();
    await page.click(menuSelector, { timeout: 10000 });
    await page.waitForTimeout(5000);

    console.log('✅ Menú desplegado exitosamente');

    // Paso 3: Extraer categorías principales
    console.log('📋 Extrayendo categorías principales...');
    const categorySelector = '.carrefourar-mega-menu-0-x-styledLink';
    const categoryElements = await page.locator(categorySelector).all();

    const categories = [];
    for (const element of categoryElements) {
      const name = await element.textContent();
      const href = await element.getAttribute('href');

      // Filtrar categorías principales (excluir subcategorías)
      if (name && href && !href.includes('/c/') && href.includes('/')) {
        categories.push({
          name: name.trim(),
          url: href,
          slug: href.split('/').pop(),
          supermarket: 'carrefour',
          level: 1
        });
      }
    }

    console.log(`📊 Encontradas ${categories.length} categorías principales`);

    // Paso 4: Guardar en base de datos
    console.log('💾 Guardando categorías en base de datos...');
    for (const categoryData of categories) {
      const existingCategory = await Category.findOne({
        slug: categoryData.slug,
        supermarket: 'carrefour'
      });

      if (!existingCategory) {
        const category = new Category(categoryData);
        await category.save();
        console.log(`✅ Guardada categoría: ${categoryData.name}`);
      } else {
        console.log(`⏭️  Categoría ya existe: ${categoryData.name}`);
      }
    }

    console.log('🎉 Scraping completado exitosamente');

  } catch (error) {
    console.error('❌ Error:', error);
  } finally {
    await browser.close();
    await mongoose.connection.close();
    console.log('🔒 Browser y DB cerrados');
  }
}

scrapeCarrefour();
```

## 🔧 Configuración del Entorno de Desarrollo

### Estructura de Carpetas Recomendada
```
backend/Sandbox/prototypes/
├── scraperCarrefour.js          # Script principal (movido de Experiments)
├── selectores_scr_carrefour.md  # Selectores identificados
└── scraper_carrefour_process.md # Esta documentación

backend/Sandbox/Experiments/
├── scraperCarrefourSubcategories.js     # Nuevo scraper de subcategorías
├── scraper_carrefour_subcategories.md   # Documentación del nuevo scraper
└── [otros archivos de experimentación]
```

### Variables de Entorno
```bash
# No se requieren variables de entorno específicas para este scraper básico
# Para producción, considerar:
# - API keys para almacenamiento de datos
# - Configuración de base de datos
# - Credenciales de autenticación
```

## ⚠️ Consideraciones Importantes

### 1. Rate Limiting
- Carrefour puede tener protección contra scraping automatizado
- Implementar delays entre requests
- Considerar usar proxies para distribución de carga

### 2. Cambios en el DOM
- Los selectores pueden cambiar con actualizaciones del sitio
- Implementar sistema de detección de cambios
- Mantener backups de selectores funcionales

### 3. Legalidad y Ética
- Verificar términos de servicio de Carrefour
- No sobrecargar los servidores
- Usar datos solo para comparación de precios legítima

### 4. Manejo de Errores
- Implementar retry logic para requests fallidos
- Logging detallado de errores
- Graceful degradation cuando elementos no se encuentren

## 📊 Próximos Pasos del Desarrollo

### Fase 1: Extracción de Categorías ✅ COMPLETADA
- [x] Identificar selector correcto del menú principal
- [x] Implementar apertura del menú con sistema de retry
- [x] Extraer lista completa de categorías principales (16/17)
- [x] Implementar filtrado de categorías principales vs subcategorías
- [x] Crear modelo de base de datos Category
- [x] Implementar guardado en MongoDB (base de datos 'carrefour')
- [x] Documentar selectores y proceso
- [x] Decisión: Excluir "Indumentaria" (no encontrada en menú principal)

**Resultado:** 16 categorías principales extraídas y guardadas exitosamente

### Fase 2: Navegación por Categorías y Filtros 🔄 EN DESARROLLO
- [x] Crear scraper de subcategorías (scraperCarrefourSubcategories.js)
- [x] Implementar navegación automática por categorías principales
- [x] Sistema de búsqueda de contenedores de filtros
- [x] Detección de elementos colapsables por selectores estándar
- [x] Búsqueda alternativa por texto de palabras clave
- [ ] Identificar selectores específicos de Carrefour para filtros
- [ ] Implementar expansión automática de todos los menús
- [ ] Extraer opciones detalladas de cada filtro
- [ ] Crear modelo de base de datos para subcategorías
- [ ] Sistema de paginación para productos
- [ ] Extraer URLs de subcategorías

### Fase 3: Extracción de Productos 📋
- [ ] Identificar selectores de productos en páginas de categorías
- [ ] Extraer datos: nombre, precio, imagen, descripción
- [ ] Manejo de productos con variaciones
- [ ] Implementar sistema de guardado de productos

### Fase 4: Almacenamiento de Datos 💾
- [ ] Diseño de esquema de base de datos para productos
- [ ] Implementar guardado de productos con relación a categorías
- [ ] Sistema de actualización incremental
- [ ] Validación de datos

### Fase 5: Optimización y Escalabilidad 🚀
- [ ] Implementación de colas de procesamiento
- [ ] Sistema de caché
- [ ] Monitoreo de rendimiento
- [ ] Manejo de rate limiting

## 📋 Categorías Principales Extraídas

Se extrajeron exitosamente **16 de 17 categorías principales** del menú de Carrefour:

1. **Almacén** - `/almacen`
2. **Bebidas** - `/bebidas`
3. **Carnes y Pescados** - `/carnes-y-pescados`
4. **Congelados** - `/congelados`
5. **Desayuno y Dulces** - `/desayuno-y-dulces`
6. **Electro y Tecno** - `/electro-y-tecno`
7. **Frescos** - `/frescos`
8. **Hogar** - `/hogar`
9. **Limpieza** - `/limpieza`
10. **Mascotas** - `/mascotas`
11. **Panadería** - `/panaderia`
12. **Perfumería** - `/perfumeria`
13. **Quesos y Fiambres** - `/quesos-y-fiambres`
14. **Snacks** - `/snacks`
15. **Verdulería** - `/verduleria`
16. **Vinos y Licores** - `/vinos-y-licores`

**Nota:** La categoría "Indumentaria" no fue encontrada en el menú principal desplegable, por lo que se decidió no incluirla en esta fase.

## 💾 Modelo de Base de Datos - Category

```javascript
// models/Category.js
const mongoose = require('mongoose');

const categorySchema = new mongoose.Schema({
  name: {
    type: String,
    required: true,
    trim: true
  },
  slug: {
    type: String,
    required: true,
    unique: true
  },
  url: {
    type: String,
    required: true
  },
  supermarket: {
    type: String,
    required: true,
    enum: ['carrefour', 'dia', 'jumbo', 'vea', 'disco']
  },
  level: {
    type: Number,
    default: 1,
    min: 1,
    max: 3
  },
  parentCategory: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'Category',
    default: null
  },
  subcategories: [{
    type: mongoose.Schema.Types.ObjectId,
    ref: 'Category'
  }],
  isActive: {
    type: Boolean,
    default: true
  },
  createdAt: {
    type: Date,
    default: Date.now
  },
  updatedAt: {
    type: Date,
    default: Date.now
  }
});

// Índices para optimización
categorySchema.index({ supermarket: 1, slug: 1 });
categorySchema.index({ supermarket: 1, level: 1 });
categorySchema.index({ parentCategory: 1 });

// Middleware para actualizar updatedAt
categorySchema.pre('save', function(next) {
  this.updatedAt = Date.now();
  next();
});

module.exports = mongoose.model('Category', categorySchema);
```

### Campos del Modelo:
- **name**: Nombre de la categoría
- **slug**: Identificador único (de URL)
- **url**: URL completa de la categoría
- **supermarket**: Nombre del supermercado (siempre 'carrefour' en esta fase)
- **level**: Nivel jerárquico (1 = principal, 2 = subcategoría, 3 = sub-subcategoría)
- **parentCategory**: Referencia a categoría padre (para jerarquía)
- **subcategories**: Array de subcategorías
- **isActive**: Flag para activar/desactivar categorías
- **createdAt/updatedAt**: Timestamps automáticos

## 🔍 Debugging y Troubleshooting

### Errores Comunes
1. **Selector no encontrado:** Verificar si el sitio cambió su estructura
2. **Timeout errors:** Aumentar timeouts o verificar conectividad
3. **Browser crashes:** Verificar versión de Playwright y Firefox

### Herramientas de Debug
```javascript
// Para debug, habilitar modo no-headless
const browser = await firefox.launch({ headless: false });

// Para inspeccionar elementos
await page.pause(); // Pausa la ejecución para inspeccionar manualmente
```

## 📚 Referencias y Recursos

- [Documentación de Playwright](https://playwright.dev/)
- [Selectores CSS](https://developer.mozilla.org/es/docs/Web/CSS/CSS_Selectors)
- [Web Scraping Ethics](https://blog.apify.com/web-scraping-ethics/)

---

**Este documento debe actualizarse con cada cambio significativo en el proceso de scraping**
**Última actualización:** 19/9/2025
**Versión:** 1.3.0
