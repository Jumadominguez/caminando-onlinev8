const { Product } = require('./Product');
const { Supermarket } = require('./Supermarket');
const { User, registerSchema, loginSchema } = require('./User');
const { Category } = require('./Category');

module.exports = {
  Product,
  Supermarket,
  User,
  Category,
  registerSchema,
  loginSchema,
};
