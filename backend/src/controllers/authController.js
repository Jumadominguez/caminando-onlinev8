const jwt = require('jsonwebtoken');
const { User, registerSchema, loginSchema } = require('../models');
const Joi = require('joi');

// Generate JWT token
const generateToken = (user) => {
  return jwt.sign(
    { id: user._id, email: user.email, role: user.role },
    process.env.JWT_SECRET,
    { expiresIn: process.env.JWT_EXPIRES_IN || '7d' }
  );
};

// Register new user
const register = async (req, res) => {
  try {
    // Validate input
    const { error } = registerSchema.validate(req.body);
    if (error) {
      return res.status(400).json({ error: error.details[0].message });
    }

    const { email, password, name } = req.body;

    // Check if user already exists
    const existingUser = await User.findOne({ email });
    if (existingUser) {
      return res.status(409).json({ error: 'User already exists with this email.' });
    }

    // Create new user
    const user = new User({ email, password, name });
    await user.save();

    // Generate token
    const token = generateToken(user);

    res.status(201).json({
      message: 'User registered successfully.',
      user: user.toJSON(),
      token,
    });
  } catch (error) {
    console.error('Registration error:', error);
    res.status(500).json({ error: 'Internal server error.' });
  }
};

// Login user
const login = async (req, res) => {
  try {
    // Validate input
    const { error } = loginSchema.validate(req.body);
    if (error) {
      return res.status(400).json({ error: error.details[0].message });
    }

    const { email, password } = req.body;

    // Find user
    const user = await User.findOne({ email });
    if (!user || !user.isActive) {
      return res.status(401).json({ error: 'Invalid credentials.' });
    }

    // Check password
    const isPasswordValid = await user.comparePassword(password);
    if (!isPasswordValid) {
      return res.status(401).json({ error: 'Invalid credentials.' });
    }

    // Update last login
    user.lastLogin = new Date();
    await user.save();

    // Generate token
    const token = generateToken(user);

    res.json({
      message: 'Login successful.',
      user: user.toJSON(),
      token,
    });
  } catch (error) {
    console.error('Login error:', error);
    res.status(500).json({ error: 'Internal server error.' });
  }
};

// Get current user profile
const getProfile = async (req, res) => {
  try {
    const user = await User.findById(req.user._id);
    if (!user) {
      return res.status(404).json({ error: 'User not found.' });
    }

    res.json({ user: user.toJSON() });
  } catch (error) {
    console.error('Get profile error:', error);
    res.status(500).json({ error: 'Internal server error.' });
  }
};

// Update user profile
const updateProfile = async (req, res) => {
  try {
    const allowedUpdates = ['name', 'email'];
    const updates = {};

    allowedUpdates.forEach(field => {
      if (req.body[field] !== undefined) {
        updates[field] = req.body[field];
      }
    });

    const user = await User.findByIdAndUpdate(req.user._id, updates, {
      new: true,
      runValidators: true,
    });

    if (!user) {
      return res.status(404).json({ error: 'User not found.' });
    }

    res.json({
      message: 'Profile updated successfully.',
      user: user.toJSON(),
    });
  } catch (error) {
    console.error('Update profile error:', error);
    if (error.code === 11000) {
      res.status(409).json({ error: 'Email already in use.' });
    } else {
      res.status(500).json({ error: 'Internal server error.' });
    }
  }
};

module.exports = {
  register,
  login,
  getProfile,
  updateProfile,
};
