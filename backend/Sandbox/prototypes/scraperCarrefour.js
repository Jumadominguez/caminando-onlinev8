#!/usr/bin/env node

/**
 * Scraper de categorías de Carrefour Argentina
 * Uso: node scraperCarrefour.js [comando]
 *
 * Comandos disponibles:
 * - scrape: Ejecuta el scraping completo (default)
 * - get: Muestra las categorías guardadas en la DB
 */

const { firefox } = require('playwright');
const mongoose = require('mongoose');
const { Category } = require('../../src/models/Category');

async function scrapeCarrefourCategories() {
  console.log('🚀 Iniciando scraping de categorías de Carrefour...');
  console.log('📅 Fecha:', new Date().toLocaleString('es-AR'));
  console.log('🎯 Objetivo: Extraer todas las categorías principales y guardar en DB');

  // Conectar a la base de datos
  try {
    await mongoose.connect(process.env.MONGODB_URI || 'mongodb://localhost:27017/carrefour');
    console.log('✅ Conectado a MongoDB (Base de datos: carrefour)');
  } catch (error) {
    console.error('❌ Error conectando a MongoDB:', error.message);
    return;
  }

  const browser = await firefox.launch({
    headless: false,
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });

  try {
    const page = await browser.newPage();
    await page.setViewportSize({ width: 1280, height: 720 });

    // Paso 1: Navegar a Carrefour
    console.log('\n📍 Paso 1: Navegando a Carrefour...');

    // Intentar navegación con retry
    let navigationSuccess = false;
    for (let attempt = 1; attempt <= 3; attempt++) {
      try {
        console.log(`🔄 Intento ${attempt}/3 de navegación...`);
        await page.goto('https://www.carrefour.com.ar', {
          waitUntil: 'networkidle',
          timeout: 90000 // 90 segundos
        });
        navigationSuccess = true;
        break;
      } catch (error) {
        console.log(`⚠️  Intento ${attempt} falló: ${error.message}`);
        if (attempt < 3) {
          console.log('⏳ Esperando antes del siguiente intento...');
          await page.waitForTimeout(5000);
        }
      }
    }

    if (!navigationSuccess) {
      throw new Error('No se pudo cargar la página después de 3 intentos');
    }

    console.log('✅ Página cargada');

    // Paso 2: Abrir menú de categorías
    console.log('\n🎯 Paso 2: Abriendo menú de categorías...');
    const menuSelector = 'button.carrefourar-mega-menu-0-x-triggerContainer:has-text("Categorías")';

    console.log('⏳ Esperando que el selector esté disponible...');
    await page.waitForSelector(menuSelector, { timeout: 20000 });

    console.log('👆 Intentando hacer click en el menú...');
    await page.locator(menuSelector).scrollIntoViewIfNeeded();

    // Intentar click con retry
    let clickSuccess = false;
    for (let attempt = 1; attempt <= 3; attempt++) {
      try {
        console.log(`🔄 Intento ${attempt}/3 de hacer click...`);
        await page.click(menuSelector, { timeout: 5000 });
        clickSuccess = true;
        break;
      } catch (error) {
        console.log(`⚠️  Intento ${attempt} falló: ${error.message}`);
        if (attempt < 3) {
          console.log('⏳ Esperando antes del siguiente intento...');
          await page.waitForTimeout(2000);
        }
      }
    }

    if (!clickSuccess) {
      throw new Error('No se pudo hacer click en el menú de categorías después de 3 intentos');
    }

    console.log('⏳ Esperando que el menú se despliegue completamente...');
    await page.waitForTimeout(5000);
    console.log('✅ Menú abierto');

    // Paso 3: Extraer todas las categorías principales
    console.log('\n📋 Paso 3: Extrayendo categorías principales...');
    const categorySelector = '.carrefourar-mega-menu-0-x-styledLink';

    const categories = await page.$$eval(categorySelector, (elements) => {
      return elements.map((el, index) => {
        const text = el.textContent?.trim();
        const href = el.href;

        if (!text || !href || href === '#') return null;

        let slug = '';
        try {
          if (href && href.startsWith('http')) {
            const url = new URL(href);
            slug = url.pathname.split('/').pop() || '';
          }
        } catch (error) {
          // Ignorar errores de URL inválida
        }

        return {
          id: index + 1,
          name: text,
          url: href,
          slug: slug,
          supermarket: 'Carrefour'
        };
      }).filter(cat => cat !== null);
    });

    console.log(`📊 Encontradas ${categories.length} categorías totales`);

    // Paso 4: Filtrar solo categorías principales
    console.log('\n🔍 Paso 4: Filtrando categorías principales...');

    const mainCategories = categories.filter(cat => {
      const url = cat.url;
      const name = cat.name.toLowerCase();

      // Excluir elementos promocionales
      if (name.includes('ofertas') && !name.includes('indumentaria')) return false;
      if (name.includes('destacados')) return false;

      // Solo URLs directas (categorías principales)
      const urlParts = url.replace('https://www.carrefour.com.ar/', '').split('/');
      if (urlParts.length > 1 && !urlParts[1].includes('?') && !urlParts[1].includes('&')) {
        return false;
      }

      // Categorías principales conocidas
      const mainCategoryNames = [
        'electro y tecnología', 'bazar y textil', 'almacén', 'desayuno y merienda',
        'bebidas', 'lácteos y productos frescos', 'carnes y pescados', 'frutas y verduras',
        'panadería', 'congelados', 'limpieza', 'perfumería', 'mundo bebé', 'mascotas',
        'indumentaria', 'librería', 'automotor'
      ];

      return mainCategoryNames.some(mainName =>
        name.includes(mainName) || mainName.includes(name)
      );
    });

    console.log(`✅ Filtradas ${mainCategories.length} categorías principales`);

    // Paso 5: Guardar en base de datos una por una
    console.log('\n💾 Paso 5: Guardando categorías en base de datos...');

    let savedCount = 0;
    let updatedCount = 0;

    for (const categoryData of mainCategories) {
      try {
        console.log(`\n🔄 Procesando: ${categoryData.name}`);

        // Verificar si la categoría ya existe
        const existingCategory = await Category.findOne({
          slug: categoryData.slug,
          supermarket: 'Carrefour'
        });

        if (existingCategory) {
          // Actualizar categoría existente
          existingCategory.name = categoryData.name;
          existingCategory.url = categoryData.url;
          existingCategory.lastScraped = new Date();
          await existingCategory.save();
          updatedCount++;
          console.log(`   ✅ Actualizada: ${categoryData.name}`);
        } else {
          // Crear nueva categoría
          const newCategory = new Category({
            name: categoryData.name,
            slug: categoryData.slug,
            url: categoryData.url,
            supermarket: 'Carrefour',
            level: 1,
            isActive: true,
            lastScraped: new Date()
          });

          await newCategory.save();
          savedCount++;
          console.log(`   ✅ Guardada: ${categoryData.name}`);
        }

        // Pequeña pausa entre inserciones para evitar sobrecargar la DB
        await new Promise(resolve => setTimeout(resolve, 100));

      } catch (error) {
        console.error(`   ❌ Error guardando ${categoryData.name}:`, error.message);
      }
    }

    // Paso 6: Resumen final
    console.log('\n📊 Resumen del proceso:');
    console.log(`   📋 Categorías encontradas: ${categories.length}`);
    console.log(`   🎯 Categorías principales: ${mainCategories.length}`);
    console.log(`   💾 Nuevas categorías: ${savedCount}`);
    console.log(`   🔄 Categorías actualizadas: ${updatedCount}`);
    console.log(`   ✅ Proceso completado exitosamente`);

    // Mostrar lista de categorías guardadas
    console.log('\n📋 Lista de categorías principales guardadas:');
    const savedCategories = await Category.find({
      supermarket: 'Carrefour',
      level: 1,
      isActive: true
    }).sort({ name: 1 });

    savedCategories.forEach((cat, index) => {
      console.log(`${index + 1}. ${cat.name} (${cat.slug})`);
    });

  } catch (error) {
    console.error('\n❌ Error durante el scraping:', error.message);

    if (error.name === 'TimeoutError') {
      console.log('💡 Posible causa: El sitio está lento o cambió su estructura');
    } else if (error.message.includes('MongoError')) {
      console.log('💡 Posible causa: Problemas de conexión con la base de datos');
    }

  } finally {
    console.log('\n🔒 Cerrando conexiones...');
    await browser.close();
    await mongoose.connection.close();
    console.log('✅ Scraping finalizado');
  }
}

// Función para obtener categorías guardadas (útil para debugging)
async function getSavedCategories() {
  try {
    await mongoose.connect(process.env.MONGODB_URI || 'mongodb://localhost:27017/carrefour');
    const categories = await Category.find({
      supermarket: 'Carrefour',
      level: 1,
      isActive: true
    }).sort({ name: 1 });

    console.log(`📋 Categorías guardadas en DB (carrefour): ${categories.length}`);
    categories.forEach((cat, index) => {
      console.log(`${index + 1}. ${cat.name} - ${cat.url}`);
    });

    await mongoose.connection.close();
  } catch (error) {
    console.error('❌ Error obteniendo categorías:', error.message);
  }
}

// Ejecutar el scraper si se llama directamente
if (require.main === module) {
  const command = process.argv[2] || 'scrape';

  console.log('🛒 Carrefour Categories Scraper');
  console.log('===============================');
  console.log(`Comando: ${command}`);
  console.log('');

  if (command === 'get') {
    console.log('📋 Obteniendo categorías guardadas...');
    getSavedCategories();
  } else if (command === 'scrape') {
    console.log('🚀 Iniciando scraping de categorías...');
    scrapeCarrefourCategories();
  } else {
    console.log('❌ Comando no reconocido. Use: scrape o get');
    console.log('Ejemplos:');
    console.log('  node scraperCarrefour.js scrape  # Ejecuta el scraping');
    console.log('  node scraperCarrefour.js get     # Muestra categorías guardadas');
    process.exit(1);
  }
}

module.exports = { scrapeCarrefourCategories, getSavedCategories };
