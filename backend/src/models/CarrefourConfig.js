// Configuración para el scraper de Carrefour
// Basado en el análisis del OuterHTML y estructura del sitio

const carrefourConfig = {
  // URLs base
  baseUrl: 'https://www.carrefour.com.ar',
  apiBaseUrl: 'https://www.carrefour.com.ar/api',

  // URLs específicas
  categoriesUrl: 'https://www.carrefour.com.ar/almacen',
  searchUrl: 'https://www.carrefour.com.ar/busca',

  // Selectores CSS identificados del OuterHTML
  selectors: {
    // Información básica del producto
    productName: '[data-testid="product-name"]',
    productBrand: '[data-testid="product-brand"]',
    productPrice: '[data-testid="product-price"]',
    productOriginalPrice: '[data-testid="product-original-price"]',
    productSku: '[data-testid="product-sku"]',

    // Imágenes
    productImages: '.product-images img',
    mainImage: '.product-main-image img',

    // Categorización
    breadcrumbs: '.breadcrumb-item',
    categoryPath: '.breadcrumb a',

    // Descripción y detalles
    productDescription: '[data-testid="product-description"]',
    productSpecs: '.product-specifications',

    // Disponibilidad
    availabilityStatus: '[data-testid="availability-status"]',
    stockIndicator: '.stock-indicator',

    // Información nutricional (si aplica)
    nutritionalTable: '.nutritional-info table',

    // Precio por unidad
    pricePerUnit: '.price-per-unit',
    unitMeasure: '.unit-measure',

    // Información de empaque
    packageWeight: '.package-weight',
    packageDimensions: '.package-dimensions',

    // Listado de productos (para scraping masivo)
    productList: '.product-item',
    productLink: '.product-item a',
    productCard: '.product-card',

    // Paginación
    nextPage: '.pagination .next',
    pageNumbers: '.pagination .page-number',

    // Filtros y búsqueda
    searchInput: '[data-testid="search-input"]',
    categoryFilter: '.category-filter',
    priceFilter: '.price-filter'
  },

  // Selectores JSON-LD (datos estructurados)
  jsonLdSelectors: {
    productSchema: 'script[type="application/ld+json"]',
    breadcrumbSchema: '.breadcrumb script[type="application/ld+json"]'
  },

  // Headers para requests HTTP
  headers: {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'es-AR,es;q=0.9,en;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Cache-Control': 'max-age=0'
  },

  // Configuración de scraping
  scraping: {
    // Delay entre requests (en ms)
    delayBetweenRequests: 1000,

    // Timeout para requests (en ms)
    requestTimeout: 30000,

    // Número máximo de reintentos
    maxRetries: 3,

    // Delay entre reintentos (en ms)
    retryDelay: 2000,

    // Límite de productos por categoría
    productsPerCategory: 100,

    // Límite de páginas por categoría
    maxPagesPerCategory: 10
  },

  // Categorías principales conocidas
  mainCategories: [
    'almacen',
    'bebidas',
    'frescos',
    'congelados',
    'limpieza',
    'perfumeria',
    'electro',
    'juguetes',
    'deportes',
    'mascotas'
  ],

  // Mapeo de categorías a URLs
  categoryUrls: {
    almacen: '/almacen',
    bebidas: '/bebidas',
    frescos: '/frescos',
    congelados: '/congelados',
    limpieza: '/limpieza',
    perfumeria: '/perfumeria',
    electro: '/electro',
    juguetes: '/juguetes',
    deportes: '/deportes',
    mascotas: '/mascotas'
  },

  // Configuración de base de datos
  database: {
    collectionName: 'carrefour_products',
    updateExisting: true, // Si true, actualiza productos existentes
    upsert: true // Si true, inserta si no existe
  },

  // Configuración de logging
  logging: {
    level: 'info', // error, warn, info, debug
    file: 'carrefour_scraper.log',
    maxFileSize: '10m',
    maxFiles: 5
  }
};

module.exports = carrefourConfig;