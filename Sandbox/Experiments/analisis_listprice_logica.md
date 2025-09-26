# Análisis de Lógica para Campo "listPrice" en almacen_scraper.py

## Resumen Ejecutivo

El script `almacen_scraper.py` implementa una lógica robusta para extraer precios de productos de Carrefour Argentina, enfocándose en el campo `listPrice` que representa el precio de lista o precio anterior del producto.

## Estructura de Precios en Carrefour

Carrefour utiliza un sistema de precios que incluye:
- **Precio de venta actual** (selling price): Precio al que se vende actualmente
- **Precio de lista** (list price): Precio anterior tachado (cuando hay descuento)

## Lógica de Extracción de Precios

### Función Principal: `extract_prices(element)`

Esta función es el punto de entrada para la extracción de precios:

```python
def extract_prices(self, element):
    """Extrae información de precios del producto"""
    prices = {}

    try:
        # Buscar contenedor de precios
        price_container = element.find_element(By.CLASS_NAME, 'valtech-carrefourar-product-price-0-x-priceContainer')
        
        # 1. Extraer precio de venta (siempre presente)
        try:
            selling_price_element = price_container.find_element(By.CLASS_NAME, 'valtech-carrefourar-product-price-0-x-sellingPrice')
            selling_price_text = self.extract_price_from_currency_container(selling_price_element)
            if selling_price_text:
                prices['price'] = self.parse_argentine_price(selling_price_text)
                prices['sellingPrice'] = prices['price']
        except NoSuchElementException:
            logging.warning("Precio de venta no encontrado")

        # 2. Extraer precio tachado (precio anterior, si existe)
        try:
            list_price_element = price_container.find_element(By.CLASS_NAME, 'valtech-carrefourar-product-price-0-x-listPrice')
            list_price_text = self.extract_price_from_currency_container(list_price_element)
            if list_price_text:
                prices['listPrice'] = self.parse_argentine_price(list_price_text)
        except NoSuchElementException:
            logging.debug("Precio de lista no encontrado, usando precio de venta como listPrice")
            # 3. Fallback: usar precio de venta como listPrice
            selling_price_element = element.find_element(By.CLASS_NAME, 'valtech-carrefourar-product-price-0-x-sellingPriceValue')
            selling_price_text = self.extract_price_from_currency_container(selling_price_element)
            if selling_price_text:
                prices['listPrice'] = self.parse_argentine_price(selling_price_text)
                logging.debug(f"Usando precio de venta como listPrice: {prices['listPrice']}")

    except Exception as e:
        logging.error(f"Error extrayendo precios: {e}")

    return prices
```

### Algoritmo Paso a Paso

1. **Buscar Contenedor de Precios**
   - Localiza el elemento con clase `valtech-carrefourar-product-price-0-x-priceContainer`
   - Este contenedor agrupa todos los elementos de precio del producto

2. **Extraer Precio de Venta (Obligatorio)**
   - Busca elemento con clase `valtech-carrefourar-product-price-0-x-sellingPrice`
   - Extrae el texto usando `extract_price_from_currency_container()`
   - Convierte a float usando `parse_argentine_price()`
   - Asigna tanto a `price` como `sellingPrice`

3. **Extraer Precio de Lista (Opcional)**
   - Busca elemento con clase `valtech-carrefourar-product-price-0-x-listPrice`
   - Si existe, extrae y convierte el precio tachado
   - Este es el precio anterior cuando hay descuento

4. **Fallback Strategy**
   - Si no se encuentra precio de lista, usa el precio de venta como `listPrice`
   - Busca elemento alternativo con clase `valtech-carrefourar-product-price-0-x-sellingPriceValue`
   - Garantiza que siempre haya un valor para `listPrice`

### Función Auxiliar: `extract_price_from_currency_container(container_element)`

Extrae el precio formateado de un contenedor de moneda:

```python
def extract_price_from_currency_container(self, container_element):
    """Extrae precio de un contenedor de moneda"""
    try:
        spans = container_element.find_elements(By.XPATH, './/span[contains(@class, "valtech-carrefourar-product-price-0-x-")]')
        price_parts = []

        for span in spans:
            classes = span.get_attribute('class')
            text = span.text.strip()

            if 'currencyCode' in classes:      # Símbolo de moneda ($)
                price_parts.append(text)
            elif 'currencyInteger' in classes: # Parte entera (123)
                price_parts.append(text)
            elif 'currencyGroup' in classes:   # Separador de miles (.)
                price_parts.append(text)
            elif 'currencyDecimal' in classes: # Separador decimal (,)
                price_parts.append(text)
            elif 'currencyFraction' in classes:# Parte decimal (99)
                price_parts.append(text)

        return ''.join(price_parts)
    except Exception as e:
        logging.error(f"Error extrayendo precio del contenedor: {e}")
        return None
```

**Componentes identificados:**
- `currencyCode`: Símbolo de moneda (ARS, $)
- `currencyInteger`: Parte entera del precio
- `currencyGroup`: Punto separador de miles
- `currencyDecimal`: Coma separador decimal
- `currencyFraction`: Parte decimal (centavos)

### Función Auxiliar: `parse_argentine_price(price_str)`

Convierte string de precio argentino a float:

```python
def parse_argentine_price(self, price_str):
    """Parsea precio argentino ($X.XXX,XX) a float"""
    try:
        # Remover símbolo de moneda y espacios
        clean_price = re.sub(r'[^\d.,]', '', price_str)
        # Reemplazar punto como separador de miles y coma como decimal
        clean_price = clean_price.replace('.', '').replace(',', '.')
        return float(clean_price)
    except (ValueError, AttributeError):
        logging.error(f"Error parseando precio: {price_str}")
        return 0.0
```

**Formato esperado:** `$1.234,56` → `1234.56`

## Campos Resultantes en el Producto

Después de la extracción, el objeto producto incluye:

```javascript
{
  "price": 1234.56,        // Precio de venta actual (float)
  "sellingPrice": 1234.56, // Mismo que price
  "listPrice": 1499.99,    // Precio de lista (float) - puede ser igual a price si no hay descuento
  // ... otros campos
}
```

## Estrategias de Robustez

1. **Múltiples Selectores**: Usa diferentes clases CSS para encontrar elementos de precio
2. **Fallback Hierárquico**: Si no encuentra precio de lista, usa precio de venta
3. **Manejo de Errores**: Logging detallado para debugging
4. **Parsing Robusto**: Maneja diferentes formatos de precio argentino

## Casos de Uso

- **Producto con descuento**: `listPrice` > `price`
- **Producto sin descuento**: `listPrice` = `price`
- **Producto con precio único**: Solo `price`, `listPrice` toma el mismo valor

Esta lógica garantiza que siempre se tenga un valor válido para `listPrice`, priorizando el precio tachado cuando existe, y usando el precio de venta como fallback.</content>
<parameter name="filePath">d:\dev\caminando-onlinev8\Sandbox\Experiments\analisis_listprice_logica.md