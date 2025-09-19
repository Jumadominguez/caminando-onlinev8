const mongoose = require('mongoose');

const supermarketSchema = new mongoose.Schema({
  name: {
    type: String,
    required: [true, 'Supermarket name is required'],
    trim: true,
    unique: true,
    enum: ['Carrefour', 'Jumbo', 'Dia', 'Vea', 'Disco'],
  },
  logo: {
    type: String,
    trim: true,
  },
  color: {
    type: String,
    trim: true,
    default: '#007bff',
  },
  website: {
    type: String,
    trim: true,
  },
  address: {
    type: String,
    trim: true,
  },
  phone: {
    type: String,
    trim: true,
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

// Index
supermarketSchema.index({ name: 1 });

// Update updatedAt on save
supermarketSchema.pre('save', function(next) {
  this.updatedAt = Date.now();
  next();
});

module.exports = mongoose.model('Supermarket', supermarketSchema);
