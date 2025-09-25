#!/usr/bin/env node

const { MongoClient } = require('mongodb');

async function updateProductTypesSchema() {
    const client = new MongoClient('mongodb://localhost:27017/');
    const db = client.db('carrefour');
    const collection = db.collection('producttypes');

    try {
        console.log('Conectado a MongoDB');

        // Agregar campo 'products' como array vacío a todos los documentos que no lo tengan
        const result = await collection.updateMany(
            { products: { $exists: false } },
            {
                $set: {
                    products: [],
                    last_updated: new Date()
                }
            }
        );

        console.log(`✓ Actualizados ${result.modifiedCount} productTypes para agregar campo 'products'`);

        // Verificar algunos ejemplos
        const examples = await collection.find({}).limit(3).toArray();
        console.log('\nEjemplos de productTypes actualizados:');
        examples.forEach((pt, i) => {
            console.log(`${i + 1}. ${pt.name} (${pt.subcategory}) - ${pt.products ? pt.products.length : 0} productos`);
        });

    } catch (error) {
        console.error('Error actualizando esquema:', error);
    } finally {
        await client.close();
        console.log('Conexión cerrada');
    }
}

updateProductTypesSchema();