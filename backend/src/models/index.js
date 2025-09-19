const { Product } = require('./Product');
const { Supermarket } = require('./Supermarket');
const { User, registerSchema, loginSchema } = require('./User');

module.exports = {
  Product,
  Supermarket,
  User,
  registerSchema,
  loginSchema,
};
