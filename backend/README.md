# Caminando Online - Backend API

Backend API for the price comparison platform across Argentine supermarkets (Carrefour, Jumbo, Dia, Vea, Disco).

## Features

- **Secure Authentication**: JWT-based authentication with bcrypt password hashing
- **Product Management**: CRUD operations for products with validation
- **Supermarket Management**: Manage supermarket information and locations
- **Price Comparison**: Compare prices across different supermarkets
- **Security**: Helmet, CORS, rate limiting, input validation with Joi
- **Error Handling**: Comprehensive error handling middleware
- **MongoDB Integration**: Mongoose ODM with secure connection

## Tech Stack

- **Runtime**: Node.js
- **Framework**: Express.js
- **Database**: MongoDB with Mongoose
- **Authentication**: JWT (jsonwebtoken)
- **Validation**: Joi
- **Security**: Helmet, CORS, express-rate-limit
- **Password Hashing**: bcryptjs
- **Logging**: Morgan

## Installation

1. **Install Dependencies**
   ```bash
   cd backend
   npm install
   ```

2. **Environment Setup**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Start MongoDB**
   Make sure MongoDB is running on port 27017 (default)

4. **Initialize Database**
   ```bash
   cd ../Sandbox/temps
   node init_databases.js
   ```

5. **Start Server**
   ```bash
   cd ../../backend
   npm start
   ```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `NODE_ENV` | Environment mode | `development` |
| `PORT` | Server port | `5000` |
| `MONGODB_URI` | MongoDB connection string | `mongodb://localhost:27017/caminando-online` |
| `JWT_SECRET` | JWT signing secret | `your-super-secret-jwt-key-change-in-production` |
| `JWT_EXPIRES_IN` | JWT expiration time | `7d` |
| `FRONTEND_URL` | Frontend URL for CORS | `http://localhost:3000` |

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `GET /api/auth/profile` - Get user profile (protected)
- `PUT /api/auth/profile` - Update user profile (protected)

### Products
- `GET /api/products` - Get all products (with filtering/pagination)
- `GET /api/products/:id` - Get single product
- `POST /api/products` - Create product (protected)
- `PUT /api/products/:id` - Update product (protected)
- `DELETE /api/products/:id` - Delete product (protected)
- `GET /api/products/category/:category` - Get products by category
- `GET /api/products/compare/:name` - Compare prices for a product

### Supermarkets
- `GET /api/supermarkets` - Get all supermarkets
- `GET /api/supermarkets/:id` - Get single supermarket
- `POST /api/supermarkets` - Create supermarket (protected)
- `PUT /api/supermarkets/:id` - Update supermarket (protected)
- `DELETE /api/supermarkets/:id` - Delete supermarket (protected)
- `GET /api/supermarkets/nearby` - Get nearby supermarkets
- `GET /api/supermarkets/:id/stats` - Get supermarket statistics

### Health Check
- `GET /health` - Server health check

## Testing

Run the test script to verify backend functionality:

```bash
cd Sandbox/temps
node test_backend.js
```

## Security Features

- **Helmet**: Security headers
- **CORS**: Cross-origin resource sharing configuration
- **Rate Limiting**: 100 requests per 15 minutes per IP
- **Input Validation**: Joi schemas for all inputs
- **Password Hashing**: bcrypt with 12 salt rounds
- **JWT Authentication**: Secure token-based auth
- **Error Handling**: No stack traces in production

## Development

### Project Structure
```
backend/
├── src/
│   ├── app.js              # Express app configuration
│   ├── server.js           # Server entry point
│   ├── config/
│   │   ├── database.js     # MongoDB connection
│   │   └── index.js        # Configuration constants
│   ├── controllers/        # Route handlers
│   ├── middleware/         # Custom middleware
│   ├── models/             # Mongoose models
│   └── routes/             # API routes
├── .env.example            # Environment template
└── package.json
```

### Available Scripts
- `npm start` - Start production server
- `npm run dev` - Start development server with nodemon
- `npm test` - Run tests

## Contributing

1. Follow the existing code style
2. Add validation for all inputs
3. Include error handling
4. Update documentation
5. Test your changes

## License

This project is licensed under the MIT License.
