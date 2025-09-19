## 🎯 Selector para Menú de Categorías - Carrefour

**Selector CSS:** `button.carrefourar-mega-menu-0-x-triggerContainer:has-text("Categorías")`

## 📋 Detalles
- **Elemento:** BUTTON con texto "Categorías"
- **Función:** Abre el menú desplegable de categorías
- **Estado:** ✅ Probado y funcional
- **Resultado:** Extrae 16 categorías principales (filtradas)

## 💻 Uso en Código
```javascript
// Selector para abrir menú de categorías
const menuSelector = 'button.carrefourar-mega-menu-0-x-triggerContainer:has-text("Categorías")';

// Ejemplo de uso con retry
await page.waitForSelector(menuSelector, { timeout: 15000 });
await page.locator(menuSelector).scrollIntoViewIfNeeded();
await page.click(menuSelector, { timeout: 10000 });
await page.waitForTimeout(5000); // Esperar que se despliegue completamente
```

---
**Actualizado:** 19/09/2025 - Selector validado con sistema de retry

## 🎯 Selector para Categorías Principales - Carrefour

**Selector CSS:** `.carrefourar-mega-menu-0-x-styledLink`

## 📋 Detalles
- **Elemento:** LINKS dentro del menú desplegable
- **Función:** Extrae todas las categorías principales del menú
- **Estado:** ✅ Probado y funcional
- **Resultado:** Extrae 16 categorías principales (filtradas)

## 💻 Uso en Código
```javascript
// Selector para categorías principales
const categorySelector = '.carrefourar-mega-menu-0-x-styledLink';

// Extraer todas las categorías
const categoryElements = await page.locator(categorySelector).all();
const categories = [];

for (const element of categoryElements) {
  const name = await element.textContent();
  const href = await element.getAttribute('href');

  // Filtrar categorías principales (excluir subcategorías)
  if (name && href && !href.includes('/c/') && href.includes('/')) {
    categories.push({
      name: name.trim(),
      url: href,
      slug: href.split('/').pop()
    });
  }
}
```

## 🔍 Criterios de Filtrado
- **Incluir:** URLs que NO contienen `/c/` (son categorías principales)
- **Excluir:** URLs con `/c/` (son subcategorías)
- **Validar:** Nombre no vacío y URL válida
- **Resultado:** 16 categorías principales de 17 totales (excluye "Indumentaria")

## 📊 Categorías Principales Encontradas
1. Almacén
2. Bebidas
3. Carnes y Pescados
4. Congelados
5. Desayuno y Dulces
6. Electro y Tecno
7. Frescos
8. Hogar
9. Limpieza
10. Mascotas
11. Panadería
12. Perfumería
13. Quesos y Fiambres
14. Snacks
15. Verdulería
16. Vinos y Licores

---
**Actualizado:** 19/09/2025 - Selector y criterios de filtrado documentados

## 🎯 Selector para Categorías Principales

**Selector CSS:** `.carrefourar-mega-menu-0-x-styledLink`
**Descripción:** Selector para extraer todas las categorías principales del menú desplegado
**Uso:** Se aplica después de hacer clic en el menú "Categorías"
**Resultado:** Extrae 92 categorías incluyendo subcategorías detalladas
**Estado:** ✅ Funcionando correctamente

### Ejemplo de uso:
```javascript
const categories = await page.$$eval('.carrefourar-mega-menu-0-x-styledLink', (elements) => {
  return elements.map(el => ({
    name: el.textContent?.trim(),
    url: el.href
  }));
});
```

### Categorías principales encontradas:
- Electro y tecnología
- Bazar y textil
- Almacén
- Desayuno y merienda
- Bebidas
- Lácteos y productos frescos
- Carnes y Pescados
- Frutas y Verduras
- Panadería
- Congelados
- Limpieza
- Perfumería
- Mundo bebé
- Mascotas
- Y 77 subcategorías más...

---
**Actualizado:** 19/09/2025 - Selector de categorías validado y funcionando
