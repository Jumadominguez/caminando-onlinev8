const mongoose = require('mongoose');

async function checkBrands() {
  try {
    await mongoose.connect('mongodb://localhost:27017/carrefour');
    console.log('Connected to MongoDB');

    const brands = await mongoose.connection.db.collection('filters').find({type: 'brand'}).limit(5).toArray();
    console.log('Sample brand filters:');
    brands.forEach((b, i) => {
      console.log(`${i+1}. ${JSON.stringify(b, null, 2)}`);
    });

    await mongoose.connection.close();
  } catch (err) {
    console.error('Error:', err);
  }
}

checkBrands();