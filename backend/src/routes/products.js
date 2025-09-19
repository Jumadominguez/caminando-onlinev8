const express = require('express');
const {
  getProducts,
  getProduct,
  createProduct,
  updateProduct,
  deleteProduct,
  getProductsByCategory,
  getPriceComparison,
} = require('../controllers/productController');
const auth = require('../middleware/auth');

const router = express.Router();

// Public routes
router.get('/', getProducts);
router.get('/category/:category', getProductsByCategory);
router.get('/compare/:name', getPriceComparison);
router.get('/:id', getProduct);

// Protected routes (require authentication)
router.post('/', auth, createProduct);
router.put('/:id', auth, updateProduct);
router.delete('/:id', auth, deleteProduct);

module.exports = router;
