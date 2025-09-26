from pymongo import MongoClient
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    client = MongoClient('mongodb://localhost:27017/')
    db = client['carrefour']
    products_collection = db['products']

    # Contar productos por tipo
    pipeline = [
        {'$group': {'_id': '$product_type', 'count': {'$sum': 1}}},
        {'$sort': {'count': -1}}
    ]

    results = list(products_collection.aggregate(pipeline))

    total_products = products_collection.count_documents({})
    logger.info(f'📊 Total productos en colección: {total_products}')

    # Buscar específicamente productos de tipo "Adaptador USB"
    usb_adapters = products_collection.count_documents({'product_type': 'Adaptador USB'})
    logger.info(f'🔌 Productos de tipo "Adaptador USB": {usb_adapters}')

    if results:
        logger.info('📋 Top 5 tipos de producto:')
        for result in results[:5]:
            logger.info(f'  {result["_id"]}: {result["count"]} productos')

    client.close()

except Exception as e:
    logger.error(f'❌ Error consultando base de datos: {e}')