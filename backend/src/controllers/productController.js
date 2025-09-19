const { Product, Supermarket } = require('../models');
const Joi = require('joi');

// Validation schemas
const createProductSchema = Joi.object({
  name: Joi.string().min(2).max(100).required(),
  description: Joi.string().max(500),
  price: Joi.number().min(0).required(),
  category: Joi.string().min(2).max(50).required(),
  supermarketId: Joi.string().length(24).required(), // MongoDB ObjectId
  imageUrl: Joi.string().uri(),
  barcode: Joi.string().max(50),
  unit: Joi.string().max(20),
  brand: Joi.string().max(50),
});

const updateProductSchema = Joi.object({
  name: Joi.string().min(2).max(100),
  description: Joi.string().max(500),
  price: Joi.number().min(0),
  category: Joi.string().min(2).max(50),
  imageUrl: Joi.string().uri(),
  barcode: Joi.string().max(50),
  unit: Joi.string().max(20),
  brand: Joi.string().max(50),
}).min(1); // At least one field required

const querySchema = Joi.object({
  page: Joi.number().min(1).default(1),
  limit: Joi.number().min(1).max(100).default(20),
  category: Joi.string(),
  supermarketId: Joi.string().length(24),
  search: Joi.string(),
  minPrice: Joi.number().min(0),
  maxPrice: Joi.number().min(0),
  sortBy: Joi.string().valid('price', 'name', 'createdAt').default('createdAt'),
  sortOrder: Joi.string().valid('asc', 'desc').default('desc'),
});

// Get all products with filtering and pagination
const getProducts = async (req, res) => {
  try {
    // Validate query parameters
    const { error, value } = querySchema.validate(req.query);
    if (error) {
      return res.status(400).json({ error: error.details[0].message });
    }

    const {
      page,
      limit,
      category,
      supermarketId,
      search,
      minPrice,
      maxPrice,
      sortBy,
      sortOrder,
    } = value;

    // Build filter object
    const filter = {};
    if (category) filter.category = category;
    if (supermarketId) filter.supermarketId = supermarketId;
    if (search) {
      filter.$or = [
        { name: { $regex: search, $options: 'i' } },
        { description: { $regex: search, $options: 'i' } },
        { brand: { $regex: search, $options: 'i' } },
      ];
    }
    if (minPrice !== undefined || maxPrice !== undefined) {
      filter.price = {};
      if (minPrice !== undefined) filter.price.$gte = minPrice;
      if (maxPrice !== undefined) filter.price.$lte = maxPrice;
    }

    // Build sort object
    const sort = {};
    sort[sortBy] = sortOrder === 'desc' ? -1 : 1;

    // Execute query with pagination
    const skip = (page - 1) * limit;
    const products = await Product.find(filter)
      .populate('supermarketId', 'name logo')
      .sort(sort)
      .skip(skip)
      .limit(limit)
      .lean();

    const total = await Product.countDocuments(filter);

    res.json({
      products,
      pagination: {
        page,
        limit,
        total,
        pages: Math.ceil(total / limit),
      },
    });
  } catch (error) {
    console.error('Get products error:', error);
    res.status(500).json({ error: 'Internal server error.' });
  }
};

// Get single product by ID
const getProduct = async (req, res) => {
  try {
    const { id } = req.params;

    const product = await Product.findById(id)
      .populate('supermarketId', 'name logo')
      .lean();

    if (!product) {
      return res.status(404).json({ error: 'Product not found.' });
    }

    res.json({ product });
  } catch (error) {
    console.error('Get product error:', error);
    if (error.kind === 'ObjectId') {
      return res.status(400).json({ error: 'Invalid product ID.' });
    }
    res.status(500).json({ error: 'Internal server error.' });
  }
};

// Create new product
const createProduct = async (req, res) => {
  try {
    // Validate input
    const { error, value } = createProductSchema.validate(req.body);
    if (error) {
      return res.status(400).json({ error: error.details[0].message });
    }

    // Check if supermarket exists
    const supermarket = await Supermarket.findById(value.supermarketId);
    if (!supermarket) {
      return res.status(400).json({ error: 'Invalid supermarket ID.' });
    }

    // Create product
    const product = new Product(value);
    await product.save();

    // Populate supermarket data
    await product.populate('supermarketId', 'name logo');

    res.status(201).json({
      message: 'Product created successfully.',
      product,
    });
  } catch (error) {
    console.error('Create product error:', error);
    if (error.code === 11000) {
      res.status(409).json({ error: 'Product with this barcode already exists.' });
    } else {
      res.status(500).json({ error: 'Internal server error.' });
    }
  }
};

// Update product
const updateProduct = async (req, res) => {
  try {
    // Validate input
    const { error, value } = updateProductSchema.validate(req.body);
    if (error) {
      return res.status(400).json({ error: error.details[0].message });
    }

    const { id } = req.params;

    // Check if supermarket exists if updating supermarketId
    if (value.supermarketId) {
      const supermarket = await Supermarket.findById(value.supermarketId);
      if (!supermarket) {
        return res.status(400).json({ error: 'Invalid supermarket ID.' });
      }
    }

    const product = await Product.findByIdAndUpdate(id, value, {
      new: true,
      runValidators: true,
    }).populate('supermarketId', 'name logo');

    if (!product) {
      return res.status(404).json({ error: 'Product not found.' });
    }

    res.json({
      message: 'Product updated successfully.',
      product,
    });
  } catch (error) {
    console.error('Update product error:', error);
    if (error.code === 11000) {
      res.status(409).json({ error: 'Product with this barcode already exists.' });
    } else if (error.kind === 'ObjectId') {
      res.status(400).json({ error: 'Invalid product ID.' });
    } else {
      res.status(500).json({ error: 'Internal server error.' });
    }
  }
};

// Delete product
const deleteProduct = async (req, res) => {
  try {
    const { id } = req.params;

    const product = await Product.findByIdAndDelete(id);

    if (!product) {
      return res.status(404).json({ error: 'Product not found.' });
    }

    res.json({ message: 'Product deleted successfully.' });
  } catch (error) {
    console.error('Delete product error:', error);
    if (error.kind === 'ObjectId') {
      return res.status(400).json({ error: 'Invalid product ID.' });
    }
    res.status(500).json({ error: 'Internal server error.' });
  }
};

// Get products by category
const getProductsByCategory = async (req, res) => {
  try {
    const { category } = req.params;
    const { page = 1, limit = 20 } = req.query;

    const skip = (page - 1) * limit;
    const products = await Product.find({ category })
      .populate('supermarketId', 'name logo')
      .sort({ price: 1 }) // Sort by price ascending
      .skip(skip)
      .limit(parseInt(limit))
      .lean();

    const total = await Product.countDocuments({ category });

    res.json({
      products,
      pagination: {
        page: parseInt(page),
        limit: parseInt(limit),
        total,
        pages: Math.ceil(total / limit),
      },
    });
  } catch (error) {
    console.error('Get products by category error:', error);
    res.status(500).json({ error: 'Internal server error.' });
  }
};

// Get product price comparison
const getPriceComparison = async (req, res) => {
  try {
    const { name } = req.params;

    const products = await Product.find({
      name: { $regex: name, $options: 'i' }
    })
      .populate('supermarketId', 'name logo')
      .sort({ price: 1 })
      .lean();

    if (products.length === 0) {
      return res.status(404).json({ error: 'No products found with that name.' });
    }

    const comparison = {
      productName: name,
      cheapest: products[0],
      mostExpensive: products[products.length - 1],
      averagePrice: products.reduce((sum, p) => sum + p.price, 0) / products.length,
      supermarkets: products.map(p => ({
        supermarket: p.supermarketId,
        price: p.price,
        productId: p._id,
      })),
    };

    res.json({ comparison });
  } catch (error) {
    console.error('Get price comparison error:', error);
    res.status(500).json({ error: 'Internal server error.' });
  }
};

module.exports = {
  getProducts,
  getProduct,
  createProduct,
  updateProduct,
  deleteProduct,
  getProductsByCategory,
  getPriceComparison,
};
