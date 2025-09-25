const { Product } = require('./Product');
const { Supermarket } = require('./Supermarket');
const { User, registerSchema, loginSchema } = require('./User');
const { Category } = require('./Category');
const CarrefourProduct = require('./Product');

module.exports = {
  Product,
  Supermarket,
  User,
  Category,
  CarrefourProduct,
  registerSchema,
  loginSchema,
};
