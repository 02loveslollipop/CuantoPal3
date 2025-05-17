import unittest
import time
import logging
import os

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class HomePageTest(unittest.TestCase):
    BASE_URL = "http://localhost:3000"
    GRADE_INPUT_SELECTOR = "input.home__input[placeholder=\"0.0\"][type=\"number\"]"
    PERCENTAGE_INPUT_SELECTOR = "input.home__input[placeholder=\"0\"][type=\"number\"]"
    ADD_GRADE_BUTTON_SELECTOR = "button.home__add-button"
    GRADES_LIST_ITEM_SELECTOR = "div.home__grades-container > div.home__grade-row"
    CALCULATE_BUTTON_SELECTOR = "button.home__calculate-button"
    FIRST_TIME_ALERT_BUTTON_SELECTOR = ".alert__button.alert__button--single"
    ALERT_OVERLAY_SELECTOR = "div.alert__overlay"
    NAV_BACK_BUTTON_XPATH = "//button[contains(@class, 'nav-bar__button') and .//span[contains(@class, 'back-icon')]/svg[contains(@class, 'lucide-chevron-left')]]"
    HOME_CONTAINER_SELECTOR = "div.home__container"
    DELETE_BUTTON_IN_ROW_SELECTOR = "button.home__delete-button"

    # This method will be called by a pytest fixture or a custom runner
    # to inject the driver and set up waits.
    def set_driver_fixture(self, driver):
        self.driver = driver
        self.wait_short = WebDriverWait(self.driver, 5)
        self.wait_long = WebDriverWait(self.driver, 15)
        if not os.path.exists("screenshots"):
            os.makedirs("screenshots")

    def setUp(self):
        # This setUp is for unittest.TestCase. 
        # If using pytest, the driver fixture in conftest.py handles setup.
        # We need to ensure self.driver is available. 
        # A common pattern is to have a pytest fixture that calls set_driver_fixture.
        # For now, assume self.driver is populated by a fixture before setUp is called.
        if not hasattr(self, 'driver') or not self.driver:
            logger.error("WebDriver not initialized. Ensure a pytest fixture is injecting the driver via set_driver_fixture.")
            # Fallback for direct unittest execution (not ideal with conftest.py)
            # This part should ideally not be needed if tests are run via pytest.
            try:
                from webdriver_manager.chrome import ChromeDriverManager
                from selenium.webdriver.chrome.service import Service as ChromeService
                options = webdriver.ChromeOptions()
                if os.environ.get('GITHUB_ACTIONS') == 'true':
                    options.add_argument('--headless')
                    options.add_argument('--no-sandbox')
                    options.add_argument('--disable-dev-shm-usage')
                options.add_argument('--window-size=1920,1080')
                driver_instance = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
                self.set_driver_fixture(driver_instance) # Use the new method name
                self.is_driver_managed_by_fallback = True # Flag to manage driver lifecycle
            except Exception as e:
                logger.fatal(f"Fallback driver setup failed: {e}")
                raise
        else:
            self.is_driver_managed_by_fallback = False

        self._initial_setup()

    def tearDown(self):
        if hasattr(self, 'is_driver_managed_by_fallback') and self.is_driver_managed_by_fallback:
            if self.driver:
                self.driver.quit()
                logger.info("Fallback driver quit in tearDown.")
        # If pytest manages the driver, its fixture will handle teardown.

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
        if not hasattr(self, 'driver') or not self.driver:
            logger.error("Driver not initialized in _add_grade_and_percentage.")
            self.fail("Driver not initialized for adding grade.")
            return
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

    def _get_grades_list_item_count(self):
        if not hasattr(self, 'driver') or not self.driver:
            logger.error("Driver not initialized in _get_grades_list_item_count.")
            return 0
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

    # US01 Tests - ensure they use self.driver which is set by the fixture via set_driver_fixture

    def test_us01_add_single_valid_grade(self):
        test_name = self._testMethodName
        logger.info(f"Running test: {test_name}")
        
        initial_item_count = self._get_grades_list_item_count()
        logger.info(f"Initial grade item count: {initial_item_count}")

        grade_to_add = "4.5"
        percentage_to_add = "25"
        self._add_grade_and_percentage(grade_to_add, percentage_to_add)

        expected_count_after_add = initial_item_count + 1 # Changed from +2 to +1
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
                             f"Grade item count did not increase by 1. Initial: {initial_item_count}, Expected: {expected_count_after_add}, Current: {current_item_count}")
        except AssertionError as e:
            self._take_screenshot(f"{test_name}_assertion_failed")
            raise e
        logger.info(f"Test {test_name} completed successfully.")


    def test_us01_add_multiple_valid_grades(self):
        test_name = self._testMethodName
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
            expected_count_after_item_add = initial_item_count + (i + 1) # Changed from +2*(i+1) to +(i+1)
            try:
                self.wait_long.until(
                    lambda d: self._get_grades_list_item_count() == expected_count_after_item_add
                )
            except TimeoutException:
                self._take_screenshot(f"{test_name}_timeout_item_{i+1}")
                logger.error(f"Timeout waiting for grade item count to be {expected_count_after_item_add} after adding item {i+1}.")
            
            time.sleep(0.2)

        expected_final_count = initial_item_count + len(grades_data) # Changed from +2*len() to +len()
        current_item_count = self._get_grades_list_item_count()
        logger.info(f"Current grade item count after multiple adds: {current_item_count}")
        try:
            self.assertEqual(current_item_count, expected_final_count,
                             f"Grade item count did not increase correctly. Initial: {initial_item_count}, Expected: {expected_final_count}, Got: {current_item_count}")
        except AssertionError as e:
            self._take_screenshot(f"{test_name}_assertion_failed")
            raise e
        logger.info(f"Test {test_name} completed successfully.")

    def test_us01_validate_grade_input_below_range(self):
        test_name = self._testMethodName
        logger.info(f"Running test: {test_name}")
        initial_item_count = self._get_grades_list_item_count()

        grade_rows = self.driver.find_elements(By.CSS_SELECTOR, self.GRADES_LIST_ITEM_SELECTOR)
        if not grade_rows: 
            self._take_screenshot(f"{test_name}_no_rows_for_invalid_input")
            self.fail("No grade rows found for invalid input test.")
        last_row = grade_rows[-1]
        grade_input_element = last_row.find_element(By.CSS_SELECTOR, self.GRADE_INPUT_SELECTOR)
        percentage_input_element = last_row.find_element(By.CSS_SELECTOR, self.PERCENTAGE_INPUT_SELECTOR)
        
        grade_input_element.clear(); grade_input_element.send_keys("-1.0")
        percentage_input_element.clear(); percentage_input_element.send_keys("20")
        
        add_button = self.wait_long.until(EC.element_to_be_clickable((By.CSS_SELECTOR, self.ADD_GRADE_BUTTON_SELECTOR)))
        add_button.click()
        time.sleep(0.5) # allow for UI update (consider explicit wait for error message or count change)
        
        current_item_count = self._get_grades_list_item_count()
        try:
            # Expectation: if validation is robust, count should NOT change.
            self.assertEqual(current_item_count, initial_item_count, 
                             f"Item count changed after attempting to add invalid grade. Initial: {initial_item_count}, Current: {current_item_count}")
            # TODO: Add assertion for a specific error message if the application displays one.
        except AssertionError as e:
            self._take_screenshot(f"{test_name}_assertion_failed")
            raise e
        logger.info(f"Test {test_name} completed.")

    def test_us01_validate_grade_input_above_range(self):
        test_name = self._testMethodName
        logger.info(f"Running test: {test_name}")
        initial_item_count = self._get_grades_list_item_count()

        grade_rows = self.driver.find_elements(By.CSS_SELECTOR, self.GRADES_LIST_ITEM_SELECTOR)
        if not grade_rows: self.fail("No grade rows for test")
        last_row = grade_rows[-1]
        grade_input_element = last_row.find_element(By.CSS_SELECTOR, self.GRADE_INPUT_SELECTOR)
        percentage_input_element = last_row.find_element(By.CSS_SELECTOR, self.PERCENTAGE_INPUT_SELECTOR)
        grade_input_element.clear(); grade_input_element.send_keys("6.0")
        percentage_input_element.clear(); percentage_input_element.send_keys("20")
        
        add_button = self.wait_long.until(EC.element_to_be_clickable((By.CSS_SELECTOR, self.ADD_GRADE_BUTTON_SELECTOR)))
        add_button.click()
        time.sleep(0.5)

        current_item_count = self._get_grades_list_item_count()
        try:
            self.assertEqual(current_item_count, initial_item_count,
                             f"Item count changed for out-of-range grade. Initial: {initial_item_count}, Current: {current_item_count}")
            # TODO: Add assertion for a specific error message.
        except AssertionError as e:
            self._take_screenshot(f"{test_name}_assertion_failed")
            raise e
        logger.info(f"Test {test_name} completed.")

    def test_us01_validate_percentage_input_negative(self):
        test_name = self._testMethodName
        logger.info(f"Running test: {test_name}")
        initial_item_count = self._get_grades_list_item_count()

        grade_rows = self.driver.find_elements(By.CSS_SELECTOR, self.GRADES_LIST_ITEM_SELECTOR)
        if not grade_rows: self.fail("No grade rows for test")
        last_row = grade_rows[-1]
        grade_input_element = last_row.find_element(By.CSS_SELECTOR, self.GRADE_INPUT_SELECTOR)
        percentage_input_element = last_row.find_element(By.CSS_SELECTOR, self.PERCENTAGE_INPUT_SELECTOR)
        grade_input_element.clear(); grade_input_element.send_keys("3.0")
        percentage_input_element.clear(); percentage_input_element.send_keys("-10")
        
        add_button = self.wait_long.until(EC.element_to_be_clickable((By.CSS_SELECTOR, self.ADD_GRADE_BUTTON_SELECTOR)))
        add_button.click()
        time.sleep(0.5)

        current_item_count = self._get_grades_list_item_count()
        try:
            self.assertEqual(current_item_count, initial_item_count,
                             f"Item count changed for negative percentage. Initial: {initial_item_count}, Current: {current_item_count}")
            # TODO: Add assertion for a specific error message.
        except AssertionError as e:
            self._take_screenshot(f"{test_name}_assertion_failed")
            raise e
        logger.info(f"Test {test_name} completed.")
        
    def test_us01_validate_percentage_input_non_numeric(self):
        test_name = self._testMethodName
        logger.info(f"Running test: {test_name}")
        initial_item_count = self._get_grades_list_item_count()

        grade_rows = self.driver.find_elements(By.CSS_SELECTOR, self.GRADES_LIST_ITEM_SELECTOR)
        if not grade_rows: self.fail("No grade rows for test")
        last_row = grade_rows[-1]
        grade_input_element = last_row.find_element(By.CSS_SELECTOR, self.GRADE_INPUT_SELECTOR)
        percentage_input_element = last_row.find_element(By.CSS_SELECTOR, self.PERCENTAGE_INPUT_SELECTOR)
        grade_input_element.clear(); grade_input_element.send_keys("3.0")
        percentage_input_element.clear(); percentage_input_element.send_keys("abc")
        
        current_percentage_value = percentage_input_element.get_attribute("value")
        logger.info(f"Percentage input value after sending 'abc': '{current_percentage_value}'")

        add_button = self.wait_long.until(EC.element_to_be_clickable((By.CSS_SELECTOR, self.ADD_GRADE_BUTTON_SELECTOR)))
        add_button.click()
        time.sleep(0.5)

        current_item_count = self._get_grades_list_item_count()
        try:
            # If type=\"number\" prevents "abc", value might be empty. App might treat empty as 0 or invalid.
            # Expecting count to not change if "abc" is effectively rejected.
            self.assertEqual(current_item_count, initial_item_count,
                             f"Item count changed for non-numeric percentage. Initial: {initial_item_count}, Current: {current_item_count}")
            # TODO: Add assertion for a specific error message or input state.
        except AssertionError as e:
            self._take_screenshot(f"{test_name}_assertion_failed")
            raise e
        logger.info(f"Test {test_name} completed.")

    # US02: Edición y Eliminación de Calificaciones

    def test_us02_edit_existing_grade_value(self):
        test_name = self._testMethodName
        logger.info(f"Running test: {test_name}")

        self._add_grade_and_percentage("3.0", "20") # Adds one grade, results in 2 rows (1 filled, 1 empty)
        
        initial_item_count = self._get_grades_list_item_count() # Should be 2
        logger.info(f"Initial item count for edit test: {initial_item_count}")

        grade_rows = self.driver.find_elements(By.CSS_SELECTOR, self.GRADES_LIST_ITEM_SELECTOR)
        if not grade_rows:
            self._take_screenshot(f"{test_name}_no_grade_rows_found")
            raise NoSuchElementException("No grade rows found to edit.")
        
        first_row = grade_rows[0] # Target the first (filled) grade row
        
        new_grade_value = "4.5"
        try:
            grade_input_in_first_row = first_row.find_element(By.CSS_SELECTOR, self.GRADE_INPUT_SELECTOR)
            grade_input_in_first_row.clear()
            grade_input_in_first_row.send_keys(new_grade_value)
            # Allow a moment for React to process the change if necessary
            time.sleep(0.5) 
            
            actual_new_grade = grade_input_in_first_row.get_attribute("value")
            self.assertEqual(actual_new_grade, new_grade_value,
                             f"Grade value was not edited correctly. Expected: {new_grade_value}, Got: {actual_new_grade}")

            # Verify row count remains the same
            current_item_count_after_edit = self._get_grades_list_item_count()
            self.assertEqual(current_item_count_after_edit, initial_item_count,
                             f"Row count changed after editing grade. Initial: {initial_item_count}, Current: {current_item_count_after_edit}")

        except NoSuchElementException as e:
            self._take_screenshot(f"{test_name}_element_not_found_for_edit")
            logger.error(f"Element not found during grade edit: {e}")
            raise
        except AssertionError as e:
            self._take_screenshot(f"{test_name}_assertion_failed")
            raise e
        
        logger.info(f"Test {test_name} completed successfully.")

    def test_us02_edit_existing_percentage_value(self):
        test_name = self._testMethodName
        logger.info(f"Running test: {test_name}")

        self._add_grade_and_percentage("3.0", "20") # Adds one grade
        
        initial_item_count = self._get_grades_list_item_count()
        logger.info(f"Initial item count for edit percentage test: {initial_item_count}")

        grade_rows = self.driver.find_elements(By.CSS_SELECTOR, self.GRADES_LIST_ITEM_SELECTOR)
        if not grade_rows:
            self._take_screenshot(f"{test_name}_no_grade_rows_found")
            raise NoSuchElementException("No grade rows found to edit percentage.")
            
        first_row = grade_rows[0]
        
        new_percentage_value = "35"
        try:
            percentage_input_in_first_row = first_row.find_element(By.CSS_SELECTOR, self.PERCENTAGE_INPUT_SELECTOR)
            percentage_input_in_first_row.clear()
            percentage_input_in_first_row.send_keys(new_percentage_value)
            time.sleep(0.5)

            actual_new_percentage = percentage_input_in_first_row.get_attribute("value")
            self.assertEqual(actual_new_percentage, new_percentage_value,
                             f"Percentage value was not edited correctly. Expected: {new_percentage_value}, Got: {actual_new_percentage}")

            current_item_count_after_edit = self._get_grades_list_item_count()
            self.assertEqual(current_item_count_after_edit, initial_item_count,
                             f"Row count changed after editing percentage. Initial: {initial_item_count}, Current: {current_item_count_after_edit}")

        except NoSuchElementException as e:
            self._take_screenshot(f"{test_name}_element_not_found_for_edit")
            logger.error(f"Element not found during percentage edit: {e}")
            raise
        except AssertionError as e:
            self._take_screenshot(f"{test_name}_assertion_failed")
            raise e
            
        logger.info(f"Test {test_name} completed successfully.")

    def test_us02_delete_grade_entry(self):
        test_name = self._testMethodName
        logger.info(f"Running test: {test_name}")

        self._add_grade_and_percentage("3.0", "20")
        self._add_grade_and_percentage("4.0", "30")
        
        initial_item_count = self._get_grades_list_item_count()
        logger.info(f"Initial item count for delete test: {initial_item_count}")
        if initial_item_count < 2: 
             self._take_screenshot(f"{test_name}_not_enough_rows_to_delete")
             self.fail("Not enough rows to perform a delete test. Need at least 1 filled row to delete and observe change.")

        grade_rows = self.driver.find_elements(By.CSS_SELECTOR, self.GRADES_LIST_ITEM_SELECTOR)
        first_row = grade_rows[0]
        expected_count_after_delete = initial_item_count - 1 # Define before try block

        try:
            delete_button_in_first_row = first_row.find_element(By.CSS_SELECTOR, self.DELETE_BUTTON_IN_ROW_SELECTOR)
            delete_button_in_first_row.click()
            
            # Wait for the row count to decrease
            self.wait_long.until(
                lambda d: self._get_grades_list_item_count() == expected_count_after_delete
            )
            
            current_item_count_after_delete = self._get_grades_list_item_count()
            self.assertEqual(current_item_count_after_delete, expected_count_after_delete,
                             f"Grade item count did not decrease by 1 after deletion. Initial: {initial_item_count}, Expected: {expected_count_after_delete}, Current: {current_item_count_after_delete}")

        except NoSuchElementException as e:
            self._take_screenshot(f"{test_name}_delete_button_not_found")
            logger.error(f"Delete button not found in row: {e}")
            raise
        except TimeoutException:
            self._take_screenshot(f"{test_name}_timeout_waiting_for_delete")
            current_item_count = self._get_grades_list_item_count()
            logger.error(f"Timeout waiting for grade item count to decrease after delete. Initial: {initial_item_count}, Expected: {expected_count_after_delete}, Current: {current_item_count}")
            self.fail(f"Timeout waiting for delete. Current count {current_item_count}, expected {expected_count_after_delete}")
        except AssertionError as e:
            self._take_screenshot(f"{test_name}_assertion_failed")
            raise e
            
        logger.info(f"Test {test_name} completed successfully.")

# To run with pytest, ensure conftest.py has a fixture that calls set_driver_fixture:
# Example in conftest.py:
# @pytest.fixture(scope="function")
# def driver_fixture(driver): # 'driver' here is the one from your existing conftest
#     # Find all test classes in the item's module that inherit from unittest.TestCase
#     # and have a set_driver_fixture method.
#     if hasattr(item.instance, "set_driver_fixture"):
# item.instance.set_driver_fixture(driver)
#     yield driver # The original driver fixture continues to manage lifecycle

if __name__ == '__main__':
    # This allows running the test file directly with `python test_home_page.py`
    # It will use the fallback driver setup in setUp.
    unittest.main(verbosity=2)