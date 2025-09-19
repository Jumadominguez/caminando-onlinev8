require('dotenv').config();
const app = require('./src/app');
const connectDB = require('./src/config/database');
const config = require('./src/config');

const startServer = async () => {
  try {
    // Connect to MongoDB
    await connectDB();

    // Start server
    const server = app.listen(config.PORT, () => {
      console.log(`Server running in ${config.NODE_ENV} mode on port ${config.PORT}`);
      console.log(`Health check available at http://localhost:${config.PORT}/health`);
    });

    // Handle server errors
    server.on('error', (error) => {
      console.error('Server error:', error);
      process.exit(1);
    });

  } catch (error) {
    console.error('Failed to start server:', error);
    process.exit(1);
  }
};

startServer();
