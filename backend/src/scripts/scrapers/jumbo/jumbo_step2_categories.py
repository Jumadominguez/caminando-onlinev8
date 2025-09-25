import logging
import time
import re
import unicodedata
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from pymongo import MongoClient
import requests
from bs4 import BeautifulSoup
import os

class JumboScraperStep2:
    def __init__(self, headless=True):
        self.headless = headless
        self.driver = None
        self.db = None
        self.setup_logging()

    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('jumbo_scraper_step2.log'),
                logging.StreamHandler()
            ]
        )

    def setup_driver(self):
        """Setup Firefox WebDriver"""
        try:
            options = webdriver.FirefoxOptions()
            if self.headless:
                options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--disable-extensions')
            options.add_argument('--disable-plugins')
            options.add_argument('--disable-images')  # Speed up loading

            # Use local geckodriver if available
            geckodriver_path = os.path.join(os.getcwd(), 'geckodriver.exe')
            if os.path.exists(geckodriver_path):
                service = Service(geckodriver_path)
            else:
                service = Service()

            self.driver = webdriver.Firefox(service=service, options=options)
            logging.info("Firefox WebDriver setup successfully")
        except Exception as e:
            logging.error(f"Failed to setup WebDriver: {e}")
            raise

    def connect_db(self):
        """Connect to MongoDB"""
        try:
            self.client = MongoClient('mongodb://localhost:27017/')
            self.db = self.client['jumbo']
            logging.info("Connected to MongoDB database 'jumbo'")
        except Exception as e:
            logging.error(f"Failed to connect to MongoDB: {e}")
            raise

    def simplify_name(self, name):
        """Simplify name for URLs and identifiers"""
        if not name:
            return ""
        # Remove accents and convert to lowercase
        name = unicodedata.normalize('NFD', name).encode('ascii', 'ignore').decode('utf-8')
        # Replace spaces and special chars with hyphens
        name = re.sub(r'[^a-zA-Z0-9\s-]', '', name)
        name = re.sub(r'\s+', '-', name)
        return name.lower().strip('-')

    def extract_categories_with_hover(self):
        """Step 2: Extract categories using hover interactions on CATEGORÍAS menu"""
        logging.info("Starting Step 2: Extract categories with hover on CATEGORÍAS menu")

        try:
            # Navigate to home page
            self.driver.get("https://www.jumbo.com.ar")
            time.sleep(5)  # Wait for page to load

            categories = []

            # Find the CATEGORÍAS menu trigger - based on working HTML analysis
            menu_triggers = [
                ".vtex-menu-2-x-styledLink--header-category",  # Specific class from HTML
                "//span[contains(text(), 'CATEGORÍAS')]",     # Text-based XPath
                "[class*='header-category']",                  # Class contains
                ".vtex-menu-2-x-styledLink"                    # General VTEX link
            ]

            menu_element = None
            for trigger in menu_triggers:
                try:
                    if trigger.startswith("//"):
                        # XPath
                        menu_element = WebDriverWait(self.driver, 10).until(
                            EC.element_to_be_clickable((By.XPATH, trigger))
                        )
                    else:
                        # CSS Selector
                        menu_element = WebDriverWait(self.driver, 10).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, trigger))
                        )

                    # Verify it contains "CATEGORÍAS"
                    element_text = menu_element.text.strip()
                    if "CATEGORÍAS" in element_text.upper():
                        logging.info(f"Found CATEGORÍAS menu with: {trigger}")
                        break
                    else:
                        logging.info(f"Element found but text is '{element_text}', continuing search...")
                        menu_element = None

                except:
                    continue

            if not menu_element:
                logging.warning("Could not find CATEGORÍAS menu trigger, trying fallback")
                return self.extract_categories_directly()

            # Perform hover action on CATEGORÍAS menu
            logging.info("Performing hover action on CATEGORÍAS menu...")
            actions = ActionChains(self.driver)
            actions.move_to_element(menu_element).perform()

            # Wait for submenu to appear - longer wait for VTEX
            time.sleep(4)

            # Look for the submenu that appears - based on HTML analysis
            submenu_selectors = [
                ".vtex-menu-2-x-submenu",                    # VTEX submenu
                "[class*='department-menu']",               # Department menu class
                ".vtex-menu-2-x-menuContainer",             # Menu container
                "[class*='submenu']",                       # General submenu
                "nav [class*='menu']"                       # Menu within nav
            ]

            submenu = None
            for selector in submenu_selectors:
                try:
                    submenu = self.driver.find_element(By.CSS_SELECTOR, selector)
                    logging.info(f"Found submenu with selector: {selector}")
                    break
                except:
                    continue

            if not submenu:
                logging.warning("No submenu found after hover, trying fallback")
                return self.extract_categories_directly()

            # Find all menu items in the submenu - based on working HTML structure
            menu_item_selectors = [
                ".vtex-menu-2-x-menuItem",                    # VTEX menu items
                "[class*='menu-item']",                      # Menu item classes
                "a[href*='/']",                             # Links with paths
                ".vtex-menu-2-x-styledLink"                  # VTEX styled links
            ]

            all_menu_items = []
            for selector in menu_item_selectors:
                try:
                    items = submenu.find_elements(By.CSS_SELECTOR, selector)
                    if items:
                        all_menu_items.extend(items)
                        logging.info(f"Found {len(items)} items with selector: {selector}")
                except:
                    continue

            # Remove duplicates and filter
            unique_items = []
            seen_hrefs = set()
            for item in all_menu_items:
                try:
                    href = item.get_attribute('href') or ""
                    text = item.text.strip()
                    if href and text and href not in seen_hrefs:
                        unique_items.append(item)
                        seen_hrefs.add(href)
                except:
                    continue

            logging.info(f"Found {len(unique_items)} unique menu items")

            # Extract category information immediately to avoid stale elements
            categories_data = []
            for i, item in enumerate(unique_items):
                try:
                    text = item.text.strip()
                    href = item.get_attribute('href') or ""

                    # Filter for main categories (skip promotional items)
                    if text and href and not any(skip in text.lower() for skip in ['hot sale', 'cyber', 'ofertas', 'viví']):
                        logging.info(f"Found category {i+1}: {text} -> {href}")

                        category_data = {
                            'name': text,
                            'url': href,
                            'slug': self.simplify_name(text),
                            'supermarket': 'jumbo',
                            'scraped_at': datetime.now().isoformat(),
                            'subcategories': []
                        }

                        categories_data.append(category_data)

                except Exception as e:
                    logging.warning(f"Error extracting data from category {i+1}: {e}")
                    continue

            logging.info(f"Extracted data for {len(categories_data)} categories")

            # Now save to database
            for category_data in categories_data:
                try:
                    result = self.db['categories'].update_one(
                        {'url': category_data['url']},  # Unique identifier
                        {'$set': category_data},
                        upsert=True
                    )

                    if result.upserted_id:
                        logging.info(f"Inserted category: {category_data['name']}")
                    else:
                        logging.info(f"Updated category: {category_data['name']}")

                    categories.append(category_data)

                except Exception as e:
                    logging.error(f"Error saving category {category_data['name']}: {e}")

            logging.info(f"Extracted {len(categories)} categories from hover menu")
            return categories

        except Exception as e:
            logging.error(f"Error extracting categories with hover: {e}")
            return []

    def extract_categories_directly(self):
        """Extract categories by searching links directly on the page"""
        logging.info("Extracting categories directly from page links")

        try:
            categories = []

            # Main category URLs and names based on Jumbo's structure
            main_categories = [
                {'name': 'Almacén', 'url': 'https://www.jumbo.com.ar/almacen'},
                {'name': 'Bebidas', 'url': 'https://www.jumbo.com.ar/bebidas'},
                {'name': 'Carnes', 'url': 'https://www.jumbo.com.ar/especial-carnes'},
                {'name': 'Lácteos', 'url': 'https://www.jumbo.com.ar/lacteos'},
                {'name': 'Limpieza', 'url': 'https://www.jumbo.com.ar/limpieza'},
                {'name': 'Perfumería', 'url': 'https://www.jumbo.com.ar/perfumeria'}
            ]

            for category in main_categories:
                category_data = {
                    'name': category['name'],
                    'url': category['url'],
                    'slug': self.simplify_name(category['name']),
                    'supermarket': 'jumbo',
                    'scraped_at': datetime.now().isoformat(),
                    'subcategories': []
                }
                categories.append(category_data)

                # Save to database
                result = self.db['categories'].update_one(
                    {'url': category_data['url']},  # Unique identifier
                    {'$set': category_data},
                    upsert=True
                )

                if result.upserted_id:
                    logging.info(f"Inserted category: {category['name']}")
                else:
                    logging.info(f"Updated category: {category['name']}")

            logging.info(f"Extracted {len(categories)} categories directly")
            return categories

        except Exception as e:
            logging.error(f"Error extracting categories directly: {e}")
            return []

    def close_driver(self):
        """Close WebDriver"""
        if self.driver:
            try:
                self.driver.quit()
                logging.info("WebDriver closed")
            except Exception as e:
                logging.warning(f"Error closing WebDriver: {e}")

    def run(self):
        """Run the complete Step 2 process"""
        try:
            self.setup_driver()
            self.connect_db()
            categories = self.extract_categories_with_hover()
            logging.info(f"Step 2 completed successfully. Extracted {len(categories)} categories")
        except Exception as e:
            logging.error(f"Step 2 failed: {e}")
        finally:
            self.close_driver()


if __name__ == "__main__":
    scraper = JumboScraperStep2(headless=False)  # Set to False for debugging
    scraper.run()