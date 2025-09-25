#!/usr/bin/env python3
"""
Script para procesar la primera categoría de Carrefour siguiendo las instrucciones detalladas
Basado en el proceso documentado en proceso-detallado-carrefour-step4.md
"""
import time
import logging
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pymongo import MongoClient
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def setup_driver():
    """Setup Firefox WebDriver (NO HEADLESS para que el usuario pueda ver)"""
    firefox_options = Options()
    # NO headless - el usuario quiere ver el proceso
    firefox_options.add_argument("--no-sandbox")
    firefox_options.add_argument("--disable-dev-shm-usage")
    firefox_options.add_argument("--window-size=1920,1080")

    geckodriver_path = r"d:\dev\caminando-onlinev8\geckodriver_temp\geckodriver.exe"
    service = Service(geckodriver_path)
    driver = webdriver.Firefox(service=service, options=firefox_options)
    logging.info("WebDriver initialized successfully (NO HEADLESS)")
    return driver

def handle_cookies(driver):
    """Handle cookie popup if present"""
    try:
        accept_buttons = driver.find_elements(By.XPATH, "//button[contains(text(), 'Aceptar') or contains(text(), 'Accept') or contains(text(), 'OK')]")
        for btn in accept_buttons:
            try:
                btn.click()
                logging.info("Clicked cookie accept button")
                time.sleep(2)
                break
            except:
                continue
    except Exception as e:
        logging.warning(f"Could not handle cookie popup: {e}")

def open_filters_panel(driver):
    """Open the filters panel if not already open"""
    try:
        filters_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Filtrar')]"))
        )
        filters_button.click()
        logging.info("Opened filters panel")
        time.sleep(2)
    except:
        logging.info("Filters panel already open or no button found")

def scroll_to_load_filters(driver):
    """Scroll down to ensure filters are loaded"""
    driver.execute_script("window.scrollTo(0, 500);")
    time.sleep(3)
    logging.info("Scrolled down to load filters")

def get_all_categories():
    """Get all categories from MongoDB categories collection"""
    try:
        client = MongoClient('mongodb://localhost:27017/')
        db = client['carrefour']
        collection = db['categories']

        # Get all categories sorted by _id
        categories = list(collection.find({}, {'name': 1, 'url': 1, '_id': 0}, sort=[('_id', 1)]))

        client.close()

        if categories:
            logging.info(f"✓ Retrieved {len(categories)} categories from database:")
            for i, cat in enumerate(categories, 1):
                logging.info(f"  {i}. {cat.get('name')} -> {cat.get('url')}")
            return categories
        else:
            logging.error("No categories found in database")
            return []

    except Exception as e:
        logging.error(f"Error retrieving categories from database: {e}")
        return []

def expand_subcategory_menu_if_collapsed(driver):
    """Revisar si el menú de Sub-Categoría está colapsado y expandirlo si es necesario"""
    try:
        # Find the subcategory container with multiple selectors for robustness
        subcategory_container = None
        selectors = [
            "div.valtech-carrefourar-search-result-3-x-filter__container--category-3",
            "div[data-testid*='category']",
            "div.filter__container--category"
        ]

        for selector in selectors:
            try:
                subcategory_container = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                if subcategory_container:
                    logging.info(f"Found subcategory container with selector: {selector}")
                    break
            except:
                continue

        if not subcategory_container:
            logging.error("No subcategory container found with any selector")
            return None

        # Check if there's an expand button (role='button')
        try:
            expand_button = subcategory_container.find_element(By.CSS_SELECTOR, "div[role='button']")
            if expand_button and expand_button.is_displayed():
                driver.execute_script("arguments[0].scrollIntoView();", expand_button)
                time.sleep(1)
                driver.execute_script("arguments[0].click();", expand_button)
                logging.info("✓ Expanded subcategory menu (was collapsed)")
                time.sleep(2)
            else:
                logging.info("Subcategory menu already expanded")
        except Exception as e:
            logging.info(f"No expand button found for subcategories (already expanded): {e}")

        return subcategory_container

    except Exception as e:
        logging.error(f"Error checking/expanding subcategory menu: {e}")
        return None

def scroll_and_click_ver_mas_subcategories(driver, subcategory_container):
    """Hacer scroll hasta el final del menú Sub-Categoría y encontrar botón 'Ver más N' y darle click"""
    try:
        # Scroll to the bottom of the container
        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight;", subcategory_container)
        time.sleep(2)
        logging.info("Scrolled to bottom of subcategory menu")

        # Look for "Ver más" button - try multiple selectors
        ver_mas_selectors = [
            "button.valtech-carrefourar-search-result-3-x-seeMoreButton",
            "span.vtex-button__label",
            "button:contains('Ver más')",
            "//button[contains(text(), 'Ver más')]",
            "//span[contains(text(), 'Ver más')]"
        ]

        for selector in ver_mas_selectors:
            try:
                if selector.startswith("//"):
                    # XPath selector
                    buttons = driver.find_elements(By.XPATH, selector)
                else:
                    # CSS selector
                    buttons = driver.find_elements(By.CSS_SELECTOR, selector)

                for btn in buttons:
                    text = btn.text.lower()
                    if "ver más" in text or "ver mas" in text:
                        driver.execute_script("arguments[0].scrollIntoView();", btn)
                        time.sleep(1)
                        driver.execute_script("arguments[0].click();", btn)
                        logging.info(f"✓ Clicked 'Ver más' button for subcategories: '{btn.text}'")
                        time.sleep(3)
                        return True

            except Exception as e:
                logging.debug(f"Selector {selector} failed: {e}")
                continue

        logging.info("No 'Ver más' button found for subcategories")
        return False

    except Exception as e:
        logging.error(f"Error scrolling and clicking 'Ver más' for subcategories: {e}")
        return False

def count_all_product_types(driver):
    """Contar TODOS los tipos de producto expandiendo completamente el filtro primero"""
    try:
        # Forzar una recarga completa: colapsar y expandir el menú de tipos de producto
        logging.info("Forzando recarga completa del menú de tipos de producto...")

        # Primero intentar colapsar el menú si está expandido
        try:
            product_type_header = driver.find_element(By.CSS_SELECTOR, "[data-testid*='product-type'], .valtech-carrefourar-search-result-3-x-filterItem")
            if product_type_header:
                # Hacer click para colapsar si está expandido
                driver.execute_script("arguments[0].click();", product_type_header)
                time.sleep(2)
                logging.info("✓ Collapsed product types menu for fresh reload")
        except:
            logging.debug("Could not collapse product types menu")

        # Ahora expandir completamente el menú de tipos de producto
        product_types_container = expand_product_type_menu(driver)
        if not product_types_container:
            logging.error("No se pudo expandir el menú de tipos de producto para contar")
            return 0

        # Esperar un poco más para que se carguen dinámicamente los elementos
        time.sleep(3)

        # Hacer click en "ver más" si existe para expandir completamente
        # Intentar múltiples veces con scrolls adicionales
        for attempt in range(3):
            logging.info(f"Attempting to find 'Ver más' button (attempt {attempt + 1}/3)...")
            if scroll_and_click_ver_mas_product_types(driver, product_types_container):
                # Si se encontró y clickeó, esperar un poco más
                time.sleep(2)
                break

            # Si no se encontró, hacer otro scroll y esperar
            driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight;", product_types_container)
            time.sleep(2)

        # Ahora contar todos los checkboxes disponibles
        return count_product_types(driver)

    except Exception as e:
        logging.error(f"Error counting all product types: {e}")
        return 0

def count_product_types(driver):
    """Contar el número total de opciones en el filtro 'Tipo de Producto'"""
    try:
        # Find the product types container
        product_types_container = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.valtech-carrefourar-search-result-3-x-filter__container--tipo-de-producto"))
        )

        # Try multiple selectors for product type checkboxes
        checkbox_selectors = [
            "input[type='checkbox'][id^='tipo-de-producto-']",
            "input[type='checkbox']",
            ".valtech-carrefourar-search-result-3-x-filter__checkbox input[type='checkbox']",
            "input[id*='tipo-de-producto']"
        ]

        checkboxes = []
        for selector in checkbox_selectors:
            try:
                elements = product_types_container.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    checkboxes = elements
                    break
            except Exception as e:
                logging.debug(f"Selector {selector} failed: {e}")
                continue

        count = len(checkboxes)
        logging.info(f"✓ Counted {count} product type options")
        return count

    except Exception as e:
        logging.error(f"Error counting product types: {e}")
        return 0

def process_all_subcategories(driver, category_name, category_url):
    """Procesar todas las subcategorías de una categoría, extrayendo tipos de producto para cada una"""
    try:
        # NO guardamos las checkboxes al inicio porque se vuelven stale después del refresh
        # En su lugar, las obtendremos en cada iteración después del refresh

        # Obtener el número total de subcategorías UNA SOLA VEZ al inicio
        subcategory_container = expand_subcategory_menu_if_collapsed(driver)
        if not subcategory_container:
            logging.error("No se pudo encontrar el contenedor de subcategorías")
            return False

        temp_checkboxes = subcategory_container.find_elements(By.CSS_SELECTOR, "input[type='checkbox'][id^='category-3-']")
        total_subcategories = len(temp_checkboxes)
        logging.info(f"✓ Encontradas {total_subcategories} subcategorías para procesar")

        # Procesar cada subcategoría
        for subcategory_index in range(total_subcategories):
            logging.info(f"{'='*50}")
            logging.info(f"PROCESANDO SUBCATEGORÍA {subcategory_index + 1}/{total_subcategories}")
            logging.info(f"{'='*50}")

            # DESPUÉS DE CADA REFRESH: VOLVER A OBTENER LAS CHECKBOXES DEL DOM ACTUALIZADO
            subcategory_container = expand_subcategory_menu_if_collapsed(driver)
            if not subcategory_container:
                logging.warning(f"No se pudo re-expandir el menú de subcategorías para subcategoría {subcategory_index + 1}")
                continue

            checkboxes = subcategory_container.find_elements(By.CSS_SELECTOR, "input[type='checkbox'][id^='category-3-']")
            if subcategory_index >= len(checkboxes):
                logging.warning(f"No se pudo acceder a la subcategoría {subcategory_index + 1} (índice fuera de rango)")
                continue

            # Limpiar cualquier selección previa
            logging.info("Limpiando selecciones previas...")
            for checkbox in checkboxes:
                if checkbox.is_selected():
                    driver.execute_script("arguments[0].click();", checkbox)
                    time.sleep(0.5)
            logging.info("✓ Selecciones previas limpiadas")

            # Seleccionar la subcategoría actual
            current_checkbox = checkboxes[subcategory_index]
            input_id = current_checkbox.get_attribute("id")

            # Obtener nombre de la subcategoría
            try:
                label = driver.find_element(By.CSS_SELECTOR, f"label[for='{input_id}']")
                subcategory_name = label.get_attribute("textContent").strip()
                subcategory_name = subcategory_name.split('(')[0].strip()  # Remove count if present
            except:
                subcategory_name = f"Subcategory_{input_id}"

            logging.info(f"Seleccionando subcategoría: {subcategory_name}")

            # Hacer scroll y seleccionar
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", current_checkbox)
            time.sleep(1)
            driver.execute_script("arguments[0].click();", current_checkbox)
            logging.info(f"✓ Subcategoría '{subcategory_name}' seleccionada")

            # Aplicar el filtro
            aplicar_selectors = [
                "div.vtex-button__label",
                "button[class*='Aplicar']",
                "button:contains('Aplicar')",
                "//button[contains(text(), 'Aplicar')]",
                "//div[contains(text(), 'Aplicar')]",
                "//span[contains(text(), 'Aplicar')]"
            ]

            filter_applied = False
            for selector in aplicar_selectors:
                try:
                    if selector.startswith("//"):
                        elements = driver.find_elements(By.XPATH, selector)
                    else:
                        elements = driver.find_elements(By.CSS_SELECTOR, selector)

                    for element in elements:
                        text = element.text.lower()
                        if "aplicar" in text:
                            driver.execute_script("arguments[0].scrollIntoView();", element)
                            time.sleep(1)
                            driver.execute_script("arguments[0].click();", element)
                            logging.info("✓ Filtro aplicado")
                            logging.info("⏳ Esperando que se carguen dinámicamente los filtros después de aplicar subcategoría...")
                            time.sleep(3)  # Reducido a 3 segundos como indica el .md

                            # Usar la función segura para refresh y reabrir filtros
                            if not safe_refresh_and_reopen_filters(driver):
                                logging.error(f"No se pudo refrescar y reabrir filtros para subcategoría '{subcategory_name}'")
                                continue

                            filter_applied = True
                            break
                    if filter_applied:
                        break
                except Exception as e:
                    logging.debug(f"Selector {selector} failed: {e}")
                    continue

            if not filter_applied:
                logging.error(f"No se pudo aplicar el filtro para subcategoría '{subcategory_name}'")
                continue

            # Extraer y guardar tipos de producto para esta subcategoría
            logging.info(f"Extrayendo tipos de producto para subcategoría '{subcategory_name}'...")

            # Expandir menú de tipos de producto
            product_types_container = expand_product_type_menu(driver)
            if not product_types_container:
                logging.warning(f"No se pudo expandir menú de tipos de producto para '{subcategory_name}'")
                continue

            # ESPERAR un poco más para que se carguen dinámicamente todas las opciones después de expandir
            logging.info("⏳ Esperando que se carguen dinámicamente todas las opciones del menú...")
            time.sleep(5)
            logging.info("✓ Menú debería estar completamente cargado")

            # Hacer scroll y buscar botón "Ver más"
            scroll_and_click_ver_mas_product_types(driver, product_types_container)

            # Extraer nombres de tipos de producto
            product_type_names = extract_product_type_names(driver)
            if not product_type_names:
                logging.warning(f"No se pudieron extraer tipos de producto para '{subcategory_name}'")
                continue

            # Guardar en base de datos
            saved_count = save_product_types_to_db(product_type_names, category_name, subcategory_name, category_url)
            logging.info(f"✓ Guardados {saved_count} tipos de producto para subcategoría '{subcategory_name}'")

        logging.info(f"{'='*50}")
        logging.info(f"PROCESAMIENTO COMPLETADO: {total_subcategories} subcategorías procesadas")
        logging.info(f"{'='*50}")
        return True

    except Exception as e:
        logging.error(f"Error procesando subcategorías: {e}")
        return False

def safe_refresh_and_reopen_filters(driver, max_retries=3):
    """Función segura para refrescar página y reabrir filtros con reintentos"""
    for attempt in range(max_retries):
        try:
            logging.info(f"✓ Actualizando página después de aplicar filtro (intento {attempt + 1}/{max_retries})...")
            driver.refresh()
            time.sleep(5)  # Esperar más tiempo para que se recargue completamente
            logging.info("✓ Página actualizada - filtros deberían estar cargados dinámicamente")

            # Reabrir panel de filtros después del refresh
            logging.info("⏳ Reabriendo panel de filtros después del refresh...")
            open_filters_panel(driver)
            scroll_to_load_filters(driver)

            # Re-expandir el menú de subcategorías después del refresh
            subcategory_container = expand_subcategory_menu_if_collapsed(driver)
            if subcategory_container:
                scroll_and_click_ver_mas_subcategories(driver, subcategory_container)
                return True
            else:
                logging.warning(f"Intento {attempt + 1}: No se pudo re-expandir menú de subcategorías")
                if attempt < max_retries - 1:
                    time.sleep(2)
                    continue
                return False

        except Exception as e:
            logging.warning(f"Intento {attempt + 1} falló: {e}")
            if attempt < max_retries - 1:
                time.sleep(2)
                continue
            return False

    return False

def expand_product_type_menu(driver):
    """Buscar el menú 'Tipo de Producto' en el contenedor de filtros y expandirlo"""
    try:
        # Find the product types container with multiple selectors for robustness
        product_types_container = None
        selectors = [
            "div.valtech-carrefourar-search-result-3-x-filter__container--tipo-de-producto",
            "div[data-testid*='tipo-de-producto']",
            "div.filter__container--tipo-de-producto",
            "div.valtech-carrefourar-search-result-3-x-filter__container"
        ]

        for selector in selectors:
            try:
                product_types_container = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                # Verify it contains product type elements
                checkboxes = product_types_container.find_elements(By.CSS_SELECTOR, "input[type='checkbox']")
                if checkboxes:
                    logging.info(f"Found product types container with selector: {selector} ({len(checkboxes)} checkboxes)")
                    break
            except:
                continue

        if not product_types_container:
            logging.error("No product types container found with any selector")
            return None

        # Check if there's an expand button
        try:
            expand_button = product_types_container.find_element(By.CSS_SELECTOR, "div[role='button']")
            if expand_button and expand_button.is_displayed():
                driver.execute_script("arguments[0].scrollIntoView();", expand_button)
                time.sleep(1)
                driver.execute_script("arguments[0].click();", expand_button)
                logging.info("✓ Expanded product types menu")
                time.sleep(2)
            else:
                logging.info("Product types menu already expanded")
        except Exception as e:
            logging.info(f"No expand button found for product types (already expanded): {e}")

        return product_types_container

    except Exception as e:
        logging.error(f"Error expanding product types menu: {e}")
        return None

def scroll_and_click_ver_mas_product_types(driver, product_types_container):
    """Hacer scroll hasta el final de 'Tipo de Producto' y encontrar botón 'Ver Mas N'"""
    try:
        # Scroll to the bottom of the container
        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight;", product_types_container)
        time.sleep(2)
        logging.info("Scrolled to bottom of product types menu")

        # Look for "Ver más" or "Ver mas" button - try multiple selectors
        ver_mas_selectors = [
            "span.vtex-button__label",
            "button.valtech-carrefourar-search-result-3-x-seeMoreButton",
            "button:contains('Ver más')",
            "button:contains('Ver mas')",
            "//button[contains(text(), 'Ver más')]",
            "//button[contains(text(), 'Ver mas')]",
            "//span[contains(text(), 'Ver más')]",
            "//span[contains(text(), 'Ver mas')]"
        ]

        for selector in ver_mas_selectors:
            try:
                if selector.startswith("//"):
                    buttons = driver.find_elements(By.XPATH, selector)
                else:
                    buttons = driver.find_elements(By.CSS_SELECTOR, selector)

                for btn in buttons:
                    text = btn.text.lower()
                    if "ver más" in text or "ver mas" in text:
                        driver.execute_script("arguments[0].scrollIntoView();", btn)
                        time.sleep(1)
                        driver.execute_script("arguments[0].click();", btn)
                        logging.info(f"✓ Clicked 'Ver más' button for product types: '{btn.text}'")
                        time.sleep(3)
                        return True

            except Exception as e:
                logging.debug(f"Selector {selector} failed: {e}")
                continue

        logging.info("No 'Ver más' button found for product types")
        return False

    except Exception as e:
        logging.error(f"Error scrolling and clicking 'Ver más' for product types: {e}")
        return False

def extract_product_type_names(driver):
    """Extraer los nombres de todos los tipos de producto disponibles"""
    try:
        # Find the product types container
        product_types_container = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.valtech-carrefourar-search-result-3-x-filter__container--tipo-de-producto"))
        )

        # Try multiple selectors for product type checkboxes
        checkbox_selectors = [
            "input[type='checkbox'][id^='tipo-de-producto-']",
            "input[type='checkbox']",
            ".valtech-carrefourar-search-result-3-x-filter__checkbox input[type='checkbox']",
            "input[id*='tipo-de-producto']"
        ]

        checkboxes = []
        for selector in checkbox_selectors:
            try:
                elements = product_types_container.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    checkboxes = elements
                    break
            except Exception as e:
                logging.debug(f"Selector {selector} failed: {e}")
                continue

        if not checkboxes:
            logging.warning("No product type checkboxes found")
            return []

        product_type_names = []
        logging.info(f"Extracting names from {len(checkboxes)} product type checkboxes")

        for i, checkbox in enumerate(checkboxes):
            try:
                input_id = checkbox.get_attribute("id")

                # Try to extract product type name from label
                try:
                    label = driver.find_element(By.CSS_SELECTOR, f"label[for='{input_id}']")
                    product_type_name = label.get_attribute("textContent").strip()

                    if product_type_name:
                        # Clean the name (remove extra spaces, etc.)
                        product_type_name = ' '.join(product_type_name.split())
                        # Remove the number in parentheses (e.g., "Cargador portátil (18)" -> "Cargador portátil")
                        if '(' in product_type_name and ')' in product_type_name:
                            product_type_name = product_type_name.split('(')[0].strip()
                        product_type_names.append(product_type_name)
                        logging.debug(f"Extracted product type {i+1}: '{product_type_name}'")

                except Exception as e:
                    logging.debug(f"Could not extract label for checkbox {input_id}: {e}")
                    continue

            except Exception as e:
                logging.debug(f"Error processing checkbox {i+1}: {e}")
                continue

        logging.info(f"✓ Successfully extracted {len(product_type_names)} product type names")
        return product_type_names

    except Exception as e:
        logging.error(f"Error extracting product type names: {e}")
        return []

def save_product_type_to_db(product_type_name, subcategory_name, category_name, category_url):
    """Save or update the product type to MongoDB producttypes collection (avoid duplicates)"""
    try:
        client = MongoClient('mongodb://localhost:27017/')
        db = client['carrefour']
        collection = db['producttypes']

        # Create simplified name (name is already cleaned in extract_product_type_names)
        simplified_name = product_type_name

        # Use upsert to replace if exists or insert if not
        filter_query = {
            'name': product_type_name,
            'subcategory': subcategory_name,
            'category': category_name
        }

        document = {
            'name': product_type_name,
            'simplified_name': simplified_name,
            'subcategory': subcategory_name,
            'category': category_name,
            'category_url': category_url,
            'extracted_at': datetime.now(),
            'source': 'carrefour_step4_md_instructions.py'
        }

        result = collection.update_one(filter_query, {'$set': document}, upsert=True)
        if result.upserted_id:
            logging.info(f"✓ Inserted new product type '{product_type_name}' to database (ID: {result.upserted_id})")
        else:
            logging.info(f"✓ Updated existing product type '{product_type_name}' in database")

        client.close()
        return True

    except Exception as e:
        logging.error(f"Error saving/updating product type to database: {e}")
        return False

def save_product_types_to_db(product_type_names, category_name, subcategory_name, category_url):
    """Save multiple product types to database, returning count of successfully saved items"""
    if not product_type_names:
        logging.warning("No product type names to save")
        return 0

    saved_count = 0
    for product_type_name in product_type_names:
        if save_product_type_to_db(product_type_name, subcategory_name, category_name, category_url):
            saved_count += 1

    logging.info(f"✓ Successfully saved {saved_count} out of {len(product_type_names)} product types to database")
    return saved_count

def main():
    """Main function following the detailed process from the .md file - processes ALL categories"""
    driver = None

    try:
        logging.info("=== INICIANDO SCRIPT PARA PROCESAR TODAS LAS CATEGORÍAS ===")

        # PASO 1: Inicialización y Configuración
        logging.info("PASO 1: Inicialización y Configuración del WebDriver Firefox...")
        driver = setup_driver()

        # PASO 2: Obtención de TODAS las Categorías desde Base de Datos
        logging.info("PASO 2: Obtención de TODAS las Categorías desde Base de Datos...")
        categories = get_all_categories()
        if not categories:
            logging.error("No se pudieron obtener las categorías")
            return

        total_categories = len(categories)
        logging.info(f"{'='*60}")
        logging.info(f"INICIANDO PROCESAMIENTO DE {total_categories} CATEGORÍAS")
        logging.info(f"{'='*60}")

        # Procesar cada categoría (SALTANDO LAS PRIMERAS 2 CATEGORÍAS QUE YA FUERON PROCESADAS)
        for category_index, category in enumerate(categories, 1):
            category_name = category.get('name')
            category_url = category.get('url')

            # SALTAR LAS PRIMERAS 2 CATEGORÍAS QUE YA FUERON PROCESADAS
            if category_index <= 2:
                logging.info(f"⏭️  SALTANDO CATEGORÍA {category_index}/{total_categories}: {category_name} (YA PROCESADA)")
                continue

            logging.info(f"{'='*80}")
            logging.info(f"PROCESANDO CATEGORÍA {category_index}/{total_categories}: {category_name}")
            logging.info(f"{'='*80}")

            try:
                # PASO 3: Navegación a la Categoría
                logging.info(f"PASO 3: Navegación a la Categoría '{category_name}'...")
                driver.get(category_url)
                time.sleep(5)

                # Handle cookies (solo en la primera categoría)
                if category_index == 1:
                    handle_cookies(driver)

                # PASO 4: Apertura del Panel de Filtros
                logging.info("PASO 4: Apertura del Panel de Filtros...")
                open_filters_panel(driver)

                # PASO 5: Carga de Filtros
                logging.info("PASO 5: Carga de Filtros...")
                scroll_to_load_filters(driver)

                # PASO 6: Expansión del Menú de Subcategorías
                logging.info("PASO 6: Expansión del Menú de Subcategorías...")
                subcategory_container = expand_subcategory_menu_if_collapsed(driver)
                if not subcategory_container:
                    logging.error(f"No se pudo encontrar el contenedor de subcategorías para '{category_name}'")
                    continue

                # PASO 7: Expansión Completa de Subcategorías
                logging.info("PASO 7: Expansión Completa de Subcategorías (Ver más)...")
                scroll_and_click_ver_mas_subcategories(driver, subcategory_container)

                # PASO 8: Conteo de Tipos de Producto Totales
                logging.info("PASO 8: Conteo de Tipos de Producto Totales (antes de filtrar)...")
                total_product_types_before = count_all_product_types(driver)
                logging.info(f"Total product types before filtering: {total_product_types_before}")

                # PASO 9: Procesamiento de Todas las Subcategorías
                logging.info("PASO 9: Procesamiento de Todas las Subcategorías...")
                success = process_all_subcategories(driver, category_name, category_url)
                if not success:
                    logging.error(f"No se pudieron procesar las subcategorías para '{category_name}'")
                    continue

                logging.info(f"{'='*60}")
                logging.info(f"✓ CATEGORÍA {category_index}/{total_categories} COMPLETADA: {category_name}")
                logging.info(f"{'='*60}")

            except Exception as e:
                logging.error(f"Error procesando categoría '{category_name}': {e}")
                # Continuar con la siguiente categoría en caso de error
                continue

        logging.info("=== PROCESO COMPLETADO EXITOSAMENTE ===")
        logging.info(f"Todas las {total_categories} categorías han sido procesadas")
        logging.info("El navegador permanecerá abierto para que puedas ver el resultado")

        # Keep browser open for 30 seconds so user can see the result
        time.sleep(30)

    except Exception as e:
        logging.error(f"Error en main: {e}")
        raise

    finally:
        if driver:
            driver.quit()
            logging.info("WebDriver closed")

if __name__ == "__main__":
    main()