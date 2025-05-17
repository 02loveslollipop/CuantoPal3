import unittest
import time
import os
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class US03Tests(unittest.TestCase):
    BASE_URL = "http://localhost:3000"
    GRADE_INPUT_SELECTOR = "input.home__input[placeholder='0.0'][type='number']"
    PERCENTAGE_INPUT_SELECTOR = "input.home__input[placeholder='0'][type='number']"
    ADD_GRADE_BUTTON_SELECTOR = "button.home__add-button"
    GRADES_LIST_ITEM_SELECTOR = "div.home__grades-container > div.home__grade-row"
    REMAINING_PERCENTAGE_DISPLAY_SELECTOR = "div.home__results-card p.home__card-text span"
    
    FIRST_TIME_ALERT_BUTTON_SELECTOR = ".alert__button.alert__button--single"
    ALERT_OVERLAY_SELECTOR = "div.alert__overlay"
    NAV_BACK_BUTTON_XPATH = "//button[contains(@class, 'nav-bar__button') and .//span[contains(@class, 'back-icon')]/svg[contains(@class, 'lucide-chevron-left')]]"
    HOME_CONTAINER_SELECTOR = "div.home__container"

    def set_driver_fixture(self, driver):
        self.driver = driver
        self.wait_short = WebDriverWait(self.driver, 5)
        self.wait_long = WebDriverWait(self.driver, 15)
        if not os.path.exists("screenshots"):
            os.makedirs("screenshots")

    def setUp(self):
        # This setup is primarily for direct unittest execution.
        # Pytest will use the fixture from conftest.py
        if not hasattr(self, 'driver') or not self.driver:
            logger.info("WebDriver not set by fixture, attempting fallback setup for direct unittest execution.")
            try:
                options = webdriver.ChromeOptions()
                # Add any desired options here, e.g., headless
                # options.add_argument('--headless')
                # options.add_argument('--disable-gpu')
                self.driver = webdriver.Chrome(options=options)
                self.set_driver_fixture(self.driver) # Call to setup waits and screenshot dir
                self.is_driver_managed_by_fallback = True
                logger.info("Fallback WebDriver initialized for direct unittest execution.")
            except Exception as e:
                logger.error(f"Failed to initialize fallback WebDriver: {e}")
                self.fail(f"Failed to initialize fallback WebDriver: {e}")
        else:
            logger.info("WebDriver already set, likely by a pytest fixture.")
            self.is_driver_managed_by_fallback = False
        self._initial_setup()

    def tearDown(self):
        if hasattr(self, 'is_driver_managed_by_fallback') and self.is_driver_managed_by_fallback:
            if self.driver:
                self.driver.quit()
                logger.info("Fallback WebDriver quit.")
        else:
            logger.info("Driver teardown managed by pytest fixture (if applicable).")

    def _take_screenshot(self, name_suffix):
        timestamp = int(time.time())
        test_method_name = getattr(self, '_testMethodName', 'unknown_test')
        screenshot_name = f"screenshots/{test_method_name}_{name_suffix}_{timestamp}.png"
        try:
            if hasattr(self, 'driver') and self.driver:
                self.driver.save_screenshot(screenshot_name)
                logger.info(f"Screenshot saved: {screenshot_name}")
        except Exception as e:
            logger.error(f"Error saving screenshot {screenshot_name}: {e}")

    def _initial_setup(self):
        if not hasattr(self, 'driver') or not self.driver:
            logger.error("Driver not initialized in _initial_setup. Aborting setup.")
            self.fail("Driver not initialized for test setup.")
            return

        self.driver.get(self.BASE_URL)
        logger.info(f"Navigated to base URL: {self.BASE_URL}")

        try:
            logger.info(f"Attempting to handle first-time alert with button '{self.FIRST_TIME_ALERT_BUTTON_SELECTOR}'.")
            alert_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, self.FIRST_TIME_ALERT_BUTTON_SELECTOR))
            )
            alert_button.click()
            logger.info(f"Clicked first-time alert button: '{self.FIRST_TIME_ALERT_BUTTON_SELECTOR}'.")

            WebDriverWait(self.driver, 5).until(
                EC.invisibility_of_element_located((By.CSS_SELECTOR, self.ALERT_OVERLAY_SELECTOR))
            )
            logger.info(f"Alert overlay '{self.ALERT_OVERLAY_SELECTOR}' is no longer visible. App should be on Settings page.")
            
            # Navigate back to home page
            nav_back_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, self.NAV_BACK_BUTTON_XPATH))
            )
            nav_back_button.click()
            logger.info("Clicked nav back button to return to Home page.")

            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, self.HOME_CONTAINER_SELECTOR))
            )
            logger.info("Successfully navigated back to the Home page.")

        except TimeoutException:
            logger.info("First-time user alert or navigation elements not found or timed out. Assuming already on Home page or flow is different.")
            # Check if we are on the home page, if not, try to navigate.
            if self.HOME_CONTAINER_SELECTOR not in self.driver.page_source:
                self.driver.get(self.BASE_URL) # Re-navigate if something went wrong
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, self.HOME_CONTAINER_SELECTOR))
                )
                logger.info("Re-navigated to Home page as a fallback.")
        except Exception as e:
            logger.error(f"An unexpected error occurred during initial setup: {e}")
            self._take_screenshot("initial_setup_error")
            # self.fail(f"Critical error during initial setup: {e}") # Decide if this should fail the test or just log

    def _add_grade_and_percentage(self, grade, percentage):
        if not hasattr(self, 'driver') or not self.driver:
            logger.error("Driver not available in _add_grade_and_percentage.")
            self.fail("Driver not available.")
            return

        grade_rows = self.driver.find_elements(By.CSS_SELECTOR, self.GRADES_LIST_ITEM_SELECTOR)
        if not grade_rows:
            logger.error("No grade rows found to add grade and percentage.")
            self._take_screenshot("no_grade_rows_found")
            self.fail("No grade rows found.")
            return

        last_row = grade_rows[-1]
        logger.info(f"Targeting the last of {len(grade_rows)} grade rows for input.")

        try:
            grade_input_element = last_row.find_element(By.CSS_SELECTOR, self.GRADE_INPUT_SELECTOR)
            percentage_input_element = last_row.find_element(By.CSS_SELECTOR, self.PERCENTAGE_INPUT_SELECTOR)
        except NoSuchElementException as e:
            logger.error(f"Could not find grade or percentage input in the last row: {e}")
            logger.info(f"HTML of last row: {last_row.get_attribute('outerHTML')}")
            self._take_screenshot("input_not_found_in_last_row")
            self.fail("Input elements not found in the last row.")
            return
        
        add_button = self.wait_long.until(EC.element_to_be_clickable((By.CSS_SELECTOR, self.ADD_GRADE_BUTTON_SELECTOR)))

        grade_input_element.clear()
        grade_input_element.send_keys(str(grade))
        percentage_input_element.clear()
        percentage_input_element.send_keys(str(percentage))
        
        add_button.click() 
        logger.info(f"Clicked 'Agregar nota' after attempting to add grade: {grade}, percentage: {percentage} to the last row.")
        # Wait for UI to update, especially if new rows are added dynamically.
        # A more robust wait would be for the number of rows to change or for a specific element to appear.
        time.sleep(0.5) # Small delay for React state updates

    def _get_remaining_percentage(self):
        cleaned_text = "" # Initialize cleaned_text
        try:
            # Wait for the element to be present and contain some text
            percentage_element = self.wait_long.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, self.REMAINING_PERCENTAGE_DISPLAY_SELECTOR))
            )
            # Add a small delay or check for text to be non-empty if necessary
            time.sleep(0.2) # give a brief moment for text to update
            
            # Attempt to get text, retry if it's empty initially due to rendering delays
            text_value = percentage_element.text.strip()
            attempts = 0
            while text_value == "" and attempts < 5: # Retry if empty
                time.sleep(0.3)
                text_value = percentage_element.text.strip()
                attempts += 1
            
            logger.info(f"Raw remaining percentage text: '{text_value}'")
            if not text_value: # If still empty after retries
                logger.warning("Remaining percentage text is empty after retries.")
                self._take_screenshot("empty_remaining_percentage")
                return "Error: Empty Value" # Or raise an error

            # Assuming the text is like "XX %" or "XX%", we remove "%" and convert to float
            # If it's just "XX", this will also work.
            cleaned_text = text_value.replace('%', '').strip()
            return float(cleaned_text)
        except TimeoutException:
            logger.error(f"Timeout waiting for remaining percentage display element: {self.REMAINING_PERCENTAGE_DISPLAY_SELECTOR}")
            self._take_screenshot("remaining_percentage_timeout")
            return "Error: Timeout" # Or raise an error
        except ValueError:
            logger.error(f"Could not convert remaining percentage text '{cleaned_text}' to float.") # cleaned_text is now defined
            self._take_screenshot("remaining_percentage_value_error")
            return "Error: Conversion" # Or raise an error
        except Exception as e:
            logger.error(f"Error getting remaining percentage: {e}")
            self._take_screenshot("get_remaining_percentage_error")
            return "Error: General" # Or raise an error

    # US03: Calculo del porcentaje faltante
    def test_us03_verify_calculation_of_remaining_percentage(self):
        test_name = self._testMethodName
        logger.info(f"Running test: {test_name}")

        try:
            # 1. Initial state: Verify remaining percentage is 100%
            logger.info("Verifying initial remaining percentage.")
            initial_remaining = self._get_remaining_percentage()
            self.assertEqual(initial_remaining, 100.0, 
                             f"Initial remaining percentage expected 100.0, but got {initial_remaining}")
            logger.info(f"Initial remaining percentage is correct: {initial_remaining}%")

            # 2. Add one grade and verify
            logger.info("Adding first grade (20%).")
            self._add_grade_and_percentage("3.0", "20")
            # It might take a moment for the calculation to update
            time.sleep(0.5) # Wait for calculation update
            remaining_after_first_grade = self._get_remaining_percentage()
            self.assertEqual(remaining_after_first_grade, 80.0,
                             f"Remaining percentage after 1st grade (20%) expected 80.0, but got {remaining_after_first_grade}")
            logger.info(f"Remaining percentage after 1st grade (20%) is correct: {remaining_after_first_grade}%")

            # 3. Add a second grade and verify
            logger.info("Adding second grade (30%). Total 50%.")
            self._add_grade_and_percentage("4.0", "30")
            time.sleep(0.5) # Wait for calculation update
            remaining_after_second_grade = self._get_remaining_percentage()
            self.assertEqual(remaining_after_second_grade, 50.0,
                             f"Remaining percentage after 2nd grade (total 50%) expected 50.0, but got {remaining_after_second_grade}")
            logger.info(f"Remaining percentage after 2nd grade (total 50%) is correct: {remaining_after_second_grade}%")

            # 4. Add a third grade to make total 100% and verify
            logger.info("Adding third grade (50%). Total 100%.")
            self._add_grade_and_percentage("5.0", "50")
            time.sleep(0.5) # Wait for calculation update
            remaining_after_third_grade = self._get_remaining_percentage()
            self.assertEqual(remaining_after_third_grade, 0.0,
                             f"Remaining percentage after 3rd grade (total 100%) expected 0.0, but got {remaining_after_third_grade}")
            logger.info(f"Remaining percentage after 3rd grade (total 100%) is correct: {remaining_after_third_grade}%")

        except AssertionError as e:
            logger.error(f"AssertionError in {test_name}: {e}")
            self._take_screenshot(f"{test_name}_assertion_failure")
            raise  # Re-raise the assertion error to fail the test
        except Exception as e:
            logger.error(f"An unexpected error occurred in {test_name}: {e}")
            self._take_screenshot(f"{test_name}_unexpected_error")
            raise # Re-raise to fail the test

        logger.info(f"Test {test_name} completed successfully.")

if __name__ == '__main__':
    # This allows running the test file directly with `python us3.py`
    # For more comprehensive test runs, use pytest.
    unittest.main(verbosity=2)
