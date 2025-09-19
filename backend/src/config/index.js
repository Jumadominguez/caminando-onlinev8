// Application configuration constants
const config = {
  // Server
  PORT: process.env.PORT || 5000,
  NODE_ENV: process.env.NODE_ENV || 'development',

  // Database
  MONGODB_URI: process.env.MONGODB_URI || 'mongodb://localhost:27017/caminando-online',

  // JWT
  JWT_SECRET: process.env.JWT_SECRET || 'your-super-secret-jwt-key-change-in-production',
  JWT_EXPIRES_IN: process.env.JWT_EXPIRES_IN || '7d',

  // CORS
  FRONTEND_URL: process.env.FRONTEND_URL || 'http://localhost:3000',

  // Rate Limiting
  RATE_LIMIT_WINDOW_MS: 15 * 60 * 1000, // 15 minutes
  RATE_LIMIT_MAX_REQUESTS: 100,

  // File Upload
  MAX_FILE_SIZE: 10 * 1024 * 1024, // 10MB

  // Pagination
  DEFAULT_PAGE_SIZE: 20,
  MAX_PAGE_SIZE: 100,

  // Supermarkets
  SUPPORTED_SUPERMARKETS: [
    'Carrefour',
    'Jumbo',
    'Dia',
    'Vea',
    'Disco'
  ],

  // Categories
  PRODUCT_CATEGORIES: [
    'Alimentos',
    'Bebidas',
    'Limpieza',
    'Higiene',
    'Electrónicos',
    'Ropa',
    'Hogar',
    'Otros'
  ],
};

module.exports = config;
