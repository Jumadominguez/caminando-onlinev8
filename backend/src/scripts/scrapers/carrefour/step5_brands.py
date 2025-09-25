import logging
import time
import re
import unicodedata
import random
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from pymongo import MongoClient
import os

class CarrefourScraperBrands:
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
                logging.FileHandler('carrefour_brands.log'),
                logging.StreamHandler()
            ]
        )

    def setup_driver(self):
        """Setup Firefox WebDriver with anti-bot measures"""
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
            options.add_argument('--disable-web-security')
            options.add_argument('--allow-running-insecure-content')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('--disable-features=VizDisplayCompositor')

            # Set user agent to look like a real browser
            options.set_preference("general.useragent.override",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0")

            # Disable webdriver property to avoid detection
            options.set_preference("dom.webdriver.enabled", False)
            options.set_preference('useAutomationExtension', False)

            # Randomize viewport size
            options.add_argument('--width=1920')
            options.add_argument('--height=1080')

            # Use local geckodriver if available
            geckodriver_path = os.path.join(os.getcwd(), 'geckodriver.exe')
            if os.path.exists(geckodriver_path):
                service = Service(geckodriver_path)
            else:
                service = Service()

            self.driver = webdriver.Firefox(service=service, options=options)

            # Execute script to remove webdriver property
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

            logging.info("Firefox WebDriver setup successfully with anti-bot measures")
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

    def extract_brands(self):
        """Extract brands for all categories in database"""
        logging.info("Starting Brand Extraction")

        # Get all categories from database
        categories = list(self.db['categories'].find({}, {'_id': 0, 'url': 1, 'name': 1}))

        if not categories:
            logging.warning("No categories found in database. Run Step 2 first.")
            return

        # Process all categories
        logging.info(f"Processing {len(categories)} categories for brands")

        total_brands = 0

        for category in categories:
            category_name = category['name']
            category_url = category['url']

            logging.info(f"Processing brands for: {category_name}")

            try:
                # Navigate to category page
                self.driver.get(category_url)
                time.sleep(3)  # Wait for page to load

                # Random additional delay to simulate human behavior
                human_delay = random.uniform(1.0, 3.0)
                time.sleep(human_delay)

                # Aggressive scroll to move navigation menu out of view
                self.driver.execute_script("window.scrollTo(0, 1000);")
                time.sleep(2)

                # Try to close any open menus by clicking ESC key
                try:
                    body = self.driver.find_element(By.TAG_NAME, 'body')
                    body.send_keys(Keys.ESCAPE)
                    time.sleep(1)
                    logging.info("Pressed ESC to close menus")
                except Exception as e:
                    logging.warning(f"Could not press ESC: {e}")

                # Additional scroll and wait
                self.driver.execute_script("window.scrollTo(0, 1200);")
                time.sleep(2)

                # Look for brand filter container
                brand_selectors = [
                    'div.valtech-carrefourar-search-result-3-x-filter__container--brand',
                    'div[data-testid="brand-filter"]',
                    '[class*="brand"]',
                    '[class*="marca"]'
                ]

                brand_container = None
                for selector in brand_selectors:
                    try:
                        brand_container = self.driver.find_element(By.CSS_SELECTOR, selector)
                        logging.info(f"Found brand container with selector: {selector}")
                        break
                    except NoSuchElementException:
                        continue

                if not brand_container:
                    logging.warning(f"No brand container found for {category_name}")
                    continue

                # Check if it's collapsed and expand it
                try:
                    expand_button = brand_container.find_element(By.CSS_SELECTOR, 'div[role="button"]')
                    if expand_button and expand_button.is_displayed():
                        # More aggressive scrolling to ensure menu is out of view
                        self.driver.execute_script("window.scrollTo(0, 1500);")
                        time.sleep(1)

                        # Scroll the expand button into view and additional offset
                        self.driver.execute_script("arguments[0].scrollIntoView(true);", expand_button)
                        self.driver.execute_script("window.scrollBy(0, 200);")  # Additional scroll down
                        time.sleep(2)

                        # Try JavaScript click instead of Selenium click
                        try:
                            self.driver.execute_script("arguments[0].click();", expand_button)
                            time.sleep(3)
                            logging.info(f"Expanded brand container for {category_name} using JavaScript click")
                        except Exception as js_error:
                            logging.warning(f"JavaScript click failed, trying Selenium click: {js_error}")
                            # Fallback to Selenium click with more scrolling
                            self.driver.execute_script("window.scrollTo(0, 2000);")
                            time.sleep(1)
                            expand_button.click()
                            time.sleep(3)
                            logging.info(f"Expanded brand container for {category_name} using Selenium click")
                except NoSuchElementException:
                    logging.info(f"Brand container already expanded for {category_name}")

                # Scroll to bottom of the page to trigger loading of "ver más" button
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)

                # Look for "ver N más" button within the container
                try:
                    see_more_button = brand_container.find_element(By.CSS_SELECTOR, 'button.valtech-carrefourar-search-result-3-x-seeMoreButton')
                    if see_more_button.is_displayed():
                        # Scroll to the button with extra offset
                        self.driver.execute_script("arguments[0].scrollIntoView(true);", see_more_button)
                        self.driver.execute_script("window.scrollBy(0, 100);")
                        time.sleep(1)

                        # Try JavaScript click for "ver más" button too
                        self.driver.execute_script("arguments[0].click();", see_more_button)
                        time.sleep(3)
                        logging.info(f"Clicked 'ver más' button for brands in {category_name}")
                except NoSuchElementException:
                    logging.info(f"No 'ver más' button found for brands in {category_name}")

                # Extract brand options
                brand_checkboxes = brand_container.find_elements(By.CSS_SELECTOR, 'input[type="checkbox"][id^="brand-"]')

                brands = []
                for checkbox in brand_checkboxes:
                    try:
                        # Get the associated label - try different approaches
                        label = None

                        # Method 1: Look for label with 'for' attribute matching checkbox id
                        checkbox_id = checkbox.get_attribute('id')
                        if checkbox_id:
                            try:
                                label = self.driver.find_element(By.CSS_SELECTOR, f'label[for="{checkbox_id}"]')
                            except NoSuchElementException:
                                pass

                        # Method 2: Look for following sibling label
                        if not label:
                            try:
                                label = checkbox.find_element(By.XPATH, 'following-sibling::label')
                            except NoSuchElementException:
                                pass

                        # Method 3: Look for parent label
                        if not label:
                            try:
                                parent = checkbox.find_element(By.XPATH, '..')
                                if parent.tag_name == 'label':
                                    label = parent
                            except NoSuchElementException:
                                pass

                        if label:
                            brand_name = label.text.strip()
                            # Remove count in parentheses (e.g., "(181)" -> "")
                            brand_name = re.sub(r'\s*\(\d+\)$', '', brand_name)
                            if brand_name:
                                brand_data = {
                                    'name': brand_name,
                                    'name_simple': self.simplify_name(brand_name),
                                    'categories': [category_name],  # Array of categories where this brand appears
                                    'type': 'brand',  # Identify this as a brand filter
                                    'scraped_at': datetime.now().isoformat()
                                }

                                brands.append(brand_data)

                    except Exception as e:
                        logging.warning(f"Error extracting brand: {e}")
                        continue

                # Upsert brands into database (avoiding global duplicates, tracking all categories)
                inserted_count = 0
                updated_count = 0
                for brand in brands:
                    # Check if brand already exists
                    existing_brand = self.db['filters'].find_one({
                        'name': brand['name'],
                        'type': 'brand'
                    })

                    if existing_brand:
                        # Brand exists, add category to array if not already present
                        result = self.db['filters'].update_one(
                            {
                                'name': brand['name'],
                                'type': 'brand'
                            },
                            {
                                '$addToSet': {'categories': brand['categories'][0]},  # Add category if not exists
                                '$set': {
                                    'name_simple': brand['name_simple'],
                                    'scraped_at': brand['scraped_at']
                                }
                            }
                        )
                        if result.modified_count > 0:
                            updated_count += 1
                    else:
                        # Brand doesn't exist, insert new document
                        result = self.db['filters'].insert_one(brand)
                        inserted_count += 1

                logging.info(f"Brands for {category_name}: {inserted_count} inserted, {updated_count} updated")
                total_brands += len(brands)

                # Random delay between categories to avoid bot detection
                delay = random.uniform(2.0, 5.0)
                logging.info(f"Waiting {delay:.1f} seconds before next category...")
                time.sleep(delay)

            except Exception as e:
                logging.error(f"Error processing brands for category {category_name}: {e}")
                continue

        logging.info(f"Total brands extracted: {total_brands}")

    def close_driver(self):
        """Close WebDriver"""
        if self.driver:
            try:
                self.driver.quit()
                logging.info("WebDriver closed")
            except Exception as e:
                logging.warning(f"Error closing WebDriver: {e}")

    def run(self):
        """Run the complete brand extraction process"""
        try:
            self.setup_driver()
            self.connect_db()
            self.extract_brands()
            logging.info("Brand extraction completed successfully")
        except Exception as e:
            logging.error(f"Brand extraction failed: {e}")
        finally:
            self.close_driver()


if __name__ == "__main__":
    scraper = CarrefourScraperBrands(headless=True)  # Headless for production efficiency
    scraper.run()