const express = require('express');
const {
  getSupermarkets,
  getSupermarket,
  createSupermarket,
  updateSupermarket,
  deleteSupermarket,
  getNearbySupermarkets,
  getSupermarketStats,
} = require('../controllers/supermarketController');
const auth = require('../middleware/auth');

const router = express.Router();

// Public routes
router.get('/', getSupermarkets);
router.get('/nearby', getNearbySupermarkets);
router.get('/:id', getSupermarket);
router.get('/:id/stats', getSupermarketStats);

// Protected routes (require authentication)
router.post('/', auth, createSupermarket);
router.put('/:id', auth, updateSupermarket);
router.delete('/:id', auth, deleteSupermarket);

module.exports = router;
