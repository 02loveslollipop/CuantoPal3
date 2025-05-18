\
import unittest
import os
import time
import re
import logging

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
    ADD_GRADE_BUTTON_SELECTOR = "button.home__add-button"
    GRADES_LIST_ITEM_SELECTOR = "div.home__grades-container > div.home__grade-row"
    CALCULATE_BUTTON_SELECTOR = "button.home__calculate-button"
    
    # Selectors for US05 - specific to the result page
    REQUIRED_GRADE_DISPLAY_SELECTOR = "p.result__card-needed" # Hypothetical, needs verification
    # For "impossible to approve" or "already approved" messages, it might be the same element
    # or a different status message area. Assuming it's the same for now.
    
    RESULT_PAGE_CONTAINER_SELECTOR = "div.result"
    FIRST_TIME_ALERT_BUTTON_SELECTOR = ".alert__button.alert__button--single"
    ALERT_OVERLAY_SELECTOR = "div.alert__overlay"
    NAV_BACK_BUTTON_XPATH = "//button[contains(@class, 'nav-bar__button') and .//span[contains(@class, 'back-icon')]/svg[contains(@class, 'lucide-chevron-left')]]"
    HOME_CONTAINER_SELECTOR = "div.home__container"
    SETTINGS_NAV_BUTTON_XPATH = "//button[contains(@class, 'nav-bar__button') and .//span[contains(@class, 'settings-icon')]/svg[contains(@class, 'lucide-settings')]]"
    APPROVAL_GRADE_INPUT_SELECTOR = "input.settings__input[type='number']" # Hypothetical for settings page

    def set_driver_fixture(self, driver):
        self.driver = driver
        self.wait_short = WebDriverWait(self.driver, 5)
        self.wait_long = WebDriverWait(self.driver, 15)
        if not os.path.exists("screenshots"):
            os.makedirs("screenshots")

    def setUp(self):
        if not hasattr(self, 'driver') or not self.driver:
            logger.info("WebDriver not set by fixture, attempting fallback setup for direct unittest execution.")
            try:
                options = webdriver.ChromeOptions()
                # options.add_argument('--headless')
                # options.add_argument('--disable-gpu')
                # options.add_argument('--window-size=1920,1080')
                self.driver = webdriver.Chrome(options=options)
                self.is_driver_managed_by_fallback = True
            except Exception as e:
                logger.error(f"Failed to initialize fallback WebDriver: {e}")
                self.fail(f"Failed to initialize fallback WebDriver: {e}")
        else:
            self.is_driver_managed_by_fallback = False
        
        if hasattr(self, 'driver') and self.driver:
            self.set_driver_fixture(self.driver)
        else:
            logger.error("Driver is not initialized after setup attempt.")
            self.fail("Driver could not be initialized.")
            return
        self._initial_setup()

    def tearDown(self):
        if hasattr(self, 'is_driver_managed_by_fallback') and self.is_driver_managed_by_fallback:
            if self.driver:
                self.driver.quit()
        # For pytest-managed driver, teardown is handled by the fixture

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
        self.driver.get(self.BASE_URL)
        logger.info(f"Navigated to base URL: {self.BASE_URL}")
        try:
            alert_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, self.FIRST_TIME_ALERT_BUTTON_SELECTOR))
            )
            alert_button.click()
            WebDriverWait(self.driver, 5).until(
                EC.invisibility_of_element_located((By.CSS_SELECTOR, self.ALERT_OVERLAY_SELECTOR))
            )
            nav_back_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, self.NAV_BACK_BUTTON_XPATH))
            )
            nav_back_button.click()
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, self.HOME_CONTAINER_SELECTOR))
            )
            logger.info("Successfully navigated back to the Home page after initial alert.")
        except TimeoutException:
            logger.info("First-time user alert or subsequent navigation elements not found. Assuming already on Home page or alert handled.")
            try:
                self.wait_long.until(EC.presence_of_element_located((By.CSS_SELECTOR, self.HOME_CONTAINER_SELECTOR)))
                logger.info("Confirmed on Home page.")
            except TimeoutException:
                logger.error(f"Failed to ensure presence on Home page. Current URL: {self.driver.current_url}")
                self._take_screenshot("initial_setup_home_fallback_failed")
                self.fail("Could not ensure presence on the Home page during initial setup.")
        except Exception as e:
            logger.error(f"An unexpected error occurred during initial setup: {e}", exc_info=True)
            self._take_screenshot("initial_setup_error")
            self.fail(f"Unexpected error during initial setup: {e}")
        
        # Ensure approval grade is 3.0 (default)
        self._set_approval_grade("3.0")


    def _set_approval_grade(self, approval_grade_value):
        logger.info(f"Setting approval grade to: {approval_grade_value}")
        # Navigate to settings if not already there or on home
        current_url = self.driver.current_url
        on_settings_page = False
        try:
            if self.driver.find_element(By.CSS_SELECTOR, self.APPROVAL_GRADE_INPUT_SELECTOR).is_displayed():
                on_settings_page = True
        except NoSuchElementException: # Not on settings
            pass
        
        if not on_settings_page:
            # If on result page, go back home first
            try:
                if self.driver.find_element(By.CSS_SELECTOR, self.RESULT_PAGE_CONTAINER_SELECTOR).is_displayed():
                    self.driver.find_element(By.XPATH, self.NAV_BACK_BUTTON_XPATH).click()
                    self.wait_long.until(EC.presence_of_element_located((By.CSS_SELECTOR, self.HOME_CONTAINER_SELECTOR)))
            except NoSuchElementException:
                pass # Not on result page, or already home

            # Now on home (or was already), navigate to settings
            self.wait_long.until(EC.element_to_be_clickable((By.XPATH, self.SETTINGS_NAV_BUTTON_XPATH))).click()
            self.wait_long.until(EC.presence_of_element_located((By.CSS_SELECTOR, self.APPROVAL_GRADE_INPUT_SELECTOR)))
            logger.info("Navigated to Settings page.")

        approval_input = self.wait_long.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.APPROVAL_GRADE_INPUT_SELECTOR)))
        approval_input.clear()
        approval_input.send_keys(str(approval_grade_value))
        logger.info(f"Set approval grade input to {approval_grade_value}.")
        
        # Navigate back to Home page
        self.driver.find_element(By.XPATH, self.NAV_BACK_BUTTON_XPATH).click()
        self.wait_long.until(EC.presence_of_element_located((By.CSS_SELECTOR, self.HOME_CONTAINER_SELECTOR)))
        logger.info("Navigated back to Home page from Settings.")


    def _add_grade_and_percentage(self, grade, percentage):
        on_result_page = False
        try:
            if self.driver.find_element(By.CSS_SELECTOR, self.RESULT_PAGE_CONTAINER_SELECTOR).is_displayed():
                on_result_page = True
        except NoSuchElementException:
            on_result_page = False

        if on_result_page:
            logger.info("On result page, navigating back to home to add grades.")
            self.driver.find_element(By.XPATH, self.NAV_BACK_BUTTON_XPATH).click()
            self.wait_long.until(EC.presence_of_element_located((By.CSS_SELECTOR, self.HOME_CONTAINER_SELECTOR)))

        grade_rows = self.driver.find_elements(By.CSS_SELECTOR, self.GRADES_LIST_ITEM_SELECTOR)
        if not grade_rows:
            self.driver.find_element(By.CSS_SELECTOR, self.ADD_GRADE_BUTTON_SELECTOR).click()
            time.sleep(0.5) 
            grade_rows = self.driver.find_elements(By.CSS_SELECTOR, self.GRADES_LIST_ITEM_SELECTOR)
            if not grade_rows: self.fail("Failed to add initial grade row.")

        last_row = grade_rows[-1]
        grade_input_element = last_row.find_element(By.CSS_SELECTOR, self.GRADE_INPUT_SELECTOR)
        percentage_input_element = last_row.find_element(By.CSS_SELECTOR, self.PERCENTAGE_INPUT_SELECTOR)
        
        grade_input_element.clear()
        grade_input_element.send_keys(str(grade))
        percentage_input_element.clear()
        percentage_input_element.send_keys(str(percentage))
        
        self.driver.find_element(By.CSS_SELECTOR, self.ADD_GRADE_BUTTON_SELECTOR).click()
        time.sleep(0.5)
        logger.info(f"Added grade: {grade}, percentage: {percentage}.")

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
