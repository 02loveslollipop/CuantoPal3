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

    def _initial_setup(self): # Removed driver argument
        self.driver.get(self.BASE_URL) # Use BASE_URL
        
        first_time_alert_handled = False
        try:
            logger.info(f"Attempting to handle first-time alert with button '{self.FIRST_TIME_ALERT_BUTTON_SELECTOR}'.")
            alert_button = WebDriverWait(self.driver, 5).until( # Using wait_short's timeout
                EC.element_to_be_clickable((By.CSS_SELECTOR, self.FIRST_TIME_ALERT_BUTTON_SELECTOR))
            )
            alert_button.click()
            logger.info(f"Clicked first-time alert button: '{self.FIRST_TIME_ALERT_BUTTON_SELECTOR}'.");

            # Wait for the overlay to become invisible
            WebDriverWait(self.driver, 5).until( # Using wait_short's timeout
                EC.invisibility_of_element_located((By.CSS_SELECTOR, self.ALERT_OVERLAY_SELECTOR))
            )
            logger.info(f"Alert overlay '{self.ALERT_OVERLAY_SELECTOR}' is no longer visible.")
            first_time_alert_handled = True;
            
        except TimeoutException:
            logger.info(f"First-time alert (button '{self.FIRST_TIME_ALERT_BUTTON_SELECTOR}' or overlay '{self.ALERT_OVERLAY_SELECTOR}') not found or not handled within timeout. Assuming not first time or alert already dismissed.")
            # self._take_screenshot("debug_first_time_alert_timeout") # Optional: for debugging if this path is unexpected
        except Exception as e:
            logger.warning(f"An unexpected error occurred while trying to handle first-time alert: {e}")
            self._take_screenshot("error_initial_alert_handling")

        if first_time_alert_handled:
            try:
                logger.info("First-time alert was handled, app should be on Settings page. Attempting to navigate back to Home.")
                nav_back_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, self.NAV_BACK_BUTTON_XPATH))
                )
                nav_back_button.click()
                logger.info("Clicked navigation bar 'Atras' button to return to Home page.")
                # Add a short wait for page transition if necessary, before checking for home page elements
                time.sleep(0.5) # Allow a moment for navigation
            except TimeoutException:
                logger.error(f"Failed to find or click the navigation bar 'Atras' button (XPATH: {self.NAV_BACK_BUTTON_XPATH}) after handling first-time alert.")
                self._take_screenshot("error_nav_back_button_not_found")
                # This is a critical failure in the setup flow if the first-time alert was handled
                raise Exception("Failed to navigate back from Settings page during initial setup.")
            except Exception as e:
                logger.error(f"An error occurred clicking the navigation bar 'Atras' button: {e}")
                self._take_screenshot("error_nav_back_button_click")
                raise

        # Final verification: Ensure the Home page grade input is present
        try:
            self.wait_long.until(EC.presence_of_element_located((By.CSS_SELECTOR, self.GRADE_INPUT_SELECTOR)))
            logger.info(f"Grade input ('{self.GRADE_INPUT_SELECTOR}') found on page. Setup complete.")
        except TimeoutException:
            current_url = self.driver.current_url
            logger.error(f"Failed to find grade input ('{self.GRADE_INPUT_SELECTOR}') after setup attempts. Current URL: {current_url}")
            self._take_screenshot("error_final_grade_input_not_found")
            raise Exception(f"Could not find the grade input ('{self.GRADE_INPUT_SELECTOR}') after setup. Current URL: {current_url}")

    def _add_grade_and_percentage(self, grade, percentage): # Removed driver argument
        # Find the *first* available grade and percentage input.
        # This assumes new inputs are added, or we always fill the first empty/available ones.
        
        # Find all grade inputs and percentage inputs
        grade_inputs = self.driver.find_elements(By.CSS_SELECTOR, self.GRADE_INPUT_SELECTOR)
        percentage_inputs = self.driver.find_elements(By.CSS_SELECTOR, self.PERCENTAGE_INPUT_SELECTOR)

        if not grade_inputs or not percentage_inputs:
            logger.error("Could not find grade or percentage input fields.")
            self._take_screenshot("error_add_grade_no_inputs")
            raise NoSuchElementException("Grade or percentage input fields not found.")

        # Assuming we target the last grade input row for adding new grades,
        # which is typical if "Agregar nota" adds a new row and we fill that.
        # Or, if there's only one set of inputs that are cleared and reused.
        # The provided HTML shows one set of inputs initially.
        # If "Agregar nota" adds more, this logic might need to target the *last* set.
        # For now, let's assume we are targeting the first (and possibly only) input fields.
        grade_input_element = grade_inputs[0] 
        percentage_input_element = percentage_inputs[0]
        
        add_button = self.wait_long.until(EC.element_to_be_clickable((By.CSS_SELECTOR, self.ADD_GRADE_BUTTON_SELECTOR)))

        grade_input_element.clear()
        grade_input_element.send_keys(str(grade))
        percentage_input_element.clear()
        percentage_input_element.send_keys(str(percentage))
        
        # It's crucial to know if "Agregar nota" should be clicked *before* or *after* filling the inputs.
        # Based on typical UI, you fill, then click "Agregar".
        # If "Agregar nota" creates a new blank row first, then this click should happen *before* send_keys.
        # Assuming fill then click "Agregar nota" to submit that row.
        add_button.click() 
        logger.info(f"Clicked 'Agregar nota' after attempting to add grade: {grade}, percentage: {percentage}")

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

        # Wait for the item count to increase or for a specific element to appear
        try:
            self.wait_long.until(
                lambda d: self._get_grades_list_item_count() > initial_item_count
            )
        except TimeoutException:
            self._take_screenshot(f"{test_name}_timeout_waiting_for_grade_add")
            logger.error("Timeout waiting for grade item count to increase.")
        
        current_item_count = self._get_grades_list_item_count()
        logger.info(f"Current grade item count after add: {current_item_count}")
        self.assertEqual(current_item_count, initial_item_count + 1, 
                         f"Grade item count did not increase by 1. Initial: {initial_item_count}, Current: {current_item_count}")
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
            try:
                # Wait for the item count to reflect the new addition
                self.wait_long.until(
                    lambda d: self._get_grades_list_item_count() == initial_item_count + i + 1
                )
            except TimeoutException:
                self._take_screenshot(f"{test_name}_timeout_item_{i+1}")
                logger.error(f"Timeout waiting for grade item count to be {initial_item_count + i + 1} after adding item {i+1}.")
                # Optionally re-raise or assert here if this is critical for continuation
            
            # Small pause to ensure UI stability if adding multiple items rapidly
            time.sleep(0.2) 


        current_item_count = self._get_grades_list_item_count()
        logger.info(f"Current grade item count after multiple adds: {current_item_count}")
        self.assertEqual(current_item_count, initial_item_count + len(grades_data),
                         f"Grade item count did not increase correctly. Expected: {initial_item_count + len(grades_data)}, Got: {current_item_count}")
        logger.info(f"Test {test_name} completed successfully.")

    def test_us01_validate_grade_input_below_range(self, request=None):
        test_name = request.node.name if request else self._testMethodName
        logger.info(f"Running test: {test_name}")
        # self._initial_setup() # Removed redundant call, already called by self.setUp()

        initial_item_count = self._get_grades_list_item_count()
        self._add_grade_and_percentage("-1.0", "20") # Invalid grade (below min 0)
        
        # Assuming invalid input does not add a grade item
        current_item_count = self._get_grades_list_item_count()
        self.assertEqual(current_item_count, initial_item_count, 
                         "Grade item count should not change for invalid grade input below range.")
        # Add assertion for error message if visible
        logger.info(f"Test {test_name} completed.")

    def test_us01_validate_grade_input_above_range(self, request=None):
        test_name = request.node.name if request else self._testMethodName
        logger.info(f"Running test: {test_name}")
        # self._initial_setup() # Removed redundant call

        initial_item_count = self._get_grades_list_item_count()
        self._add_grade_and_percentage("8.0", "20") # Invalid grade (above max 7)
        
        current_item_count = self._get_grades_list_item_count()
        self.assertEqual(current_item_count, initial_item_count, 
                         "Grade item count should not change for invalid grade input above range.")
        # Add assertion for error message
        logger.info(f"Test {test_name} completed.")

    def test_us01_validate_percentage_input_negative(self, request=None):
        test_name = request.node.name if request else self._testMethodName
        logger.info(f"Running test: {test_name}")
        # self._initial_setup() # Removed redundant call

        initial_item_count = self._get_grades_list_item_count()
        self._add_grade_and_percentage("4.0", "-10") # Invalid percentage
        
        current_item_count = self._get_grades_list_item_count()
        self.assertEqual(current_item_count, initial_item_count, 
                         "Grade item count should not change for negative percentage input.")
        # Add assertion for error message
        logger.info(f"Test {test_name} completed.")

    def test_us01_validate_percentage_input_non_numeric(self, request=None):
        test_name = request.node.name if request else self._testMethodName
        logger.info(f"Running test: {test_name}")
        # self._initial_setup() # Removed redundant call

        initial_item_count = self._get_grades_list_item_count()
        self._add_grade_and_percentage("4.0", "abc") # Non-numeric percentage
        
        current_item_count = self._get_grades_list_item_count()
        self.assertEqual(current_item_count, initial_item_count, 
                         "Grade item count should not change for non-numeric percentage input.")
        # Add assertion for error message
        logger.info(f"Test {test_name} completed.")

# ... (rest of the file, e.g., if __name__ == '__main__': unittest.main())
if __name__ == '__main__':
    unittest.main(verbosity=2)