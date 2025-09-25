const { MongoClient } = require('mongodb');

async function removeTotalProductsField() {
  const client = new MongoClient('mongodb://localhost:27017/');

  try {
    await client.connect();
    const db = client.db('carrefour');
    const collection = db.collection('producttypes');

    console.log('Conectado a MongoDB...');

    // Eliminar el campo total_products de todos los documentos
    const result = await collection.updateMany(
      {}, // Todos los documentos
      { $unset: { total_products: "" } } // Eliminar el campo total_products
    );

    console.log(`✓ Campo 'total_products' eliminado de ${result.modifiedCount} documentos`);

  } catch (error) {
    console.error('Error:', error);
  } finally {
    await client.close();
    console.log('Conexión cerrada');
  }
}

removeTotalProductsField();