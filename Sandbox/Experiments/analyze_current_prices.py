#!/usr/bin/env python3
"""
Analizar precios actuales en la página de Carrefour Almacén
para entender qué precios están disponibles
"""

import logging
import re
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

class PriceAnalyzer:
    def __init__(self):
        # Configuración de Selenium
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')

        self.driver = webdriver.Firefox(options=options)
        self.wait = WebDriverWait(self.driver, 10)

    def analyze_prices(self):
        """Analiza los precios disponibles en la página"""
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

        # Analizar primeros 5 productos
        product_elements = self.driver.find_elements(By.CLASS_NAME, 'valtech-carrefourar-search-result-3-x-galleryItem')[:5]

        for i, element in enumerate(product_elements):
            print(f"\n=== PRODUCTO {i+1} ===")

            # Nombre del producto
            try:
                name_element = element.find_element(By.CLASS_NAME, 'vtex-product-summary-2-x-productBrand')
                name = name_element.text.strip()
                print(f"Nombre: {name}")
            except:
                print("Nombre: No encontrado")

            # Analizar todos los elementos de precio
            self.analyze_price_elements(element)

    def analyze_price_elements(self, element):
        """Analiza todos los elementos de precio en un producto"""
        print("Elementos de precio encontrados:")

        # Buscar todos los elementos que podrían contener precios
        price_selectors = [
            '.valtech-carrefourar-product-price-0-x-listPriceValue',
            '.valtech-carrefourar-product-price-0-x-sellingPriceValue',
            '.valtech-carrefourar-product-price-0-x-price',
            '.valtech-carrefourar-product-price-0-x-currencyContainer',
            '[class*="price"]',
            '[class*="Price"]'
        ]

        found_prices = {}

        for selector in price_selectors:
            try:
                elements = element.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    for j, el in enumerate(elements):
                        text = el.text.strip()
                        if text and '$' in text:
                            key = f"{selector}_{j}"
                            found_prices[key] = text
                            print(f"  {key}: {text}")
            except Exception as e:
                pass

        # También buscar spans dentro de contenedores de precio
        try:
            currency_containers = element.find_elements(By.CLASS_NAME, 'valtech-carrefourar-product-price-0-x-currencyContainer')
            for i, container in enumerate(currency_containers):
                spans = container.find_elements(By.TAG_NAME, 'span')
                span_texts = []
                for span in spans:
                    span_texts.append(span.text.strip())
                combined = ''.join(span_texts)
                if combined and '$' in combined:
                    print(f"  currency_container_{i}: {combined}")
        except:
            pass

        # Buscar cualquier texto que contenga $ en el elemento producto
        try:
            all_text = element.text
            dollar_matches = re.findall(r'\$[0-9.,]+', all_text)
            if dollar_matches:
                print(f"  Todos los precios encontrados en texto: {dollar_matches}")
        except:
            pass

        if not found_prices:
            print("  No se encontraron elementos de precio específicos")

def main():
    analyzer = PriceAnalyzer()
    analyzer.analyze_prices()
    analyzer.driver.quit()

if __name__ == "__main__":
    main()