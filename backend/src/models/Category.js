const mongoose = require('mongoose');

const categorySchema = new mongoose.Schema({
  name: {
    type: String,
    required: [true, 'Category name is required'],
    trim: true,
  },
  slug: {
    type: String,
    required: [true, 'Category slug is required'],
    trim: true,
    unique: true,
  },
  url: {
    type: String,
    required: [true, 'Category URL is required'],
    trim: true,
  },
  supermarket: {
    type: String,
    required: [true, 'Supermarket is required'],
    enum: ['Carrefour', 'Jumbo', 'Dia', 'Vea', 'Disco'],
    default: 'Carrefour',
  },
  parentCategory: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'Category',
    default: null,
  },
  level: {
    type: Number,
    default: 1, // 1 = categoría principal, 2 = subcategoría, etc.
  },
  isActive: {
    type: Boolean,
    default: true,
  },
  productCount: {
    type: Number,
    default: 0,
  },
  lastScraped: {
    type: Date,
    default: null,
  },
  createdAt: {
    type: Date,
    default: Date.now,
  },
  updatedAt: {
    type: Date,
    default: Date.now,
  },
});

// Índices para optimizar consultas
categorySchema.index({ supermarket: 1, slug: 1 });
categorySchema.index({ supermarket: 1, level: 1 });
categorySchema.index({ parentCategory: 1 });

// Update updatedAt on save
categorySchema.pre('save', function(next) {
  this.updatedAt = Date.now();
  next();
});

// Método para obtener subcategorías
categorySchema.methods.getSubcategories = function() {
  return mongoose.model('Category').find({
    parentCategory: this._id,
    isActive: true
  });
};

// Método estático para obtener categorías principales
categorySchema.statics.getMainCategories = function(supermarket = 'Carrefour') {
  return this.find({
    supermarket,
    level: 1,
    isActive: true
  }).sort({ name: 1 });
};

// Método estático para buscar categoría por slug
categorySchema.statics.findBySlug = function(slug, supermarket = 'Carrefour') {
  return this.findOne({
    slug,
    supermarket,
    isActive: true
  });
};

const Category = mongoose.model('Category', categorySchema);

module.exports = { Category };
