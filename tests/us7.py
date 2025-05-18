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

class US07Tests(unittest.TestCase):
    BASE_URL = "http://localhost:3000"
    GRADE_INPUT_SELECTOR = "input.home__input[placeholder='0.0'][type='number']"
    PERCENTAGE_INPUT_SELECTOR = "input.home__input[placeholder='0'][type='number']"
    ADD_GRADE_BUTTON_SELECTOR = "button.home__add-button"
    GRADES_LIST_CONTAINER_SELECTOR = "div.home__grades-container" # Container for all grade rows
    GRADES_LIST_ITEM_SELECTOR = "div.home__grades-container > div.home__grade-row" # Individual grade row
    CALCULATE_BUTTON_SELECTOR = "button.home__calculate-button"
    
    RESULT_PAGE_CONTAINER_SELECTOR = "div.result" 
    FIRST_TIME_ALERT_BUTTON_SELECTOR = ".alert__button.alert__button--single"
    ALERT_OVERLAY_SELECTOR = "div.alert__overlay"
    NAV_BACK_BUTTON_XPATH = "//button[contains(@class, 'nav-bar__button') and .//span[contains(@class, 'back-icon')]/svg[contains(@class, 'lucide-chevron-left')]]"
    NAV_BACK_BUTTON_SELECTOR = "nav.nav-bar > button.nav-bar__button:first-child"
    HOME_CONTAINER_SELECTOR = "div.home__container"

    # Selectors for results verification (from US4, US5, US6)
    CURRENT_AVERAGE_DISPLAY_SELECTOR = "p.result__card-current"
    REQUIRED_GRADE_DISPLAY_SELECTOR = "p.result__card-needed"
    FINAL_STATUS_DISPLAY_SELECTOR = "p.result__card-final" # Updated for consistency

    # Placeholder for reset button - User Story 07
    # The selenium-test-dev.md does not specify a selector. Common patterns: id="reset-button", text "Reiniciar", type="reset"
    RESET_BUTTON_SELECTOR = "button[aria-label='Reiniciar formulario de notas']" # Using aria-label

    # Selectors needed for setting up scenarios (from US05, though not directly tested here)
    SETTINGS_NAV_BUTTON_XPATH = "//button[contains(@class, 'nav-bar__button') and .//span[contains(@class, 'settings-icon')]/svg[contains(@class, 'lucide-settings')]]"
    APPROVAL_GRADE_INPUT_SELECTOR = "input.settings__input[type='number']"


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
                self.driver = webdriver.Chrome(options=options)
                self.set_driver_fixture(self.driver)
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

    def _set_approval_grade(self, approval_grade_value): # From US05, potentially useful for consistent setup
        logger.info(f"Setting approval grade to: {approval_grade_value} using JavaScript injection")
        script = f"""
        localStorage.setItem('settings', JSON.stringify({{
            minAcceptValue: parseFloat({approval_grade_value}),
            minValue: 0,
            maxValue: 5
        }}));
        localStorage.setItem("isFirstTime", "false");
        """
        self.driver.execute_script(script)
        logger.info(f"Settings updated via JavaScript. Approval grade set to: {approval_grade_value}")
        self.driver.refresh()
        self.wait_long.until(EC.presence_of_element_located((By.CSS_SELECTOR, self.HOME_CONTAINER_SELECTOR)))
        logger.info("Page refreshed after setting approval grade")
    
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
            
        self._set_approval_grade("3.0") # Default approval grade for tests
                
    def _add_grade_and_percentage(self, grade, percentage):
        # Simplified version for adding one grade at a time.
        # Assumes we are on the home page.
        if not hasattr(self, 'driver') or not self.driver:
            logger.error("Driver not available in _add_grade_and_percentage.")
            self.fail("Driver not available.")
            return

        # Ensure on home page
        try:
            self.wait_long.until(EC.presence_of_element_located((By.CSS_SELECTOR, self.HOME_CONTAINER_SELECTOR)))
        except TimeoutException:
            logger.error("Not on home page when trying to add grade.")
            self._take_screenshot("add_grade_not_on_home")
            self.fail("Not on home page for _add_grade_and_percentage")


        grade_rows = self.driver.find_elements(By.CSS_SELECTOR, self.GRADES_LIST_ITEM_SELECTOR)
        logger.info(f"Found {len(grade_rows)} grade rows before potentially adding new one for input.")
        
        target_row = None
        if grade_rows:
            last_row = grade_rows[-1]
            try:
                # Check if last row is empty and can be used
                grade_input_in_last_row = last_row.find_element(By.CSS_SELECTOR, self.GRADE_INPUT_SELECTOR)
                perc_input_in_last_row = last_row.find_element(By.CSS_SELECTOR, self.PERCENTAGE_INPUT_SELECTOR)
                if not grade_input_in_last_row.get_attribute("value") and not perc_input_in_last_row.get_attribute("value"):
                    target_row = last_row
                    logger.info("Using existing empty last row for input.")
                else:
                    logger.info("Last row is not empty. A new row will be implicitly created by React or by clicking add button first.")
            except NoSuchElementException:
                logger.info("Could not find input fields in the last row, assuming it's not a standard input row or new row needed.")

        if not target_row:
            # If no suitable empty last row, click add button to ensure a fresh row is available if necessary
            # The application's React logic might add a row automatically on input to the last row,
            # but clicking "Add Grade" button explicitly ensures a new row if the current last one is filled.
            pass # We will target the last row's inputs directly.

        # Re-fetch rows in case clicking "Add Grade" was done (though removed from this simplified version)
        grade_rows = self.driver.find_elements(By.CSS_SELECTOR, self.GRADES_LIST_ITEM_SELECTOR)
        if not grade_rows:
            # This case should ideally be handled by the app providing an initial row or test clicking add first
            logger.error("No grade rows found to input grade and percentage.")
            self._take_screenshot("no_grade_rows_for_input")
            self.fail("No grade rows available to input data.")
            return
            
        target_row_for_input = grade_rows[-1] # Always target the last row for new input

        try:
            grade_input_element = target_row_for_input.find_element(By.CSS_SELECTOR, self.GRADE_INPUT_SELECTOR)
            percentage_input_element = target_row_for_input.find_element(By.CSS_SELECTOR, self.PERCENTAGE_INPUT_SELECTOR)
            
            grade_input_element.clear()
            grade_input_element.send_keys(str(grade))
            percentage_input_element.clear()
            percentage_input_element.send_keys(str(percentage))
            logger.info(f"Entered Grade: {grade}, Percentage: {percentage} into the last row.")
            
            # Click the main "Add Grade" button to submit this entry and add a new template row
            add_button_main = self.wait_long.until(EC.element_to_be_clickable((By.CSS_SELECTOR, self.ADD_GRADE_BUTTON_SELECTOR)))
            add_button_main.click()
            logger.info(f"Clicked main 'Add Grade' button to confirm entry.")
            
            time.sleep(0.5) # Allow UI to update
            
        except NoSuchElementException as e:
            self._take_screenshot(f"input_elements_not_found_in_last_row")
            logger.error(f"Error finding input elements in the last row: {e}", exc_info=True)
            self.fail(f"Could not find grade/percentage input elements in the last row: {e}")
        except Exception as e:
            self._take_screenshot(f"error_adding_grade_percentage")
            logger.error(f"Generic error in _add_grade_and_percentage: {e}", exc_info=True)
            self.fail(f"Generic error adding grade/percentage: {e}")

    def _click_calculate_and_wait_for_result_page(self):
        try:
            calculate_button = self.wait_long.until(EC.element_to_be_clickable((By.CSS_SELECTOR, self.CALCULATE_BUTTON_SELECTOR)))
            calculate_button.click()
            self.wait_long.until(EC.presence_of_element_located((By.CSS_SELECTOR, self.RESULT_PAGE_CONTAINER_SELECTOR)))
            logger.info("Clicked 'Calcular' and result page container is present.")
        except TimeoutException:
            self._take_screenshot("calculate_or_result_page_timeout")
            self.fail("Timeout clicking calculate or waiting for result page.")

    def _navigate_back_to_home(self):
        try:
            nav_back_button = self.wait_long.until(EC.element_to_be_clickable((By.CSS_SELECTOR, self.NAV_BACK_BUTTON_SELECTOR)))
            nav_back_button.click()
            self.wait_long.until(EC.presence_of_element_located((By.CSS_SELECTOR, self.HOME_CONTAINER_SELECTOR)))
            logger.info("Navigated back to home page.")
        except TimeoutException:
            try: # Fallback to XPath
                nav_back_button = self.wait_long.until(EC.element_to_be_clickable((By.XPATH, self.NAV_BACK_BUTTON_XPATH)))
                nav_back_button.click()
                self.wait_long.until(EC.presence_of_element_located((By.CSS_SELECTOR, self.HOME_CONTAINER_SELECTOR)))
                logger.info("Navigated back to home page using XPath.")
            except TimeoutException:
                self._take_screenshot("navigate_back_home_timeout")
                self.fail("Timeout navigating back to home page.")
    
    def _get_current_weighted_average_text(self): # Adapted from US04
        raw_text = ""
        try:
            self.wait_long.until(EC.presence_of_element_located((By.CSS_SELECTOR, self.RESULT_PAGE_CONTAINER_SELECTOR)))
            display_element = self.wait_long.until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, self.CURRENT_AVERAGE_DISPLAY_SELECTOR))
            )
            time.sleep(0.2)
            raw_text = display_element.text.strip()
            logger.info(f"Raw current average text: \'{raw_text}\'") # Corrected f-string
            return raw_text
        except TimeoutException:
            logger.error(f"Timeout waiting for current average display: {self.CURRENT_AVERAGE_DISPLAY_SELECTOR}")
            self._take_screenshot("current_average_timeout")
            return "Error: Timeout"
        except Exception as e:
            logger.error(f"Error getting current average text: {e}", exc_info=True)
            self._take_screenshot("get_current_average_error")
            return "Error: General"

    def _get_required_grade_text(self): # Adapted from US05
        raw_text = ""
        try:
            self.wait_long.until(EC.presence_of_element_located((By.CSS_SELECTOR, self.RESULT_PAGE_CONTAINER_SELECTOR)))
            display_element = self.wait_long.until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, self.REQUIRED_GRADE_DISPLAY_SELECTOR))
            )
            time.sleep(0.2)
            raw_text = display_element.text.strip()
            logger.info(f"Raw required grade/message text: '{raw_text}'")
            return raw_text
        except TimeoutException:
            logger.error(f"Timeout waiting for required grade display: {self.REQUIRED_GRADE_DISPLAY_SELECTOR}")
            self._take_screenshot("required_grade_timeout")
            return "Error: Timeout"
        except Exception as e:
            logger.error(f"Error getting required grade/message: {e}", exc_info=True)
            self._take_screenshot("get_required_grade_error")
            return "Error: General"

    def _get_final_status_message_text(self): # From US06
        raw_text = ""
        try:
            self.wait_long.until(EC.presence_of_element_located((By.CSS_SELECTOR, self.RESULT_PAGE_CONTAINER_SELECTOR)))
            status_element = self.wait_long.until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, self.FINAL_STATUS_DISPLAY_SELECTOR))
            )
            time.sleep(0.2)
            raw_text = status_element.text.strip()
            logger.info(f"Raw final status message text: '{raw_text}'")
            return raw_text
        except TimeoutException:
            logger.error(f"Timeout waiting for final status display: {self.FINAL_STATUS_DISPLAY_SELECTOR}")
            self._take_screenshot("final_status_timeout")
            return "Error: Timeout"
        except Exception as e:
            logger.error(f"Error getting final status message: {e}", exc_info=True)
            self._take_screenshot("get_final_status_error")
            return "Error: General"

    # --- Test Case for US07 ---
    def test_us07_form_reset(self):
        # Corresponds to Task 7.1
        test_name = self._testMethodName
        logger.info(f"Running test: {test_name}")

        try:
            # 1. Add several grades and percentages
            self._add_grade_and_percentage("4.0", "25")
            self._add_grade_and_percentage("3.5", "25")
            
            # Verify grades were added (at least 2 filled rows + 1 template = 3, or just check count > 1)
            grade_rows_before_reset = self.driver.find_elements(By.CSS_SELECTOR, self.GRADES_LIST_ITEM_SELECTOR)
            # Depending on app logic, after adding 2 grades, we might have 2 filled rows + 1 empty template, or just 2 rows if template is reused.
            # Let's check that we have at least 2 rows that are presumably filled.
            self.assertTrue(len(grade_rows_before_reset) >= 2, f"Should have at least 2 grade rows after adding two grades, found {len(grade_rows_before_reset)}.")

            # 2. Click calculate and observe some results (optional, but good for confirming state change)
            self._click_calculate_and_wait_for_result_page()
            avg_before_reset = self._get_current_weighted_average_text()
            self.assertNotIn("Error:", avg_before_reset, "Should get valid average before reset")
            self._navigate_back_to_home()

            # 3. Locate and click the reset button
            logger.info(f"Attempting to find and click reset button with selector: {self.RESET_BUTTON_SELECTOR}")
            try:
                # First, wait for the button to be present in the DOM
                logger.info(f"Waiting for presence of reset button: {self.RESET_BUTTON_SELECTOR}")
                self.wait_long.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, self.RESET_BUTTON_SELECTOR))
                )
                logger.info(f"Reset button '{self.RESET_BUTTON_SELECTOR}' is present in the DOM.")
                
                # Then, wait for it to be clickable
                logger.info(f"Waiting for reset button '{self.RESET_BUTTON_SELECTOR}' to be clickable.")
                reset_button = self.wait_long.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, self.RESET_BUTTON_SELECTOR))
                )
                logger.info(f"Reset button '{self.RESET_BUTTON_SELECTOR}' is clickable.")
                reset_button.click()
                logger.info("Clicked reset button.")
                time.sleep(0.5) # Allow UI to update
            except TimeoutException as e:
                logger.error(f"Timeout related to reset button '{self.RESET_BUTTON_SELECTOR}'. Current URL: {self.driver.current_url}", exc_info=True)
                # Add more debug info: check if home container is still there
                try:
                    home_container_present = self.driver.find_element(By.CSS_SELECTOR, self.HOME_CONTAINER_SELECTOR).is_displayed()
                    logger.info(f"Home container is present and displayed on reset button timeout: {home_container_present}")
                except NoSuchElementException:
                    logger.error("Home container NOT present on reset button timeout. Likely on wrong page.")
                self._take_screenshot("reset_button_timeout")
                self.fail(f"Reset button with selector '{self.RESET_BUTTON_SELECTOR}' not found or not clickable. Details: {e}")
            except Exception as e_click: # Catch other exceptions during click
                logger.error(f"Error clicking reset button '{self.RESET_BUTTON_SELECTOR}': {e_click}", exc_info=True)
                self._take_screenshot("reset_button_click_error")
                self.fail(f"Error clicking reset button: {e_click}")


            # 4. Verify input fields are cleared and list of added grades is cleared/reset
            # Check if the main input fields in the (usually first or only) row are empty
            grade_rows_after_reset = self.driver.find_elements(By.CSS_SELECTOR, self.GRADES_LIST_ITEM_SELECTOR)
            if not grade_rows_after_reset: # Should be at least one empty template row
                 self.fail("No grade rows found after reset. Expected at least one empty template row.")

            # Typically, a reset form might leave one empty row.
            # Check the first/last row's inputs
            first_row_inputs = grade_rows_after_reset[0].find_elements(By.CSS_SELECTOR, self.GRADE_INPUT_SELECTOR)
            first_row_perc_inputs = grade_rows_after_reset[0].find_elements(By.CSS_SELECTOR, self.PERCENTAGE_INPUT_SELECTOR)

            if first_row_inputs: # Ensure the input exists
                 self.assertEqual(first_row_inputs[0].get_attribute("value"), "", "Grade input in the first row should be empty after reset.")
            if first_row_perc_inputs: # Ensure the input exists
                 self.assertEqual(first_row_perc_inputs[0].get_attribute("value"), "", "Percentage input in the first row should be empty after reset.")
            
            # Check number of rows. Expect 1 empty template row.
            # The exact behavior (0 rows, 1 empty row) depends on implementation.
            # If it clears all rows and adds one fresh one:
            self.assertEqual(len(grade_rows_after_reset), 1, "Expected 1 grade row (empty template) after reset.")


            # 5. Verify all calculated result displays are reset to their initial/empty states
            self._click_calculate_and_wait_for_result_page()
            
            # Define expected initial/empty states (these might need adjustment based on actual app behavior)
            # Assuming default approval grade is 3.0 for these initial checks
            expected_initial_avg = "Actualmente tienes un promedio de 0.0 en el 0% de la materia" 
            expected_initial_needed = "Necesitas un 3.0 en el 100% restante para aprobar la materia con un 3.0"
            expected_initial_status = "En riesgo" # Or "Información insuficiente" or similar

            current_avg_after_reset = self._get_current_weighted_average_text()
            required_grade_after_reset = self._get_required_grade_text()
            final_status_after_reset = self._get_final_status_message_text()

            self.assertIn("0.0", current_avg_after_reset, f"Current average after reset should be initial. Got: {current_avg_after_reset}")
            self.assertIn("0%", current_avg_after_reset, f"Current average percentage after reset should be initial. Got: {current_avg_after_reset}")
            
            # For required grade, it might depend on the default approval grade.
            # If default is 3.0, it should say something like "Necesitas un 3.0 en el 100% restante..."
            self.assertIn("3.0", required_grade_after_reset, f"Required grade after reset should reflect default. Got: {required_grade_after_reset}")
            self.assertIn("100%", required_grade_after_reset, f"Required percentage after reset should be 100%. Got: {required_grade_after_reset}")

            self.assertEqual(final_status_after_reset, expected_initial_status, f"Final status after reset. Expected '{expected_initial_status}', got '{final_status_after_reset}'")

            logger.info(f"Test {test_name} passed.")

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
