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
import json

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('carrefour_offers_analysis.log'),
        logging.StreamHandler()
    ]
)

class CarrefourOffersAnalyzer:
    def __init__(self):
        # Configuración de Selenium
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')

        self.driver = webdriver.Firefox(options=options)
        self.wait = WebDriverWait(self.driver, 10)

        # Resultados del análisis
        self.offers_analysis = {
            'summary': {},
            'offer_types': [],
            'categories_with_offers': [],
            'promotion_clusters': [],
            'price_structures': [],
            'special_offers': [],
            'recommendations': []
        }

    def analyze_main_page(self):
        """Analiza la página principal de Carrefour"""
        logging.info("Analizando página principal...")
        self.driver.get('https://www.carrefour.com.ar')

        try:
            # Buscar elementos de ofertas en la página principal
            offer_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'oferta') or contains(text(), 'Oferta') or contains(text(), 'OFERTA') or contains(@class, 'offer') or contains(@class, 'promo')]")

            # Buscar banners de promociones
            promo_banners = self.driver.find_elements(By.XPATH, "//div[contains(@class, 'banner') or contains(@class, 'promo') or contains(@class, 'offer')]")

            # Buscar secciones de ofertas
            offer_sections = self.driver.find_elements(By.XPATH, "//section[contains(@class, 'offer') or contains(@class, 'promo') or contains(@class, 'discount')]")

            self.offers_analysis['summary']['main_page_offers'] = {
                'offer_elements_count': len(offer_elements),
                'promo_banners_count': len(promo_banners),
                'offer_sections_count': len(offer_sections)
            }

            logging.info(f"Página principal: {len(offer_elements)} elementos de oferta, {len(promo_banners)} banners promocionales")

        except Exception as e:
            logging.error(f"Error analizando página principal: {e}")

    def analyze_offers_page(self):
        """Analiza páginas específicas de ofertas"""
        offers_urls = [
            'https://www.carrefour.com.ar/ofertas',
            'https://www.carrefour.com.ar/promociones',
            'https://www.carrefour.com.ar/descuentos'
        ]

        for url in offers_urls:
            try:
                logging.info(f"Analizando {url}")
                self.driver.get(url)
                time.sleep(3)  # Esperar carga

                # Extraer tipos de ofertas
                offer_types = self.extract_offer_types()
                self.offers_analysis['offer_types'].extend(offer_types)

                # Extraer clusters promocionales
                clusters = self.extract_promotion_clusters()
                self.offers_analysis['promotion_clusters'].extend(clusters)

            except Exception as e:
                logging.error(f"Error analizando {url}: {e}")

    def extract_offer_types(self):
        """Extrae tipos de ofertas de la página actual"""
        offer_types = []

        try:
            # Buscar elementos con información de ofertas
            offer_containers = self.driver.find_elements(By.XPATH, "//div[contains(@class, 'product') or contains(@class, 'item') or contains(@class, 'card')]")

            for container in offer_containers[:10]:  # Limitar a 10 para análisis
                try:
                    # Buscar texto de ofertas
                    offer_text = container.text

                    # Buscar patrones de ofertas
                    patterns = [
                        r'(\d+)%\s*off',
                        r'(\d+)\s*al\s*(\d+)',
                        r'(\d+)\s*x\s*(\d+)',
                        r'Hasta\s*(\d+)%',
                        r'(\d+)\s*unidades',
                        r'(\d+)\s*lleva\s*(\d+)',
                        r'(\d+)\s*paga\s*(\d+)'
                    ]

                    for pattern in patterns:
                        matches = re.findall(pattern, offer_text, re.IGNORECASE)
                        if matches:
                            offer_types.extend([f"Patrón: {pattern} - Texto: {match}" for match in matches])

                    # Buscar clusters específicos
                    if '2do al' in offer_text.lower():
                        offer_types.append("2do al X%")
                    if 'hasta' in offer_text.lower() and 'off' in offer_text.lower():
                        offer_types.append("Hasta X% off")
                    if 'promo' in offer_text.lower():
                        offer_types.append("PROMO especial")

                except Exception as e:
                    continue

        except Exception as e:
            logging.error(f"Error extrayendo tipos de oferta: {e}")

        return list(set(offer_types))  # Remover duplicados

    def extract_promotion_clusters(self):
        """Extrae clusters promocionales"""
        clusters = []

        try:
            # Buscar elementos con data-highlight o clusters
            cluster_elements = self.driver.find_elements(By.XPATH, "//div[contains(@data-highlight-name, '') or contains(@class, 'cluster') or contains(@class, 'highlight')]")

            for element in cluster_elements:
                try:
                    name = element.get_attribute('data-highlight-name') or element.text.strip()
                    if name and len(name) > 2:
                        clusters.append({
                            'name': name,
                            'type': self.classify_cluster_type(name)
                        })
                except Exception as e:
                    continue

        except Exception as e:
            logging.error(f"Error extrayendo clusters: {e}")

        return clusters

    def classify_cluster_type(self, cluster_name):
        """Clasifica el tipo de cluster promocional"""
        name_lower = cluster_name.lower()

        if '2do al 50' in name_lower:
            return '2do_al_50'
        elif '2do al 70' in name_lower:
            return '2do_al_70'
        elif 'hasta 35% off' in name_lower:
            return 'hasta_35_off'
        elif 'max 48' in name_lower or '48' in name_lower:
            return 'promo_max_48'
        elif 'mi crf' in name_lower:
            return 'mi_crf'
        else:
            return 'other'

    def analyze_categories(self):
        """Analiza diferentes categorías para encontrar ofertas"""
        categories = [
            'Almacen',
            'Bebidas',
            'Lacteos',
            'Carniceria',
            'Verduleria',
            'Panaderia',
            'Limpieza',
            'Perfumeria'
        ]

        for category in categories:
            try:
                url = f'https://www.carrefour.com.ar/{category}'
                logging.info(f"Analizando categoría: {category}")
                self.driver.get(url)
                time.sleep(3)

                # Contar productos con ofertas
                offer_products = self.driver.find_elements(By.XPATH, "//div[contains(@class, 'galleryItem') and (.//span[contains(@class, 'listPrice')] or .//div[contains(@data-highlight-name, '')])]")

                # Extraer tipos de precio
                price_structures = self.extract_price_structures()

                self.offers_analysis['categories_with_offers'].append({
                    'category': category,
                    'url': url,
                    'products_with_offers': len(offer_products),
                    'price_structures': price_structures
                })

            except Exception as e:
                logging.error(f"Error analizando categoría {category}: {e}")

    def extract_price_structures(self):
        """Extrae estructuras de precios encontradas"""
        structures = []

        try:
            # Buscar diferentes tipos de elementos de precio
            price_elements = self.driver.find_elements(By.XPATH, "//span[contains(@class, 'price') or contains(@class, 'Price')]")

            for element in price_elements[:20]:  # Limitar muestra
                try:
                    classes = element.get_attribute('class')
                    text = element.text.strip()
                    if text:
                        structures.append({
                            'classes': classes,
                            'text': text,
                            'type': self.classify_price_type(classes, text)
                        })
                except Exception as e:
                    continue

        except Exception as e:
            logging.error(f"Error extrayendo estructuras de precio: {e}")

        return structures

    def classify_price_type(self, classes, text):
        """Clasifica el tipo de elemento de precio"""
        if 'sellingPrice' in classes:
            return 'precio_venta'
        elif 'listPrice' in classes:
            return 'precio_lista'
        elif 'currencyContainer' in classes:
            return 'contenedor_moneda'
        elif 'currencyInteger' in classes:
            return 'parte_entera'
        elif 'currencyFraction' in classes:
            return 'parte_decimal'
        else:
            return 'otro'

    def analyze_special_offers(self):
        """Analiza ofertas especiales y promociones destacadas"""
        special_offers = []

        try:
            # Buscar elementos destacados
            special_elements = self.driver.find_elements(By.XPATH, "//div[contains(@class, 'highlight') or contains(@class, 'featured') or contains(@class, 'special')]")

            for element in special_elements:
                try:
                    text = element.text.strip()
                    if text and len(text) > 10:
                        special_offers.append({
                            'text': text,
                            'type': 'oferta_destacada'
                        })
                except Exception as e:
                    continue

            # Buscar popups o modales de ofertas
            try:
                modal_offers = self.driver.find_elements(By.XPATH, "//div[contains(@class, 'modal') or contains(@class, 'popup')]//div[contains(text(), 'oferta') or contains(text(), 'promo')]")
                for modal in modal_offers:
                    special_offers.append({
                        'text': modal.text.strip(),
                        'type': 'modal_oferta'
                    })
            except Exception as e:
                pass

        except Exception as e:
            logging.error(f"Error analizando ofertas especiales: {e}")

        self.offers_analysis['special_offers'] = special_offers

    def generate_recommendations(self):
        """Genera recomendaciones basadas en el análisis"""
        recommendations = []

        # Analizar tipos de ofertas encontrados
        offer_types = self.offers_analysis.get('offer_types', [])
        if offer_types:
            recommendations.append("**Tipos de Ofertas Identificados:**")
            for offer_type in list(set(offer_types))[:10]:  # Limitar a 10
                recommendations.append(f"- {offer_type}")

        # Analizar clusters promocionales
        clusters = self.offers_analysis.get('promotion_clusters', [])
        if clusters:
            recommendations.append("\n**Clusters Promocionales:**")
            unique_clusters = list(set([c['name'] for c in clusters]))
            for cluster in unique_clusters[:10]:
                recommendations.append(f"- {cluster}")

        # Recomendaciones técnicas
        recommendations.extend([
            "\n**Recomendaciones Técnicas:**",
            "- Implementar extracción de clusters promocionales usando data-highlight-name",
            "- Manejar múltiples estructuras de precio (sellingPrice, listPrice, currencyContainer)",
            "- Detectar ofertas por porcentaje, 2x1, y promociones especiales",
            "- Considerar ofertas por categoría y productos destacados",
            "- Implementar lógica para calcular descuentos efectivos"
        ])

        self.offers_analysis['recommendations'] = recommendations

    def run_analysis(self):
        """Ejecuta el análisis completo"""
        try:
            logging.info("Iniciando análisis exhaustivo de ofertas de Carrefour...")

            # Análisis de página principal
            self.analyze_main_page()

            # Análisis de páginas de ofertas
            self.analyze_offers_page()

            # Análisis por categorías
            self.analyze_categories()

            # Análisis de ofertas especiales
            self.analyze_special_offers()

            # Generar recomendaciones
            self.generate_recommendations()

            logging.info("Análisis completado")

        except Exception as e:
            logging.error(f"Error en análisis: {e}")
        finally:
            self.driver.quit()

    def save_results(self):
        """Guarda los resultados en un archivo Markdown"""
        filename = 'carrefour_offers_analysis.md'

        with open(filename, 'w', encoding='utf-8') as f:
            f.write("# Análisis Exhaustivo de Ofertas - Carrefour.com.ar\n\n")
            f.write(f"**Fecha de Análisis:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("**Análisis realizado por:** CarrefourOffersAnalyzer\n\n")

            # Resumen
            f.write("## 📊 Resumen Ejecutivo\n\n")
            summary = self.offers_analysis.get('summary', {})
            if summary:
                for key, value in summary.items():
                    f.write(f"- **{key}:** {value}\n")
            f.write("\n")

            # Tipos de ofertas
            f.write("## 🎯 Tipos de Ofertas Identificadas\n\n")
            offer_types = self.offers_analysis.get('offer_types', [])
            if offer_types:
                for i, offer_type in enumerate(list(set(offer_types)), 1):
                    f.write(f"{i}. {offer_type}\n")
            else:
                f.write("No se encontraron tipos específicos de ofertas.\n")
            f.write("\n")

            # Clusters promocionales
            f.write("## 🏷️ Clusters Promocionales\n\n")
            clusters = self.offers_analysis.get('promotion_clusters', [])
            if clusters:
                unique_clusters = list(set([c['name'] for c in clusters]))
                for i, cluster in enumerate(unique_clusters, 1):
                    cluster_type = next((c['type'] for c in clusters if c['name'] == cluster), 'unknown')
                    f.write(f"{i}. **{cluster}** (Tipo: {cluster_type})\n")
            else:
                f.write("No se encontraron clusters promocionales específicos.\n")
            f.write("\n")

            # Categorías con ofertas
            f.write("## 📂 Categorías con Ofertas\n\n")
            categories = self.offers_analysis.get('categories_with_offers', [])
            if categories:
                for category in categories:
                    f.write(f"### {category['category']}\n")
                    f.write(f"- **URL:** {category['url']}\n")
                    f.write(f"- **Productos con ofertas:** {category['products_with_offers']}\n")
                    if category.get('price_structures'):
                        f.write("- **Estructuras de precio encontradas:**\n")
                        for structure in category['price_structures'][:5]:  # Limitar
                            f.write(f"  - {structure['type']}: `{structure['text']}`\n")
                    f.write("\n")
            else:
                f.write("No se encontraron categorías con ofertas específicas.\n")
            f.write("\n")

            # Estructuras de precio
            f.write("## 💰 Estructuras de Precio\n\n")
            all_structures = []
            for category in categories:
                all_structures.extend(category.get('price_structures', []))

            if all_structures:
                unique_structures = list(set([s['type'] for s in all_structures]))
                for structure_type in unique_structures:
                    f.write(f"### {structure_type.replace('_', ' ').title()}\n")
                    examples = [s for s in all_structures if s['type'] == structure_type][:3]
                    for example in examples:
                        f.write(f"- `{example['text']}` (Clases: {example['classes']})\n")
                    f.write("\n")
            else:
                f.write("No se encontraron estructuras de precio específicas.\n")
            f.write("\n")

            # Ofertas especiales
            f.write("## ⭐ Ofertas Especiales\n\n")
            special_offers = self.offers_analysis.get('special_offers', [])
            if special_offers:
                for i, offer in enumerate(special_offers, 1):
                    f.write(f"{i}. **{offer['type']}:** {offer['text'][:100]}{'...' if len(offer['text']) > 100 else ''}\n")
            else:
                f.write("No se encontraron ofertas especiales destacadas.\n")
            f.write("\n")

            # Recomendaciones
            f.write("## 💡 Recomendaciones para Implementación\n\n")
            recommendations = self.offers_analysis.get('recommendations', [])
            if recommendations:
                for rec in recommendations:
                    f.write(f"{rec}\n")
            else:
                f.write("No hay recomendaciones específicas generadas.\n")
            f.write("\n")

            # Conclusión
            f.write("## 📋 Conclusión\n\n")
            f.write("Este análisis proporciona una base sólida para implementar la extracción de ofertas en el scraper de Carrefour. ")
            f.write("Los patrones identificados pueden ser utilizados para mejorar la detección y clasificación de promociones.\n\n")

            f.write("**Próximos pasos recomendados:**\n")
            f.write("1. Implementar la lógica de extracción basada en los patrones encontrados\n")
            f.write("2. Probar con diferentes categorías y períodos de tiempo\n")
            f.write("3. Validar la precisión de la detección de ofertas\n")
            f.write("4. Implementar actualizaciones automáticas para nuevos tipos de ofertas\n")

        logging.info(f"Resultados guardados en {filename}")

if __name__ == '__main__':
    analyzer = CarrefourOffersAnalyzer()
    analyzer.run_analysis()
    analyzer.save_results()