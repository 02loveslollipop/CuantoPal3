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
    CALCULATE_BUTTON_SELECTOR = "button.home__calculate-button"  # Added
    ALERT_TITLE_SELECTOR = "div.alert__title"  # Added
    ALERT_MESSAGE_SELECTOR = "div.alert__message" # Added
    ALERT_CONFIRM_BUTTON_SELECTOR = "div.alert__actions button.alert__button" # General confirm, can be more specific if needed
    
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

        # Find all grade input rows. The last one is the one we want to fill.
        # If it's the first grade, it's the only row.
        # If we've added one, a new empty row is typically added by the app, so we target that.
        
        # Click "Agregar nota" first to ensure a new empty row is available if needed,
        # or to use the existing one if it's the first entry.
        # This logic might need adjustment based on how `handleAddGrade` in home.jsx works.
        # For now, assume we always fill the *last* available input row.
        
        # If it's not the first grade being added in the test sequence, click "Agregar nota"
        # to generate a new row for this entry.
        # This assumes that _add_grade_and_percentage is called for each new grade entry
        # and the app adds a new row template upon clicking "Agregar nota" *after* filling the previous.
        
        # Let's refine: The "Agregar nota" button adds a new *blank* row.
        # We should fill the *current last* row's inputs, then click "Agregar nota"
        # if we intend to add *another* one after this.
        # The current _add_grade_and_percentage is designed to fill inputs and then click "Agregar nota".
        # This implies "Agregar nota" serves dual purpose: commit current and prepare next.
        # This seems to be the behavior from US01/US02.

        grade_rows = self.driver.find_elements(By.CSS_SELECTOR, self.GRADES_LIST_ITEM_SELECTOR)
        if not grade_rows:
            logger.error("No grade rows found to add grade and percentage.")
            self._take_screenshot("no_grade_rows_found")
            self.fail("No grade rows found.")
            return

        last_row = grade_rows[-1] # Target the last row for input
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
        
        # The "Agregar nota" button is outside the rows, so it's found globally.
        add_button = self.wait_long.until(EC.element_to_be_clickable((By.CSS_SELECTOR, self.ADD_GRADE_BUTTON_SELECTOR)))

        grade_input_element.clear()
        grade_input_element.send_keys(str(grade))
        percentage_input_element.clear()
        percentage_input_element.send_keys(str(percentage))
        
        # Click "Agregar nota" AFTER filling the inputs.
        # This should add the current grade and potentially prepare a new row.
        add_button.click() 
        logger.info(f"Clicked \'Agregar nota\' after filling grade: {grade}, percentage: {percentage} into the last available row.")
        
        # Wait for UI to update, e.g., for a new row to be added if that's the behavior.
        # A more robust wait would be for the number of rows to change or for a specific element to appear.
        time.sleep(0.5) # Small delay for React state updates

    # US03: Verify alert for percentage sum > 100%
    def test_us03_verify_percentage_sum_alert(self):
        test_name = self._testMethodName
        logger.info(f"Running test: {test_name}")

        try:
            # 1. Add grades with percentages summing > 100%
            logger.info("Adding first grade (70%).")
            self._add_grade_and_percentage("3.0", "70")
            
            # The previous _add_grade_and_percentage clicks "Agregar nota",
            # which should make a new row available for the next grade.
            logger.info("Adding second grade (40%). Total percentage should be 110%.")
            self._add_grade_and_percentage("4.0", "40")
            # After this, we should have two rows with data, and possibly a third empty template row.

            # 2. Click "Calcular" button
            logger.info(f"Clicking \'Calcular\' button with selector: {self.CALCULATE_BUTTON_SELECTOR}")
            calculate_button = self.wait_long.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, self.CALCULATE_BUTTON_SELECTOR))
            )
            calculate_button.click()
            logger.info("\'Calcular\' button clicked.")

            # 3. Verify the alert is displayed with correct title and message
            logger.info("Verifying alert for percentage sum > 100%.")
            
            alert_title_element = self.wait_long.until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, self.ALERT_TITLE_SELECTOR))
            )
            alert_title_text = alert_title_element.text
            expected_title = "La suma de los porcentajes es mayor al 100%"
            self.assertEqual(alert_title_text, expected_title,
                             f"Alert title expected \'{expected_title}\', but got \'{alert_title_text}\'")
            logger.info(f"Alert title is correct: \'{alert_title_text}\'")

            alert_message_element = self.wait_long.until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, self.ALERT_MESSAGE_SELECTOR))
            )
            alert_message_text = alert_message_element.text
            expected_message = "Por favor verifica los porcentajes de las notas ingresadas, para que la suma sea menor o igual a 100%."
            self.assertEqual(alert_message_text, expected_message,
                             f"Alert message expected \'{expected_message}\', but got \'{alert_message_text}\'")
            logger.info(f"Alert message is correct: \'{alert_message_text}\'")

            # 4. Close the alert
            alert_confirm_button = self.wait_long.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, self.ALERT_CONFIRM_BUTTON_SELECTOR))
            )
            # Based on alert.jsx, if showCancel is false (which it is for this alert),
            # the confirm button will have 'alert__button--single'
            # We can use a more general selector for the button within alert__actions
            alert_confirm_button.click()
            logger.info("Alert confirm button clicked.")

            # Verify alert is closed
            WebDriverWait(self.driver, 5).until(
                EC.invisibility_of_element_located((By.CSS_SELECTOR, self.ALERT_OVERLAY_SELECTOR))
            )
            logger.info("Alert successfully closed.")

        except AssertionError as e:
            logger.error(f"AssertionError in {test_name}: {e}")
            self._take_screenshot(f"{test_name}_assertion_failure")
            raise
        except Exception as e:
            logger.error(f"An unexpected error occurred in {test_name}: {e}")
            self._take_screenshot(f"{test_name}_unexpected_error")
            raise

        logger.info(f"Test {test_name} completed successfully.")

if __name__ == '__main__':
    # This allows running the test file directly with `python us3.py`
    # For more comprehensive test runs, use pytest.
    unittest.main(verbosity=2)
