#!/usr/bin/env python3
"""
Script para limpiar todos los documentos de la colección 'products' en la base de datos 'carrefour'
"""
import logging
from pymongo import MongoClient

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def clear_products_collection():
    """Elimina todos los documentos de la colección 'products' en la base de datos 'carrefour'"""
    try:
        # Conectar a MongoDB
        client = MongoClient('mongodb://localhost:27017/')
        db = client['carrefour']
        products_collection = db['products']

        # Contar documentos antes de eliminar
        count_before = products_collection.count_documents({})
        logging.info(f"Documentos en la colección 'products' antes de limpiar: {count_before}")

        # Eliminar todos los documentos
        result = products_collection.delete_many({})

        # Verificar resultado
        logging.info(f"Documentos eliminados: {result.deleted_count}")

        # Contar documentos después de eliminar
        count_after = products_collection.count_documents({})
        logging.info(f"Documentos en la colección 'products' después de limpiar: {count_after}")

        # Cerrar conexión
        client.close()

        logging.info("✅ Limpieza de la colección 'products' completada exitosamente")

    except Exception as e:
        logging.error(f"❌ Error al limpiar la colección 'products': {e}")
        raise

if __name__ == "__main__":
    clear_products_collection()