const { Supermarket } = require('../models');
const Joi = require('joi');

// Validation schemas
const createSupermarketSchema = Joi.object({
  name: Joi.string().min(2).max(50).required(),
  logo: Joi.string().uri().required(),
  address: Joi.string().max(200),
  phone: Joi.string().max(20),
  website: Joi.string().uri(),
  location: Joi.object({
    type: Joi.string().valid('Point').default('Point'),
    coordinates: Joi.array().items(Joi.number()).length(2), // [longitude, latitude]
  }),
});

const updateSupermarketSchema = Joi.object({
  name: Joi.string().min(2).max(50),
  logo: Joi.string().uri(),
  address: Joi.string().max(200),
  phone: Joi.string().max(20),
  website: Joi.string().uri(),
  location: Joi.object({
    type: Joi.string().valid('Point'),
    coordinates: Joi.array().items(Joi.number()).length(2),
  }),
}).min(1); // At least one field required

// Get all supermarkets
const getSupermarkets = async (req, res) => {
  try {
    const supermarkets = await Supermarket.find({ isActive: true })
      .sort({ name: 1 })
      .lean();

    res.json({ supermarkets });
  } catch (error) {
    console.error('Get supermarkets error:', error);
    res.status(500).json({ error: 'Internal server error.' });
  }
};

// Get single supermarket by ID
const getSupermarket = async (req, res) => {
  try {
    const { id } = req.params;

    const supermarket = await Supermarket.findById(id).lean();

    if (!supermarket) {
      return res.status(404).json({ error: 'Supermarket not found.' });
    }

    res.json({ supermarket });
  } catch (error) {
    console.error('Get supermarket error:', error);
    if (error.kind === 'ObjectId') {
      return res.status(400).json({ error: 'Invalid supermarket ID.' });
    }
    res.status(500).json({ error: 'Internal server error.' });
  }
};

// Create new supermarket
const createSupermarket = async (req, res) => {
  try {
    // Validate input
    const { error, value } = createSupermarketSchema.validate(req.body);
    if (error) {
      return res.status(400).json({ error: error.details[0].message });
    }

    // Check if supermarket already exists
    const existingSupermarket = await Supermarket.findOne({ name: value.name });
    if (existingSupermarket) {
      return res.status(409).json({ error: 'Supermarket with this name already exists.' });
    }

    // Create supermarket
    const supermarket = new Supermarket(value);
    await supermarket.save();

    res.status(201).json({
      message: 'Supermarket created successfully.',
      supermarket,
    });
  } catch (error) {
    console.error('Create supermarket error:', error);
    res.status(500).json({ error: 'Internal server error.' });
  }
};

// Update supermarket
const updateSupermarket = async (req, res) => {
  try {
    // Validate input
    const { error, value } = updateSupermarketSchema.validate(req.body);
    if (error) {
      return res.status(400).json({ error: error.details[0].message });
    }

    const { id } = req.params;

    const supermarket = await Supermarket.findByIdAndUpdate(id, value, {
      new: true,
      runValidators: true,
    });

    if (!supermarket) {
      return res.status(404).json({ error: 'Supermarket not found.' });
    }

    res.json({
      message: 'Supermarket updated successfully.',
      supermarket,
    });
  } catch (error) {
    console.error('Update supermarket error:', error);
    if (error.code === 11000) {
      res.status(409).json({ error: 'Supermarket with this name already exists.' });
    } else if (error.kind === 'ObjectId') {
      res.status(400).json({ error: 'Invalid supermarket ID.' });
    } else {
      res.status(500).json({ error: 'Internal server error.' });
    }
  }
};

// Delete supermarket (soft delete)
const deleteSupermarket = async (req, res) => {
  try {
    const { id } = req.params;

    const supermarket = await Supermarket.findByIdAndUpdate(
      id,
      { isActive: false },
      { new: true }
    );

    if (!supermarket) {
      return res.status(404).json({ error: 'Supermarket not found.' });
    }

    res.json({ message: 'Supermarket deleted successfully.' });
  } catch (error) {
    console.error('Delete supermarket error:', error);
    if (error.kind === 'ObjectId') {
      return res.status(400).json({ error: 'Invalid supermarket ID.' });
    }
    res.status(500).json({ error: 'Internal server error.' });
  }
};

// Get supermarkets near location
const getNearbySupermarkets = async (req, res) => {
  try {
    const { lng, lat, maxDistance = 5000 } = req.query; // maxDistance in meters

    if (!lng || !lat) {
      return res.status(400).json({ error: 'Longitude and latitude are required.' });
    }

    const supermarkets = await Supermarket.find({
      location: {
        $near: {
          $geometry: {
            type: 'Point',
            coordinates: [parseFloat(lng), parseFloat(lat)],
          },
          $maxDistance: parseInt(maxDistance),
        },
      },
      isActive: true,
    }).lean();

    res.json({ supermarkets });
  } catch (error) {
    console.error('Get nearby supermarkets error:', error);
    res.status(500).json({ error: 'Internal server error.' });
  }
};

// Get supermarket statistics
const getSupermarketStats = async (req, res) => {
  try {
    const { id } = req.params;

    const supermarket = await Supermarket.findById(id);
    if (!supermarket) {
      return res.status(404).json({ error: 'Supermarket not found.' });
    }

    // Get product count and price statistics
    const stats = await Supermarket.aggregate([
      { $match: { _id: supermarket._id } },
      {
        $lookup: {
          from: 'products',
          localField: '_id',
          foreignField: 'supermarketId',
          as: 'products',
        },
      },
      {
        $project: {
          name: 1,
          productCount: { $size: '$products' },
          averagePrice: { $avg: '$products.price' },
          minPrice: { $min: '$products.price' },
          maxPrice: { $max: '$products.price' },
          categories: { $setUnion: '$products.category' },
        },
      },
    ]);

    res.json({ stats: stats[0] });
  } catch (error) {
    console.error('Get supermarket stats error:', error);
    if (error.kind === 'ObjectId') {
      return res.status(400).json({ error: 'Invalid supermarket ID.' });
    }
    res.status(500).json({ error: 'Internal server error.' });
  }
};

module.exports = {
  getSupermarkets,
  getSupermarket,
  createSupermarket,
  updateSupermarket,
  deleteSupermarket,
  getNearbySupermarkets,
  getSupermarketStats,
};
