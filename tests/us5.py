import unittest
import os
import time
import re # Added for parsing
import logging # Added for logging

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class US05Tests(unittest.TestCase):
    BASE_URL = "http://localhost:3000"
    GRADE_INPUT_SELECTOR = "input.home__input[placeholder='0.0'][type='number']"
    PERCENTAGE_INPUT_SELECTOR = "input.home__input[placeholder='0'][type='number']"
    ADD_GRADE_BUTTON_SELECTOR = "button.home__add-button" # General button to add a new grade entry/row
    GRADES_LIST_ITEM_SELECTOR = "div.home__grades-container > div.home__grade-row"
    CALCULATE_BUTTON_SELECTOR = "button.home__calculate-button"
    
    # Selectors for US05 - specific to the result page
    REQUIRED_GRADE_DISPLAY_SELECTOR = "p.result__card-needed" # For required grade display
    RESULT_PAGE_CONTAINER_SELECTOR = "div.result" 
    FIRST_TIME_ALERT_BUTTON_SELECTOR = ".alert__button.alert__button--single"
    ALERT_OVERLAY_SELECTOR = "div.alert__overlay"
    # Original complex XPath selector
    NAV_BACK_BUTTON_XPATH = "//button[contains(@class, 'nav-bar__button') and .//span[contains(@class, 'back-icon')]/svg[contains(@class, 'lucide-chevron-left')]]"
    # Simpler CSS selector for the back button - targeting the first button in the nav-bar
    NAV_BACK_BUTTON_SELECTOR = "nav.nav-bar > button.nav-bar__button:first-child"
    HOME_CONTAINER_SELECTOR = "div.home__container"
    SETTINGS_NAV_BUTTON_XPATH = "//button[contains(@class, 'nav-bar__button') and .//span[contains(@class, 'settings-icon')]/svg[contains(@class, 'lucide-settings')]]"
    APPROVAL_GRADE_INPUT_SELECTOR = "input.settings__input[type='number']"
    
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
            
    def _set_approval_grade(self, approval_grade_value):
        logger.info(f"Setting approval grade to: {approval_grade_value} using JavaScript injection")
        # Instead of navigating to settings, set the approval grade directly using JavaScript
        # This is more reliable and faster than navigating through the UI
        
        script = f"""
        const settingsManager = {{}};
        settingsManager._minAcceptValue = {approval_grade_value};
        settingsManager._minValue = 0;
        settingsManager._maxValue = 5;
        
        localStorage.setItem('settings', JSON.stringify({{
            minAcceptValue: settingsManager._minAcceptValue,
            minValue: settingsManager._minValue,
            maxValue: settingsManager._maxValue
        }}));
        
        localStorage.setItem("isFirstTime", "false");
        """
        
        # Execute the script to update the settings
        self.driver.execute_script(script)
        logger.info(f"Settings updated via JavaScript. Approval grade set to: {approval_grade_value}")
        
        # Refresh the page to apply the settings
        self.driver.refresh()
        self.wait_long.until(EC.presence_of_element_located((By.CSS_SELECTOR, self.HOME_CONTAINER_SELECTOR)))
        logger.info("Page refreshed after setting approval grade")
    
    def _get_required_grade_or_message(self):
        raw_text = ""
        try:
            # Ensure on result page
            self.wait_long.until(EC.presence_of_element_located((By.CSS_SELECTOR, self.RESULT_PAGE_CONTAINER_SELECTOR)))
            
            display_element = self.wait_long.until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, self.REQUIRED_GRADE_DISPLAY_SELECTOR))
            )
            time.sleep(0.2) # Allow text to stabilize
            raw_text = display_element.text.strip()
            logger.info(f"Raw required grade/message text: '{raw_text}'")

            if not raw_text:
                logger.warning("Required grade/message text is empty.")
                self._take_screenshot("empty_required_grade_message")
                return "Error: Empty Value"

            # Check for specific messages first
            if "No es posible aprobar la materia" in raw_text:
                return "No es posible aprobar" # Standardized message
            if "Ya se ha aprobado la materia" in raw_text:
                return "Ya se ha aprobado la materia"
            
            # Try to parse a grade
            # Example text: "Necesitas un 4.0 en el 50% restante para aprobar la materia con un 3.0"
            match = re.search(r"Necesitas un (\d+\.?\d*|\.\d+) en el", raw_text)
            if match:
                grade_str = match.group(1)
                logger.info(f"Extracted required grade string: '{grade_str}'")
                return float(grade_str)
            else:
                logger.error(f"Could not parse required grade from text: '{raw_text}'")
                self._take_screenshot("required_grade_parse_error")
                return "Error: Parse"
        except TimeoutException:
            logger.error(f"Timeout waiting for required grade display: {self.REQUIRED_GRADE_DISPLAY_SELECTOR}")
            self._take_screenshot("required_grade_timeout")
            return "Error: Timeout"
        except ValueError:
            logger.error(f"Could not convert extracted grade string to float from '{raw_text}'.")
            self._take_screenshot("required_grade_value_error")
            return "Error: Conversion"
        except Exception as e:
            logger.error(f"Error getting required grade/message: {e}", exc_info=True)
            self._take_screenshot("get_required_grade_error")
            return "Error: General"
            
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
            
            # Try CSS selector first, fall back to XPath if needed
            try:
                nav_back_button = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, self.NAV_BACK_BUTTON_SELECTOR))
                )
                logger.info("Found back button using CSS selector.")
            except TimeoutException:
                logger.info("CSS selector failed for back button, trying XPath...")
                nav_back_button = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, self.NAV_BACK_BUTTON_XPATH))
                )
                logger.info("Found back button using XPath selector.")
                
            nav_back_button.click()
            logger.info("Clicked nav back button to return to Home page.")
            
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, self.HOME_CONTAINER_SELECTOR))
            )
            logger.info("Successfully navigated back to the Home page after initial alert.")

        except TimeoutException:
            logger.info("First-time user alert or subsequent navigation elements not found or timed out. Checking if already on Home page.")
            try:
                self.driver.find_element(By.CSS_SELECTOR, self.HOME_CONTAINER_SELECTOR)
                logger.info("Already on the Home page or initial alert was not present.")
            except NoSuchElementException:
                logger.warning(f"Home container '{self.HOME_CONTAINER_SELECTOR}' not found. Attempting to re-navigate to BASE_URL.")
                self.driver.get(self.BASE_URL) 
                try:
                    WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, self.HOME_CONTAINER_SELECTOR))
                    )
                    logger.info("Successfully navigated to Home page as a fallback.")
                except TimeoutException:
                    logger.error("Failed to ensure presence on Home page even after fallback. Current URL: %s", self.driver.current_url)
                    self._take_screenshot("initial_setup_home_fallback_failed")
                    self.fail("Could not ensure presence on the Home page during initial setup.")
        except Exception as e:
            logger.error(f"An unexpected error occurred during initial setup: {e}", exc_info=True)
            self._take_screenshot("initial_setup_error")
            self.fail(f"Unexpected error during initial setup: {e}")
            
        # Ensure approval grade is set to 3.0 (default for tests)
        self._set_approval_grade("3.0")
                
    def _add_grade_and_percentage(self, grade, percentage):
        if not hasattr(self, 'driver') or not self.driver:
            logger.error("Driver not available in _add_grade_and_percentage.")
            self.fail("Driver not available.")
            return

        # First check if we're on the result page and navigate back if needed
        on_result_page = False
        try:
            if self.driver.find_element(By.CSS_SELECTOR, self.RESULT_PAGE_CONTAINER_SELECTOR).is_displayed():
                on_result_page = True
        except NoSuchElementException:
            on_result_page = False

        if on_result_page:
            logger.info("Currently on result page, navigating back to home to add grades.")
            try:
                # First try with the CSS selector
                nav_back_button = self.wait_short.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, self.NAV_BACK_BUTTON_SELECTOR))
                )
                logger.info("Found back button using CSS selector in _add_grade_and_percentage.")
            except TimeoutException:
                try:
                    # Then try with XPath
                    logger.info("CSS selector failed for back button in _add_grade_and_percentage, trying XPath...")
                    nav_back_button = self.wait_long.until(
                        EC.element_to_be_clickable((By.XPATH, self.NAV_BACK_BUTTON_XPATH))
                    )
                    logger.info("Found back button using XPath selector in _add_grade_and_percentage.")
                except TimeoutException:
                    # As a last resort, try to find any buttons in the nav bar
                    logger.info("XPath also failed. Looking for any button in the nav bar...")
                    nav_bar = self.wait_long.until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "nav.nav-bar"))
                    )
                    nav_buttons = nav_bar.find_elements(By.TAG_NAME, "button")
                    if nav_buttons:
                        nav_back_button = nav_buttons[0]  # First button in nav bar is usually back
                        logger.info("Using first button found in nav bar")
                    else:
                        logger.error("No buttons found in nav bar")
                        self._take_screenshot("no_buttons_in_nav_bar_add_grade")
                        self.fail("No buttons found in nav bar when trying to navigate back")
            
            # Click the back button once found
            nav_back_button.click()
            self.wait_long.until(EC.presence_of_element_located((By.CSS_SELECTOR, self.HOME_CONTAINER_SELECTOR)))
            logger.info("Successfully navigated back to home page.")
            
            # Take a small pause to ensure the UI is fully loaded
            time.sleep(0.5)

        # Now we're on the home page
        # Take a screenshot of the current state for debugging
        self._take_screenshot("before_adding_grade")
        
        # Find all grade rows currently in the UI
        grade_rows = self.driver.find_elements(By.CSS_SELECTOR, self.GRADES_LIST_ITEM_SELECTOR)
        logger.info(f"Found {len(grade_rows)} grade rows before adding.")
        
        # First check if we need to add a new row
        need_new_row = True
        if grade_rows:
            # Check if the last row is empty (which means we can use it)
            last_row = grade_rows[-1]
            try:
                grade_input = last_row.find_element(By.CSS_SELECTOR, self.GRADE_INPUT_SELECTOR)
                percentage_input = last_row.find_element(By.CSS_SELECTOR, self.PERCENTAGE_INPUT_SELECTOR)
                
                grade_value = grade_input.get_attribute("value")
                percentage_value = percentage_input.get_attribute("value")
                
                # If both inputs are empty, we can use this row
                if not grade_value and not percentage_value:
                    need_new_row = False
                    logger.info("Found empty row to use for new grade entry.")
            except NoSuchElementException:
                # If we can't find inputs in the last row, we'll add a new one
                logger.warning("Last row doesn't have expected input elements.")
                need_new_row = True
        
        # If we need a new row or there are no rows, add one
        if need_new_row or not grade_rows:
            logger.info("Adding a new grade row...")
            add_button = self.wait_long.until(EC.element_to_be_clickable((By.CSS_SELECTOR, self.ADD_GRADE_BUTTON_SELECTOR)))
            add_button.click()
            time.sleep(0.5)  # Wait for the row to be added
            
            # Refresh the list of grade rows
            grade_rows = self.driver.find_elements(By.CSS_SELECTOR, self.GRADES_LIST_ITEM_SELECTOR)
            if not grade_rows:
                logger.error("Failed to add grade row - no rows found after clicking 'Add' button")
                self._take_screenshot("failed_to_add_grade_row")
                self.fail("Failed to add grade row - no rows found after clicking 'Add' button")
        
        # Now use the last row to add our grade
        last_row = grade_rows[-1]
        logger.info(f"Using the last of {len(grade_rows)} rows to add grade: {grade}, percentage: {percentage}")
        
        try:
            grade_input_element = last_row.find_element(By.CSS_SELECTOR, self.GRADE_INPUT_SELECTOR)
            percentage_input_element = last_row.find_element(By.CSS_SELECTOR, self.PERCENTAGE_INPUT_SELECTOR)
            
            # Clear and enter the grade and percentage
            grade_input_element.clear()
            grade_input_element.send_keys(str(grade))
            percentage_input_element.clear()
            percentage_input_element.send_keys(str(percentage))
            
            # Take screenshot after entering values
            self._take_screenshot(f"after_entering_grade_{grade}_percent_{percentage}")
            
            # Click the add button to confirm this grade
            add_button = self.wait_long.until(EC.element_to_be_clickable((By.CSS_SELECTOR, self.ADD_GRADE_BUTTON_SELECTOR)))
            add_button.click()
            logger.info(f"Clicked 'Add' button after entering grade: {grade}, percentage: {percentage}")
            
            # Allow time for the UI to update
            time.sleep(0.5)
            
            # Verify the grade was added by checking for more rows or for values in the inputs
            new_grade_rows = self.driver.find_elements(By.CSS_SELECTOR, self.GRADES_LIST_ITEM_SELECTOR)
            logger.info(f"After adding: {len(new_grade_rows)} grade rows (previously {len(grade_rows)})")
            
            # Take screenshot after adding grade
            self._take_screenshot("after_adding_grade")
            
        except NoSuchElementException as e:
            logger.error(f"Could not find input elements in the grade row: {e}")
            self._take_screenshot("input_elements_not_found")
            self.fail(f"Input elements not found: {e}")
            return
            
    def _click_calculate_and_wait_for_result_page(self):
        calculate_button = self.wait_long.until(EC.element_to_be_clickable((By.CSS_SELECTOR, self.CALCULATE_BUTTON_SELECTOR)))
        calculate_button.click()
        self.wait_long.until(EC.presence_of_element_located((By.CSS_SELECTOR, self.RESULT_PAGE_CONTAINER_SELECTOR)))
        logger.info("Clicked 'Calcular' and result page container is present.")

    # --- Test Cases for US05 ---

    def test_us05_calculate_required_grade_for_approval(self):
        # Corresponds to Task 5.1
        # Approval grade default 3.0
        # Add grades: Grade: "2.0", Percentage: "50%".
        # Expected: Nota Necesaria = 4.0
        test_name = self._testMethodName
        logger.info(f"Running test: {test_name}")
        try:
            self._add_grade_and_percentage("2.0", "50")
            self._click_calculate_and_wait_for_result_page()
            
            required_grade = self._get_required_grade_or_message()
            self.assertEqual(required_grade, 4.0, f"Test {test_name}: Expected 4.0, got {required_grade}")
            logger.info(f"Test {test_name} passed. Required grade: {required_grade}")

        except AssertionError as e:
            logger.error(f"AssertionError in {test_name}: {e}", exc_info=True)
            self._take_screenshot(f"{test_name}_assertion_error")
            self.fail(f"AssertionError in {test_name}: {e}")
        except Exception as e:
            logger.error(f"Exception in {test_name}: {e}", exc_info=True)
            self._take_screenshot(f"{test_name}_exception")
            self.fail(f"Exception in {test_name}: {e}")

    def test_us05_impossible_to_approve_scenario(self):
        # Corresponds to Task 5.2
        # Approval grade default 3.0
        # Add grades: Grade: "1.0", Percentage: "80%".
        # Expected: "No es posible aprobar"
        test_name = self._testMethodName
        logger.info(f"Running test: {test_name}")
        try:
            self._add_grade_and_percentage("1.0", "80")
            self._click_calculate_and_wait_for_result_page()

            message = self._get_required_grade_or_message()
            self.assertEqual(message, "No es posible aprobar", f"Test {test_name}: Expected 'No es posible aprobar', got '{message}'")
            logger.info(f"Test {test_name} passed. Message: {message}")

        except AssertionError as e:
            logger.error(f"AssertionError in {test_name}: {e}", exc_info=True)
            self._take_screenshot(f"{test_name}_assertion_error")
            self.fail(f"AssertionError in {test_name}: {e}")
        except Exception as e:
            logger.error(f"Exception in {test_name}: {e}", exc_info=True)
            self._take_screenshot(f"{test_name}_exception")
            self.fail(f"Exception in {test_name}: {e}")

    def test_us05_already_approved_scenario(self):
        # Corresponds to Task 5.3
        # Approval grade default 3.0
        # Add grades: Grade: "4.0", Percentage: "80%".
        # Expected: "Ya se ha aprobado la materia"
        test_name = self._testMethodName
        logger.info(f"Running test: {test_name}")
        try:
            self._add_grade_and_percentage("4.0", "80")
            self._click_calculate_and_wait_for_result_page()

            message = self._get_required_grade_or_message()
            self.assertEqual(message, "Ya se ha aprobado la materia", f"Test {test_name}: Expected 'Ya se ha aprobado la materia', got '{message}'")
            logger.info(f"Test {test_name} passed. Message: {message}")

        except AssertionError as e:
            logger.error(f"AssertionError in {test_name}: {e}", exc_info=True)
            self._take_screenshot(f"{test_name}_assertion_error")
            self.fail(f"AssertionError in {test_name}: {e}")
        except Exception as e:
            logger.error(f"Exception in {test_name}: {e}", exc_info=True)
            self._take_screenshot(f"{test_name}_exception")
            self.fail(f"Exception in {test_name}: {e}")

if __name__ == '__main__':
    unittest.main(verbosity=2)
