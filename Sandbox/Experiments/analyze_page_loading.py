#!/usr/bin/env python3
"""
Analizar cómo se cargan los productos en la página de Carrefour
para entender por qué solo se ven 8 en lugar de 16
"""

import logging
import time
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class PageAnalyzer:
    def __init__(self):
        # Configuración de Selenium
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')

        self.driver = webdriver.Firefox(options=options)
        self.wait = WebDriverWait(self.driver, 10)

    def analyze_page_loading(self):
        """Analiza cómo se cargan los productos"""
        url = 'https://www.carrefour.com.ar/Almacen'
        logging.info(f"Navegando a {url}")
        self.driver.get(url)

        # Esperar a que cargue la página
        try:
            self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'valtech-carrefourar-search-result-3-x-galleryItem')))
            logging.info("Página cargada correctamente")
        except TimeoutException:
            logging.error("Timeout al cargar la página")
            return

        # Contar productos inicialmente
        initial_products = self.driver.find_elements(By.CLASS_NAME, 'valtech-carrefourar-search-result-3-x-galleryItem')
        logging.info(f"Productos iniciales: {len(initial_products)}")

        # Hacer scroll hacia abajo para cargar más productos
        logging.info("Haciendo scroll para cargar más productos...")

        # Scroll gradual
        for i in range(5):
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)

            current_products = self.driver.find_elements(By.CLASS_NAME, 'valtech-carrefourar-search-result-3-x-galleryItem')
            logging.info(f"Después de scroll {i+1}: {len(current_products)} productos")

            if len(current_products) >= 16:
                break

        # Verificar si hay botón "ver más" o paginación
        try:
            load_more_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Ver más')]")
            logging.info("Encontrado botón 'Ver más'")
            load_more_button.click()
            time.sleep(3)

            final_products = self.driver.find_elements(By.CLASS_NAME, 'valtech-carrefourar-search-result-3-x-galleryItem')
            logging.info(f"Después de 'Ver más': {len(final_products)} productos")
        except NoSuchElementException:
            logging.info("No se encontró botón 'Ver más'")

        # Análisis final
        final_count = len(self.driver.find_elements(By.CLASS_NAME, 'valtech-carrefourar-search-result-3-x-galleryItem'))
        logging.info(f"Total final de productos encontrados: {final_count}")

        # Verificar si hay paginación
        try:
            pagination = self.driver.find_elements(By.CLASS_NAME, 'pagination')
            if pagination:
                logging.info("Se encontró paginación en la página")
        except:
            pass

        # Verificar si hay lazy loading
        try:
            # Buscar elementos que podrían indicar lazy loading
            lazy_elements = self.driver.find_elements(By.XPATH, "//*[contains(@class, 'lazy') or contains(@class, 'loading')]")
            if lazy_elements:
                logging.info(f"Encontrados {len(lazy_elements)} elementos que podrían indicar lazy loading")
        except:
            pass

    def check_product_visibility(self):
        """Verificar si todos los productos son visibles"""
        products = self.driver.find_elements(By.CLASS_NAME, 'valtech-carrefourar-search-result-3-x-galleryItem')

        visible_count = 0
        hidden_count = 0

        for i, product in enumerate(products):
            is_visible = self.driver.execute_script("""
                var elem = arguments[0];
                var style = window.getComputedStyle(elem);
                return style.display !== 'none' && style.visibility !== 'hidden' && style.opacity !== '0';
            """, product)

            if is_visible:
                visible_count += 1
            else:
                hidden_count += 1

        logging.info(f"Productos visibles: {visible_count}")
        logging.info(f"Productos ocultos: {hidden_count}")

def main():
    analyzer = PageAnalyzer()
    analyzer.analyze_page_loading()
    analyzer.check_product_visibility()
    analyzer.driver.quit()

if __name__ == "__main__":
    main()