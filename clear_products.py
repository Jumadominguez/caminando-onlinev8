from pymongo import MongoClient
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    # Conectar a MongoDB
    client = MongoClient('mongodb://localhost:27017/')
    db = client['carrefour']

    # Limpiar colección products
    products_collection = db['products']
    result = products_collection.delete_many({})

    logger.info(f'🗑️ Eliminados {result.deleted_count} documentos de la colección products')

    # Verificar que está vacía
    count = products_collection.count_documents({})
    logger.info(f'📊 Documentos restantes en products: {count}')

    client.close()

except Exception as e:
    logger.error(f'❌ Error limpiando colección: {e}')