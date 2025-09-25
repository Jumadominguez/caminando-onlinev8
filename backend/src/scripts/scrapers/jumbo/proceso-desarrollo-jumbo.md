# Proceso de Desarrollo de Scripts para Jumbo

Este documento detalla el proceso para replicar y adaptar los scripts de scraping de Carrefour para Jumbo, considerando las diferencias específicas de la plataforma Jumbo.

## 📋 Información General

**Fecha de creación**: Septiembre 2025
**Versión**: 1.0.0
**Estado**: Documento de planificación
**Alcance**: Scripts de scraping para Jumbo
**Diferencias clave con Carrefour**:
- **Menú de Categorías**: Se activa con `hover` en lugar de `click`
- **Estructura DOM**: Diferente estructura HTML y selectores CSS
- **Base de datos**: Usar base de datos `jumbo` en lugar de `carrefour`

## 🎯 Scripts a Desarrollar

### 1. `jumbo_step1_supermarket.py`
**Propósito**: Extraer información básica del supermercado Jumbo
**Basado en**: `carrefour_step1_supermarket.py`

**Adaptaciones necesarias**:
- Cambiar URLs de Carrefour a Jumbo
- Adaptar selectores CSS para la estructura de Jumbo
- Usar base de datos `jumbo` en lugar de `carrefour`
- Considerar diferencias en el layout de la página principal

**Pasos de desarrollo**:
1. Crear script base copiando `carrefour_step1_supermarket.py`
2. Cambiar todas las URLs de `carrefour.com.ar` a `jumbo.com.ar`
3. Analizar HTML de Jumbo para identificar selectores correctos
4. Adaptar funciones de extracción de datos
5. Cambiar nombre de base de datos a `jumbo`
6. Probar y validar funcionamiento

### 2. `jumbo_step2_categories.py`
**Propósito**: Extraer todas las categorías principales de Jumbo
**Basado en**: `carrefour_step2_categories.py`

**Adaptaciones necesarias**:
- **Menú hover**: Implementar lógica de `hover` en lugar de `click`
- Adaptar selectores para el menú desplegable de Jumbo
- Usar `ActionChains` de Selenium para simular hover
- Cambiar base de datos a `jumbo`

**Pasos de desarrollo**:
1. Copiar `carrefour_step2_categories.py` como base
2. Cambiar URLs a Jumbo
3. Implementar función `hover_over_categories_menu()`:
   ```python
   from selenium.webdriver.common.action_chains import ActionChains

   def hover_over_categories_menu(driver):
       # Localizar el elemento del menú de categorías
       menu_element = WebDriverWait(driver, 10).until(
           EC.presence_of_element_located((By.CSS_SELECTOR, "selector-del-menu"))
       )
       # Realizar hover
       actions = ActionChains(driver)
       actions.move_to_element(menu_element).perform()
       time.sleep(2)  # Esperar que se despliegue el menú
   ```
4. Adaptar selectores para extraer categorías del menú hover
5. Cambiar base de datos a `jumbo`
6. Probar extracción de categorías

### 3. `jumbo_step3_subcategory.py`
**Propósito**: Extraer subcategorías para cada categoría de Jumbo
**Basado en**: `carrefour_step3_subcategory.py`

**Adaptaciones necesarias**:
- Mantener lógica de hover para acceder a categorías
- Adaptar navegación a subcategorías
- Cambiar selectores CSS según estructura de Jumbo
- Usar base de datos `jumbo`

**Pasos de desarrollo**:
1. Copiar `carrefour_step3_subcategory.py` como base
2. Adaptar función de navegación con hover
3. Modificar selectores para encontrar subcategorías
4. Implementar lógica de extracción de subcategorías
5. Cambiar base de datos a `jumbo`
6. Validar que se extraigan todas las subcategorías por categoría

### 4. `jumbo_step4_producttypes.py`
**Propósito**: Extraer tipos de producto para cada subcategoría de Jumbo
**Basado en**: `carrefour_step4_producttypes.py` y `carrefour_step4_md_instructions.py`

**Adaptaciones necesarias**:
- Implementar navegación completa con hover para categorías
- Adaptar filtros y paneles de Jumbo
- Modificar lógica de expansión de menús
- Cambiar selectores para tipos de producto
- Usar base de datos `jumbo`

**Pasos de desarrollo**:
1. Copiar `carrefour_step4_md_instructions.py` como base (versión más robusta)
2. Adaptar todas las funciones de navegación con hover
3. Modificar selectores CSS para:
   - Panel de filtros
   - Menú de subcategorías
   - Contenedor de tipos de producto
   - Botones de expansión
4. Implementar función específica para hover:
   ```python
   def navigate_to_category_with_hover(driver, category_url):
       driver.get(category_url)
       time.sleep(3)
       hover_over_categories_menu(driver)
       # Continuar con navegación específica
   ```
5. Cambiar base de datos a `jumbo`
6. Probar procesamiento completo de tipos de producto

## 🔧 Consideraciones Técnicas para Hover

### Implementación de Hover en Selenium
```python
from selenium.webdriver.common.action_chains import ActionChains

def hover_and_click_category(driver, category_selector):
    """Realizar hover sobre menú y hacer click en categoría"""
    try:
        # Localizar menú principal
        menu = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "selector-menu-principal"))
        )

        # Realizar hover
        actions = ActionChains(driver)
        actions.move_to_element(menu).perform()

        # Esperar que aparezca el submenú
        time.sleep(2)

        # Localizar y hacer click en la categoría específica
        category = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, category_selector))
        )
        category.click()

        return True
    except Exception as e:
        logging.error(f"Error en hover y click: {e}")
        return False
```

### Selectores Específicos de Jumbo
- Analizar `jumbohomeOuterHTML.md` para identificar selectores correctos
- Usar herramientas de desarrollo del navegador para inspeccionar elementos
- Considerar que los selectores pueden cambiar con actualizaciones del sitio

## 📊 Estructura de Base de Datos

### Base de Datos: `jumbo`
**Colecciones**:
- `supermarket`: Información del supermercado
- `categories`: Categorías principales
- `subcategories`: Subcategorías por categoría
- `producttypes`: Tipos de producto por subcategoría

### Campos por Colección
```javascript
// supermarket
{
  name: "Jumbo",
  url: "https://www.jumbo.com.ar",
  logo: "...",
  // ... otros campos
}

// categories
{
  name: "Almacén",
  url: "https://www.jumbo.com.ar/almacen",
  // ... otros campos
}

// subcategories
{
  category_id: ObjectId,
  name: "Arroz y Legumbres",
  url: "https://www.jumbo.com.ar/almacen/arroz-legumbres",
  // ... otros campos
}

// producttypes
{
  subcategory_id: ObjectId,
  name: "Arroz",
  // ... otros campos
}
```

## 🔄 Flujo de Desarrollo

### Fase 1: Análisis y Planificación
1. **Analizar HTML**: Estudiar `jumbohomeOuterHTML.md` y `categoryexample-outerhtml.md`
2. **Identificar diferencias**: Comparar con estructura de Carrefour
3. **Documentar selectores**: Crear lista de selectores CSS necesarios
4. **Planificar hover**: Diseñar lógica de navegación con hover

### Fase 2: Desarrollo Paso a Paso
1. **Step 1**: Desarrollar `jumbo_step1_supermarket.py`
2. **Step 2**: Desarrollar `jumbo_step2_categories.py` (con hover)
3. **Step 3**: Desarrollar `jumbo_step3_subcategory.py`
4. **Step 4**: Desarrollar `jumbo_step4_producttypes.py`

### Fase 3: Testing y Validación
1. **Test individual**: Probar cada script por separado
2. **Test integrado**: Verificar flujo completo
3. **Validación de datos**: Confirmar que se guarden correctamente en BD
4. **Manejo de errores**: Probar casos edge y recuperación

### Fase 4: Optimización
1. **Performance**: Optimizar tiempos de espera y navegación
2. **Robustez**: Mejorar manejo de errores y reintentos
3. **Logging**: Implementar logging detallado
4. **Documentación**: Actualizar este documento con hallazgos

## 🎯 Diferencias Clave con Carrefour

| Aspecto | Carrefour | Jumbo |
|---------|-----------|-------|
| Menú Categorías | Click | **Hover** |
| Base de Datos | `carrefour` | `jumbo` |
| URL Base | `carrefour.com.ar` | `jumbo.com.ar` |
| Estructura DOM | Conocida | **Por analizar** |
| Panel Filtros | Click para abrir | **Por determinar** |

## 📝 Próximos Pasos

1. **Análisis de HTML**: Profundizar en `jumbohomeOuterHTML.md` y `categoryexample-outerhtml.md`
2. **Identificación de selectores**: Documentar todos los selectores CSS necesarios
3. **Implementación de hover**: Crear funciones reutilizables para navegación hover
4. **Desarrollo del Step 1**: Comenzar con el script más simple
5. **Iteración**: Desarrollar cada step probando y ajustando según sea necesario

## 📚 Referencias

- **Scripts base**: `backend/src/scripts/scrapers/carrefour/`
- **Documentos de análisis**: `jumbohomeOuterHTML.md`, `categoryexample-outerhtml.md`
- **Base de datos**: MongoDB `jumbo`
- **Framework**: Selenium WebDriver con Firefox

---

**Este documento debe actualizarse a medida que se desarrolla cada script y se descubran nuevas particularidades de Jumbo.**</content>
<parameter name="filePath">d:\dev\caminando-onlinev8\backend\src\scripts\scrapers\jumbo\proceso-desarrollo-jumbo.md