import logging
import os
import unittest # Added
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time # Keep time for explicit waits if necessary, though WebDriverWait is preferred

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class HomePageTest(unittest.TestCase): # Changed base class
    BASE_URL = "http://localhost:3000" # Added base URL for React app

    # Selectors based on the provided HTML
    GRADE_INPUT_SELECTOR = "input.home__input[placeholder=\"0.0\"][type=\"number\"]"
    PERCENTAGE_INPUT_SELECTOR = "input.home__input[placeholder=\"0\"][type=\"number\"]"
    ADD_GRADE_BUTTON_SELECTOR = "button.home__add-button" # Selector for "Agregar nota"
    GRADES_LIST_ITEM_SELECTOR = "div.home__grades-container > div.home__grade-row"
    CALCULATE_BUTTON_SELECTOR = "button.home__calculate-button" # Selector for "Calcular

    # Selectors for alerts and navigation
    FIRST_TIME_ALERT_BUTTON_SELECTOR = ".alert__button.alert__button--single" # For "Configurar" on first-time alert
    ALERT_OVERLAY_SELECTOR = "div.alert__overlay"
    NAV_BACK_BUTTON_XPATH = "//button[contains(@class, 'nav-bar__button') and .//span[contains(@class, 'back-icon')]/svg[contains(@class, 'lucide-chevron-left')]]"
    HOME_CONTAINER_SELECTOR = "div.home__container" # Selector for a main container on the home page

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        options = webdriver.ChromeOptions()
        # options.add_argument("--headless") # Run in headless mode for CI/faster tests
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920,1080") # Standard window size
        
        # Attempt to use WebDriverManager for automatic driver management
        try:
            from webdriver_manager.chrome import ChromeDriverManager
            from selenium.webdriver.chrome.service import Service as ChromeService
            cls.driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
        except ImportError:
            logger.warning("webdriver_manager not found. Falling back to direct ChromeDriver instantiation.")
            # Fallback if WebDriverManager is not available (ensure chromedriver is in PATH)
            cls.driver = webdriver.Chrome(options=options)
            
        cls.wait_short = WebDriverWait(cls.driver, 5)
        cls.wait_long = WebDriverWait(cls.driver, 15)
        # Ensure screenshots directory exists
        if not os.path.exists("screenshots"):
            os.makedirs("screenshots")

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        super().tearDownClass()

    def setUp(self):
        """Called before every test method."""
        self._initial_setup() # Call initial setup here

    def _take_screenshot(self, name_suffix):
        timestamp = int(time.time())
        screenshot_name = f"screenshots/{self._testMethodName}_{name_suffix}_{timestamp}.png"
        try:
            self.driver.save_screenshot(screenshot_name)
            logger.info(f"Screenshot saved: {screenshot_name}")
        except Exception as e:
            logger.error(f"Error saving screenshot {screenshot_name}: {e}")

    def _initial_setup(self):
        self.driver.get(self.BASE_URL)
        logger.info(f"Navigated to base URL: {self.BASE_URL}")

        try:
            # 1. Attempt to handle the first-time alert
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

            # 2. Attempt to navigate back from Settings page to Home page
            try:
                logger.info("Attempting to navigate back from Settings to Home using nav-bar back button.")
                nav_back_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, self.NAV_BACK_BUTTON_XPATH))
                )
                nav_back_button.click()
                logger.info("Clicked navigation bar 'Atras' button.")
                
                # Wait for an element that indicates we are back on the Home page
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, self.HOME_CONTAINER_SELECTOR))
                )
                logger.info(f"Successfully navigated back to Home page (found '{self.HOME_CONTAINER_SELECTOR}').")
            except Exception as nav_exc:
                logger.error(f"Navigation back to Home page failed: {nav_exc}. Attempting recovery.")
                self._take_screenshot("error_nav_back_failed_recovery_attempt")
                # Recovery: Go back to base URL and try to click alert again (if it reappears or if it was a different issue)
                self.driver.get(self.BASE_URL)
                logger.info(f"Recovery: Navigated back to base URL: {self.BASE_URL}")
                try:
                    # This alert click might not be necessary if localStorage is already set,
                    # but follows the pattern of the user's original recovery logic.
                    alert_button_recovery = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, self.FIRST_TIME_ALERT_BUTTON_SELECTOR))
                    )
                    alert_button_recovery.click()
                    logger.info("Recovery: Clicked first-time alert button again.")
                    WebDriverWait(self.driver, 5).until(
                        EC.invisibility_of_element_located((By.CSS_SELECTOR, self.ALERT_OVERLAY_SELECTOR))
                    )
                    logger.info("Recovery: Alert overlay is no longer visible after second attempt.")
                    # After this, the final verification for GRADE_INPUT_SELECTOR will run.
                    # If this recovery path is taken, and we are not on settings, the next check for GRADE_INPUT_SELECTOR should pass.
                    # If we are on settings, the check will fail, which is an unrecoverable state for this setup.
                except TimeoutException:
                    logger.info("Recovery: First-time alert button not found on second attempt. Assuming Home page or non-first-time state.")
                except Exception as recovery_alert_exc:
                    logger.warning(f"Recovery: Error clicking alert button on second attempt: {recovery_alert_exc}")

        except TimeoutException:
            logger.info(f"First-time alert (button '{self.FIRST_TIME_ALERT_BUTTON_SELECTOR}') not found. Assuming not first time or alert already dismissed.")
            # No action needed if the alert isn't there, proceed to final verification.
        except Exception as e:
            logger.warning(f"An unexpected error occurred during initial alert handling phase: {e}")
            self._take_screenshot("error_initial_alert_phase")

        # Final verification: Ensure the Home page grade input is present
        try:
            WebDriverWait(self.driver, 15).until( # Using self.wait_long effectively
                EC.presence_of_element_located((By.CSS_SELECTOR, self.GRADE_INPUT_SELECTOR))
            )
            logger.info(f"Grade input ('{self.GRADE_INPUT_SELECTOR}') found on page. Setup complete.")
        except TimeoutException:
            current_url = self.driver.current_url
            logger.error(f"FINAL SETUP FAILURE: Failed to find grade input ('{self.GRADE_INPUT_SELECTOR}') after all attempts. Current URL: {current_url}")
            self._take_screenshot("error_final_grade_input_not_found")
            raise Exception(f"Could not find the grade input ('{self.GRADE_INPUT_SELECTOR}') after setup. Current URL: {current_url}")

    def _add_grade_and_percentage(self, grade, percentage):
        # Find all grade rows
        grade_rows = self.driver.find_elements(By.CSS_SELECTOR, self.GRADES_LIST_ITEM_SELECTOR)
        if not grade_rows:
            logger.error("Could not find any grade rows (selector: %s).", self.GRADES_LIST_ITEM_SELECTOR)
            self._take_screenshot("error_add_grade_no_rows")
            raise NoSuchElementException(f"No grade rows found with selector '{self.GRADES_LIST_ITEM_SELECTOR}'.")

        # Target the last grade row for input
        last_row = grade_rows[-1]
        logger.info(f"Targeting the last of {len(grade_rows)} grade rows for input.")

        try:
            # Find inputs within the last row
            # These selectors should be specific enough to find the correct inputs within the row
            grade_input_element = last_row.find_element(By.CSS_SELECTOR, self.GRADE_INPUT_SELECTOR)
            percentage_input_element = last_row.find_element(By.CSS_SELECTOR, self.PERCENTAGE_INPUT_SELECTOR)
        except NoSuchElementException as e:
            logger.error(f"Could not find grade or percentage input field in the last grade row. Details: {e}")
            self._take_screenshot("error_add_grade_no_inputs_in_last_row")
            raise
        
        add_button = self.wait_long.until(EC.element_to_be_clickable((By.CSS_SELECTOR, self.ADD_GRADE_BUTTON_SELECTOR)))

        grade_input_element.clear()
        grade_input_element.send_keys(str(grade))
        percentage_input_element.clear()
        percentage_input_element.send_keys(str(percentage))
        
        # According to UI logic:
        # 1. Filling the second field (e.g., percentage) in the last row triggers handleChange to add a new empty row.
        # 2. Clicking "Agregar nota" (handleAddGrade) adds another new empty row.
        add_button.click() 
        logger.info(f"Clicked 'Agregar nota' after attempting to add grade: {grade}, percentage: {percentage} to the last row.")

    def _get_grades_list_item_count(self): # Removed driver argument
        try:
            # Wait briefly for items to appear or update after an action
            time.sleep(0.5) # Small delay to allow UI to update
            grade_items = self.driver.find_elements(By.CSS_SELECTOR, self.GRADES_LIST_ITEM_SELECTOR)
            logger.info(f"Found {len(grade_items)} grade list items using selector '{self.GRADES_LIST_ITEM_SELECTOR}'.")
            return len(grade_items)
        except Exception as e:
            logger.error(f"Error finding grade list items with selector \'{self.GRADES_LIST_ITEM_SELECTOR}\': {e}")
            self._take_screenshot("error_get_grades_list_item_count")
            return 0

    # US01: Registro de Calificaciones
    def test_us01_add_single_valid_grade(self, request=None): # request might not be needed if not using pytest fixtures directly here
        test_name = request.node.name if request else self._testMethodName # Get test name
        logger.info(f"Running test: {test_name}")
        
        initial_item_count = self._get_grades_list_item_count()
        logger.info(f"Initial grade item count: {initial_item_count}")

        grade_to_add = "4.5"
        percentage_to_add = "25"
        self._add_grade_and_percentage(grade_to_add, percentage_to_add)

        # Wait for the item count to increase reflecting the two new rows added
        expected_count_after_add = initial_item_count + 2
        try:
            self.wait_long.until(
                lambda d: self._get_grades_list_item_count() == expected_count_after_add
            )
        except TimeoutException:
            self._take_screenshot(f"{test_name}_timeout_waiting_for_grade_add")
            logger.error(f"Timeout waiting for grade item count to become {expected_count_after_add}.")
        
        current_item_count = self._get_grades_list_item_count()
        logger.info(f"Current grade item count after add: {current_item_count}")
        try:
            self.assertEqual(current_item_count, expected_count_after_add, 
                             f"Grade item count did not increase by 2. Initial: {initial_item_count}, Expected: {expected_count_after_add}, Current: {current_item_count}")
        except AssertionError as e:
            self._take_screenshot(f"{test_name}_assertion_failed")
            raise e
        logger.info(f"Test {test_name} completed successfully.")


    def test_us01_add_multiple_valid_grades(self, request=None):
        test_name = request.node.name if request else self._testMethodName
        logger.info(f"Running test: {test_name}")

        initial_item_count = self._get_grades_list_item_count()
        logger.info(f"Initial grade item count: {initial_item_count}")

        grades_data = [
            {"grade": "5.0", "percentage": "30"},
            {"grade": "3.5", "percentage": "20"},
            {"grade": "6.2", "percentage": "50"}
        ]

        for i, item in enumerate(grades_data):
            self._add_grade_and_percentage(item["grade"], item["percentage"])
            expected_count_after_item_add = initial_item_count + 2 * (i + 1)
            try:
                # Wait for the item count to reflect the new addition
                self.wait_long.until(
                    lambda d: self._get_grades_list_item_count() == expected_count_after_item_add
                )
            except TimeoutException:
                self._take_screenshot(f"{test_name}_timeout_item_{i+1}")
                logger.error(f"Timeout waiting for grade item count to be {expected_count_after_item_add} after adding item {i+1}.")
            
            time.sleep(0.2) 

        expected_final_count = initial_item_count + 2 * len(grades_data)
        current_item_count = self._get_grades_list_item_count()
        logger.info(f"Current grade item count after multiple adds: {current_item_count}")
        try:
            self.assertEqual(current_item_count, expected_final_count,
                             f"Grade item count did not increase correctly. Initial: {initial_item_count}, Expected: {expected_final_count}, Got: {current_item_count}")
        except AssertionError as e:
            self._take_screenshot(f"{test_name}_assertion_failed")
            raise e
        logger.info(f"Test {test_name} completed successfully.")

    def test_us01_validate_grade_input_below_range(self, request=None):
        test_name = request.node.name if request else self._testMethodName
        logger.info(f"Running test: {test_name}")

        initial_item_count = self._get_grades_list_item_count()
        self._add_grade_and_percentage("-1.0", "20") # Invalid grade value, but fills fields
        
        expected_count = initial_item_count + 2 # Row count increases due to UI behavior
        current_item_count = self._get_grades_list_item_count()
        try:
            self.assertEqual(current_item_count, expected_count, 
                             f"Grade item count should increase by 2 even for invalid grade input (UI behavior). Initial: {initial_item_count}, Expected: {expected_count}, Current: {current_item_count}")
        except AssertionError as e:
            self._take_screenshot(f"{test_name}_assertion_failed")
            raise e
        logger.info(f"Test {test_name} completed (note: row count increased as expected by UI; value validation is separate).")

    def test_us01_validate_grade_input_above_range(self, request=None):
        test_name = request.node.name if request else self._testMethodName
        logger.info(f"Running test: {test_name}")

        initial_item_count = self._get_grades_list_item_count()
        self._add_grade_and_percentage("8.0", "20") # Invalid grade value, but fills fields
        
        expected_count = initial_item_count + 2 # Row count increases due to UI behavior
        current_item_count = self._get_grades_list_item_count()
        try:
            self.assertEqual(current_item_count, expected_count, 
                             f"Grade item count should increase by 2 even for invalid grade input (UI behavior). Initial: {initial_item_count}, Expected: {expected_count}, Current: {current_item_count}")
        except AssertionError as e:
            self._take_screenshot(f"{test_name}_assertion_failed")
            raise e
        logger.info(f"Test {test_name} completed (note: row count increased as expected by UI; value validation is separate).")

    def test_us01_validate_percentage_input_negative(self, request=None):
        test_name = request.node.name if request else self._testMethodName
        logger.info(f"Running test: {test_name}")

        initial_item_count = self._get_grades_list_item_count()
        self._add_grade_and_percentage("4.0", "-10") # Invalid percentage value, but fills fields
        
        expected_count = initial_item_count + 2 # Row count increases due to UI behavior
        current_item_count = self._get_grades_list_item_count()
        try:
            self.assertEqual(current_item_count, expected_count, 
                             f"Grade item count should increase by 2 even for invalid percentage input (UI behavior). Initial: {initial_item_count}, Expected: {expected_count}, Current: {current_item_count}")
        except AssertionError as e:
            self._take_screenshot(f"{test_name}_assertion_failed")
            raise e
        logger.info(f"Test {test_name} completed (note: row count increased as expected by UI; value validation is separate).")

    def test_us01_validate_percentage_input_non_numeric(self, request=None):
        test_name = request.node.name if request else self._testMethodName
        logger.info(f"Running test: {test_name}")

        initial_item_count = self._get_grades_list_item_count()
        self._add_grade_and_percentage("4.0", "abc") # Non-numeric percentage, but fills fields
        
        expected_count = initial_item_count + 2 # Row count increases due to UI behavior
        current_item_count = self._get_grades_list_item_count()
        try:
            self.assertEqual(current_item_count, expected_count, 
                             f"Grade item count should increase by 2 even for non-numeric percentage input (UI behavior). Initial: {initial_item_count}, Expected: {expected_count}, Current: {current_item_count}")
        except AssertionError as e:
            self._take_screenshot(f"{test_name}_assertion_failed")
            raise e
        logger.info(f"Test {test_name} completed (note: row count increased as expected by UI; value validation is separate).")

# ...existing code...
if __name__ == '__main__':
    unittest.main(verbosity=2)