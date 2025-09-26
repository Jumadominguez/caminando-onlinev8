#!/usr/bin/env python3
"""
Script para extraer TODOS los productos de UNA categoría y guardarlos en la colección 'products'
Sigue la lógica de iteración de step5_products.py pero guarda productos individuales en lugar de arrays
Incluye el campo 'productType' en cada producto
"""
import time
import logging
import json
import os
import random
import re
import threading
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from pymongo import MongoClient
from datetime import datetime

# Configure logging - SIMPLIFIED
logging.basicConfig(level=logging.WARNING, format='%(levelname)s: %(message)s')

# Anti-detection constants
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0'
]

# Optimized delays for faster processing
MIN_DELAY = 0.5  # Reduced from 1
MAX_DELAY = 1.5  # Reduced from 3

def random_delay():
    """Shorter random delay for faster processing"""
    time.sleep(random.uniform(MIN_DELAY, MAX_DELAY))

# Retry configuration
MAX_RETRIES = 3
BASE_RETRY_DELAY = 5  # Base delay in seconds for exponential backoff

# Global tracking lists for final report
successful_types = []
partial_types = []
failed_types = []
tracking_lock = threading.Lock()

def retry_with_backoff(func, max_retries=MAX_RETRIES, base_delay=BASE_RETRY_DELAY, *args, **kwargs):
    """Execute a function with exponential backoff retry logic"""
    for attempt in range(max_retries + 1):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if attempt == max_retries:
                logging.error(f"Function {func.__name__} failed after {max_retries + 1} attempts: {e}")
                raise e

            delay = base_delay * (2 ** attempt) + random.uniform(0, 2)  # Exponential backoff with jitter
            logging.warning(f"Attempt {attempt + 1} failed for {func.__name__}: {e}. Retrying in {delay:.2f} seconds...")
            time.sleep(delay)

    return None

def simulate_human_behavior(driver):
    """Simulate human-like behavior to avoid detection"""
    try:
        # Random scroll to simulate reading
        scroll_amount = random.randint(200, 800)
        driver.execute_script(f"window.scrollTo(0, {scroll_amount});")

        # Random pause
        time.sleep(random.uniform(0.5, 2.0))

        # Simulate mouse movement
        actions = ActionChains(driver)
        # Move mouse to random position
        actions.move_by_offset(random.randint(-100, 100), random.randint(-50, 50))
        actions.perform()

        # Another random pause
        time.sleep(random.uniform(0.3, 1.5))

    except Exception as e:
        logging.debug(f"Could not simulate human behavior: {e}")

def get_random_user_agent():
    """Get a random user agent"""
    return random.choice(USER_AGENTS)

def setup_driver(user_agent=None):
    """Setup Firefox WebDriver with anti-detection measures"""
    firefox_options = Options()
    # NO headless - el usuario quiere ver el proceso
    firefox_options.add_argument("--no-sandbox")
    firefox_options.add_argument("--disable-dev-shm-usage")
    firefox_options.add_argument("--window-size=1920,1080")

    # Anti-detection measures
    if user_agent:
        firefox_options.set_preference("general.useragent.override", user_agent)

    # Disable WebRTC to prevent IP leaks
    firefox_options.set_preference("media.peerconnection.enabled", False)

    # Randomize other preferences to avoid fingerprinting
    firefox_options.set_preference("dom.webdriver.enabled", False)
    firefox_options.set_preference('useAutomationExtension', False)

    # Disable images to speed up loading (optional)
    # firefox_options.set_preference("permissions.default.image", 2)

    geckodriver_path = r"d:\dev\caminando-onlinev8\geckodriver_temp\geckodriver.exe"
    service = Service(geckodriver_path)
    driver = webdriver.Firefox(service=service, options=firefox_options)

    # Execute script to remove webdriver property
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    return driver

def handle_cookies(driver):
    """Handle cookie popup if present"""
    try:
        accept_buttons = driver.find_elements(By.XPATH, "//button[contains(text(), 'Aceptar') or contains(text(), 'Accept') or contains(text(), 'OK')]")
        for btn in accept_buttons:
            try:
                btn.click()
                time.sleep(1)
                break
            except:
                continue
    except Exception as e:
        pass

def open_filters_panel(driver):
    """Open the filters panel if not already open"""
    try:
        filters_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Filtrar')]"))
        )
        filters_button.click()
        time.sleep(0.5)
    except:
        pass

def scroll_to_load_filters(driver):
    """Scroll down to ensure filters are loaded"""
    driver.execute_script("window.scrollTo(0, 500);")
    time.sleep(0.5)

def get_all_categories():
    """Get all categories from MongoDB categories collection"""
    try:
        client = MongoClient('mongodb://localhost:27017/')
        db = client['carrefour']
        collection = db['categories']

        # Get all categories
        categories = list(collection.find({}, {'name': 1, 'url': 1, '_id': 0}))

        client.close()

        if categories:
            logging.warning(f"Retrieved {len(categories)} categories from database")
            return categories
        else:
            logging.error("No categories found in database")
            return []

    except Exception as e:
        logging.error(f"Error retrieving categories from database: {e}")
        return []

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
                time.sleep(0.5)
                driver.execute_script("arguments[0].click();", expand_button)
                time.sleep(1)
        except Exception as e:
            pass

        return product_types_container

    except Exception as e:
        logging.error(f"Error expanding product types menu: {e}")
        return None

def scroll_and_click_ver_mas_product_types(driver, product_types_container):
    """Hacer scroll hasta el final de 'Tipo de Producto' y hacer clic en botón 'Ver Mas' una vez, luego verificar que toda la lista sea visible"""
    try:
        # Scroll to the bottom of the container
        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight;", product_types_container)
        time.sleep(1)

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

        button_clicked = False
        for selector in ver_mas_selectors:
            try:
                if selector.startswith("//"):
                    buttons = driver.find_elements(By.XPATH, selector)
                else:
                    buttons = driver.find_elements(By.CSS_SELECTOR, selector)

                for btn in buttons:
                    text = btn.text.lower()
                    if "ver más" in text or "ver mas" in text:
                        # Check if button is visible and enabled
                        if btn.is_displayed() and btn.is_enabled():
                            driver.execute_script("arguments[0].scrollIntoView();", btn)
                            time.sleep(0.5)
                            driver.execute_script("arguments[0].click();", btn)
                            button_clicked = True
                            time.sleep(0.5)
                            break

                if button_clicked:
                    break

            except Exception as e:
                logging.debug(f"Selector {selector} failed: {e}")
                continue

        # Scroll again to ensure all items are visible
        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight;", product_types_container)
        time.sleep(0.5)

        return True

    except Exception as e:
        logging.error(f"Error scrolling and clicking 'Ver más' for product types: {e}")
        return False

def get_all_product_types(driver):
    """Get all available product types from the filter"""
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
            return []

        product_types = []
        for checkbox in checkboxes:
            try:
                input_id = checkbox.get_attribute("id")
                if input_id:
                    label = driver.find_element(By.CSS_SELECTOR, f"label[for='{input_id}']")
                    label_text = label.get_attribute("textContent").strip()
                    # Remove count in parentheses if present
                    clean_label = label_text.split('(')[0].strip()

                    if clean_label and clean_label not in product_types:
                        product_types.append(clean_label)
            except Exception as e:
                continue

        logging.warning(f"Found {len(product_types)} product types")
        return product_types

    except Exception as e:
        logging.error(f"Error getting all product types: {e}")
        return []

def apply_filter(driver):
    """Aplicar el filtro después de seleccionar el tipo de producto"""
    try:
        aplicar_selectors = [
            "div.vtex-button__label",
            "button[class*='Aplicar']",
            "button:contains('Aplicar')",
            "//button[contains(text(), 'Aplicar')]",
            "//div[contains(text(), 'Aplicar')]",
            "//span[contains(text(), 'Aplicar')]"
        ]

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
                        time.sleep(0.5)
                        driver.execute_script("arguments[0].click();", element)
                        time.sleep(0.5)
                        return True

            except Exception as e:
                continue

        return False

    except Exception as e:
        logging.error(f"Error applying filter: {e}")
        return False

def is_product_name_relevant(product_name, product_type_name):
    """Check if product name is relevant for the given product type"""
    if not product_name or not product_type_name:
        return True  # If we can't determine, assume it's relevant

    product_name_lower = product_name.lower()
    product_type_lower = product_type_name.lower()

    # Basic keyword matching - product name should contain product type keywords
    type_keywords = product_type_lower.split()

    # For product types with multiple words, check if at least some keywords match
    matching_keywords = 0
    for keyword in type_keywords:
        if keyword in product_name_lower:
            matching_keywords += 1

    # Require at least 50% of keywords to match for relevance
    min_matches = max(1, len(type_keywords) // 2)
    return matching_keywords >= min_matches

def get_total_products(driver):
    """Get total number of products from the page"""
    try:
        # Look for total products text
        selectors = [
            "span.valtech-carrefourar-search-result-0-x-totalProducts",
            "span[data-testid*='total']",
            "span:contains('productos')",
            ".search-result-info span"
        ]

        for selector in selectors:
            try:
                if selector.startswith("span:contains"):
                    elements = driver.find_elements(By.XPATH, "//span[contains(text(), 'productos')]")
                else:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)

                for element in elements:
                    if element.is_displayed():
                        text = element.text.strip()
                        # Extract number from text
                        import re
                        match = re.search(r'(\d+(?:[.,]\d+)*)', text)
                        if match:
                            count_str = match.group(1).replace('.', '').replace(',', '')
                            return int(count_str)
            except:
                continue

        return 0
    except Exception as e:
        logging.debug(f"Error getting total products: {e}")
        return 0

def validate_product_type_consistency(products_data, expected_product_type, category_name):
    """Validate that extracted products match the expected product type"""
    if not products_data:
        return 0

    consistent_count = 0
    for product in products_data:
        product_name = product.get('name', '').lower()
        if is_product_name_relevant(product_name, expected_product_type):
            consistent_count += 1

    return consistent_count

# Global cache for brands to avoid repeated database queries
BRANDS_CACHE = None

def extract_brand(product_name):
    """Extract brand from product name using sophisticated matching logic with cache"""
    if not product_name:
        return None

    # Cache for brands to avoid repeated database queries
    if not hasattr(extract_brand, 'brands_cache'):
        try:
            client = MongoClient('mongodb://localhost:27017/')
            db = client['carrefour']
            filters_collection = db['filters']

            # Load all brands from filters collection
            brands_docs = filters_collection.find({'type': 'brand'}, {'name': 1})
            extract_brand.brands_cache = [doc['name'] for doc in brands_docs]

            client.close()

            if not extract_brand.brands_cache:
                logging.debug("No brands found in filters collection")
                return 'Carrefour'

        except Exception as e:
            logging.debug(f"Error loading brands cache: {e}")
            extract_brand.brands_cache = []

    # If cache is empty, return default
    if not extract_brand.brands_cache:
        return 'Carrefour'

    product_name_lower = product_name.lower()

    # Strategy 1: Exact match
    for brand in extract_brand.brands_cache:
        if brand.lower() == product_name_lower:
            return brand

    # Strategy 2: Brand contained in product name
    for brand in extract_brand.brands_cache:
        if brand.lower() in product_name_lower:
            return brand

    # Strategy 3: Extract from initial words (1-3 words)
    words = product_name.split()
    if words:
        for i in range(min(3, len(words))):
            candidate = ' '.join(words[:i+1])
            for brand in extract_brand.brands_cache:
                if brand.lower() == candidate.lower():
                    return brand

    # Strategy 4: Fallback to Carrefour for own-brand products
    return 'Carrefour'

# Global cache for product types to avoid repeated database queries
PRODUCT_TYPES_CACHE = None

def parse_argentine_price(price_text):
    """Parse Argentine price format ($X.XXX,XX or X.XXX,XX) to float"""
    try:
        if not price_text:
            return None

        # Remove currency symbols and clean up spaces
        clean_text = price_text.replace('$', '').replace('ARS', '').strip()

        # Remove extra spaces that might be in the extracted text
        clean_text = ' '.join(clean_text.split())

        # Handle the specific format from currencyContainer: "140 . 000 , 00"
        # Remove spaces and reconstruct the number
        parts = clean_text.split()
        if len(parts) >= 1:
            # Join all parts and remove spaces
            clean_text = ''.join(parts)

        # Handle Argentine format: X.XXX,XX -> XXXX.XX
        if ',' in clean_text and '.' in clean_text:
            # Remove dots (thousands separators) and replace comma with dot
            clean_text = clean_text.replace('.', '').replace(',', '.')
        elif ',' in clean_text:
            # Only comma (decimal separator)
            clean_text = clean_text.replace(',', '.')

        return float(clean_text)
    except (ValueError, AttributeError) as e:
        logging.debug(f"Error parsing price '{price_text}': {e}")
        return None

def extract_price_from_currency_container(container_element):
    """Extract complete price from a currency container with multiple spans"""
    try:
        # First try: get the complete text from the container element
        complete_text = container_element.text.strip()
        if complete_text and ('$' in complete_text or 'ARS' in complete_text):
            return complete_text

        # Fallback: try to extract from individual spans
        spans = container_element.find_elements(By.XPATH, './/span[contains(@class, "valtech-carrefourar-product-price-0-x-")]')
        price_parts = []

        for span in spans:
            classes = span.get_attribute('class')
            text = span.text.strip()

            if 'currencyCode' in classes:
                price_parts.append(text)      # Currency symbol: "$"
            elif 'currencyInteger' in classes:
                price_parts.append(text)      # Integer part: "1.234"
            elif 'currencyGroup' in classes:
                price_parts.append(text)      # Thousands separator: "."
            elif 'currencyDecimal' in classes:
                price_parts.append(text)      # Decimal separator: ","
            elif 'currencyFraction' in classes:
                price_parts.append(text)      # Decimal part: "56"

        result = ''.join(price_parts)
        return result if result else None
    except Exception as e:
        logging.error(f"Error extracting price from currency container: {e}")
        return None

def extract_subcategory(product_type_name):
    """Extrae la subcategoría del tipo de producto buscando en la colección producttypes"""
    global PRODUCT_TYPES_CACHE

    # Cargar tipos de producto de la base de datos si no están en cache
    if PRODUCT_TYPES_CACHE is None:
        try:
            # Obtener todos los tipos de producto con su subcategoría
            client = MongoClient('mongodb://localhost:27017/')
            db = client['carrefour']
            producttypes_collection = db['producttypes']
            producttypes_docs = producttypes_collection.find({}, {'name': 1, 'subcategory': 1})
            PRODUCT_TYPES_CACHE = {doc['name']: doc.get('subcategory') for doc in producttypes_docs}
            client.close()
            logging.info(f"Cargados {len(PRODUCT_TYPES_CACHE)} tipos de producto desde la base de datos")
        except Exception as e:
            logging.error(f"Error cargando tipos de producto desde la base de datos: {e}")
            PRODUCT_TYPES_CACHE = {}

    # Buscar coincidencia exacta del tipo de producto
    if product_type_name in PRODUCT_TYPES_CACHE:
        return PRODUCT_TYPES_CACHE[product_type_name]

    # Buscar coincidencia parcial (contenida)
    product_type_lower = product_type_name.lower()
    for pt_name, subcategory in PRODUCT_TYPES_CACHE.items():
        if pt_name.lower() in product_type_lower or product_type_lower in pt_name.lower():
            return subcategory

    # Fallback: devolver None si no se encuentra subcategoría
    return None

def extract_products(driver, product_type_name, category_name, subcategory_name=None):
    """Extraer productos de la página filtrada con campos adicionales"""
    try:
        try:
            WebDriverWait(driver, 3).until(
                lambda d: len(d.find_elements(By.CSS_SELECTOR, "[data-testid*='product'], .product-container, .vtex-product-summary")) > 0
            )
        except:
            time.sleep(0.5)

        # Try multiple selectors for product containers
        product_selectors = [
            "div.valtech-carrefourar-search-result-3-x-galleryItem",
            "div[data-testid*='product']",
            "div.vtex-product-summary"
        ]

        products = []
        for selector in product_selectors:
            try:
                product_elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if product_elements:
                    break
            except Exception as e:
                continue

        if not product_elements:
            logging.warning("No product elements found")
            return []

        logging.info(f"Extracting data from {len(product_elements)} products")

        for i, product_elem in enumerate(product_elements):
            try:
                # Extract product name - try multiple selectors
                name_selectors = [
                    "span.vtex-product-summary-2-x-productName",
                    "span.vtex-store-components-3-x-productName",
                    "h3.vtex-product-summary-2-x-productName",
                    "a.vtex-product-summary-2-x-productName",
                    "[data-testid*='product-name']",
                    ".vtex-product-summary-2-x-productName",
                    "span:contains('Aire')",
                    "span:contains('Split')",
                    "h3",
                    "a[href*='/p']"
                ]

                product_name = None
                for name_sel in name_selectors:
                    try:
                        if ":contains" in name_sel:
                            # Handle :contains pseudo-selector with XPath
                            text_to_find = name_sel.split("'")[1]
                            name_elem = product_elem.find_element(By.XPATH, f".//*[contains(text(), '{text_to_find}')]")
                        else:
                            name_elem = product_elem.find_element(By.CSS_SELECTOR, name_sel)

                        name_text = name_elem.text.strip()
                        if name_text and len(name_text) > 3:  # Avoid very short texts
                            # Validate product name relevance for product type (basic check)
                            if product_type_name and not is_product_name_relevant(name_text, product_type_name):
                                logging.debug(f"Product name '{name_text[:50]}...' may not match product type '{product_type_name}'")
                            product_name = name_text
                            break
                    except:
                        continue

                if not product_name:
                    # Try to get text from the entire product element
                    try:
                        full_text = product_elem.text.strip()
                        # Look for meaningful product name patterns
                        lines = full_text.split('\n')
                        for line in lines:
                            line = line.strip()
                            if len(line) > 5 and not any(char.isdigit() for char in line[:10]):  # Avoid price-like text
                                product_name = line
                                break

                        # If still no good name, skip this product entirely
                        if not product_name or len(product_name) < 5:
                            logging.debug(f"Skipping product {i+1} - could not extract valid name")
                            continue
                    except:
                        logging.debug(f"Skipping product {i+1} - could not extract name")
                        continue

                # Extract price information (sellingPrice, listPrice, discount logic)
                selling_price = None
                list_price = None
                original_price = None
                discount_percentage = 0
                is_on_sale = False

                # Find price container - use the wrapPrice container from the HTML structure
                price_container = None
                try:
                    price_container = product_elem.find_element(By.CLASS_NAME, 'vtex-flex-layout-0-x-flexCol--wrapPrice')
                except:
                    # Fallback: try the old priceContainer class
                    try:
                        price_container = product_elem.find_element(By.CLASS_NAME, 'valtech-carrefourar-product-price-0-x-priceContainer')
                    except:
                        pass

                # Extract selling price and list price from the container
                if price_container:
                    # Extract selling price
                    try:
                        selling_price_element = price_container.find_element(By.CLASS_NAME, 'valtech-carrefourar-product-price-0-x-sellingPrice')
                        # Find the currency container within the selling price element
                        currency_container = selling_price_element.find_element(By.CLASS_NAME, 'valtech-carrefourar-product-price-0-x-currencyContainer')
                        selling_price = extract_price_from_currency_container(currency_container)
                    except Exception as e:
                        pass

                    # Extract list price
                    try:
                        list_price_element = price_container.find_element(By.CLASS_NAME, 'valtech-carrefourar-product-price-0-x-listPrice')
                        # Find the currency container within the list price element
                        currency_container = list_price_element.find_element(By.CLASS_NAME, 'valtech-carrefourar-product-price-0-x-currencyContainer')
                        list_price = extract_price_from_currency_container(currency_container)
                    except Exception as e:
                        # Fallback: try to find listPrice anywhere in the product element
                        try:
                            list_price_element = product_elem.find_element(By.CLASS_NAME, 'valtech-carrefourar-product-price-0-x-listPrice')
                            currency_container = list_price_element.find_element(By.CLASS_NAME, 'valtech-carrefourar-product-price-0-x-currencyContainer')
                            list_price = extract_price_from_currency_container(currency_container)
                        except Exception as e2:
                            pass

                # If no prices found from containers, try direct selectors as fallback
                if selling_price is None:
                    price_selectors = [
                        "span.valtech-carrefourar-product-price-0-x-sellingPrice",
                        "span.valtech-carrefourar-product-price-0-x-sellingPriceValue",
                        "span.vtex-product-price-1-x-sellingPrice",
                        "span.vtex-product-price-1-x-currencyContainer",
                        "[data-testid*='selling-price']",
                        ".selling-price"
                    ]

                    for price_sel in price_selectors:
                        try:
                            if ":contains" in price_sel:
                                continue
                            price_elem = product_elem.find_element(By.CSS_SELECTOR, price_sel)
                            price_text = price_elem.text.strip()
                            if price_text and ('$' in price_text or 'ARS' in price_text):
                                selling_price = parse_argentine_price(price_text)
                                break
                        except:
                            continue

                # Try to extract list price (original price if on sale)
                if list_price is None:
                    list_price_selectors = [
                        "span.valtech-carrefourar-product-price-0-x-listPrice",
                        "span.vtex-product-price-1-x-listPrice",
                        "[data-testid*='list-price']",
                        ".list-price",
                        ".original-price"
                    ]

                    for price_sel in list_price_selectors:
                        try:
                            if ":contains" in price_sel:
                                continue
                            price_elem = product_elem.find_element(By.CSS_SELECTOR, price_sel)
                            price_text = price_elem.text.strip()
                            if price_text and ('$' in price_text or 'ARS' in price_text):
                                list_price = parse_argentine_price(price_text)
                                break
                        except:
                            continue

                # Convert prices to float for calculations
                selling_price_float = parse_argentine_price(selling_price) if selling_price else None
                list_price_float = parse_argentine_price(list_price) if list_price else None

                # If we have both prices, determine discount
                if selling_price_float and list_price_float:
                    if selling_price_float < list_price_float:
                        # Product is on sale
                        original_price = list_price
                        discount_percentage = round(((list_price_float - selling_price_float) / list_price_float) * 100, 2)
                        is_on_sale = True
                    else:
                        # No discount, selling price is the list price
                        original_price = selling_price
                elif selling_price_float:
                    # Only selling price found
                    original_price = selling_price
                    list_price = selling_price
                    list_price_float = selling_price_float
                else:
                    # Fallback to regex extraction
                    try:
                        product_text = product_elem.text
                        import re
                        price_match = re.search(r'\$?\d{1,3}(?:\.\d{3})*(?:,\d{2})?', product_text)
                        if price_match:
                            extracted_price = parse_argentine_price(price_match.group())
                            if extracted_price:
                                selling_price = price_match.group()
                                selling_price_float = extracted_price
                                list_price = selling_price
                                list_price_float = extracted_price
                                original_price = selling_price
                        else:
                            logging.debug(f"Skipping product {i+1} - could not extract valid price")
                            continue
                    except:
                        logging.debug(f"Skipping product {i+1} - could not extract price")
                        continue

                # Extract image URL
                image_url = None
                try:
                    img_elem = product_elem.find_element(By.CSS_SELECTOR, "img.vtex-product-summary-2-x-image")
                    image_url = img_elem.get_attribute("src")
                except:
                    try:
                        # Try alternative selectors
                        img_selectors = ["img", ".vtex-product-summary-2-x-imageContainer img"]
                        for img_sel in img_selectors:
                            try:
                                img_elem = product_elem.find_element(By.CSS_SELECTOR, img_sel)
                                image_url = img_elem.get_attribute("src")
                                if image_url:
                                    break
                            except:
                                continue
                    except:
                        pass

                # Extract brand (must match with brands from 'filters' collection)
                brand = None
                if product_name:
                    brand = extract_brand(product_name)

                # Extract subcategory (must match with subcategory from 'producttypes' collection)
                subcategory = None
                if product_type_name:
                    subcategory = extract_subcategory(product_type_name)

                # Extract promotions/ribbons
                promotions = []
                try:
                    ribbon_selectors = [
                        "span[data-specification-name]",
                        ".valtech-carrefourar-product-highlights-0-x-productRibbonHighlightWrapper",
                        "[class*='ribbon']",
                        "[class*='promotion']"
                    ]
                    for ribbon_sel in ribbon_selectors:
                        try:
                            ribbon_elems = product_elem.find_elements(By.CSS_SELECTOR, ribbon_sel)
                            for ribbon_elem in ribbon_elems:
                                ribbon_text = ribbon_elem.text.strip()
                                if ribbon_text and len(ribbon_text) > 3:
                                    promotions.append(ribbon_text)
                        except:
                            continue
                except:
                    pass

                # Extract product ID
                product_id = None
                try:
                    # Try to get from various attributes
                    id_selectors = [
                        "[data-product-id]",
                        "[data-product-sku]",
                        "[id*='product']",
                        "input[id*='739187']"
                    ]
                    for id_sel in id_selectors:
                        try:
                            id_elem = product_elem.find_element(By.CSS_SELECTOR, id_sel)
                            product_id = id_elem.get_attribute("data-product-id") or id_elem.get_attribute("data-product-sku") or id_elem.get_attribute("id")
                            if product_id:
                                break
                        except:
                            continue

                    # Try to extract from checkbox id pattern like "739187-188121-product-comparison"
                    if not product_id:
                        try:
                            checkbox = product_elem.find_element(By.CSS_SELECTOR, "input[type='checkbox']")
                            checkbox_id = checkbox.get_attribute("id")
                            if checkbox_id and "-product-comparison" in checkbox_id:
                                product_id = checkbox_id.split("-product-comparison")[0]
                        except:
                            pass
                except:
                    pass

                # Check availability (if add to cart button exists)
                available = True
                try:
                    # Look for add to cart button or unavailable indicators
                    cart_buttons = product_elem.find_elements(By.CSS_SELECTOR, "button.vtex-button, .valtech-carrefourar-add-to-cart-quantity-0-x-container")
                    unavailable_indicators = product_elem.find_elements(By.CSS_SELECTOR, "[class*='unavailable'], [class*='out-of-stock']")

                    if unavailable_indicators or not cart_buttons:
                        available = False
                except:
                    pass

                # Extract product URL
                product_url = None
                try:
                    # Try to find product link
                    link_elem = product_elem.find_element(By.CSS_SELECTOR, "a[href*='/p']")
                    product_url = link_elem.get_attribute("href")
                    if product_url and not product_url.startswith("http"):
                        product_url = f"https://www.carrefour.com.ar{product_url}"
                except:
                    try:
                        # Alternative selectors for product links
                        link_selectors = ["a.vtex-product-summary-2-x-clearLink", "a[href]", "a"]
                        for link_sel in link_selectors:
                            try:
                                link_elem = product_elem.find_element(By.CSS_SELECTOR, link_sel)
                                href = link_elem.get_attribute("href")
                                if href and '/p' in href:
                                    product_url = href if href.startswith("http") else f"https://www.carrefour.com.ar{href}"
                                    break
                            except:
                                continue
                    except:
                        pass

                # Extract description (if available in product summary)
                description = None
                try:
                    desc_selectors = [
                        ".vtex-product-summary-2-x-productDescription",
                        "[class*='description']",
                        ".valtech-carrefourar-product-summary-0-x-productDescription"
                    ]
                    for desc_sel in desc_selectors:
                        try:
                            desc_elem = product_elem.find_element(By.CSS_SELECTOR, desc_sel)
                            description = desc_elem.text.strip()
                            if description:
                                break
                        except:
                            continue
                except:
                    pass

                # Extract nutritional info (if available)
                nutritional_info = None
                try:
                    # Look for nutritional information in product details
                    nutritional_selectors = [
                        "[class*='nutritional']",
                        "[class*='nutrition']",
                        ".valtech-carrefourar-product-summary-0-x-nutritionalInfo"
                    ]
                    for nutr_sel in nutritional_selectors:
                        try:
                            nutr_elem = product_elem.find_element(By.CSS_SELECTOR, nutr_sel)
                            nutritional_info = nutr_elem.text.strip()
                            if nutritional_info:
                                break
                        except:
                            continue
                except:
                    pass

                # Extract package info (weight, volume, etc.)
                package_info = None
                try:
                    package_selectors = [
                        "[class*='package']",
                        "[class*='weight']",
                        "[class*='volume']",
                        ".valtech-carrefourar-product-summary-0-x-packageInfo"
                    ]
                    for pkg_sel in package_selectors:
                        try:
                            pkg_elem = product_elem.find_element(By.CSS_SELECTOR, pkg_sel)
                            package_info = pkg_elem.text.strip()
                            if package_info:
                                break
                        except:
                            continue
                except:
                    pass

                # Extract promotional clusters
                promotional_clusters = []
                try:
                    # Look for promotional badges or clusters
                    cluster_selectors = [
                        ".valtech-carrefourar-product-highlights-0-x-productClusterHighlight",
                        "[class*='cluster']",
                        "[class*='highlight']",
                        "[data-specification-name]"
                    ]
                    for cluster_sel in cluster_selectors:
                        try:
                            cluster_elems = product_elem.find_elements(By.CSS_SELECTOR, cluster_sel)
                            for cluster_elem in cluster_elems:
                                cluster_text = cluster_elem.text.strip()
                                if cluster_text and len(cluster_text) > 2:
                                    promotional_clusters.append(cluster_text)
                        except:
                            continue
                except:
                    pass

                product_data = {
                    'productUrl': product_url,  # URL del producto
                    'seller': 'Carrefour',  # Vendedor
                    'name': product_name,
                    'category': category_name,
                    'subcategory': subcategory,  # Campo requerido (extraído de producttypes collection)
                    'productType': product_type_name,
                    'brand': brand,
                    'listPrice': list_price,  # Precio de lista
                    'sellingPrice': selling_price,  # Precio de venta
                    'currency': 'ARS',  # Moneda
                    'isOnSale': is_on_sale,  # Si está en oferta
                    'discountPercentage': discount_percentage,  # Porcentaje de descuento
                    'promotions': promotions,
                    'promotionalClusters': promotional_clusters,  # Clusters promocionales
                    'nutritionalInfo': nutritional_info,  # Información nutricional
                    'packageInfo': package_info,  # Información de empaque
                    'mainImage': image_url,  # Imagen principal
                    'productId': product_id,
                    'createdAt': datetime.now(),  # Fecha de creación
                    'lastUpdated': datetime.now(),  # Última actualización
                    'isAvailable': available,  # Si está disponible
                    'description': description,  # Descripción del producto
                    'page': 1  # Página por defecto, se actualiza en extract_all_products_from_pages
                }

                products.append(product_data)

            except Exception as e:
                continue

        return products

    except Exception as e:
        logging.error(f"Error extracting products: {e}")
        return []

def get_total_pages(driver):
    """Detect pagination and return total number of pages"""
    try:
        # Look for pagination container
        pagination_selectors = [
            "div.valtech-carrefourar-search-result-3-x-paginationContainer",
            "div.flex.justify-center.items-center.ma6",
            ".paginationContainer",
            "[class*='pagination']"
        ]

        pagination_container = None
        for selector in pagination_selectors:
            try:
                pagination_container = driver.find_element(By.CSS_SELECTOR, selector)
                if pagination_container and pagination_container.is_displayed():
                    logging.info(f"Found pagination container with selector: {selector}")
                    break
            except:
                continue

        if not pagination_container:
            return 1

        # Find all page buttons
        page_buttons = pagination_container.find_elements(By.CSS_SELECTOR, "button[value]")

        if not page_buttons:
            return 1

        # Get the highest page number
        max_page = 1
        for btn in page_buttons:
            try:
                page_value = btn.get_attribute("value")
                if page_value and page_value.isdigit():
                    page_num = int(page_value)
                    max_page = max(max_page, page_num)
            except:
                continue

        return max_page

    except Exception as e:
        logging.warning(f"Error detecting pagination: {e}")
        return 1

def navigate_to_page(driver, page_number):
    """Navigate to a specific page by clicking the page button or using Next button - IMPROVED FOR CARREFOUR"""
    try:
        if page_number == 1:
            logging.info("Already on page 1")
            return True

        logging.info(f"Attempting to navigate to page {page_number}")

        # Wait a bit for page to stabilize
        time.sleep(1)

        # Strategy 1: Try to click the specific page number button
        if page_number > 1:
            try:
                # Find the page button container and click the button inside
                page_button_containers = driver.find_elements(By.CSS_SELECTOR, f"div.valtech-carrefourar-search-result-3-x-paginationButtonPages button[value='{page_number}']")

                for container in page_button_containers:
                    try:
                        button = container
                        if button and button.is_displayed() and button.is_enabled():
                            # Scroll to the button
                            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
                            time.sleep(0.5)

                            # Click the button
                            driver.execute_script("arguments[0].click();", button)
                            time.sleep(2)  # Wait for page to load

                            logging.info(f"Successfully clicked page {page_number} button")
                            return True
                    except Exception as e:
                        logging.debug(f"Error clicking page {page_number} button: {e}")
                        continue

            except Exception as e:
                logging.debug(f"Error in strategy 1: {e}")

        # Strategy 2: Use Next button to navigate page by page (more reliable)
        current_page = 1  # Assume we're starting from page 1 or can determine current page

        while current_page < page_number:
            try:
                # Find the Next button container
                next_button_containers = driver.find_elements(By.CSS_SELECTOR, "div.valtech-carrefourar-search-result-3-x-paginationButtonChangePageNext")

                next_button = None
                for container in next_button_containers:
                    try:
                        button = container.find_element(By.TAG_NAME, "button")
                        if button and button.is_displayed() and not button.get_attribute("disabled"):
                            next_button = button
                            break
                    except:
                        continue

                if not next_button:
                    logging.error(f"Next button not found or not clickable at page {current_page}")
                    return False

                # Scroll to and click Next button
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_button)
                time.sleep(0.5)
                driver.execute_script("arguments[0].click();", next_button)

                current_page += 1
                time.sleep(2)  # Wait for page to load

                logging.info(f"Successfully navigated to page {current_page} using Next button")

                if current_page == page_number:
                    return True

            except Exception as e:
                logging.error(f"Error navigating to page {current_page + 1}: {e}")
                return False

        return True

    except Exception as e:
        logging.error(f"Error navigating to page {page_number}: {e}")
        return False

def select_product_type(driver, target_product_type):
    """Seleccionar un tipo de producto específico usando las mismas funciones que funcionan al inicio del script"""
    try:
        # Use the same expansion logic as the initial setup
        product_types_container = expand_product_type_menu(driver)
        if not product_types_container:
            return None

        # Scroll and click "Ver más" if needed
        scroll_and_click_ver_mas_product_types(driver, product_types_container)

        # Try multiple selectors for product type checkboxes
        checkbox_selectors = [
            "input[type='checkbox'][id^='tipo-de-producto-']",
            "input[type='checkbox']",
            ".valtech-carrefourar-search-result-3-x-filter__checkbox input[type='checkbox']"
        ]

        # Function to find checkboxes
        def find_checkboxes():
            for selector in checkbox_selectors:
                try:
                    elements = product_types_container.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        return elements
                except Exception as e:
                    continue
            return []

        # Function to find target checkbox
        def find_target_checkbox(checkboxes):
            for checkbox in checkboxes:
                try:
                    input_id = checkbox.get_attribute("id")
                    if input_id:
                        label = driver.find_element(By.CSS_SELECTOR, f"label[for='{input_id}']")
                        label_text = label.get_attribute("textContent").strip()
                        # Remove count in parentheses if present
                        clean_label = label_text.split('(')[0].strip()

                        if clean_label.lower() == target_product_type.lower():
                            return checkbox, clean_label
                except Exception as e:
                    continue
            return None, None

        # Function to find target checkbox
        def find_target_checkbox(checkboxes):
            for checkbox in checkboxes:
                try:
                    input_id = checkbox.get_attribute("id")
                    if input_id:
                        label = driver.find_element(By.CSS_SELECTOR, f"label[for='{input_id}']")
                        label_text = label.get_attribute("textContent").strip()
                        # Remove count in parentheses if present
                        clean_label = label_text.split('(')[0].strip()

                        if clean_label.lower() == target_product_type.lower():
                            return checkbox, clean_label
                except Exception as e:
                    continue
            return None, None

        # Find the target checkbox
        checkboxes = find_checkboxes()
        if not checkboxes:
            return None

        target_checkbox, target_label = find_target_checkbox(checkboxes)

        if not target_checkbox:
            return None

        # Scroll to and select the checkbox
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", target_checkbox)
        time.sleep(0.5)
        driver.execute_script("arguments[0].click();", target_checkbox)

        return target_label

    except Exception as e:
        logging.error(f"Error selecting product type '{target_product_type}': {e}")
        return None

def verify_single_product_type_selection(driver, expected_product_type):
    """Verify that only the expected product type is selected in the selected filters container"""
    try:
        # Find selected filters container specifically
        selected_container_selectors = [
            "div.valtech-carrefourar-search-result-3-x-filter__container--selectedFilters",
            "div.valtech-carrefourar-search-result-3-x-selectedFilters",
            "[class*='selectedFilters']",
            "[class*='selected-filters']"
        ]

        selected_container = None
        for selector in selected_container_selectors:
            try:
                selected_container = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                logging.debug(f"Found selected filters container with selector: {selector}")
                break
            except:
                continue

        if not selected_container:
            logging.warning(f"⚠️ No selected filters container found with any selector")
            # Try to check if we're on the right page by looking for product results
            try:
                product_count_elem = driver.find_element(By.CSS_SELECTOR, "div.valtech-carrefourar-search-result-3-x-totalProducts--layout")
                if product_count_elem:
                    logging.info("✓ Found product results, filter may have been applied successfully despite missing selected filters container")
                    return True
            except:
                logging.warning("⚠️ No product results found either")
            return False

        # Find all selected filter labels within this container
        selected_labels = selected_container.find_elements(By.CSS_SELECTOR, "label.vtex-checkbox__label")

        selected_product_types = []
        for label in selected_labels:
            try:
                text = label.get_attribute("textContent").strip()
                # Remove count in parentheses if present
                clean_text = text.split('(')[0].strip()
                if clean_text:
                    selected_product_types.append(clean_text.lower())
            except:
                continue

        logging.info(f"Currently selected product types: {selected_product_types}")

        # Check if only the expected product type is selected
        expected_lower = expected_product_type.lower()
        if expected_lower == "none":
            # Should have no product types selected
            if len(selected_product_types) == 0:
                logging.info("✓ Verified no product types selected")
                return True
            else:
                logging.warning(f"⚠️ Found {len(selected_product_types)} product types selected when none expected: {selected_product_types}")
                return False
        elif len(selected_product_types) == 1 and selected_product_types[0] == expected_lower:
            logging.info(f"✓ Verified single selection: only '{expected_product_type}' is selected")
            return True
        elif len(selected_product_types) == 0:
            logging.warning(f"⚠️ No product types selected, expected '{expected_product_type}'")
            return False
        else:
            logging.warning(f"⚠️ Multiple or wrong product types selected: {selected_product_types}, expected only '{expected_product_type}'")
            return False

    except Exception as e:
        logging.warning(f"Error verifying single selection: {e}")
        return False

def clear_all_selected_filters(driver):
    """Clear all selected filters using the 'Borrar Filtros' link - OPTIMIZED VERSION"""
    try:
        # Try to find and click "Borrar Filtros" link quickly
        try:
            clear_link = driver.find_element(By.CSS_SELECTOR, "a.valtech-carrefourar-search-result-3-x-clearFilter")
            if clear_link.is_displayed() and clear_link.is_enabled():
                driver.execute_script("arguments[0].click();", clear_link)
                time.sleep(1)  # Short wait for filters to clear
                return True
        except:
            pass

        # If clear link not found, assume filters are already clear (no need for individual deselection)
        return True

    except Exception as e:
        logging.debug(f"Error clearing filters (non-critical): {e}")
        return True  # Don't fail the process for filter clearing issues

def clear_filters_individually(driver):
    """Clear filters by clicking on each selected filter individually"""
    try:
        # Find selected filters container
        selected_container_selectors = [
            "div.valtech-carrefourar-search-result-3-x-filter__container--selectedFilters",
            "div.valtech-carrefourar-search-result-3-x-selectedFilters",
            "[class*='selectedFilters']",
            "[class*='selected-filters']"
        ]

        selected_container = None
        for selector in selected_container_selectors:
            try:
                selected_container = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                break
            except:
                continue

        if not selected_container:
            logging.info("No selected filters container found - filters may already be clear")
            return True

        # Find all selected filter items
        selected_items = selected_container.find_elements(By.CSS_SELECTOR, "div.valtech-carrefourar-search-result-3-x-filterItem--selected")

        if not selected_items:
            logging.info("No selected filter items found - filters are clear")
            return True

        logging.info(f"Found {len(selected_items)} selected filters to clear")

        # Click on each selected filter to deselect it
        for i, item in enumerate(selected_items):
            try:
                # Scroll to the item
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", item)
                time.sleep(0.5)

                # Try multiple ways to click
                clicked = False
                click_methods = [
                    lambda: driver.execute_script("arguments[0].click();", item),
                    lambda: item.find_element(By.CSS_SELECTOR, "input[type='checkbox']").click(),
                    lambda: item.find_element(By.CSS_SELECTOR, "label").click()
                ]

                for click_method in click_methods:
                    try:
                        click_method()
                        clicked = True
                        logging.debug(f"Clicked selected filter {i+1}")
                        time.sleep(0.5)
                        break
                    except:
                        continue

                if not clicked:
                    logging.warning(f"Could not click selected filter {i+1}")

            except Exception as e:
                logging.debug(f"Error clearing selected filter {i+1}: {e}")
                continue

        time.sleep(1)  # Wait for deselection to take effect

        # Verify all filters are cleared
        if verify_single_product_type_selection(driver, "none"):
            logging.info("✓ Successfully cleared all filters individually")
            return True
        else:
            logging.warning("⚠️ Individual filter clearing may not have worked completely")
            return False

    except Exception as e:
        logging.error(f"Error clearing filters individually: {e}")
        return False

def count_total_products_in_category(driver, product_type_name):
    """Count total number of products shown in the current category/filter"""
    try:
        # Look for product count text
        count_selectors = [
            "span.valtech-carrefourar-search-result-0-x-totalProducts",
            "span[data-testid*='total']",
            "span:contains('productos')",
            "span:contains('products')",
            ".search-result-info span",
            "[class*='total'] span"
        ]

        for selector in count_selectors:
            try:
                if selector.startswith("span:contains"):
                    if 'productos' in selector:
                        elements = driver.find_elements(By.XPATH, "//span[contains(text(), 'productos')]")
                    elif 'products' in selector:
                        elements = driver.find_elements(By.XPATH, "//span[contains(text(), 'products')]")
                    else:
                        continue
                else:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)

                for element in elements:
                    if element.is_displayed():
                        text = element.text.strip()
                        # Extract number from text like "X productos" or "X products"
                        import re
                        match = re.search(r'(\d+(?:[.,]\d+)*)', text)
                        if match:
                            count_str = match.group(1).replace('.', '').replace(',', '')
                            try:
                                return int(count_str)
                            except ValueError:
                                continue
            except:
                continue

        # Fallback: count actual product elements on current page
        try:
            product_elements = driver.find_elements(By.CSS_SELECTOR, "article[data-testid*='product'], .product-item, .product-card")
            if product_elements:
                # Assume 24 products per page (common pagination)
                # This is a rough estimate when we can't find the total count
                return len(product_elements)  # Return count on first page as minimum
        except:
            pass

        return 0

    except Exception as e:
        logging.debug(f"Error counting total products: {e}")
        return 0

def generate_extraction_error_report(product_type_name, category_name, expected_count, extracted_count, products_data):
    """Generate a detailed error report for incomplete extraction"""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_filename = f"extraction_error_{product_type_name.replace(' ', '_')}_{timestamp}.txt"

        with open(report_filename, 'w', encoding='utf-8') as f:
            f.write("=== EXTRACTION ERROR REPORT ===\n\n")
            f.write(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Product Type: {product_type_name}\n")
            f.write(f"Category: {category_name}\n")
            f.write(f"Expected Products: {expected_count}\n")
            f.write(f"Extracted Products: {extracted_count}\n")
            f.write(f"Missing Products: {expected_count - extracted_count}\n")
            f.write(f"Extraction Rate: {(extracted_count/expected_count*100):.1f}%\n\n")

            f.write("=== EXTRACTED PRODUCTS SUMMARY ===\n")
            if products_data:
                f.write(f"Total products in extraction data: {len(products_data)}\n\n")
                # Show first few products as examples
                f.write("Sample extracted products:\n")
                for i, product in enumerate(products_data[:5]):
                    f.write(f"  {i+1}. {product.get('name', 'N/A')} - {product.get('price', 'N/A')}\n")
                if len(products_data) > 5:
                    f.write(f"  ... and {len(products_data) - 5} more products\n")
            else:
                f.write("No products extracted\n")

            f.write("\n=== RECOMMENDATIONS ===\n")
            f.write("1. Check pagination logic - may be missing pages\n")
            f.write("2. Verify filter application - product type filter may not be working\n")
            f.write("3. Check for dynamic content loading issues\n")
            f.write("4. Review anti-detection measures - site may be blocking requests\n")
            f.write("5. Consider increasing wait times between requests\n")

        logging.error(f"Error report generated: {report_filename}")
        return report_filename

    except Exception as e:
        logging.error(f"Failed to generate error report: {e}")
        return None

def extract_all_products_from_pages(driver, product_type_name, category_name, subcategory_name=None):
    """Extract products from all pages for a product type - IMPROVED VERSION"""
    try:
        all_products = []

        # Get total expected products
        total_expected = get_total_products(driver)
        if total_expected:
            logging.info(f"Expected to extract {total_expected} products for '{product_type_name}'")
        expected_pages = (total_expected + 15) // 16 if total_expected else 1

        current_page = 1
        products_extracted = 0
        max_pages = 100  # Safety limit to prevent infinite loops

        while current_page <= max_pages:
            logging.info(f"Extracting products from page {current_page}")

            # Extract products from current page
            page_products = extract_products(driver, product_type_name, category_name, subcategory_name)
            page_count = len(page_products)

            if page_count == 0:
                logging.warning(f"No products found on page {current_page}, stopping extraction")
                break

            # Add page number to products for tracking
            for product in page_products:
                product['page'] = current_page

            all_products.extend(page_products)
            products_extracted += page_count

            logging.info(f"Extracted {page_count} products from page {current_page} (total: {products_extracted})")

            # Check if we have all expected products
            if total_expected and products_extracted >= total_expected:
                logging.info(f"Reached expected total of {total_expected} products")
                break

            # Check if there are more pages by looking for pagination
            if not has_next_page(driver):
                logging.info("No more pages available")
                break

            # Try to navigate to next page
            current_page += 1
            logging.info(f"Attempting to navigate to page {current_page}")

            if not navigate_to_page(driver, current_page):
                logging.error(f"Failed to navigate to page {current_page}")
                break

            # Wait for the page to load and verify we're on the correct page
            time.sleep(3)  # Increased wait time

            # Verify we're on the correct page by checking if page button is active
            try:
                active_page_buttons = driver.find_elements(By.CSS_SELECTOR, "div.valtech-carrefourar-search-result-3-x-paginationButtonActive button")
                if active_page_buttons:
                    active_page_value = active_page_buttons[0].get_attribute("value")
                    if active_page_value and int(active_page_value) == current_page:
                        logging.info(f"Confirmed: now on page {current_page}")
                    else:
                        logging.warning(f"Page verification failed: expected page {current_page}, found active page {active_page_value}")
            except Exception as e:
                logging.debug(f"Could not verify page number: {e}")

        logging.info(f"Extraction completed: {len(all_products)} products extracted from {current_page} pages")

        # Log extraction completion (don't raise exception anymore - let caller handle it)
        if total_expected and len(all_products) < total_expected:
            error_msg = f"⚠️ EXTRACTION INCOMPLETE: Only {len(all_products)}/{total_expected} products extracted for '{product_type_name}'"
            logging.warning(error_msg)

            # Still generate error report for debugging
            generate_extraction_error_report(product_type_name, category_name, total_expected, len(all_products), all_products)

        return all_products

    except Exception as e:
        logging.error(f"Error extracting products from all pages: {e}")
        return []

def save_products_to_db(products, category_name):
    """Save individual products to the 'products' collection in MongoDB with upsert logic"""
    try:
        client = MongoClient('mongodb://localhost:27017/')
        db = client['carrefour']
        collection = db['products']

        saved_count = 0
        updated_count = 0

        for product in products:
            try:
                # Create unique filter based on name, productType, and category
                filter_criteria = {
                    'name': product.get('name'),
                    'productType': product.get('productType'),
                    'category': product.get('category')
                }

                # Use upsert to update existing products or insert new ones
                # Also remove redundant fields
                update_data = {k: v for k, v in product.items() if k not in ['extracted_at', 'available', 'scrapedAt', 'updatedAt']}
                result = collection.update_one(
                    filter_criteria,
                    {'$set': update_data, '$unset': {'extracted_at': 1, 'available': 1, 'scrapedAt': 1, 'updatedAt': 1}},
                    upsert=True
                )

                if result.upserted_id:
                    # New document was inserted
                    saved_count += 1
                elif result.modified_count > 0:
                    # Existing document was updated
                    updated_count += 1
                else:
                    # Document existed but no changes were made
                    saved_count += 1  # Count as "saved" for compatibility

            except Exception as e:
                logging.debug(f"Error saving product '{product.get('name', 'Unknown')}': {e}")
                continue

        client.close()

        total_processed = saved_count + updated_count
        logging.warning(f"Processed {total_processed} products ({saved_count} new, {updated_count} updated)")
        return total_processed

    except Exception as e:
        logging.error(f"Error saving products to database: {e}")
        return 0

def generate_final_report(successful_types, partial_types, failed_types, category_name):
    """Generate a comprehensive final report of the extraction process"""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_filename = f"extraction_report_{category_name}_{timestamp}.txt"

        with open(report_filename, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write(f"REPORTE FINAL DE EXTRACCIÓN - {category_name.upper()}\n")
            f.write(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 80 + "\n\n")

            # Summary
            total_types = len(successful_types) + len(partial_types) + len(failed_types)
            f.write("RESUMEN GENERAL:\n")
            f.write(f"- Total de tipos de producto procesados: {total_types}\n")
            f.write(f"- Tipos procesados al 100%: {len(successful_types)}\n")
            f.write(f"- Tipos procesados con problemas: {len(partial_types)}\n")
            f.write(f"- Tipos que fallaron completamente: {len(failed_types)}\n\n")

            # Successful types
            f.write("✅ TIPOS DE PRODUCTO REGISTRADOS AL 100%:\n")
            if successful_types:
                for item in successful_types:
                    f.write(f"  - {item['type']}: {item['products']} productos\n")
            else:
                f.write("  (Ninguno)\n")
            f.write("\n")

            # Partial types
            f.write("⚠️ TIPOS DE PRODUCTO CON PROBLEMAS:\n")
            if partial_types:
                for item in partial_types:
                    f.write(f"  - {item['type']}:\n")
                    f.write(f"    Esperados: {item['expected']}, Extraídos: {item['extracted']}, Válidos: {item['valid']}\n")
                    f.write(f"    Problemas: {', '.join(item['issues'])}\n")
            else:
                f.write("  (Ninguno)\n")
            f.write("\n")

            # Failed types
            f.write("❌ TIPOS DE PRODUCTO QUE FALLARON:\n")
            if failed_types:
                for item in failed_types:
                    f.write(f"  - {item['type']}: {item['reason']}\n")
            else:
                f.write("  (Ninguno)\n")
            f.write("\n")

            f.write("=" * 80 + "\n")
            f.write("FIN DEL REPORTE\n")
            f.write("=" * 80 + "\n")

        logging.warning(f"📄 Reporte final generado: {report_filename}")
        print(f"\n📄 Reporte final generado: {report_filename}")

        # Also print summary to console
        print("\n" + "=" * 60)
        print(f"RESUMEN FINAL - {category_name.upper()}")
        print("=" * 60)
        print(f"Total tipos procesados: {total_types}")
        print(f"✅ Completos (100%): {len(successful_types)}")
        print(f"⚠️ Parciales: {len(partial_types)}")
        print(f"❌ Fallidos: {len(failed_types)}")
        print("=" * 60)

    except Exception as e:
        logging.error(f"Error generating final report: {e}")

def process_single_category(category_data):
    """Process a single category with its own browser instance - MODIFIED TO SAVE TO PRODUCTS COLLECTION"""
    category_idx, category = category_data
    category_name = category.get('name')
    category_url = category.get('url')

    # Create unique logger for this thread
    thread_logger = logging.getLogger(f"Thread-{category_idx}")
    thread_logger.setLevel(logging.INFO)

    # Initialize tracking dictionaries for final report
    local_successful_types = []  # Types processed at 100%
    local_partial_types = []     # Types with some issues
    local_failed_types = []      # Types that completely failed

    # Create separate driver for this category
    user_agent = get_random_user_agent()
    driver = None

    try:
        thread_logger.info(f"🚀 Starting processing of category '{category_name}' with User-Agent: {user_agent[:50]}...")

        # Initialize driver with random user agent
        driver = setup_driver(user_agent)

        # Add random delay before starting
        random_delay()

        # Navigate to category - OPTIMIZED
        thread_logger.info(f"🚀 Loading category '{category_name}'...")
        def navigate_with_retry():
            driver.get(category_url)
            time.sleep(0.5)  # Minimal delay
            handle_cookies(driver)

        retry_with_backoff(navigate_with_retry)
        time.sleep(1)

        # Setup filters in one go - OPTIMIZED
        thread_logger.info("Setting up filters...")
        def setup_filters_with_retry():
            open_filters_panel(driver)
            time.sleep(0.5)
            scroll_to_load_filters(driver)
            time.sleep(0.5)

            # Expand product types menu
            product_types_container = expand_product_type_menu(driver)
            if not product_types_container:
                raise Exception("Failed to expand product types menu")
            time.sleep(0.5)

            # Scroll and click "Ver más" if needed
            scroll_and_click_ver_mas_product_types(driver, product_types_container)
            time.sleep(0.5)

            return product_types_container

        product_types_container = retry_with_backoff(setup_filters_with_retry)
        if not product_types_container:
            thread_logger.error(f"Failed to setup filters for category '{category_name}'")
            return False

        # Get all product types with retry
        def get_product_types_with_retry():
            all_product_types = get_all_product_types(driver)
            if not all_product_types:
                raise Exception("Failed to get product types")
            return all_product_types

        all_product_types = retry_with_backoff(get_product_types_with_retry)
        if not all_product_types:
            return False

        logging.warning(f"Found {len(all_product_types)} product types")

        # Process all product types from the beginning
        total_types = len(all_product_types)
        total_products_saved = 0

        thread_logger.info(f"🎯 Processing all product types from the beginning")

        # Process all product types starting from the first one
        for idx, product_type in enumerate(all_product_types, 1):
            thread_logger.info(f"=== Processing product type {idx}/{total_types}: '{product_type}' ===")

            # Quick delay between product types
            time.sleep(0.5)

            # Quick filter clearing
            clear_all_selected_filters(driver)
            time.sleep(0.3)

            # Select product type with retry
            def select_product_type_with_retry():
                selected_type = select_product_type(driver, product_type)
                if not selected_type:
                    raise Exception(f"Could not select product type '{product_type}'")
                return selected_type

            selected_type = retry_with_backoff(select_product_type_with_retry)
            if not selected_type:
                failed_types.append({
                    'type': product_type,
                    'reason': 'Could not select product type after retries'
                })
                continue

            time.sleep(0.3)

            # Apply filter with verification
            def apply_filter_with_retry():
                success = apply_filter(driver)
                if success:
                    # Wait for filter to be applied and verify
                    time.sleep(2)
                    if verify_single_product_type_selection(driver, selected_type):
                        logging.info(f"✓ Filter applied successfully for '{selected_type}'")
                        return True
                    else:
                        logging.warning(f"⚠️ Filter verification failed for '{selected_type}'")
                        return False
                return False

            filter_applied = retry_with_backoff(apply_filter_with_retry)
            if not filter_applied:
                logging.error(f"Failed to apply and verify filter for product type '{selected_type}'")
                failed_types.append({
                    'type': product_type,
                    'reason': 'Failed to apply and verify filter after retries'
                })
                clear_all_selected_filters(driver)
                time.sleep(0.3)
                continue

            time.sleep(0.3)

            # Count total products before extraction
            total_expected_products = count_total_products_in_category(driver, selected_type)
            thread_logger.info(f"📊 Expected to extract {total_expected_products} products for '{selected_type}'")

            # VALIDATION: Check if too many products (more than 3000)
            if total_expected_products > 3000:
                logging.warning(f"⚠️ Too many products ({total_expected_products}) for '{selected_type}' - skipping")
                failed_types.append({
                    'type': product_type,
                    'reason': f'Too many products ({total_expected_products} > 3000)'
                })
                clear_all_selected_filters(driver)
                time.sleep(0.3)
                continue

            # VALIDATION: Check if no products filtered (would get all category products)
            if total_expected_products == 0:
                logging.warning(f"⚠️ No products found for '{selected_type}' - skipping to avoid processing entire category")
                failed_types.append({
                    'type': product_type,
                    'reason': 'No products filtered (would process entire category)'
                })
                clear_all_selected_filters(driver)
                time.sleep(0.3)
                continue

            # Extract all products from all pages with retry
            try:
                all_products = extract_all_products_from_pages(driver, selected_type, category_name, None)

                if all_products:
                    extracted_count = len(all_products)
                    thread_logger.info(f"📦 Successfully extracted {extracted_count} products for '{selected_type}'")

                    # Validate that extracted products match the expected product type
                    valid_products = validate_product_type_consistency(all_products, selected_type, category_name)

                    # Save products to 'products' collection
                    saved_count = save_products_to_db(all_products, category_name)
                    total_products_saved += saved_count
                    logging.warning(f"Saved {saved_count} products for '{selected_type}'")

                    # Determine success level
                    if extracted_count == total_expected_products and valid_products == extracted_count:
                        # 100% success
                        local_successful_types.append({
                            'type': product_type,
                            'products': extracted_count
                        })
                    else:
                        # Partial success - track missing products
                        missing_products = []
                        if extracted_count < total_expected_products:
                            missing_products.append(f"{total_expected_products - extracted_count} products not extracted")
                        if valid_products < extracted_count:
                            missing_products.append(f"{extracted_count - valid_products} products don't match type")

                        local_partial_types.append({
                            'type': product_type,
                            'expected': total_expected_products,
                            'extracted': extracted_count,
                            'valid': valid_products,
                            'issues': missing_products
                        })
                else:
                    logging.warning(f"No products extracted for '{selected_type}'")
                    local_failed_types.append({
                        'type': product_type,
                        'reason': 'No products extracted'
                    })

            except Exception as e:
                error_msg = str(e)
                logging.error(f"Failed to extract products for '{selected_type}': {error_msg}")
                local_failed_types.append({
                    'type': product_type,
                    'reason': f'Extraction failed: {error_msg}'
                })

            # Quick cleanup for next iteration
            clear_all_selected_filters(driver)
            time.sleep(0.3)

        logging.warning(f"Category '{category_name}' completed - {total_products_saved} total products saved")

        # Update global tracking lists
        with tracking_lock:
            successful_types.extend(local_successful_types)
            partial_types.extend(local_partial_types)
            failed_types.extend(local_failed_types)

        return True

    except Exception as e:
        logging.error(f"Error processing category '{category_name}': {e}")
        return False

    finally:
        if driver:
            try:
                driver.quit()
                thread_logger.info(f"🛑 Driver closed for category '{category_name}'")
            except:
                pass

def validate_product_type_consistency(products_data, expected_product_type, category_name):
    """Validate that extracted products match the expected product type"""
    if not products_data:
        return 0

    consistent_count = 0
    for product in products_data:
        product_name = product.get('name', '').lower()
        if is_product_name_relevant(product_name, expected_product_type):
            consistent_count += 1

    return consistent_count

def has_next_page(driver):
    """Check if there is a next page in the pagination - IMPROVED VERSION FOR CARREFOUR"""
    try:
        # Strategy 1: Look for enabled "Siguiente" button
        try:
            # Look for the specific Next button container and check if the button inside is not disabled
            next_button_containers = driver.find_elements(By.CSS_SELECTOR, "div.valtech-carrefourar-search-result-3-x-paginationButtonChangePageNext")
            for container in next_button_containers:
                try:
                    button = container.find_element(By.TAG_NAME, "button")
                    if button and not button.get_attribute("disabled"):
                        logging.debug("Found enabled 'Siguiente' button")
                        return True
                except:
                    continue
        except:
            pass

        # Strategy 2: Check for page number buttons beyond the current page
        try:
            # Find all page number buttons
            page_buttons = driver.find_elements(By.CSS_SELECTOR, "div.valtech-carrefourar-search-result-3-x-paginationButtonPages button[value]")

            current_page = None
            max_page = 1

            for btn in page_buttons:
                try:
                    page_num = int(btn.get_attribute("value"))
                    max_page = max(max_page, page_num)

                    # Check if this button has the active class
                    parent_div = btn.find_element(By.XPATH, "..")  # Get parent div
                    if "valtech-carrefourar-search-result-3-x-paginationButtonActive" in parent_div.get_attribute("class"):
                        current_page = page_num
                        logging.debug(f"Found current active page: {current_page}")
                    elif current_page is not None and page_num > current_page and btn.is_enabled():
                        logging.debug(f"Found next page button: {page_num}")
                        return True

                except:
                    continue

            # If we have more than one page, check if current page is not the last
            if current_page is not None and max_page > current_page:
                logging.debug(f"Current page {current_page} < max page {max_page}, more pages available")
                return True

        except Exception as e:
            logging.debug(f"Error in strategy 2: {e}")

        # Strategy 3: Check if there are any page buttons with value > 1
        try:
            page_buttons = driver.find_elements(By.CSS_SELECTOR, "button[value]")
            for btn in page_buttons:
                try:
                    value = btn.get_attribute("value")
                    if value and value.isdigit():
                        page_num = int(value)
                        if page_num > 1:
                            logging.debug(f"Found page button with value > 1: {page_num}")
                            return True
                except:
                    continue
        except:
            pass

        logging.debug("No next page indicators found")
        return False

    except Exception as e:
        logging.debug(f"Error checking next page: {e}")
        return False

def main():
    """Main function - process all categories in batches of 3 simultaneously"""
    try:
        logging.warning("Starting product extraction to 'products' collection")
        logging.warning(f"Random delays: {MIN_DELAY}-{MAX_DELAY}s, Retries: {MAX_RETRIES}")

        all_categories = get_all_categories()
        if not all_categories:
            logging.error("No categories found")
            return

        # Process categories in batches of 3
        batch_size = 3
        for i in range(0, len(all_categories), batch_size):
            batch = all_categories[i:i + batch_size]
            logging.warning(f"Processing batch {i//batch_size + 1}: {[cat.get('name') for cat in batch]}")

            threads = []
            for idx, category in enumerate(batch):
                category_data = (i + idx, category)
                thread = threading.Thread(target=process_single_category, args=(category_data,))
                threads.append(thread)
                thread.start()

            # Wait for all threads in the batch to complete
            for thread in threads:
                thread.join()

            logging.warning(f"Batch {i//batch_size + 1} completed")

        # Generate final report after all batches
        generate_final_report(successful_types, partial_types, failed_types, "ALL_CATEGORIES")

        logging.warning("All categories processed - final report generated")

    except Exception as e:
        logging.error(f"Error en main: {e}")
        raise

if __name__ == "__main__":
    main()