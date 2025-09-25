import logging
import re
import time
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from pymongo import MongoClient
from datetime import datetime

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('almacen_scraper.log'),
        logging.StreamHandler()
    ]
)

class AlmacenScraper:
    def __init__(self):
        # Configuración de MongoDB
        self.client = MongoClient('mongodb://localhost:27017/')
        self.db = self.client['carrefour']
        self.collection = self.db['products']

        # Cache de marcas para evitar consultas repetidas
        self.brands_cache = None

        # Cache de subcategorías y tipos de producto
        self.subcategories_cache = None
        self.producttypes_cache = None

        # Configuración de Selenium
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')

        self.driver = webdriver.Firefox(options=options)
        self.wait = WebDriverWait(self.driver, 10)

    def navigate_to_almacen(self):
        """Navega a la página de Almacén de Carrefour"""
        url = 'https://www.carrefour.com.ar/Almacen'
        logging.info(f"Navegando a {url}")
        self.driver.get(url)

        # Esperar a que cargue la página
        try:
            self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'valtech-carrefourar-search-result-3-x-galleryItem')))
            logging.info("Página de Almacén cargada correctamente")
        except TimeoutException:
            logging.error("Timeout al cargar la página de Almacén")
            return False

        # Hacer scroll para cargar todos los productos (lazy loading)
        logging.info("Cargando todos los productos con scroll...")
        self.load_all_products()

        return True

    def load_all_products(self):
        """Hace scroll para cargar todos los productos disponibles"""
        import time

        last_count = 0
        max_scrolls = 10  # Máximo número de scrolls para evitar loops infinitos

        for scroll_attempt in range(max_scrolls):
            # Contar productos actuales
            current_products = self.driver.find_elements(By.CLASS_NAME, 'valtech-carrefourar-search-result-3-x-galleryItem')
            current_count = len(current_products)

            logging.info(f"Scroll {scroll_attempt + 1}: {current_count} productos encontrados")

            # Si no hay cambio en el número de productos, probablemente ya se cargaron todos
            if current_count == last_count and scroll_attempt > 0:
                logging.info("No se cargaron más productos, terminando scroll")
                break

            # Hacer scroll hacia abajo
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            # Esperar a que se carguen nuevos productos
            time.sleep(2)

            last_count = current_count

        # Contar productos finales
        final_products = self.driver.find_elements(By.CLASS_NAME, 'valtech-carrefourar-search-result-3-x-galleryItem')
        logging.info(f"Total de productos cargados: {len(final_products)}")

    def extract_all_products(self):
        """Extrae todos los productos de todas las páginas de la categoría"""
        all_products = []
        page_number = 1

        while True:
            logging.info(f"Procesando página {page_number}...")

            # Extraer productos de la página actual
            products = self.extract_products_from_page()
            logging.info(f"Encontrados {len(products)} productos")

            if not products:
                break

            # Procesar cada producto
            for product_element in products:
                product_data = self.extract_product_data(product_element)
                if product_data:
                    all_products.append(product_data)

            logging.info(f"Página {page_number}: {len(products)} productos extraídos")

            # Intentar ir a la siguiente página
            if not self.go_to_next_page():
                logging.info("No hay más páginas.")
                break

            page_number += 1

        return all_products

    def extract_products_from_page(self):
        """Extrae los elementos de producto de la página actual"""
        try:
            return self.driver.find_elements(By.CLASS_NAME, 'valtech-carrefourar-search-result-3-x-galleryItem')
        except Exception as e:
            logging.error(f"Error extrayendo productos de la página: {e}")
            return []

    def go_to_next_page(self):
        """Intenta ir a la siguiente página. Retorna True si tuvo éxito, False si no hay más páginas"""
        try:
            # Buscar el contenedor de paginación
            pagination_container = self.driver.find_elements(By.CLASS_NAME, 'valtech-carrefourar-search-result-3-x-paginationContainer')

            if not pagination_container:
                logging.info("No se encontró contenedor de paginación")
                return False

            # Buscar el botón "Siguiente"
            next_button = self.driver.find_elements(By.CLASS_NAME, 'valtech-carrefourar-search-result-3-x-paginationButtonChangePageNext')

            if not next_button:
                logging.info("No se encontró botón 'Siguiente'")
                return False

            next_button = next_button[0]

            # Verificar si el botón está deshabilitado
            if next_button.get_attribute('disabled') is not None:
                logging.info("Botón 'Siguiente' está deshabilitado - fin de las páginas")
                return False

            # Hacer scroll hasta el botón para asegurarse de que sea visible
            logging.info("Haciendo scroll hasta el botón 'Siguiente'...")
            self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", next_button)

            # Esperar un momento para que el scroll termine
            time.sleep(1)

            # Hacer clic en el botón siguiente
            logging.info("Haciendo clic en botón 'Siguiente'...")
            next_button.click()

            # Esperar a que cargue la nueva página
            time.sleep(3)  # Espera más tiempo para que cargue la nueva página

            # Verificar que la página cambió esperando que aparezcan productos
            self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'valtech-carrefourar-search-result-3-x-galleryItem')))

            # Hacer scroll para cargar todos los productos de la nueva página
            self.load_all_products()

            return True

        except Exception as e:
            logging.error(f"Error al intentar ir a la siguiente página: {e}")
            return False

    def extract_product_data(self, element):
        """Extrae datos de un producto individual"""
        try:
            product_data = {
                'seller': 'Carrefour',
                'currency': 'ARS',
                'condition': 'new',
                'availability': 'instock',
                'scrapedAt': datetime.now(),
                'lastUpdated': datetime.now(),
                'sourceUrl': self.driver.current_url,
                'category': 'Almacén',
                'categoryPath': ['Almacén']
            }

            # Nombre del producto
            try:
                name_element = element.find_element(By.CLASS_NAME, 'vtex-product-summary-2-x-productBrand')
                product_data['name'] = name_element.text.strip()
            except NoSuchElementException:
                logging.warning("Nombre no encontrado")

            # URL del producto
            try:
                link_element = element.find_element(By.CLASS_NAME, 'vtex-product-summary-2-x-clearLink')
                product_url = link_element.get_attribute('href')
                product_data['productUrl'] = f"https://www.carrefour.com.ar{product_url}" if product_url.startswith('/') else product_url
                product_data['canonicalUrl'] = product_data['productUrl']
            except NoSuchElementException:
                logging.warning("URL del producto no encontrada")

            # SKU (extraer del href)
            if 'productUrl' in product_data:
                sku_match = re.search(r'-(\d+)/p$', product_data['productUrl'])
                if sku_match:
                    product_data['sku'] = sku_match.group(1)

            # Imagen
            try:
                img_element = element.find_element(By.CLASS_NAME, 'vtex-product-summary-2-x-image')
                img_url = img_element.get_attribute('src')
                alt_text = img_element.get_attribute('alt')
                product_data['images'] = [{
                    'url': img_url,
                    'alt': alt_text
                }]
                product_data['mainImage'] = img_url
            except NoSuchElementException:
                logging.warning("Imagen no encontrada")

            # Precios
            prices = self.extract_prices(element)
            if prices:
                product_data.update(prices)

            # Extraer marca, subcategoría y tipo de producto
            if 'name' in product_data:
                brand = self.extract_brand(product_data['name'])
                subcategory, producttype = self.extract_subcategory_and_type(product_data['name'])

                product_data['brand'] = brand
                product_data['subcategory'] = subcategory
                product_data['productType'] = producttype

            return product_data

        except Exception as e:
            logging.error(f"Error extrayendo datos del producto: {e}")
            return None

    def extract_prices(self, element):
        """Extrae información de precios del producto"""
        prices = {}

        try:
            # Buscar contenedor de precios
            price_container = element.find_element(By.CLASS_NAME, 'valtech-carrefourar-product-price-0-x-priceContainer')

            # Precio de venta (siempre presente)
            try:
                selling_price_element = price_container.find_element(By.CLASS_NAME, 'valtech-carrefourar-product-price-0-x-sellingPrice')
                selling_price_text = self.extract_price_from_currency_container(selling_price_element)
                if selling_price_text:
                    prices['price'] = self.parse_argentine_price(selling_price_text)
                    prices['sellingPrice'] = prices['price']
            except NoSuchElementException:
                logging.warning("Precio de venta no encontrado")

            # Precio tachado (precio anterior, si existe)
            try:
                list_price_element = price_container.find_element(By.CLASS_NAME, 'valtech-carrefourar-product-price-0-x-listPrice')
                list_price_text = self.extract_price_from_currency_container(list_price_element)
                if list_price_text:
                    prices['listPrice'] = self.parse_argentine_price(list_price_text)
            except NoSuchElementException:
                logging.debug("Precio de lista no encontrado, usando precio de venta como listPrice")
                selling_price_element = element.find_element(By.CLASS_NAME, 'valtech-carrefourar-product-price-0-x-sellingPriceValue')
                selling_price_text = self.extract_price_from_currency_container(selling_price_element)
                if selling_price_text:
                    prices['listPrice'] = self.parse_argentine_price(selling_price_text)
                    logging.debug(f"Usando precio de venta como listPrice: {prices['listPrice']}")

        except Exception as e:
            logging.error(f"Error extrayendo precios: {e}")

        return prices

    def extract_price_from_currency_container(self, container_element):
        """Extrae precio de un contenedor de moneda"""
        try:
            spans = container_element.find_elements(By.XPATH, './/span[contains(@class, "valtech-carrefourar-product-price-0-x-")]')
            price_parts = []

            for span in spans:
                classes = span.get_attribute('class')
                text = span.text.strip()

                if 'currencyCode' in classes:
                    price_parts.append(text)
                elif 'currencyInteger' in classes:
                    price_parts.append(text)
                elif 'currencyGroup' in classes:
                    price_parts.append(text)
                elif 'currencyDecimal' in classes:
                    price_parts.append(text)
                elif 'currencyFraction' in classes:
                    price_parts.append(text)

            return ''.join(price_parts)
        except Exception as e:
            logging.error(f"Error extrayendo precio del contenedor: {e}")
            return None

    def extract_brand(self, product_name):
        """Extrae la marca del nombre del producto buscando en la colección filters"""
        # Cargar marcas de la base de datos si no están en cache
        if self.brands_cache is None:
            try:
                # Obtener todas las marcas de la colección filters
                brands_docs = self.db['filters'].find({'type': 'brand'}, {'name': 1})
                self.brands_cache = [doc['name'] for doc in brands_docs]
                logging.info(f"Cargadas {len(self.brands_cache)} marcas desde la base de datos")
            except Exception as e:
                logging.error(f"Error cargando marcas desde la base de datos: {e}")
                self.brands_cache = []

        # Buscar coincidencia exacta primero
        product_name_lower = product_name.lower()
        for brand in self.brands_cache:
            if brand.lower() == product_name_lower:
                return brand

        # Buscar marca contenida en el nombre del producto
        for brand in self.brands_cache:
            if brand.lower() in product_name_lower:
                return brand

        # Si no encuentra marca conocida, intentar extraer de las primeras palabras
        words = product_name.split()
        if words:
            # Probar con las primeras 2-3 palabras para encontrar marcas compuestas
            for i in range(min(3, len(words))):
                candidate = ' '.join(words[:i+1])
                for brand in self.brands_cache:
                    if brand.lower() == candidate.lower():
                        return brand

        # Fallback: devolver 'Carrefour' para productos de marca propia
        return 'Carrefour'

    def extract_subcategory_and_type(self, product_name, category="Almacén"):
        """Extrae subcategoría y tipo de producto usando jerarquía de BD con lógica mejorada"""
        name_lower = product_name.lower()
        category_lower = category.lower()

        # Cargar caches si no existen
        if not self.subcategories_cache:
            try:
                subcategories = list(self.db.subcategories.find({}, {'name': 1, 'category_name': 1}))
                # Crear cache con clave por categoría para acceso rápido
                self.subcategories_cache = {}
                for sub in subcategories:
                    cat_name = sub.get('category_name', '').lower()
                    if cat_name not in self.subcategories_cache:
                        self.subcategories_cache[cat_name] = []
                    self.subcategories_cache[cat_name].append(sub)
                logging.info(f"Cargadas subcategorías para {len(self.subcategories_cache)} categorías")
            except Exception as e:
                logging.error(f"Error cargando subcategorías: {e}")
                return 'Complementos', 'Polvo para hornear'

        if not self.producttypes_cache:
            try:
                producttypes = list(self.db.producttypes.find({}, {'name': 1, 'category': 1, 'subcategory': 1}))
                # Crear cache organizado por subcategory
                self.producttypes_cache = {}
                for pt in producttypes:
                    sub_name = pt.get('subcategory', '').lower()
                    if sub_name not in self.producttypes_cache:
                        self.producttypes_cache[sub_name] = []
                    self.producttypes_cache[sub_name].append(pt)
                logging.info(f"Cargados tipos de producto para {len(self.producttypes_cache)} subcategorías")
            except Exception as e:
                logging.error(f"Error cargando tipos de producto: {e}")
                return 'Complementos', 'Polvo para hornear'

        # 1. Filtrar subcategorías que pertenecen a la categoría del producto
        category_subcategories = self.subcategories_cache.get(category_lower, [])
        if not category_subcategories:
            logging.warning(f"No se encontraron subcategorías para categoría '{category}'")
            return 'Complementos', 'Polvo para hornear'

        # Función para verificar si una palabra está completa en el nombre
        def word_in_name(word, text):
            pattern = r'\b' + re.escape(word) + r'\b'
            return bool(re.search(pattern, text, re.IGNORECASE))

        # Función para calcular score basado en múltiples factores
        def calculate_score(product_name, subcategory_name, producttype_name=None):
            score = 0
            prod_lower = product_name.lower()
            sub_lower = subcategory_name.lower()
            type_lower = producttype_name.lower() if producttype_name else ""

            # Score por matching exacto de subcategoría
            if word_in_name(subcategory_name, product_name):
                score += 100

            # Score por tipo de producto específico
            if producttype_name and word_in_name(producttype_name, product_name):
                score += 50

            # Score por palabras clave específicas de cada subcategoría
            subcategory_patterns = {
                'aceites comunes': ['aceite', 'girasol', 'maíz', 'mezcla'],
                'aceites de oliva': ['aceite', 'oliva', 'extra virgen'],
                'aceites en aerosol': ['aceite', 'aerosol', 'spray'],
                'aceites especiales': ['aceite', 'canola', 'coco', 'sésamo'],
                'aceitunas y encurtidos': ['aceituna', 'encurtido', 'pepino', 'jalapeño', 'choclo', 'espárrago', 'hoja de parra'],
                'arroz': ['arroz', 'carnaroli', 'yamaní', 'parboil', 'integral', 'sushi'],
                'avena': ['avena', 'copos', 'instantánea'],
                'caldos': ['caldo', 'saborizador', 'deshidratado', 'cubo'],
                'coberturas, rellenos y salsas': ['baño', 'repostería', 'grana', 'leche condensada', 'salsa', 'caramelo', 'chocolate', 'frutilla'],
                'conservas de frutas': ['ananá', 'cereza', 'durazno', 'pera', 'coctel', 'tomate'],
                'conservas de legumbres y vegetales': ['arveja', 'garbanzo', 'lenteja', 'poroto', 'choclo', 'chaucha', 'palmito', 'remolacha', 'zanahoria', 'champignon', 'jardinera', 'mix vegetal'],
                'conservas y salsas de tomate': ['tomate', 'puré', 'pulpa', 'extracto', 'salsa', 'pomarola', 'pomodoro', 'filetto', 'portuguesa', 'tuco', 'pizza', 'guiso'],
                'conservas de pescado': ['atún', 'caballa', 'jurel', 'bacalao', 'sardina', 'almeja', 'mejillón', 'calamar', 'camarón', 'berberecho'],
                'fideos guiseros y para sopas': ['fideo', 'codito', 'moño', 'mostachol', 'rigatoni', 'penne', 'fusilli', 'tallarín', 'spaghetti', 'celentano', 'letrita', 'munición', 'nido', 'pamperito', 'tirabuzón'],
                'fideos largos': ['fideo', 'spaghetti', 'tallarín', 'fettuccini', 'linguine', 'tagliatelle', 'cinta', 'foratini'],
                'gelatinas en polvo': ['gelatina', 'premezcla'],
                'harinas comunes y leudantes': ['harina', 'trigo', 'integral', 'leudante', 'pizza'],
                'hierbas secas y especias': ['ajo', 'cebolla', 'perejil', 'albahaca', 'orégano', 'tomillo', 'laurel', 'pimienta', 'comino', 'canela', 'curry', 'paprika', 'azafrán', 'cúrcuma', 'chimichurri', 'provenzal', 'mostaza', 'nuez moscada'],
                'legumbres': ['arveja', 'garbanzo', 'lenteja', 'poroto', 'quinoa', 'maíz', 'trigo', 'burgol', 'candeal', 'provenzal'],
                'nachos, maní y palitos': ['nachos', 'maní', 'palito', 'snack', 'japonés'],
                'otras harinas': ['almidón', 'fécula', 'mandioca', 'papa', 'arroz', 'avena', 'coco', 'quinoa', 'garbanzo', 'algodón', 'sémola', 'semolín'],
                'otros snacks salados': ['snack', 'salado', 'chip', 'palito'],
                'papas fritas y snacks de maíz': ['papa', 'frita', 'pay', 'maicito', 'batata', 'snack', 'maíz'],
                'pastas secas rellenas y listas': ['ravioles', 'capelletis', 'ñoquis', 'lasagna', 'lucchetinis'],
                'picadillos y paté': ['paté', 'pate', 'picadillo', 'jamón del diablo'],
                'polentas': ['polenta', 'instantánea'],
                'postres y flanes en polvo': ['flan', 'postre', 'vainilla', 'chocolate', 'caramelo'],
                'premezclas de bizcochuelos': ['bizcochuelo', 'brownie', 'premezcla', 'budín', 'torta'],
                'premezclas saladas': ['premezcla', 'chipá', 'croqueta', 'ñoqui', 'pan', 'pizza', 'torta frita', 'pasta'],
                'purés instantáneos': ['puré', 'instantáneo', 'papa'],
                'saborizadores': ['saborizador', 'condimento', 'arroz', 'carne', 'pescado', 'pizza', 'taco', 'empanada', 'resaltador'],
                'sal': ['sal', 'fina', 'gruesa', 'marina', 'parrillera', 'entrefina', 'saborizada'],
                'salsas y aderezos': ['salsa', 'aderezo', 'kétchup', 'ketchup', 'mayonesa', 'mostaza', 'barbacoa', 'chimichurri', 'alioli', 'caesar', 'ranch', 'teriyaki', 'soja', 'inglesa', 'golf', 'criolla', 'pesto', 'napolitana', 'portuguesa', 'provincial', 'rosa', 'blanca', 'bolognesa', 'burger', 'cheddar', '4 quesos', 'agridulce', 'big tau', 'coleslaw', 'guacamole', 'habanero', 'honey', 'jalapeño', 'picante', 'sriracha', 'taquera'],
                'semillas': ['semilla', 'chía', 'lino', 'sésamo', 'girasol', 'amapola'],
                'sopas': ['sopa', 'instantánea', 'deshidratada'],
                'tapas de alfajores y merengues': ['merengue', 'tapa', 'alfajor'],
                'vinagres, acetos y limón': ['vinagre', 'aceto', 'balsámico', 'limón', 'jugo', 'concentrado']
            }

            # Buscar patrones para la subcategoría
            if sub_lower in subcategory_patterns:
                patterns = subcategory_patterns[sub_lower]
                for pattern in patterns:
                    if pattern in prod_lower:
                        score += 20  # Score por cada patrón encontrado

            # Score adicional por tipo de producto específico
            if producttype_name:
                type_patterns = {
                    'aceite de girasol': ['girasol'],
                    'aceite de maíz': ['maíz'],
                    'aceite de oliva': ['oliva'],
                    'aceite de canola': ['canola'],
                    'aceite de coco': ['coco'],
                    'atún al natural': ['natural'],
                    'atún en aceite': ['aceite'],
                    'puré de tomate': ['puré', 'tomate'],
                    'salsa de tomate': ['salsa', 'tomate'],
                    'fideos spaghetti': ['spaghetti'],
                    'fideos tallarines': ['tallarín'],
                    'harina de trigo': ['trigo'],
                    'harina integral': ['integral'],
                    'mayonesa': ['mayonesa'],
                    'kétchup': ['kétchup', 'ketchup'],
                    'mostaza': ['mostaza'],
                    'vinagre de alcohol': ['alcohol'],
                    'vinagre de vino': ['vino'],
                    'polenta': ['polenta'],
                    'gelatina': ['gelatina'],
                    'paté': ['paté', 'pate']
                }

                if type_lower in type_patterns:
                    patterns = type_patterns[type_lower]
                    for pattern in patterns:
                        if pattern in prod_lower:
                            score += 30

            # Penalización por subcategorías menos específicas
            if sub_lower in ['complementos', 'otros snacks salados']:
                score -= 10

            return score

        # 2. Buscar la mejor coincidencia de subcategoría
        best_subcategory = None
        best_score = 0

        for sub in category_subcategories:
            sub_name = sub['name']
            score = calculate_score(product_name, sub_name)
            if score > best_score:
                best_score = score
                best_subcategory = sub

        if not best_subcategory:
            logging.warning(f"No se encontró subcategoría para producto '{product_name}' en categoría '{category}'")
            return 'Complementos', 'Polvo para hornear'

        selected_subcategory = best_subcategory['name']

        # 3. Buscar el mejor productType para la subcategoría seleccionada
        subcategory_producttypes = self.producttypes_cache.get(selected_subcategory.lower(), [])
        if not subcategory_producttypes:
            logging.warning(f"No se encontraron tipos de producto para subcategoría '{selected_subcategory}'")
            return selected_subcategory, 'Polvo para hornear'

        best_producttype = None
        best_score = 0

        for pt in subcategory_producttypes:
            pt_name = pt['name']
            score = calculate_score(product_name, selected_subcategory, pt_name)
            if score > best_score:
                best_score = score
                best_producttype = pt

        if best_producttype:
            return selected_subcategory, best_producttype['name']
        else:
            # Fallback: devolver el primer productType de la subcategoría
            return selected_subcategory, subcategory_producttypes[0]['name']

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

    def save_to_database(self, products):
        """Guarda productos en MongoDB"""
        saved_count = 0
        for product in products:
            try:
                # Verificar si el producto ya existe por SKU
                if 'sku' in product:
                    existing = self.collection.find_one({'sku': product['sku']})
                    if existing:
                        # Actualizar producto existente
                        self.collection.update_one(
                            {'sku': product['sku']},
                            {'$set': product}
                        )
                        logging.info(f"Producto actualizado: {product['sku']}")
                    else:
                        # Insertar nuevo producto
                        self.collection.insert_one(product)
                        logging.info(f"Producto insertado: {product['sku']}")
                else:
                    # Insertar sin SKU (usar nombre como identificador único aproximado)
                    existing = self.collection.find_one({'name': product['name']})
                    if not existing:
                        self.collection.insert_one(product)
                        logging.info(f"Producto insertado (sin SKU): {product['name']}")

                saved_count += 1

            except Exception as e:
                logging.error(f"Error guardando producto: {e}")

        logging.info(f"Total productos procesados: {saved_count}")

    def run(self):
        """Ejecuta el scraper completo"""
        try:
            if not self.navigate_to_almacen():
                return

            products = self.extract_all_products()
            logging.info(f"Extraídos {len(products)} productos en total")

            if products:
                self.save_to_database(products)

        except Exception as e:
            logging.error(f"Error en ejecución del scraper: {e}")
        finally:
            self.driver.quit()

if __name__ == '__main__':
    scraper = AlmacenScraper()
    scraper.run()