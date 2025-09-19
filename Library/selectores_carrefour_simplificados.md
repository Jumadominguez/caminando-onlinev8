# Lista Simplificada de Selectores para Carrefour

Esta lista contiene los selectores CSS identificados para el menú de filtros de Carrefour, basados en el análisis del HTML del archivo `menuFiltro.md`. Estos selectores permiten automatizar la extracción de categorías, subcategorías, marcas y tipos de producto.

## Container Selectors
- `.valtech-carrefourar-search-result-3-x-filter__container--brand` - Contenedor de filtros de marca
- `.valtech-carrefourar-search-result-3-x-filter__container--category-2` - Contenedor de filtros de categoría nivel 2
- `.valtech-carrefourar-search-result-3-x-filter__container--category-3` - Contenedor de filtros de categoría nivel 3
- `.valtech-carrefourar-search-result-3-x-filter__container--tipo-de-producto` - Contenedor de filtros de tipo de producto
- `.valtech-carrefourar-search-result-3-x-filter__container--priceRange` - Contenedor de filtros de rango de precio

## Input Patterns
- `input[id^="brand-"]` - Inputs de selección de marcas
- `input[id^="category-2-"]` - Inputs de selección de categorías nivel 2
- `input[id^="category-3-"]` - Inputs de selección de categorías nivel 3
- `input[id^="tipo-de-producto-"]` - Inputs de selección de tipos de producto

## Content Selectors
- `.valtech-carrefourar-search-result-3-x-filterContent` - Contenido general del filtro
- `.valtech-carrefourar-search-result-3-x-filterItem` - Elementos individuales del filtro

## Control Selectors
- `.valtech-carrefourar-search-result-3-x-seeMoreButton` - Botón "Ver Más" para expandir listas
- `.valtech-carrefourar-search-result-3-x-filterApplyButtonWrapper` - Contenedor del botón de aplicar filtros

## Notas de Uso
- Utiliza estos selectores en scripts de scraping con Playwright para interactuar con los filtros de Carrefour.
- Para listas truncadas, haz clic en el botón "Ver Más" antes de extraer opciones.
- Los patrones de input permiten seleccionar múltiples elementos usando atributos `id` que comienzan con el prefijo correspondiente.

Fecha de creación: Septiembre 19, 2025
