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

class CarrefourScraperStep1:
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
                logging.FileHandler('scraper_step1.log'),
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

    def extract_supermarket_info(self):
        """Step 1: Extract supermarket information from home page"""
        logging.info("Starting Step 1: Extract supermarket info")

        try:
            # Navigate to home page
            self.driver.get("https://www.carrefour.com.ar")
            time.sleep(3)  # Wait for page to load

            supermarket_data = {
                'name': 'Carrefour Argentina',
                'url': 'https://www.carrefour.com.ar',
                'country': 'Argentina',
                'scraped_at': datetime.now().isoformat()
            }

            # Try to extract additional info from footer or header
            try:
                # Look for contact info, address, etc.
                footer = self.driver.find_element(By.TAG_NAME, 'footer')
                footer_text = footer.text

                # Extract phone if available
                phone_match = re.search(r'\d{3,4}[-.\s]?\d{3,4}[-.\s]?\d{3,4}', footer_text)
                if phone_match:
                    supermarket_data['phone'] = phone_match.group()

                # Extract email if available
                email_match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', footer_text)
                if email_match:
                    supermarket_data['email'] = email_match.group()

            except Exception as e:
                logging.warning(f"Could not extract additional supermarket info: {e}")

            # Upsert to database
            result = self.db['supermarket-info'].update_one(
                {'url': supermarket_data['url']},  # Unique identifier
                {'$set': supermarket_data},
                upsert=True
            )

            if result.upserted_id:
                logging.info("Inserted new supermarket info")
            else:
                logging.info("Updated existing supermarket info")

        except Exception as e:
            logging.error(f"Error extracting supermarket info: {e}")
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
        """Run the complete Step 1 process"""
        try:
            self.setup_driver()
            self.connect_db()
            self.extract_supermarket_info()
            logging.info("Step 1 completed successfully")
        except Exception as e:
            logging.error(f"Step 1 failed: {e}")
        finally:
            self.close_driver()


if __name__ == "__main__":
    scraper = CarrefourScraperStep1(headless=False)  # Set to False for debugging
    scraper.run()