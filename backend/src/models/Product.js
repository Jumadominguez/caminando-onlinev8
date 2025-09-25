const mongoose = require('mongoose');

const carrefourProductSchema = new mongoose.Schema({
  // Información básica del producto
  name: {
    type: String,
    trim: true,
    maxlength: [200, 'Name cannot exceed 200 characters'],
  },

  // Identificadores únicos
  sku: {
    type: String,
    trim: true,
  },
  mpn: {
    type: String,
    trim: true,
  },
  gtin: {
    type: String,
    trim: true,
  },
  retailerPartNo: {
    type: String,
    trim: true,
  },

  // Marca y fabricante
  brand: {
    type: String,
    trim: true,
  },

  // Precio y moneda
  price: {
    type: Number,
    min: [0, 'Price cannot be negative'],
  },
  currency: {
    type: String,
    default: 'ARS',
    enum: ['ARS', 'USD'],
  },
  sellingPrice: {
    type: Number,
    min: [0, 'Selling price cannot be negative'],
  },
  listPrice: {
    type: Number,
    min: [0, 'List price cannot be negative'],
  },
  pricePerUnit: {
    type: Number,
    min: [0, 'Price per unit cannot be negative'],
  },
  unit: {
    type: String,
    trim: true,
  },

  // Categorización jerárquica
  category: {
    type: String,
    trim: true,
  },
  subcategory: {
    type: String,
    trim: true,
  },
  productType: {
    type: String,
    trim: true,
  },
  categoryPath: [{
    type: String,
    trim: true,
  }],

  // Descripción y detalles
  description: {
    type: String,
    trim: true,
    maxlength: [1000, 'Description cannot exceed 1000 characters'],
  },

  // Imágenes
  images: [{
    url: {
      type: String,
      trim: true,
    },
    alt: {
      type: String,
      trim: true,
    },
  }],
  mainImage: {
    type: String,
    trim: true,
  },

  // Disponibilidad y stock
  availability: {
    type: String,
    enum: ['instock', 'outofstock', 'discontinued'],
    default: 'instock',
  },
  stockQuantity: {
    type: Number,
    min: [0, 'Stock quantity cannot be negative'],
  },

  // Información del vendedor
  seller: {
    type: String,
    enum: ['Carrefour'],
    default: 'Carrefour',
  },

  // Condición del producto
  condition: {
    type: String,
    enum: ['new', 'used', 'refurbished'],
    default: 'new',
  },

  // URLs y enlaces
  productUrl: {
    type: String,
    trim: true,
  },
  canonicalUrl: {
    type: String,
    trim: true,
  },

  // Información de precios promocionales
  originalPrice: {
    type: Number,
    min: [0, 'Original price cannot be negative'],
  },
  discountPercentage: {
    type: Number,
    min: [0, 'Discount percentage cannot be negative'],
    max: [100, 'Discount percentage cannot exceed 100%'],
  },
  isOnSale: {
    type: Boolean,
    default: false,
  },

  // Información de clusters promocionales (ProductClusters)
  productClusters: [{
    id: { type: String, required: false },
    name: { type: String, required: false },
    __typename: { type: String, default: 'ProductClusters' }
  }],
  isOnPromotion: { type: Boolean, default: false },
  promotionalClusters: [{
    id: { type: String, required: false },
    name: { type: String, required: false },
    type: { type: String, enum: ['2do_al_50', '2do_al_70', 'hasta_35_off', 'promo_max_48', 'other'], default: 'other' }
  }],
  discountCodes: [{ type: String }],

  // Información nutricional (para alimentos)
  nutritionalInfo: {
    calories: Number,
    proteins: Number,
    carbohydrates: Number,
    fats: Number,
    fiber: Number,
    sodium: Number,
  },

  // Información de empaque
  packageInfo: {
    weight: Number,
    weightUnit: {
      type: String,
      enum: ['g', 'kg', 'ml', 'l', 'oz', 'lb'],
    },
    dimensions: {
      length: Number,
      width: Number,
      height: Number,
      unit: {
        type: String,
        enum: ['cm', 'm', 'in', 'ft'],
      },
    },
  },

  // Información de scraping
  scrapedAt: {
    type: Date,
    default: Date.now,
  },
  lastUpdated: {
    type: Date,
    default: Date.now,
  },
  sourceUrl: {
    type: String,
    trim: true,
  },

  // Metadatos adicionales
  tags: [{
    type: String,
    trim: true,
  }],
  attributes: {
    type: Map,
    of: String,
  },

  // Timestamps
  createdAt: {
    type: Date,
    default: Date.now,
  },
  updatedAt: {
    type: Date,
    default: Date.now,
  },
});

// Índices para optimización de consultas
carrefourProductSchema.index({ sku: 1 });
carrefourProductSchema.index({ name: 1 });
carrefourProductSchema.index({ brand: 1 });
carrefourProductSchema.index({ category: 1 });
carrefourProductSchema.index({ subcategory: 1 });
carrefourProductSchema.index({ price: 1 });
carrefourProductSchema.index({ availability: 1 });
carrefourProductSchema.index({ scrapedAt: 1 });
carrefourProductSchema.index({ 'categoryPath': 1 });

// Middleware para actualizar el campo updatedAt
carrefourProductSchema.pre('save', function(next) {
  this.updatedAt = Date.now();
  this.lastUpdated = Date.now();
  next();
});

// Método para calcular precio por unidad si no está definido
carrefourProductSchema.methods.calculatePricePerUnit = function() {
  if (this.price && this.packageInfo && this.packageInfo.weight) {
    const weightInKg = this.packageInfo.weightUnit === 'g' ?
      this.packageInfo.weight / 1000 : this.packageInfo.weight;
    this.pricePerUnit = this.price / weightInKg;
  }
};

// Método para verificar si el producto está disponible
carrefourProductSchema.methods.isAvailable = function() {
  return this.availability === 'instock' && (!this.stockQuantity || this.stockQuantity > 0);
};

// Método para verificar si está en promoción basado en clusters
carrefourProductSchema.methods.checkPromotionStatus = function() {
  if (!this.productClusters || this.productClusters.length === 0) {
    this.isOnPromotion = false;
    return false;
  }

  // Buscar clusters promocionales
  const promoClusters = this.productClusters.filter(cluster => {
    const name = cluster.name || '';
    return name.includes('2do al') ||
           name.includes('Hasta') ||
           name.includes('PROMO') ||
           name.includes('off') ||
           name.includes('descuento') ||
           name.includes('ahorro');
  });

  this.promotionalClusters = promoClusters.map(cluster => {
    let type = 'other';
    const name = cluster.name || '';

    if (name.includes('2do al 50')) type = '2do_al_50';
    else if (name.includes('2do al 70')) type = '2do_al_70';
    else if (name.includes('Hasta 35% off')) type = 'hasta_35_off';
    else if (name.includes('Max 48')) type = 'promo_max_48';

    return {
      id: cluster.id,
      name: cluster.name,
      type: type
    };
  });

  this.isOnPromotion = promoClusters.length > 0;
  return this.isOnPromotion;
};

// Método para calcular descuento efectivo
carrefourProductSchema.methods.calculateEffectiveDiscount = function() {
  if (!this.isOnPromotion || !this.promotionalClusters.length) {
    return 0;
  }

  let maxDiscount = this.discountPercentage || 0;

  this.promotionalClusters.forEach(cluster => {
    const name = cluster.name || '';
    let discount = 0;

    // Extraer porcentajes de descuento de los nombres de clusters
    const discountMatch = name.match(/(\d+)%/);
    if (discountMatch) {
      discount = parseInt(discountMatch[1]);
    } else if (name.includes('2do al 50')) {
      discount = 50;
    } else if (name.includes('2do al 70')) {
      discount = 30; // 70% del segundo producto = 30% descuento efectivo
    }

    if (discount > maxDiscount) {
      maxDiscount = discount;
    }
  });

  return maxDiscount;
};

// Método estático para buscar productos por categoría
carrefourProductSchema.statics.findByCategory = function(category) {
  return this.find({
    $or: [
      { category: new RegExp(category, 'i') },
      { subcategory: new RegExp(category, 'i') },
      { categoryPath: { $in: [new RegExp(category, 'i')] } }
    ]
  });
};

// Método estático para buscar productos en oferta
carrefourProductSchema.statics.findOnSale = function() {
  return this.find({
    isOnSale: true,
    availability: 'instock'
  }).sort({ discountPercentage: -1 });
};

// Método estático para buscar productos en promoción (basado en clusters)
carrefourProductSchema.statics.findOnPromotion = function() {
  return this.find({
    isOnPromotion: true,
    availability: 'instock'
  }).sort({ 'promotionalClusters.type': 1 });
};

// Método estático para buscar productos por tipo de promoción
carrefourProductSchema.statics.findByPromotionType = function(promoType) {
  return this.find({
    'promotionalClusters.type': promoType,
    availability: 'instock'
  });
};

// Método estático para obtener estadísticas de promociones
carrefourProductSchema.statics.getPromotionStats = async function() {
  const stats = await this.aggregate([
    {
      $match: { isOnPromotion: true }
    },
    {
      $group: {
        _id: null,
        totalPromotionalProducts: { $sum: 1 },
        promotionTypes: {
          $push: '$promotionalClusters.type'
        },
        avgDiscount: { $avg: '$discountPercentage' }
      }
    }
  ]);

  return stats[0] || {
    totalPromotionalProducts: 0,
    promotionTypes: [],
    avgDiscount: 0
  };
};

module.exports = mongoose.model('CarrefourProduct', carrefourProductSchema);