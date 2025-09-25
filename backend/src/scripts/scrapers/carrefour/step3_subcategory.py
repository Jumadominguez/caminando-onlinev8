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
import os

class CarrefourScraperStep3:
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
                logging.FileHandler('carrefour_step3.log'),
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

    def extract_subcategories(self):
        """Step 3: Extract subcategories for all categories in database"""
        logging.info("Starting Step 3: Extract subcategories")

        # Get all categories from database
        categories = list(self.db['categories'].find({}, {'_id': 0, 'url': 1, 'name': 1}))

        if not categories:
            logging.warning("No categories found in database. Run Step 2 first.")
            return

        # Process all categories
        logging.info(f"Processing {len(categories)} categories for subcategories")

        total_subcategories = 0

        for category in categories:
            category_name = category['name']
            category_url = category['url']

            logging.info(f"Processing subcategories for: {category_name}")

            try:
                # Navigate to category page
                self.driver.get(category_url)
                time.sleep(3)  # Wait for page to load

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

                # Look for subcategory container
                subcategory_selectors = [
                    'div.valtech-carrefourar-search-result-3-x-filter__container--category-3',
                    'div[data-testid="subcategory-filter"]',
                    '[class*="subcategory"]',
                    '[class*="sub-categoria"]'
                ]

                subcategory_container = None
                for selector in subcategory_selectors:
                    try:
                        subcategory_container = self.driver.find_element(By.CSS_SELECTOR, selector)
                        logging.info(f"Found subcategory container with selector: {selector}")
                        break
                    except NoSuchElementException:
                        continue

                if not subcategory_container:
                    logging.warning(f"No subcategory container found for {category_name}")
                    continue

                # Check if it's collapsed and expand it
                try:
                    expand_button = subcategory_container.find_element(By.CSS_SELECTOR, 'div[role="button"]')
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
                            logging.info(f"Expanded subcategory container for {category_name} using JavaScript click")
                        except Exception as js_error:
                            logging.warning(f"JavaScript click failed, trying Selenium click: {js_error}")
                            # Fallback to Selenium click with more scrolling
                            self.driver.execute_script("window.scrollTo(0, 2000);")
                            time.sleep(1)
                            expand_button.click()
                            time.sleep(3)
                            logging.info(f"Expanded subcategory container for {category_name} using Selenium click")
                except NoSuchElementException:
                    logging.info(f"Subcategory container already expanded for {category_name}")

                # Scroll to bottom of the page to trigger loading of "ver más" button
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)

                # Look for "ver N más" button within the container
                try:
                    see_more_button = subcategory_container.find_element(By.CSS_SELECTOR, 'button.valtech-carrefourar-search-result-3-x-seeMoreButton')
                    if see_more_button.is_displayed():
                        # Scroll to the button with extra offset
                        self.driver.execute_script("arguments[0].scrollIntoView(true);", see_more_button)
                        self.driver.execute_script("window.scrollBy(0, 100);")
                        time.sleep(1)

                        # Try JavaScript click for "ver más" button too
                        self.driver.execute_script("arguments[0].click();", see_more_button)
                        time.sleep(3)
                        logging.info(f"Clicked 'ver más' button for {category_name}")
                except NoSuchElementException:
                    logging.info(f"No 'ver más' button found for {category_name}")

                # Extract subcategory options
                subcategory_checkboxes = subcategory_container.find_elements(By.CSS_SELECTOR, 'input[type="checkbox"][id^="category-3-"]')

                subcategories = []
                for checkbox in subcategory_checkboxes:
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
                            subcategory_name = label.text.strip()
                            # Remove count in parentheses (e.g., "(181)" -> "")
                            subcategory_name = re.sub(r'\s*\(\d+\)$', '', subcategory_name)
                            if subcategory_name:
                                subcategory_data = {
                                    'name': subcategory_name,
                                    'name_simple': self.simplify_name(subcategory_name),
                                    'category_url': category_url,  # Link to parent category
                                    'category_name': category_name,
                                    'scraped_at': datetime.now().isoformat()
                                }

                                subcategories.append(subcategory_data)

                    except Exception as e:
                        logging.warning(f"Error extracting subcategory: {e}")
                        continue

                # Upsert subcategories into database
                inserted_count = 0
                updated_count = 0
                for subcategory in subcategories:
                    result = self.db['subcategories'].update_one(
                        {
                            'name': subcategory['name'],
                            'category_url': subcategory['category_url']
                        },  # Unique identifier: name + category
                        {'$set': subcategory},
                        upsert=True
                    )
                    if result.upserted_id:
                        inserted_count += 1
                    elif result.modified_count > 0:
                        updated_count += 1

                logging.info(f"Subcategories for {category_name}: {inserted_count} inserted, {updated_count} updated")
                total_subcategories += len(subcategories)

            except Exception as e:
                logging.error(f"Error processing category {category_name}: {e}")
                continue

        logging.info(f"Total subcategories extracted: {total_subcategories}")

    def close_driver(self):
        """Close WebDriver"""
        if self.driver:
            try:
                self.driver.quit()
                logging.info("WebDriver closed")
            except Exception as e:
                logging.warning(f"Error closing WebDriver: {e}")

    def run(self):
        """Run the complete Step 3 process"""
        try:
            self.setup_driver()
            self.connect_db()
            self.extract_subcategories()
            logging.info("Step 3 completed successfully")
        except Exception as e:
            logging.error(f"Step 3 failed: {e}")
        finally:
            self.close_driver()


if __name__ == "__main__":
    scraper = CarrefourScraperStep3(headless=False)  # Set to False for debugging
    scraper.run()