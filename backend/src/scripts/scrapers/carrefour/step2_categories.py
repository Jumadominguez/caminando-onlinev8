import logging
import time
import re
import unicodedata
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from pymongo import MongoClient
import requests
from bs4 import BeautifulSoup
import os

class CarrefourScraperStep2:
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
                logging.FileHandler('scraper_step2.log'),
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
            self.db = self.client['carrefour']
            logging.info("Connected to MongoDB database 'carrefour'")
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

    def extract_categories(self):
        """Step 2: Extract categories from dropdown menu"""
        logging.info("Starting Step 2: Extract categories")

        try:
            # Navigate to home page
            self.driver.get("https://www.carrefour.com.ar")
            time.sleep(3)  # Wait for page to load

            # Find and click the categories button
            categories_button = self.driver.find_element(By.CSS_SELECTOR, 'button[data-id="mega-menu-trigger-button"]')
            categories_button.click()
            time.sleep(2)  # Wait for menu to open

            # Find the menu container
            menu_container = self.driver.find_element(By.CSS_SELECTOR, 'ul.carrefourar-mega-menu-0-x-menuContainer')
            time.sleep(1)

            # Find all category items - corrected selectors based on actual HTML structure
            category_items = menu_container.find_elements(By.CSS_SELECTOR, 'li.carrefourar-mega-menu-0-x-menuItem a.carrefourar-mega-menu-0-x-styledLink')

            categories = []
            for item in category_items:
                try:
                    # Get category name from the link text
                    category_name = item.text.strip()

                    # Get category URL from href attribute
                    category_url = item.get_attribute('href')

                    if category_name and category_url:
                        category_data = {
                            'name': category_name,
                            'name_simple': self.simplify_name(category_name),
                            'url': category_url,
                            'scraped_at': datetime.now().isoformat()
                        }
                        categories.append(category_data)
                    else:
                        logging.warning(f"Incomplete category data: name='{category_name}', url='{category_url}'")

                except Exception as e:
                    logging.warning(f"Error extracting category: {e}")
                    continue

            # Upsert categories into database
            inserted_count = 0
            updated_count = 0
            for category in categories:
                result = self.db['categories'].update_one(
                    {'url': category['url']},  # Use URL as unique identifier
                    {'$set': category},
                    upsert=True
                )
                if result.upserted_id:
                    inserted_count += 1
                elif result.modified_count > 0:
                    updated_count += 1

            logging.info(f"Categories processed: {inserted_count} inserted, {updated_count} updated")

            # Close the categories menu by pressing ESC
            try:
                self.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
                time.sleep(1)
                logging.info("Pressed ESC to close categories menu")
            except Exception as e:
                logging.warning(f"Could not close categories menu: {e}")

        except Exception as e:
            logging.error(f"Error extracting categories: {e}")
            raise

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
            self.extract_categories()
            logging.info("Step 2 completed successfully")
        except Exception as e:
            logging.error(f"Step 2 failed: {e}")
        finally:
            self.close_driver()


if __name__ == "__main__":
    scraper = CarrefourScraperStep2(headless=False)  # Set to False for debugging
    scraper.run()