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
    NAV_BACK_BUTTON_SELECTOR = "nav.nav-bar > button.nav-bar__button:first-of-type"
    HOME_CONTAINER_SELECTOR = "div.home__container"

    # Selectors for alerts - based on save.jsx and alert.jsx
    ALERT_OVERLAY_SELECTOR = "div.alert__overlay"
    ALERT_CONTAINER_SELECTOR = "div.alert__container" 
    ALERT_TITLE_SELECTOR = "div.alert__title"
    ALERT_MESSAGE_SELECTOR = "div.alert__message"
    ALERT_CONFIRM_BUTTON_SELECTOR = "button.alert__button"
    ALERT_CANCEL_BUTTON_SELECTOR = "button.alert__button.alert__button--cancel"
    ALERT_CONFIRM_BUTTON_SINGLE_SELECTOR = "button.alert__button.alert__button--single"

    # Selectors needed for setting up scenarios (from US05)
    SETTINGS_NAV_BUTTON_XPATH = "//button[contains(@class, 'nav-bar__button') and .//span[contains(@class, 'settings-icon')]/svg[contains(@class, 'lucide-settings')]]"
    APPROVAL_GRADE_INPUT_SELECTOR = "input.settings__input[type='number']"

    def set_driver_fixture(self, driver):
        self.driver = driver
        self.wait_short = WebDriverWait(self.driver, 5)
        self.wait_long = WebDriverWait(self.driver, 20) # Increased to 20s
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

    def _set_approval_grade_via_js(self, approval_grade_value, min_val=0.0, max_val=5.0):
        logger.info(f"Setting approval grade to: {approval_grade_value} using JavaScript injection")
        script = f"""
        localStorage.setItem('settings', JSON.stringify({{
            minAcceptValue: parseFloat({approval_grade_value}),
            minValue: parseFloat({min_val}),
            maxValue: parseFloat({max_val})
        }}));
        localStorage.setItem("isFirstTime", "false");
        return localStorage.getItem('settings');
        """
        try:
            result = self.driver.execute_script(script)
            logger.info(f"Settings updated via JavaScript. Result: {result}")
            self.driver.refresh()
            self.wait_long.until(EC.presence_of_element_located((By.CSS_SELECTOR, self.HOME_CONTAINER_SELECTOR)))
            logger.info("Page refreshed after setting approval grade")
        except Exception as e:
            logger.error(f"Error setting approval grade via JS: {e}", exc_info=True)
            self.fail(f"Error setting approval grade via JS: {e}")

    def _initial_setup(self):
        if not hasattr(self, 'driver') or not self.driver:
            logger.error("Driver not initialized in _initial_setup. Aborting setup.")
            self.fail("Driver not initialized for test setup.")
            return
            
        self.driver.get(self.BASE_URL)
        logger.info(f"Navigated to base URL: {self.BASE_URL}")
        time.sleep(0.5)
        
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
            
        self._set_approval_grade_via_js("3.0") # Default approval grade for tests
        self._clear_grades_via_js() # Ensure no grades from previous tests

    def _clear_grades_via_js(self):
        logger.info("Clearing grades from localStorage via JavaScript.")
        try:
            self.driver.execute_script("localStorage.removeItem('grades'); console.log('Cleared grades from localStorage');")
            self.driver.refresh()
            self.wait_long.until(EC.presence_of_element_located((By.CSS_SELECTOR, self.HOME_CONTAINER_SELECTOR)))
            logger.info("Cleared grades and refreshed page.")
        except Exception as e:
            logger.error(f"Error clearing grades via JS: {e}", exc_info=True)
            self.fail(f"Error clearing grades via JS: {e}")

    def _add_grade_and_percentage_raw(self, grade_value, percentage_value):
        """Adds a grade and percentage by directly interacting with the last row's inputs, then clicks the main add button.
        Does not check for success, just performs the UI actions."""
        if not hasattr(self, 'driver') or not self.driver:
            logger.error("Driver not available in _add_grade_and_percentage_raw.")
            self.fail("Driver not available.")
            return
            
        self.wait_long.until(EC.presence_of_element_located((By.CSS_SELECTOR, self.HOME_CONTAINER_SELECTOR)))
        
        # Find all grade rows and use the last one
        grade_rows = self.driver.find_elements(By.CSS_SELECTOR, self.GRADES_LIST_ITEM_SELECTOR)
        if not grade_rows:
            logger.error("No grade rows found.")
            self._take_screenshot("no_grade_rows_found")
            self.fail("No grade rows found.")
            return
            
        target_row = grade_rows[-1]  # Get the last row
        
        try:
            # Find the input elements in the target row
            grade_input = target_row.find_element(By.CSS_SELECTOR, self.GRADE_INPUT_SELECTOR)
            percentage_input = target_row.find_element(By.CSS_SELECTOR, self.PERCENTAGE_INPUT_SELECTOR)
            
            # Input the values
            grade_input.clear()
            grade_input.send_keys(str(grade_value))
            percentage_input.clear()
            percentage_input.send_keys(str(percentage_value))
            
            # Click the add button to add the grade
            add_button = self.wait_long.until(EC.element_to_be_clickable((By.CSS_SELECTOR, self.ADD_GRADE_BUTTON_SELECTOR)))
            logger.info(f"About to click Add button after entering Grade: {grade_value}, Percentage: {percentage_value}")
            add_button.click()
            logger.info(f"Clicked add button after entering Grade: {grade_value}, Percentage: {percentage_value}")
            
            # Small wait to allow for UI update or alert to appear
            time.sleep(0.5)
        except Exception as e:
            logger.error(f"Error in _add_grade_and_percentage_raw: {e}", exc_info=True)
            self._take_screenshot("add_grade_percentage_raw_error")
            self.fail(f"Error in _add_grade_and_percentage_raw: {e}")

    def _check_for_alert(self, expected_title_part=None, expected_message_part=None):
        """Checks if an alert is currently displayed and if it contains the expected title and message.
        Returns a tuple of (alert_is_present, alert_title, alert_message)."""
        logger.info(f"Checking for alert with title_part={expected_title_part}, message_part={expected_message_part}")
        
        try:
            # Wait for the alert overlay to be visible
            self.wait_short.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.ALERT_OVERLAY_SELECTOR)))
            logger.info("Alert overlay is visible.")
            
            # Find the alert container, title and message
            alert_container = self.driver.find_element(By.CSS_SELECTOR, self.ALERT_CONTAINER_SELECTOR)
            
            # Title is optional in the Alert component, so use presence_of first
            alert_title = None
            alert_message = None
            
            try:
                title_elements = alert_container.find_elements(By.CSS_SELECTOR, self.ALERT_TITLE_SELECTOR)
                if title_elements:
                    alert_title = title_elements[0].text.strip()
                    logger.info(f"Alert title found: '{alert_title}'")
            except NoSuchElementException:
                logger.info("No alert title element found.")
                
            try:
                message_elements = alert_container.find_elements(By.CSS_SELECTOR, self.ALERT_MESSAGE_SELECTOR)
                if message_elements:
                    alert_message = message_elements[0].text.strip()
                    logger.info(f"Alert message found: '{alert_message}'")
            except NoSuchElementException:
                logger.info("No alert message element found.")
            
            # Check title and message if specified
            title_matches = True
            message_matches = True
            
            if expected_title_part and (not alert_title or expected_title_part not in alert_title):
                title_matches = False
                logger.warning(f"Alert title '{alert_title}' does not contain expected part '{expected_title_part}'")
                
            if expected_message_part and (not alert_message or expected_message_part not in alert_message):
                message_matches = False
                logger.warning(f"Alert message '{alert_message}' does not contain expected part '{expected_message_part}'")
            
            # If both title and message match (or weren't specified), dismiss the alert
            if title_matches and message_matches:
                # Try to find and click the confirm button
                try:
                    # First try the single button (most alerts in the app)
                    confirm_buttons = self.driver.find_elements(By.CSS_SELECTOR, self.ALERT_CONFIRM_BUTTON_SINGLE_SELECTOR)
                    if not confirm_buttons:
                        # Then try the regular confirm button
                        confirm_buttons = self.driver.find_elements(By.CSS_SELECTOR, self.ALERT_CONFIRM_BUTTON_SELECTOR)
                    
                    if confirm_buttons:
                        confirm_buttons[0].click()
                        logger.info("Clicked alert confirm button.")
                        time.sleep(0.5) # Wait for alert dismissal animation
                    else:
                        logger.warning("No alert confirm button found to dismiss the alert.")
                        self._take_screenshot("no_alert_confirm_button")
                except Exception as e:
                    logger.error(f"Error dismissing alert: {e}", exc_info=True)
                    self._take_screenshot("error_dismissing_alert")
            
            return (True, alert_title, alert_message, title_matches and message_matches)
            
        except TimeoutException:
            logger.info("No alert overlay found.")
            return (False, None, None, False)
        except Exception as e:
            logger.error(f"Error checking for alert: {e}", exc_info=True)
            self._take_screenshot("check_for_alert_error")
            return (False, None, None, False)

    def _get_number_of_filled_grade_rows(self):
        """Counts the number of grade rows that have values in both grade and percentage inputs."""
        try:
            self.wait_long.until(EC.presence_of_element_located((By.CSS_SELECTOR, self.HOME_CONTAINER_SELECTOR)))
            grade_rows = self.driver.find_elements(By.CSS_SELECTOR, self.GRADES_LIST_ITEM_SELECTOR)
            
            filled_rows = 0
            for row in grade_rows:
                try:
                    grade_input = row.find_element(By.CSS_SELECTOR, self.GRADE_INPUT_SELECTOR)
                    percentage_input = row.find_element(By.CSS_SELECTOR, self.PERCENTAGE_INPUT_SELECTOR)
                    
                    grade_val = grade_input.get_attribute("value")
                    percentage_val = percentage_input.get_attribute("value")
                    
                    if grade_val and percentage_val:
                        filled_rows += 1
                except NoSuchElementException:
                    continue
                    
            logger.info(f"Found {filled_rows} filled grade rows.")
            return filled_rows
        except Exception as e:
            logger.error(f"Error getting number of filled grade rows: {e}", exc_info=True)
            self._take_screenshot("get_filled_rows_error")
            return 0

    # --- Test Cases for US10 ---
    def test_us10_prevent_adding_grades_if_total_percentage_exceeds_100(self):
        """Tests that an alert is shown when attempting to add a grade that would make the total percentage exceed 100%."""
        test_name = self._testMethodName
        logger.info(f"Running test: {test_name}")
        
        try:
            # First add a grade with 80% percentage
            self._add_grade_and_percentage_raw(4.0, 80)
            
            # Verify it was added
            filled_rows_before = self._get_number_of_filled_grade_rows()
            self.assertEqual(filled_rows_before, 1, f"Expected 1 filled row after adding first grade, found {filled_rows_before}")
            
            # Now try to add another grade with 30% (which would make total 110%)
            self._add_grade_and_percentage_raw(3.5, 30)
            
            # Check for an alert indicating the total exceeds 100%
            alert_present, alert_title, alert_message, alert_matches = self._check_for_alert(
                expected_message_part="El porcentaje total no puede superar el 100%")
                
            # Assert the alert was shown with the expected message
            self.assertTrue(alert_present, "Alert should be present when adding grade with percentage that exceeds 100%")
            self.assertTrue(alert_matches, f"Alert should contain expected message. Got title: '{alert_title}', message: '{alert_message}'")
            
            # Verify the second grade was not added (still only 1 row)
            filled_rows_after = self._get_number_of_filled_grade_rows()
            self.assertEqual(filled_rows_after, 1, f"Expected still only 1 filled row after attempting to add grade exceeding 100%, found {filled_rows_after}")
            
            logger.info(f"Test {test_name} passed - alert shown correctly when percentage exceeds 100%")
            
        except AssertionError as e:
            logger.error(f"AssertionError in {test_name}: {e}", exc_info=True)
            self._take_screenshot(f"{test_name}_assertion_error")
            self.fail(f"AssertionError in {test_name}: {e}")
        except Exception as e:
            logger.error(f"Exception in {test_name}: {e}", exc_info=True)
            self._take_screenshot(f"{test_name}_exception")
            self.fail(f"Exception in {test_name}: {e}")

    def test_us10_prevent_calculation_if_total_percentage_exceeds_100(self):
        """Tests that an alert is shown when attempting to calculate with grades whose total percentage exceeds 100%."""
        test_name = self._testMethodName
        logger.info(f"Running test: {test_name}")
        
        try:
            # Set up a special scenario by directly inserting values into localStorage 
            # that would make the total percentage exceed 100%
            # This is to bypass the UI validation when adding grades
            script = """
            localStorage.setItem('grades', JSON.stringify([
                { grade: 4.0, percentage: 60 },
                { grade: 3.5, percentage: 50 }
            ]));
            return localStorage.getItem('grades');
            """
            result = self.driver.execute_script(script)
            logger.info(f"Set up grades in localStorage with total percentage exceeding 100%: {result}")
            
            # Refresh the page to load the grades from localStorage
            self.driver.refresh()
            self.wait_long.until(EC.presence_of_element_located((By.CSS_SELECTOR, self.HOME_CONTAINER_SELECTOR)))
            
            # Verify the grades were loaded (should show 2 rows with values)
            filled_rows = self._get_number_of_filled_grade_rows()
            self.assertEqual(filled_rows, 2, f"Expected 2 filled rows after loading grades from localStorage, found {filled_rows}")
            
            # Try to click calculate button
            try:
                calculate_button = self.wait_long.until(EC.element_to_be_clickable((By.CSS_SELECTOR, self.CALCULATE_BUTTON_SELECTOR)))
                calculate_button.click()
                logger.info("Clicked calculate button with grades exceeding 100%.")
                
                # Check for an alert indicating the total exceeds 100%
                alert_present, alert_title, alert_message, alert_matches = self._check_for_alert(
                    expected_message_part="El porcentaje total no puede superar el 100%")
                    
                # Assert the alert was shown with the expected message
                self.assertTrue(alert_present, "Alert should be present when calculating with percentage that exceeds 100%")
                self.assertTrue(alert_matches, f"Alert should contain expected message. Got title: '{alert_title}', message: '{alert_message}'")
                
                # Verify we did not navigate to the result page
                time.sleep(0.5) # Wait to ensure no navigation occurs
                try:
                    result_page_present = self.driver.find_element(By.CSS_SELECTOR, self.RESULT_PAGE_CONTAINER_SELECTOR).is_displayed()
                    self.assertFalse(result_page_present, "Should not navigate to result page when percentage exceeds 100%")
                except NoSuchElementException:
                    # This is expected - we should not be on the result page
                    home_page_present = self.driver.find_element(By.CSS_SELECTOR, self.HOME_CONTAINER_SELECTOR).is_displayed()
                    self.assertTrue(home_page_present, "Should remain on home page when percentage exceeds 100%")
                
                logger.info(f"Test {test_name} passed - alert shown correctly when calculating with percentage exceeding 100%")
                
            except TimeoutException:
                self._take_screenshot("calculate_button_timeout")
                self.fail("Timeout waiting for calculate button to be clickable.")
            
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
