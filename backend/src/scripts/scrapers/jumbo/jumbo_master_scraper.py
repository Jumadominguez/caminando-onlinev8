import logging
import time
import subprocess
import sys
import os
from datetime import datetime

class JumboScraperMaster:
    def __init__(self):
        self.setup_logging()
        self.scripts_dir = os.path.dirname(os.path.abspath(__file__))

    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('jumbo_master_scraper.log'),
                logging.StreamHandler()
            ]
        )

    def run_script(self, script_name, background=False):
        """Run a scraper script"""
        script_path = os.path.join(self.scripts_dir, script_name)

        if not os.path.exists(script_path):
            logging.error(f"Script not found: {script_path}")
            return False

        try:
            logging.info(f"Starting {script_name}{' in background' if background else ''}")

            if background:
                # Run in background
                process = subprocess.Popen([
                    sys.executable, script_path, '--background'
                ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                logging.info(f"{script_name} started in background (PID: {process.pid})")
                return True
            else:
                # Run synchronously
                result = subprocess.run([
                    sys.executable, script_path
                ], capture_output=True, text=True, timeout=3600)  # 1 hour timeout

                if result.returncode == 0:
                    logging.info(f"{script_name} completed successfully")
                    logging.info(f"Output: {result.stdout}")
                    return True
                else:
                    logging.error(f"{script_name} failed with return code {result.returncode}")
                    logging.error(f"Error: {result.stderr}")
                    return False

        except subprocess.TimeoutExpired:
            logging.error(f"{script_name} timed out")
            return False
        except Exception as e:
            logging.error(f"Error running {script_name}: {e}")
            return False

    def run_all_steps(self, background_mode=False):
        """Run all scraping steps in sequence"""
        logging.info("Starting Jumbo complete scraping process")

        steps = [
            ('jumbo_step1_supermarket.py', False),  # Always run synchronously
            ('jumbo_step2_categories.py', background_mode),
            ('jumbo_step3_subcategory.py', background_mode),
            ('jumbo_step4_producttypes.py', background_mode)
        ]

        for script_name, run_background in steps:
            success = self.run_script(script_name, run_background)
            if not success:
                logging.error(f"Failed at step: {script_name}")
                return False

            # Small delay between steps
            if not run_background:
                time.sleep(5)

        logging.info("Jumbo complete scraping process finished")
        return True

    def run_single_step(self, step_number, background=False):
        """Run a single scraping step"""
        step_map = {
            1: 'jumbo_step1_supermarket.py',
            2: 'jumbo_step2_categories.py',
            3: 'jumbo_step3_subcategory.py',
            4: 'jumbo_step4_producttypes.py'
        }

        if step_number not in step_map:
            logging.error(f"Invalid step number: {step_number}")
            return False

        script_name = step_map[step_number]
        return self.run_script(script_name, background)

if __name__ == "__main__":
    master = JumboScraperMaster()

    if len(sys.argv) > 1:
        if sys.argv[1] == '--all':
            # Run all steps
            background = '--background' in sys.argv
            master.run_all_steps(background_mode=background)
        elif sys.argv[1].startswith('--step='):
            # Run single step
            try:
                step = int(sys.argv[1].split('=')[1])
                background = '--background' in sys.argv
                master.run_single_step(step, background)
            except ValueError:
                logging.error("Invalid step number")
        else:
            print("Usage:")
            print("  python jumbo_master_scraper.py --all [--background]")
            print("  python jumbo_master_scraper.py --step=N [--background]")
            print("  Where N is 1-4 for the scraping step")
    else:
        print("Jumbo Master Scraper")
        print("===================")
        print("Usage:")
        print("  python jumbo_master_scraper.py --all [--background]    # Run all steps")
        print("  python jumbo_master_scraper.py --step=N [--background]  # Run single step (N=1-4)")
        print("")
        print("Options:")
        print("  --background: Run steps 2-4 in background mode (headless)")
        print("")
        print("Steps:")
        print("  1: Extract supermarket information")
        print("  2: Extract categories (with hover navigation)")
        print("  3: Extract subcategories from category pages")
        print("  4: Extract product types from subcategory pages")