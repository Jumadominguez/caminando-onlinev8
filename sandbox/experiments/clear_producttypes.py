#!/usr/bin/env python3
"""
Script para limpiar la colección producttypes de la base de datos carrefour
"""
from pymongo import MongoClient
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def clear_producttypes_collection():
    """Clear all documents from the producttypes collection"""
    try:
        client = MongoClient('mongodb://localhost:27017/')
        db = client['carrefour']
        collection = db['producttypes']

        result = collection.delete_many({})
        logging.info(f"✓ Cleared {result.deleted_count} documents from producttypes collection")

        client.close()
        return True

    except Exception as e:
        logging.error(f"Error clearing producttypes collection: {e}")
        return False

if __name__ == "__main__":
    logging.info("=== LIMPIANDO COLECCIÓN PRODUCTTYPES ===")
    if clear_producttypes_collection():
        logging.info("✅ Colección producttypes limpiada exitosamente")
    else:
        logging.error("❌ Error al limpiar la colección producttypes")