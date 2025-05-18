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

class US10Tests(unittest.TestCase):
    BASE_URL = "http://localhost:3000"
    GRADE_INPUT_SELECTOR = "input.home__input[placeholder='0.0'][type='number']"
    PERCENTAGE_INPUT_SELECTOR = "input.home__input[placeholder='0'][type='number']"
    ADD_GRADE_BUTTON_SELECTOR = "button.home__add-button"
    GRADES_LIST_ITEM_SELECTOR = "div.home__grades-container > div.home__grade-row"
    CALCULATE_BUTTON_SELECTOR = "button.home__calculate-button"
    
    RESULT_PAGE_CONTAINER_SELECTOR = "div.result" 
    FIRST_TIME_ALERT_BUTTON_SELECTOR = ".alert__button.alert__button--single"
    ALERT_OVERLAY_SELECTOR = "div.alert__overlay"
    NAV_BACK_BUTTON_XPATH = "//button[contains(@class, 'nav-bar__button') and .//span[contains(@class, 'back-icon')]/svg[contains(@class, 'lucide-chevron-left')]]"
    NAV_BACK_BUTTON_SELECTOR = "nav.nav-bar > button.nav-bar__button:first-child"
    HOME_CONTAINER_SELECTOR = "div.home__container"

    # Selectors for alerts (from selenium-test-dev.md)
    ALERT_TITLE_SELECTOR = "div.alert__title"
    ALERT_MESSAGE_SELECTOR = "div.alert__message"
    ALERT_CONFIRM_BUTTON_SELECTOR = "div.alert__actions button.alert__button" # General confirm

    # Selectors needed for setting up scenarios (from US05)
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

    def _set_approval_grade_via_js(self, approval_grade_value, min_val=0, max_val=5):
        logger.info(f"Setting approval grade to: {approval_grade_value} via JavaScript injection")
        script = f"""
        localStorage.setItem('settings', JSON.stringify({{
            minAcceptValue: parseFloat({approval_grade_value}),
            minValue: {min_val},
            maxValue: {max_val}
        }}));
        localStorage.setItem("isFirstTime", "false");
        return localStorage.getItem('settings');
        """
        try:
            self.driver.execute_script(script)
            logger.info(f"Settings updated via JavaScript. Approval grade set to: {approval_grade_value}")
            current_url = self.driver.current_url
            self.driver.refresh()
            if "settings" in current_url.lower():
                 self.wait_long.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.settings__container")))
            else:
                 self.wait_long.until(EC.presence_of_element_located((By.CSS_SELECTOR, self.HOME_CONTAINER_SELECTOR)))
            logger.info(f"Page refreshed after setting approval grade via JS. Current URL: {self.driver.current_url}")
            time.sleep(0.5)
        except Exception as e:
            logger.error(f"Error executing JS to set approval grade: {e}", exc_info=True)
            self._take_screenshot("set_approval_grade_js_error")

    def _initial_setup(self):
        if not hasattr(self, 'driver') or not self.driver:
            self.fail("Driver not initialized for test setup.")
        self.driver.get(self.BASE_URL)
        logger.info(f"Navigated to base URL: {self.BASE_URL}")
        time.sleep(0.5)
        try:
            alert_button = WebDriverWait(self.driver, 7).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, self.FIRST_TIME_ALERT_BUTTON_SELECTOR))
            )
            alert_button.click()
            WebDriverWait(self.driver, 5).until(
                EC.invisibility_of_element_located((By.CSS_SELECTOR, self.ALERT_OVERLAY_SELECTOR))
            )
            nav_back_button = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, self.NAV_BACK_BUTTON_SELECTOR))
            )
            nav_back_button.click()
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, self.HOME_CONTAINER_SELECTOR))
            )
        except TimeoutException:
            logger.info("First-time user alert not found or handled. Ensuring on Home page.")
            try:
                self.wait_long.until(EC.presence_of_element_located((By.CSS_SELECTOR, self.HOME_CONTAINER_SELECTOR)))
            except TimeoutException:
                logger.info("Attempting to set localStorage isFirstTime to false and refreshing.")
                self.driver.execute_script("localStorage.setItem('isFirstTime', 'false'); localStorage.removeItem('grades'); localStorage.removeItem('settings');")
                self.driver.refresh()
                self.wait_long.until(EC.presence_of_element_located((By.CSS_SELECTOR, self.HOME_CONTAINER_SELECTOR)))
        except Exception as e:
            self.fail(f"Unexpected error during initial setup: {e}")
        self._set_approval_grade_via_js("3.0") # Default approval grade
        self._clear_grades_via_js() # Ensure no grades from previous tests

    def _clear_grades_via_js(self):
        logger.info("Clearing grades from localStorage via JavaScript.")
        try:
            self.driver.execute_script("localStorage.removeItem('grades');")
            # Optionally, refresh or re-navigate to ensure UI updates if it relies on this for re-render
            # self.driver.refresh()
            # self.wait_long.until(EC.presence_of_element_located((By.CSS_SELECTOR, self.HOME_CONTAINER_SELECTOR)))
            logger.info("Grades cleared from localStorage.")
        except Exception as e:
            logger.error(f"Error clearing grades via JS: {e}", exc_info=True)
            self._take_screenshot("clear_grades_js_error")
            # Depending on test needs, this might be a critical failure
            # self.fail("Failed to clear grades via JS for test setup.")

    def _add_grade_and_percentage_raw(self, grade_value, percentage_value):
        """Adds a grade and percentage by directly interacting with the last row's inputs, then clicks the main add button."""
        if not hasattr(self, 'driver') or not self.driver: self.fail("Driver not available.")
        self.wait_long.until(EC.presence_of_element_located((By.CSS_SELECTOR, self.HOME_CONTAINER_SELECTOR)))
        
        grade_rows = self.driver.find_elements(By.CSS_SELECTOR, self.GRADES_LIST_ITEM_SELECTOR)
        if not grade_rows:
            # If no rows, the app might expect the first input to create the first row or an add button to be clicked first.
            # For simplicity, assume an initial row is present or created upon typing.
            # This might need adjustment based on exact app behavior for the very first grade.
            # Click add button to ensure a row exists if it's the first entry and no rows are present.
            # This logic is tricky as the app might add a row upon typing into a non-existent one.
            # Let's assume the app provides an initial empty row or handles it.
            pass 

        # Always target the last available row for new input
        # Re-fetch rows in case an add button was clicked or app structure changed
        grade_rows = self.driver.find_elements(By.CSS_SELECTOR, self.GRADES_LIST_ITEM_SELECTOR)
        if not grade_rows: # Should not happen if app provides an initial row
            self._take_screenshot("no_grade_rows_to_input")
            self.fail("No grade rows available for input.")

        target_row = grade_rows[-1]
        
        try:
            grade_input = target_row.find_element(By.CSS_SELECTOR, self.GRADE_INPUT_SELECTOR)
            percentage_input = target_row.find_element(By.CSS_SELECTOR, self.PERCENTAGE_INPUT_SELECTOR)
            
            grade_input.clear()
            grade_input.send_keys(str(grade_value))
            percentage_input.clear()
            percentage_input.send_keys(str(percentage_value))
            logger.info(f"Raw input: Grade '{grade_value}', Percentage '{percentage_value}' into last row.")
            
            # Click the main "Add Grade" button to submit this entry
            add_button = self.wait_long.until(EC.element_to_be_clickable((By.CSS_SELECTOR, self.ADD_GRADE_BUTTON_SELECTOR)))
            add_button.click()
            logger.info("Clicked main 'Add Grade' button after raw input.")
            time.sleep(0.5) # Allow UI to update (e.g., new row added, alert shown)
        except NoSuchElementException:
            self._take_screenshot("input_fields_not_in_last_row")
            self.fail("Could not find grade/percentage input fields in the last row.")
        except Exception as e:
            self._take_screenshot("error_raw_add_grade")
            self.fail(f"Error during raw add grade and percentage: {e}")

    def _check_for_alert(self, expected_title_part, expected_message_part):
        """Checks for an alert, verifies its title and message, and closes it."""
        try:
            WebDriverWait(self.driver, 3).until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.ALERT_OVERLAY_SELECTOR)))
            logger.info("Alert overlay detected.")
            
            title_element = self.driver.find_element(By.CSS_SELECTOR, self.ALERT_TITLE_SELECTOR)
            message_element = self.driver.find_element(By.CSS_SELECTOR, self.ALERT_MESSAGE_SELECTOR)
            
            title_text = title_element.text.strip()
            message_text = message_element.text.strip()
            logger.info(f"Alert Title: '{title_text}', Message: '{message_text}'")
            
            self.assertIn(expected_title_part, title_text, f"Alert title mismatch. Expected part: '{expected_title_part}', Got: '{title_text}'")
            self.assertIn(expected_message_part, message_text, f"Alert message mismatch. Expected part: '{expected_message_part}', Got: '{message_text}'")
            
            confirm_button = self.driver.find_element(By.CSS_SELECTOR, self.ALERT_CONFIRM_BUTTON_SELECTOR)
            confirm_button.click()
            WebDriverWait(self.driver, 3).until(EC.invisibility_of_element_located((By.CSS_SELECTOR, self.ALERT_OVERLAY_SELECTOR)))
            logger.info("Alert confirmed and closed.")
            return True # Alert was found and handled
        except TimeoutException:
            logger.info("No alert detected within the timeout period.")
            return False # No alert found
        except Exception as e:
            self._take_screenshot("check_alert_error")
            logger.error(f"Error while checking/handling alert: {e}")
            self.fail(f"Error during alert handling: {e}")
            return False # Error occurred

    def _get_number_of_filled_grade_rows(self):
        """Counts the number of grade rows that have actual values entered."""
        self.wait_long.until(EC.presence_of_element_located((By.CSS_SELECTOR, self.HOME_CONTAINER_SELECTOR)))
        grade_rows = self.driver.find_elements(By.CSS_SELECTOR, self.GRADES_LIST_ITEM_SELECTOR)
        filled_rows = 0
        for row in grade_rows:
            try:
                grade_val = row.find_element(By.CSS_SELECTOR, self.GRADE_INPUT_SELECTOR).get_attribute("value")
                perc_val = row.find_element(By.CSS_SELECTOR, self.PERCENTAGE_INPUT_SELECTOR).get_attribute("value")
                if grade_val and perc_val: # Both must have a value
                    filled_rows += 1
            except NoSuchElementException:
                continue # Skip if inputs not found (e.g. header row if any)
        logger.info(f"Number of filled grade rows found: {filled_rows}")
        return filled_rows

    # --- Test Cases for US10 ---
    def test_us10_prevent_adding_grades_if_total_percentage_exceeds_100(self):
        # Corresponds to Task 10.1
        test_name = self._testMethodName
        logger.info(f"Running test: {test_name}")
        self._clear_grades_via_js() # Start clean

        try:
            # 1. Add grades totaling close to 100%
            self._add_grade_and_percentage_raw("4.0", "50") # Total: 50%
            self.assertEqual(self._get_number_of_filled_grade_rows(), 1, "After 1st grade, expected 1 filled row.")
            
            self._add_grade_and_percentage_raw("3.0", "40") # Total: 90%
            self.assertEqual(self._get_number_of_filled_grade_rows(), 2, "After 2nd grade, expected 2 filled rows.")

            # 2. Attempt to add a grade that makes the total percentage exceed 100%
            logger.info("Attempting to add grade that exceeds 100% total percentage (20%).")
            # Input into the new empty row created by the previous add
            grade_rows_before_exceed = self.driver.find_elements(By.CSS_SELECTOR, self.GRADES_LIST_ITEM_SELECTOR)
            last_row_inputs = grade_rows_before_exceed[-1]
            grade_input = last_row_inputs.find_element(By.CSS_SELECTOR, self.GRADE_INPUT_SELECTOR)
            percentage_input = last_row_inputs.find_element(By.CSS_SELECTOR, self.PERCENTAGE_INPUT_SELECTOR)
            
            grade_input.clear(); grade_input.send_keys("2.0")
            percentage_input.clear(); percentage_input.send_keys("20") # This would make it 110%
            logger.info("Entered 2.0 grade with 20% into the new row inputs.")

            # Click the main "Add Grade" button
            add_button = self.wait_long.until(EC.element_to_be_clickable((By.CSS_SELECTOR, self.ADD_GRADE_BUTTON_SELECTOR)))
            add_button.click()
            logger.info("Clicked main 'Add Grade' button to attempt adding the exceeding grade.")
            time.sleep(0.5) # Give time for alert to appear

            # 3. Verify an alert is shown and the grade is NOT added
            alert_shown = self._check_for_alert(
                expected_title_part="Error de Porcentaje", 
                expected_message_part="La suma de los porcentajes no puede exceder el 100%."
            )
            self.assertTrue(alert_shown, "Expected an alert when trying to add grade exceeding 100% total percentage.")
            
            # Verify the grade was not actually added (still 2 filled rows)
            self.assertEqual(self._get_number_of_filled_grade_rows(), 2, 
                             "Number of filled rows should remain 2 after attempting to add grade exceeding 100%.")
            
            # Also check that the input fields of the last row (where the attempt was made) are now empty or reset
            # This depends on app behavior: does it clear the offending inputs or leave them?
            # Assuming it clears them or the row is removed/reset to template.
            grade_rows_after_alert = self.driver.find_elements(By.CSS_SELECTOR, self.GRADES_LIST_ITEM_SELECTOR)
            last_row_after_alert = grade_rows_after_alert[-1]
            last_grade_input_val = last_row_after_alert.find_element(By.CSS_SELECTOR, self.GRADE_INPUT_SELECTOR).get_attribute("value")
            last_perc_input_val = last_row_after_alert.find_element(By.CSS_SELECTOR, self.PERCENTAGE_INPUT_SELECTOR).get_attribute("value")
            
            self.assertTrue(last_grade_input_val == "" and last_perc_input_val == "", 
                            f"Inputs in the last row should be empty after percentage error. Got G: '{last_grade_input_val}', P: '{last_perc_input_val}'")

            logger.info(f"Test {test_name} passed.")

        except AssertionError as e:
            logger.error(f"AssertionError in {test_name}: {e}", exc_info=True)
            self._take_screenshot(f"{test_name}_assertion_error")
            self.fail(f"AssertionError in {test_name}: {e}")
        except Exception as e:
            logger.error(f"Exception in {test_name}: {e}", exc_info=True)
            self._take_screenshot(f"{test_name}_exception")
            self.fail(f"Exception in {test_name}: {e}")

    def test_us10_prevent_calculation_if_total_percentage_exceeds_100(self):
        # Corresponds to Task 10.2 (Alternative: if adding is allowed but calculation is prevented)
        # This test assumes the application MIGHT allow entering data that sums > 100% in the UI temporarily,
        # but should prevent calculation and show an alert.
        # If Task 10.1 (preventing add) is strictly enforced, this scenario might not be directly testable
        # in the same way, or the alert for adding would preempt the calculation alert.
        # For this test, we will simulate data in localStorage that exceeds 100% and then try to calculate.
        test_name = self._testMethodName
        logger.info(f"Running test: {test_name}")
        self._clear_grades_via_js() # Start clean

        try:
            # 1. Manually set localStorage to have grades exceeding 100% total percentage
            # This bypasses the UI add validation to test the calculation validation specifically.
            grades_exceeding_100 = [
                {"id": "1", "grade": "4.0", "percentage": "60"},
                {"id": "2", "grade": "3.0", "percentage": "50"} # Total 110%
            ]
            self.driver.execute_script(f"localStorage.setItem('grades', JSON.stringify({grades_exceeding_100}));")
            logger.info(f"Manually set localStorage grades to: {grades_exceeding_100}")
            
            # Refresh the page to load these grades into the UI
            self.driver.refresh()
            self.wait_long.until(EC.presence_of_element_located((By.CSS_SELECTOR, self.HOME_CONTAINER_SELECTOR)))
            time.sleep(1) # Allow UI to populate from localStorage
            self._take_screenshot("after_manual_localstorage_set")

            # Verify UI shows these grades (optional, but good for sanity check)
            num_filled_rows = self._get_number_of_filled_grade_rows()
            self.assertEqual(num_filled_rows, 2, "UI should reflect the 2 grades loaded from manipulated localStorage.")

            # 2. Attempt to click the calculate button
            logger.info("Attempting to click calculate button with percentages > 100%.")
            calculate_button = self.wait_long.until(EC.element_to_be_clickable((By.CSS_SELECTOR, self.CALCULATE_BUTTON_SELECTOR)))
            calculate_button.click()
            time.sleep(0.5) # Give time for alert to appear

            # 3. Verify an alert is shown indicating the percentage error, and calculation does not proceed
            # The alert message might be the same as in 10.1 or specific to calculation.
            # Assuming same alert for now based on typical app behavior.
            alert_shown = self._check_for_alert(
                expected_title_part="Error de Porcentaje", 
                expected_message_part="La suma de los porcentajes no puede exceder el 100%."
            )
            self.assertTrue(alert_shown, "Expected an alert when trying to calculate with total percentage > 100%.")
            
            # Verify that we are still on the home page (calculation did not proceed to result page)
            try:
                self.wait_short.until(EC.presence_of_element_located((By.CSS_SELECTOR, self.HOME_CONTAINER_SELECTOR)))
                logger.info("Still on home page after attempting calculation with >100% percentage, as expected.")
            except TimeoutException:
                self._take_screenshot("navigated_away_from_home_error")
                self.fail("Calculation proceeded or navigated away from home page despite >100% percentage error.")
            
            # Ensure result page is not shown
            with self.assertRaises(TimeoutException):
                WebDriverWait(self.driver, 1).until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.RESULT_PAGE_CONTAINER_SELECTOR)))
            logger.info("Result page is not visible, as expected.")

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
