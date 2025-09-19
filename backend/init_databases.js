const mongoose = require('mongoose');

// Databases to create
const databases = ['caminando-online', 'carrefour', 'disco', 'dia', 'vea', 'jumbo'];

const initializeDatabase = async () => {
  try {
    console.log('Starting database initialization for all supermarkets...\n');

    for (const dbName of databases) {
      console.log(`\n📊 Initializing database: ${dbName}`);
      console.log('='.repeat(50));

      // Connect to specific database
      const dbUri = `mongodb://localhost:27017/${dbName}`;
      await mongoose.connect(dbUri);

      // Get the database instance
      const db = mongoose.connection.db;

      // Collections to create
      const collections = [
        'categories',
        'subcategories',
        'producttypes',
        'products',
        'filters'
      ];

      // Add supermarket-info for all except caminando-online
      if (dbName !== 'caminando-online') {
        collections.push('supermarket-info');
      }

      // Create collections if they don't exist
      for (const collectionName of collections) {
        const collectionsList = await db.listCollections({ name: collectionName }).toArray();

        if (collectionsList.length === 0) {
          await db.createCollection(collectionName);
          console.log(`✓ Created collection: ${collectionName}`);
        } else {
          console.log(`✓ Collection already exists: ${collectionName}`);
        }
      }

      console.log(`✅ Database ${dbName} initialized successfully!`);

      // Disconnect from current database
      await mongoose.disconnect();
    }

    console.log('\n🎉 All databases initialized successfully!');
    console.log('\nDatabases created:');
    databases.forEach(name => {
      const collections = ['categories', 'subcategories', 'producttypes', 'products', 'filters'];
      if (name !== 'caminando-online') {
        collections.push('supermarket-info');
      }
      console.log(`📁 ${name}:`);
      collections.forEach(col => console.log(`   - ${col}`));
    });
    console.log('\nAll collections are empty and ready for data.');

  } catch (error) {
    console.error('Database initialization failed:', error);
  } finally {
    await mongoose.disconnect();
    console.log('All database connections closed');
  }
};

// Run initialization if this script is executed directly
if (require.main === module) {
  initializeDatabase();
}

module.exports = initializeDatabase;
