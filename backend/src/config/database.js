const mongoose = require('mongoose');
const config = require('./index');

const connectDB = async () => {
  try {
    const options = {
      useNewUrlParser: true,
      useUnifiedTopology: true,
    };

    // Add SSL options for production
    if (config.NODE_ENV === 'production') {
      options.ssl = true;
      options.sslValidate = true;
    }

    await mongoose.connect(config.MONGODB_URI, options);

    console.log('MongoDB connected successfully');

    // Handle connection events
    mongoose.connection.on('error', (err) => {
      console.error('MongoDB connection error:', err);
    });

    mongoose.connection.on('disconnected', () => {
      console.log('MongoDB disconnected');
    });

    // Graceful shutdown
    process.on('SIGINT', async () => {
      await mongoose.connection.close();
      console.log('MongoDB connection closed through app termination');
      process.exit(0);
    });

  } catch (error) {
    console.error('MongoDB connection failed:', error.message);
    process.exit(1);
  }
};

module.exports = connectDB;
