#!/usr/bin/env python3
"""
Analizar subcategorías y tipos de producto asignados
"""

from pymongo import MongoClient

def main():
    client = MongoClient('mongodb://localhost:27017/')
    db = client.carrefour

    print("Análisis de subcategorías y tipos de producto:")
    print("=" * 60)

    products = list(db.products.find({}, {
        'name': 1,
        'subcategory': 1,
        'productType': 1,
        'category': 1
    }))

    # Contadores
    categories = {}
    subcategories = {}
    product_types = {}

    print(f"Total productos: {len(products)}\n")

    for product in products:
        name = product.get('name', 'Sin nombre')
        category = product.get('category', 'Sin categoría')
        subcategory = product.get('subcategory', 'Sin subcategoría')
        product_type = product.get('productType', 'Sin tipo')

        # Contar categorías
        categories[category] = categories.get(category, 0) + 1

        # Contar subcategorías
        subcategories[subcategory] = subcategories.get(subcategory, 0) + 1

        # Contar tipos de producto
        product_types[product_type] = product_types.get(product_type, 0) + 1

        # Mostrar algunos ejemplos
        if len([p for p in products if p.get('subcategory') == subcategory]) <= 3:
            print(f"📦 {name[:50]}...")
            print(f"   Categoría: {category}")
            print(f"   Subcategoría: {subcategory}")
            print(f"   Tipo: {product_type}")
            print()

    print("RESUMEN:")
    print(f"Categorías encontradas: {len(categories)}")
    for cat, count in sorted(categories.items()):
        print(f"  • {cat}: {count} productos")

    print(f"\nSubcategorías encontradas: {len(subcategories)}")
    for sub, count in sorted(subcategories.items()):
        print(f"  • {sub}: {count} productos")

    print(f"\nTipos de producto encontrados: {len(product_types)}")
    for typ, count in sorted(product_types.items()):
        print(f"  • {typ}: {count} productos")

if __name__ == "__main__":
    main()