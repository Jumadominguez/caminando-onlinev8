const { firefox } = require('playwright');

async function expandSubcategoryFilter() {
  const browser = await firefox.launch({ headless: false }); // headless: false para ver el navegador
  const page = await browser.newPage();

  try {
    // Navegar a una categoría principal de Carrefour (ejemplo: Almacén)
    await page.goto('https://www.carrefour.com.ar/almacen', { waitUntil: 'domcontentloaded', timeout: 60000 });

    console.log('Página cargada, título:', await page.title());

    // Esperar a que el filtro de Sub-Categoría esté disponible
    await page.waitForSelector('.valtech-carrefourar-search-result-3-x-filterAvailable', { timeout: 10000 });

    // Buscar y hacer clic en el botón para expandir el filtro de Sub-Categoría
    const filterButton = page.locator('[role="button"]').filter({ hasText: 'Sub-Categoría' });
    await filterButton.click();

    // Esperar un momento para que se expanda
    await page.waitForTimeout(2000);

    // Navegar hasta el final del elemento expandido
    const subcategoryContainer = page.locator('.valtech-carrefourar-search-result-3-x-filter').filter({ hasText: 'Sub-Categoría' });
    console.log('Contenedor encontrado:', await subcategoryContainer.count());
    const filterContent = subcategoryContainer.locator('.valtech-carrefourar-search-result-3-x-filterContent');
    await filterContent.evaluate(el => el.scrollTop = el.scrollHeight);

    // Esperar a que se cargue contenido adicional
    await page.waitForTimeout(3000);

    // Verificar si hay un botón "Ver Más" y clicarlo si existe
    const seeMoreButton = subcategoryContainer.locator('[role="button"]').filter({ hasText: 'Ver más' });
    console.log('Botón Ver Más encontrado:', await seeMoreButton.count());
    if (await seeMoreButton.count() > 0) {
      await seeMoreButton.click();
      console.log('Botón "Ver Más" clicado. Esperando para verificar...');
      await page.waitForTimeout(10000); // Pausa de 10 segundos para verificar
    } else {
      console.log('No se encontró botón "Ver Más".');
    }

    console.log('Filtro de Sub-Categoría expandido exitosamente.');

  } catch (error) {
    console.error('Error al expandir el filtro:', error);
  } finally {
    await browser.close();
  }
}

expandSubcategoryFilter();
