const { MongoClient } = require('mongodb');

async function clearProductArrays() {
  const client = new MongoClient('mongodb://localhost:27017/');

  try {
    await client.connect();
    const db = client.db('carrefour');
    const collection = db.collection('producttypes');

    console.log('Conectado a MongoDB...');

    // Limpiar arrays de productos
    const result = await collection.updateMany(
      {}, // Todos los documentos
      { $set: { products: [] } } // Establecer products como array vacío
    );

    console.log(`✓ Arrays limpiados en ${result.modifiedCount} documentos`);

  } catch (error) {
    console.error('Error:', error);
  } finally {
    await client.close();
    console.log('Conexión cerrada');
  }
}

clearProductArrays();