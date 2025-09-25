#!/usr/bin/env node

const { MongoClient } = require('mongodb');

async function clearProductsField() {
    const client = new MongoClient('mongodb://localhost:27017/');
    const db = client.db('carrefour');
    const collection = db.collection('producttypes');

    try {
        console.log('Conectado a MongoDB');

        // Limpiar el campo 'products' de todos los documentos
        const result = await collection.updateMany(
            {}, // Todos los documentos
            {
                $set: {
                    products: [], // Array vacío
                    last_updated: new Date()
                }
            }
        );

        console.log(`✓ Limpiados campos 'products' de ${result.modifiedCount} documentos en producttypes`);

        // Verificar algunos ejemplos
        const examples = await collection.find({}).limit(5).toArray();
        console.log('\nEjemplos de productTypes después de limpiar:');
        examples.forEach((pt, i) => {
            console.log(`${i + 1}. ${pt.name} (${pt.subcategory}) - ${pt.products ? pt.products.length : 0} productos`);
        });

    } catch (error) {
        console.error('Error limpiando campos:', error);
    } finally {
        await client.close();
        console.log('Conexión cerrada');
    }
}

clearProductsField();