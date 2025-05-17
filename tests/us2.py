# filepath: c:\Users\Katana GF66 11UC\Documents\cp3\CuantoPal3\tests\us2.py
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

class US02Tests(unittest.TestCase):
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
                from webdriver_manager.chrome import ChromeDriverManager
                from selenium.webdriver.chrome.service import Service as ChromeService
                options = webdriver.ChromeOptions()
                if os.environ.get('GITHUB_ACTIONS') == 'true':
                    options.add_argument('--headless')
                    options.add_argument('--no-sandbox')
                    options.add_argument('--disable-dev-shm-usage')
                options.add_argument('--window-size=1920,1080')
                driver_instance = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
                self.set_driver_fixture(driver_instance)
                self.is_driver_managed_by_fallback = True
                logger.info("Fallback WebDriver initialized successfully.")
            except Exception as e:
                logger.fatal(f"Fallback driver setup failed: {e}")
                raise
        else:
            logger.info("WebDriver already set, likely by a pytest fixture.")
            self.is_driver_managed_by_fallback = False
        self._initial_setup()

    def tearDown(self):
        if hasattr(self, 'is_driver_managed_by_fallback') and self.is_driver_managed_by_fallback:
            if self.driver:
                self.driver.quit()
                logger.info("Fallback driver quit in tearDown.")
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

            try:
                logger.info("Attempting to navigate back from Settings to Home using nav-bar back button.")
                nav_back_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, self.NAV_BACK_BUTTON_XPATH))
                )
                nav_back_button.click()
                logger.info("Clicked navigation bar 'Atras' button.")
                
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, self.HOME_CONTAINER_SELECTOR))
                )
                logger.info(f"Successfully navigated back to Home page (found '{self.HOME_CONTAINER_SELECTOR}').")
            except Exception as nav_exc:
                logger.error(f"Navigation back to Home page failed: {nav_exc}. Attempting recovery.")
                self._take_screenshot("error_nav_back_failed_recovery_attempt")
                self.driver.get(self.BASE_URL)
                logger.info(f"Recovery: Navigated back to base URL: {self.BASE_URL}")
                try:
                    alert_button_recovery = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, self.FIRST_TIME_ALERT_BUTTON_SELECTOR))
                    )
                    alert_button_recovery.click()
                    logger.info("Recovery: Clicked first-time alert button again.")
                    WebDriverWait(self.driver, 5).until(
                        EC.invisibility_of_element_located((By.CSS_SELECTOR, self.ALERT_OVERLAY_SELECTOR))
                    )
                    logger.info("Recovery: Alert overlay is no longer visible after second attempt.")
                except TimeoutException:
                    logger.info("Recovery: First-time alert button not found on second attempt. Assuming Home page or non-first-time state.")
                except Exception as recovery_alert_exc:
                    logger.warning(f"Recovery: Error clicking alert button on second attempt: {recovery_alert_exc}")
        except TimeoutException:
            logger.info(f"First-time alert (button '{self.FIRST_TIME_ALERT_BUTTON_SELECTOR}') not found. Assuming not first time or alert already dismissed.")
        except Exception as e:
            logger.warning(f"An unexpected error occurred during initial alert handling phase: {e}")
            self._take_screenshot("error_initial_alert_phase")

        try:
            WebDriverWait(self.driver, 15).until(
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

        grade_rows = self.driver.find_elements(By.CSS_SELECTOR, self.GRADES_LIST_ITEM_SELECTOR)
        if not grade_rows:
            logger.error("Could not find any grade rows (selector: %s).", self.GRADES_LIST_ITEM_SELECTOR)
            self._take_screenshot("error_add_grade_no_rows")
            raise NoSuchElementException(f"No grade rows found with selector '{self.GRADES_LIST_ITEM_SELECTOR}'.")

        last_row = grade_rows[-1]
        logger.info(f"Targeting the last of {len(grade_rows)} grade rows for input.")

        try:
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
        
        add_button.click() 
        logger.info(f"Clicked 'Agregar nota' after attempting to add grade: {grade}, percentage: {percentage} to the last row.")
        # It's important to wait for the UI to reflect the new row addition if counts are checked immediately after.
        # The application adds one row on input change and another on button click.
        # We expect initial_rows + 2 after this method completes successfully from a state of filled rows.
        time.sleep(0.5) # A small delay for UI updates. Consider more robust waits if this proves flaky.

    def _get_grades_list_item_count(self):
        if not hasattr(self, 'driver') or not self.driver:
            logger.error("Driver not initialized in _get_grades_list_item_count.")
            return 0
        try:
            time.sleep(0.5) # Brief pause to allow UI to settle before counting.
            grade_items = self.driver.find_elements(By.CSS_SELECTOR, self.GRADES_LIST_ITEM_SELECTOR)
            logger.info(f"Found {len(grade_items)} grade list items using selector '{self.GRADES_LIST_ITEM_SELECTOR}'.")
            return len(grade_items)
        except Exception as e:
            logger.error(f"Error finding grade list items with selector '{self.GRADES_LIST_ITEM_SELECTOR}': {e}")
            self._take_screenshot("error_get_grades_list_item_count")
            return 0

    # US02: Edición y Eliminación de Calificaciones
    def test_us02_edit_existing_grade_value(self):
        test_name = self._testMethodName
        logger.info(f"Running test: {test_name}")

        # Add an initial grade. Expect initial_count + 2 rows after this.
        self._add_grade_and_percentage("3.0", "20") 
        
        initial_item_count_for_edit = self._get_grades_list_item_count()
        logger.info(f"Item count after initial add for edit test: {initial_item_count_for_edit}")

        grade_rows = self.driver.find_elements(By.CSS_SELECTOR, self.GRADES_LIST_ITEM_SELECTOR)
        if not grade_rows:
            self._take_screenshot(f"{test_name}_no_grade_rows_found_for_edit")
            self.fail("No grade rows found to perform edit.")
        
        # Target the first row, which should contain the grade we just added.
        first_filled_row = grade_rows[0]
        
        new_grade_value = "4.5"
        try:
            grade_input_in_first_row = first_filled_row.find_element(By.CSS_SELECTOR, self.GRADE_INPUT_SELECTOR)
            grade_input_in_first_row.clear()
            grade_input_in_first_row.send_keys(new_grade_value)
            time.sleep(0.5) # Allow React to process the change.
            
            actual_new_grade = grade_input_in_first_row.get_attribute("value")
            self.assertEqual(actual_new_grade, new_grade_value,
                             f"Grade value was not edited correctly. Expected: {new_grade_value}, Got: {actual_new_grade}")

            # Verify row count remains the same after editing a value within a row.
            current_item_count_after_edit = self._get_grades_list_item_count()
            self.assertEqual(current_item_count_after_edit, initial_item_count_for_edit,
                             f"Row count changed after editing grade. Initial: {initial_item_count_for_edit}, Current: {current_item_count_after_edit}")
        except NoSuchElementException as e:
            self._take_screenshot(f"{test_name}_element_not_found_for_edit")
            logger.error(f"Element not found during grade edit: {e}")
            raise
        except AssertionError as e:
            self._take_screenshot(f"{test_name}_assertion_failed_edit_grade")
            raise e
        logger.info(f"Test {test_name} completed successfully.")

    def test_us02_edit_existing_percentage_value(self):
        test_name = self._testMethodName
        logger.info(f"Running test: {test_name}")

        self._add_grade_and_percentage("3.0", "20")
        initial_item_count_for_edit = self._get_grades_list_item_count()
        logger.info(f"Item count after initial add for edit percentage test: {initial_item_count_for_edit}")

        grade_rows = self.driver.find_elements(By.CSS_SELECTOR, self.GRADES_LIST_ITEM_SELECTOR)
        if not grade_rows:
            self._take_screenshot(f"{test_name}_no_grade_rows_found_for_edit_percentage")
            self.fail("No grade rows found to perform percentage edit.")
            
        first_filled_row = grade_rows[0]
        
        new_percentage_value = "35"
        try:
            percentage_input_in_first_row = first_filled_row.find_element(By.CSS_SELECTOR, self.PERCENTAGE_INPUT_SELECTOR)
            percentage_input_in_first_row.clear()
            percentage_input_in_first_row.send_keys(new_percentage_value)
            time.sleep(0.5)

            actual_new_percentage = percentage_input_in_first_row.get_attribute("value")
            self.assertEqual(actual_new_percentage, new_percentage_value,
                             f"Percentage value was not edited correctly. Expected: {new_percentage_value}, Got: {actual_new_percentage}")

            current_item_count_after_edit = self._get_grades_list_item_count()
            self.assertEqual(current_item_count_after_edit, initial_item_count_for_edit,
                             f"Row count changed after editing percentage. Initial: {initial_item_count_for_edit}, Current: {current_item_count_after_edit}")
        except NoSuchElementException as e:
            self._take_screenshot(f"{test_name}_element_not_found_for_edit_percentage")
            logger.error(f"Element not found during percentage edit: {e}")
            raise
        except AssertionError as e:
            self._take_screenshot(f"{test_name}_assertion_failed_edit_percentage")
            raise e
        logger.info(f"Test {test_name} completed successfully.")

    def test_us02_delete_grade_entry(self):
        test_name = self._testMethodName
        logger.info(f"Running test: {test_name}")

        # Add two grades to ensure there's something to delete and something remaining.
        # If initial state has 1 row:
        # After 1st add: 1 + 2 = 3 rows
        # After 2nd add (to the 2nd row, which was previously empty): 3 + 2 = 5 rows (incorrect logic here, see below)
        # Corrected logic for _add_grade_and_percentage: it targets the *last* row for input.
        # If initial state has 1 row (empty):
        # 1. _add_grade_and_percentage("3.0", "20"):
        #    - Inputs into row 1. Row 1 becomes filled. handleChange adds row 2 (empty). Total = 2.
        #    - Clicks "Add Grade". handleAddGrade adds row 3 (empty). Total = 3. [F, E, E]
        # 2. _add_grade_and_percentage("4.0", "30"):
        #    - Targets last row (row 3, index 2). Inputs into row 3. Row 3 becomes filled. handleChange adds row 4 (empty). Total = 4. [F, E, F, E]
        #    - Clicks "Add Grade". handleAddGrade adds row 5 (empty). Total = 5. [F, E, F, E, E]
        # This interpretation of +2 per call seems to be what was discussed.

        self._add_grade_and_percentage("3.0", "20") 
        self._add_grade_and_percentage("4.0", "30") 
        
        initial_item_count_before_delete = self._get_grades_list_item_count()
        logger.info(f"Item count after adding two grades for delete test: {initial_item_count_before_delete}")

        grade_rows_before_delete = self.driver.find_elements(By.CSS_SELECTOR, self.GRADES_LIST_ITEM_SELECTOR)
        # We need at least one deletable row that contains data, and preferably more than one row to see a change.
        # If we added two grades, we should have at least two rows with data (the first two in the list of rows).
        if not grade_rows_before_delete or len(grade_rows_before_delete) < 2: 
             self._take_screenshot(f"{test_name}_not_enough_rows_to_delete")
             self.fail(f"Not enough grade rows to perform delete test. Found: {len(grade_rows_before_delete)}, Expected at least 2 data rows.")

        # We will delete the first grade entry (the one in grade_rows_before_delete[0])
        first_row_to_delete = grade_rows_before_delete[0]
        try:
            delete_button = first_row_to_delete.find_element(By.CSS_SELECTOR, self.DELETE_BUTTON_IN_ROW_SELECTOR)
            WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(delete_button))
            delete_button.click()
            logger.info("Clicked delete button for the first grade entry.")
            
            # Deleting one row should decrease the total count by 1.
            expected_count_after_delete = initial_item_count_before_delete - 1
            
            try:
                self.wait_long.until(
                    lambda d: self._get_grades_list_item_count() == expected_count_after_delete
                )
            except TimeoutException:
                current_count = self._get_grades_list_item_count()
                self._take_screenshot(f"{test_name}_timeout_waiting_for_delete")
                logger.error(f"Timeout waiting for grade item count to become {expected_count_after_delete} after delete. Current count: {current_count}")
                # Re-raise or assert here to ensure test fails if wait times out
                self.fail(f"Timeout waiting for delete. Expected {expected_count_after_delete}, got {current_count}")
            
            current_item_count_after_delete = self._get_grades_list_item_count()
            self.assertEqual(current_item_count_after_delete, expected_count_after_delete,
                             f"Grade item count did not decrease by 1 after delete. Initial: {initial_item_count_before_delete}, Expected: {expected_count_after_delete}, Current: {current_item_count_after_delete}")

        except NoSuchElementException:
            self._take_screenshot(f"{test_name}_delete_button_not_found")
            logger.error(f"Delete button not found in the first grade row using selector '{self.DELETE_BUTTON_IN_ROW_SELECTOR}'.")
            raise
        except TimeoutException: # For the delete button clickability
            self._take_screenshot(f"{test_name}_delete_button_not_clickable")
            logger.error("Timeout waiting for delete button to be clickable.")
            raise
        except AssertionError as e:
            self._take_screenshot(f"{test_name}_assertion_failed_delete")
            raise e
        logger.info(f"Test {test_name} completed successfully.")

if __name__ == '__main__':
    unittest.main(verbosity=2)
