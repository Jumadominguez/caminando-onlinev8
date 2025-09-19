const mongoose = require('mongoose');

const productSchema = new mongoose.Schema({
  name: {
    type: String,
    required: [true, 'Product name is required'],
    trim: true,
    maxlength: [100, 'Name cannot exceed 100 characters'],
  },
  price: {
    type: Number,
    required: [true, 'Price is required'],
    min: [0, 'Price cannot be negative'],
  },
  supermarket: {
    type: String,
    required: [true, 'Supermarket is required'],
    enum: ['Carrefour', 'Jumbo', 'Dia', 'Vea', 'Disco'],
  },
  category: {
    type: String,
    required: [true, 'Category is required'],
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
  image: {
    type: String,
    trim: true,
  },
  description: {
    type: String,
    trim: true,
    maxlength: [500, 'Description cannot exceed 500 characters'],
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

// Index for performance
productSchema.index({ name: 1, supermarket: 1 });
productSchema.index({ category: 1 });
productSchema.index({ price: 1 });

// Update updatedAt on save
productSchema.pre('save', function(next) {
  this.updatedAt = Date.now();
  next();
});

module.exports = mongoose.model('Product', productSchema);
