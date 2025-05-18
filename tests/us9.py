import unittest
import os
import time
import re
import logging
import json # For localStorage interaction

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class US09Tests(unittest.TestCase):
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

    # Selectors for results verification
    REQUIRED_GRADE_DISPLAY_SELECTOR = "p.result__card-needed"

    # Selectors for US09 - Settings page
    SETTINGS_NAV_BUTTON_XPATH = "//button[contains(@class, 'nav-bar__button') and .//span[contains(@class, 'settings-icon')]/svg[contains(@class, 'lucide-settings')]]"
    APPROVAL_GRADE_INPUT_SELECTOR = "input.settings__input[type='number']" # As per selenium-test-dev.md
    SETTINGS_PAGE_IDENTIFIER = "div.settings__container" # Assuming a container for settings page

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

    def _initial_setup(self):
        # Standard initial setup, navigates to home page, handles first time alert.
        if not hasattr(self, 'driver') or not self.driver:
            logger.error("Driver not initialized in _initial_setup. Aborting setup.")
            self.fail("Driver not initialized for test setup.")
            return

        self.driver.get(self.BASE_URL)
        logger.info(f"Navigated to base URL: {self.BASE_URL}")
        time.sleep(0.5) # Small pause for page to load initially

        # Check if first time alert is present and click it
        try:
            logger.info(f"Attempting to handle first-time alert with button '{self.FIRST_TIME_ALERT_BUTTON_SELECTOR}'.")
            alert_button = WebDriverWait(self.driver, 7).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, self.FIRST_TIME_ALERT_BUTTON_SELECTOR))
            )
            alert_button.click()
            logger.info(f"Clicked first-time alert button: '{self.FIRST_TIME_ALERT_BUTTON_SELECTOR}'.")
            WebDriverWait(self.driver, 5).until(
                EC.invisibility_of_element_located((By.CSS_SELECTOR, self.ALERT_OVERLAY_SELECTOR))
            )
            logger.info(f"Alert overlay '{self.ALERT_OVERLAY_SELECTOR}' is no longer visible. App should be on Settings page.")
            # Now on settings page, navigate back to home for tests that start there
            self._navigate_to_home_from_settings() # Ensure we are back home

        except TimeoutException:
            logger.info("First-time user alert not found or timed out. Assuming already handled or not present.")
            # Ensure we are on the home page if the alert wasn't there
            try:
                self.wait_long.until(EC.presence_of_element_located((By.CSS_SELECTOR, self.HOME_CONTAINER_SELECTOR)))
                logger.info("Confirmed on Home page.")
            except TimeoutException:
                logger.error("Failed to confirm presence on Home page after initial_setup.")
                self._take_screenshot("initial_setup_not_on_home")
                # self.fail("Could not ensure presence on the Home page during initial setup.")
                # Attempt to set localStorage directly to bypass first time if stuck
                logger.info("Attempting to set localStorage isFirstTime to false and refreshing.")
                self.driver.execute_script("localStorage.setItem('isFirstTime', 'false');")
                self.driver.refresh()
                try:
                    self.wait_long.until(EC.presence_of_element_located((By.CSS_SELECTOR, self.HOME_CONTAINER_SELECTOR)))
                    logger.info("Successfully navigated to Home page after setting localStorage.")
                except TimeoutException:
                    logger.error("Still not on home page after localStorage trick.")
                    self._take_screenshot("initial_setup_home_failed_hard")
                    self.fail("Failed to reach home page in initial_setup.")
        except Exception as e:
            logger.error(f"An unexpected error occurred during initial setup: {e}", exc_info=True)
            self._take_screenshot("initial_setup_error")
            self.fail(f"Unexpected error during initial setup: {e}")
        
        # Set a default approval grade for consistency in tests unless overridden
        self._set_approval_grade_via_js("3.0")

    def _navigate_to_settings(self):
        logger.info("Navigating to Settings page.")
        try:
            settings_button = self.wait_long.until(
                EC.element_to_be_clickable((By.XPATH, self.SETTINGS_NAV_BUTTON_XPATH))
            )
            settings_button.click()
            self.wait_long.until(EC.presence_of_element_located((By.CSS_SELECTOR, self.SETTINGS_PAGE_IDENTIFIER)))
            self.wait_long.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.APPROVAL_GRADE_INPUT_SELECTOR)))
            logger.info("Successfully navigated to Settings page.")
        except TimeoutException:
            self._take_screenshot("navigate_to_settings_timeout")
            self.fail("Timeout navigating to Settings page or finding approval grade input.")

    def _navigate_to_home_from_settings(self):
        logger.info("Navigating to Home page from Settings.")
        try:
            # Assuming the standard back button is used
            nav_back_button = self.wait_long.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, self.NAV_BACK_BUTTON_SELECTOR))
            )
            nav_back_button.click()
            self.wait_long.until(EC.presence_of_element_located((By.CSS_SELECTOR, self.HOME_CONTAINER_SELECTOR)))
            logger.info("Successfully navigated back to Home page from Settings.")
        except TimeoutException:
            self._take_screenshot("navigate_home_from_settings_timeout")
            self.fail("Timeout navigating to Home page from Settings.")

    def _set_approval_grade_in_settings_ui(self, new_approval_grade):
        logger.info(f"Setting approval grade to {new_approval_grade} via UI.")
        self._navigate_to_settings()
        try:
            approval_input = self.wait_long.until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, self.APPROVAL_GRADE_INPUT_SELECTOR))
            )
            approval_input.clear() # Clear existing value
            approval_input.send_keys(str(new_approval_grade))
            logger.info(f"Set approval grade input to: {new_approval_grade}")
            # Add a small delay or check for a confirmation if any
            time.sleep(0.5) 
            # Important: Navigate away or save settings if needed for them to apply.
            # For this app, changing the input and navigating away seems to save it (due to localStorage binding).
            self._navigate_to_home_from_settings() # This should trigger the save if it happens on blur/navigation
            # Verify with JS if necessary, or by observing calculation changes
            self.driver.refresh() # Refresh to ensure settings are loaded from localStorage
            self.wait_long.until(EC.presence_of_element_located((By.CSS_SELECTOR, self.HOME_CONTAINER_SELECTOR)))
            logger.info("Refreshed home page after attempting to set approval grade via UI.")

        except TimeoutException:
            self._take_screenshot("set_approval_grade_ui_timeout")
            self.fail(f"Timeout setting approval grade to {new_approval_grade} in UI.")
        except Exception as e:
            self._take_screenshot("set_approval_grade_ui_error")
            logger.error(f"Error setting approval grade in UI: {e}", exc_info=True)
            self.fail(f"Error setting approval grade in UI: {e}")

    def _set_approval_grade_via_js(self, approval_grade_value, min_val=0, max_val=5):
        # More reliable method from US05, kept for direct setting if UI is problematic
        logger.info(f"Setting approval grade to: {approval_grade_value} via JavaScript injection")
        script = f"""
        localStorage.setItem('settings', JSON.stringify({{
            minAcceptValue: parseFloat({approval_grade_value}),
            minValue: {min_val},
            maxValue: {max_val}
        }}));
        localStorage.setItem("isFirstTime", "false");
        // Return a value to confirm execution if needed, e.g., the new setting
        return localStorage.getItem('settings');
        """
        try:
            self.driver.execute_script(script)
            logger.info(f"Settings updated via JavaScript. Approval grade set to: {approval_grade_value}")
            # Refresh the page to apply the settings from localStorage
            current_url = self.driver.current_url
            self.driver.refresh()
            # Wait for either home or settings page to load after refresh, depending on context
            if "settings" in current_url.lower(): # if we were on settings page
                 self.wait_long.until(EC.presence_of_element_located((By.CSS_SELECTOR, self.SETTINGS_PAGE_IDENTIFIER)))
            else: # otherwise assume home page
                 self.wait_long.until(EC.presence_of_element_located((By.CSS_SELECTOR, self.HOME_CONTAINER_SELECTOR)))
            logger.info(f"Page refreshed after setting approval grade via JS. Current URL: {self.driver.current_url}")
            time.sleep(0.5) # allow UI to settle
        except Exception as e:
            logger.error(f"Error executing JS to set approval grade: {e}", exc_info=True)
            self._take_screenshot("set_approval_grade_js_error")
            # self.fail(f"Failed to set approval grade via JS: {e}") # Soft fail if used as helper

    def _add_grade_and_percentage(self, grade, percentage):
        # Simplified version from US07/US08
        if not hasattr(self, 'driver') or not self.driver:
            self.fail("Driver not available.")
        try:
            self.wait_long.until(EC.presence_of_element_located((By.CSS_SELECTOR, self.HOME_CONTAINER_SELECTOR)))
        except TimeoutException:
            self.fail("Not on home page for _add_grade_and_percentage")

        grade_rows = self.driver.find_elements(By.CSS_SELECTOR, self.GRADES_LIST_ITEM_SELECTOR)
        target_row_for_input = grade_rows[-1]
        try:
            grade_input_element = target_row_for_input.find_element(By.CSS_SELECTOR, self.GRADE_INPUT_SELECTOR)
            percentage_input_element = target_row_for_input.find_element(By.CSS_SELECTOR, self.PERCENTAGE_INPUT_SELECTOR)
            grade_input_element.clear(); grade_input_element.send_keys(str(grade))
            percentage_input_element.clear(); percentage_input_element.send_keys(str(percentage))
            add_button_main = self.wait_long.until(EC.element_to_be_clickable((By.CSS_SELECTOR, self.ADD_GRADE_BUTTON_SELECTOR)))
            add_button_main.click()
            time.sleep(0.5)
        except Exception as e:
            self.fail(f"Error adding grade/percentage: {e}")

    def _click_calculate_and_wait_for_result_page(self):
        try:
            calculate_button = self.wait_long.until(EC.element_to_be_clickable((By.CSS_SELECTOR, self.CALCULATE_BUTTON_SELECTOR)))
            calculate_button.click()
            self.wait_long.until(EC.presence_of_element_located((By.CSS_SELECTOR, self.RESULT_PAGE_CONTAINER_SELECTOR)))
        except TimeoutException:
            self.fail("Timeout clicking calculate or waiting for result page.")

    def _get_required_grade_value_from_display(self):
        # Adapted from US05, focuses on extracting the numeric value or specific messages
        raw_text = ""
        try:
            self.wait_long.until(EC.presence_of_element_located((By.CSS_SELECTOR, self.RESULT_PAGE_CONTAINER_SELECTOR)))
            display_element = self.wait_long.until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, self.REQUIRED_GRADE_DISPLAY_SELECTOR))
            )
            time.sleep(0.3) # Increased sleep for text stabilization
            raw_text = display_element.text.strip()
            logger.info(f"Raw required grade/message text: '{raw_text}'")

            if not raw_text: return "Error: Empty Value"
            if "Ya ha aprobado la materia" in raw_text or "Ya se ha aprobado la materia" in raw_text: return "Already Approved"
            if "No es posible aprobar la materia" in raw_text: return "Impossible to Approve"
            
            match = re.search(r"Necesitas (-?\d+\.?\d*|-?\.\d+) en el", raw_text)
            if match:
                grade_str = match.group(1)
                try:
                    return float(grade_str)
                except ValueError:
                    logger.error(f"Could not convert extracted grade string '{grade_str}' to float.")
                    return f"Error: Conversion '{grade_str}'"
            else:
                # Handle cases like "Necesitas 11 en el..." or "Necesitas -1 en el..." which might indicate impossibility
                if "Necesitas 11 en el" in raw_text or "Necesitas -1 en el" in raw_text: # Example of impossible values
                    logger.warning(f"Found specific impossible grade pattern: '{raw_text}'")
                    return "Impossible to Approve" # Treat as impossible
                logger.error(f"Could not parse required grade from text: '{raw_text}'")
                return "Error: Parse"
        except TimeoutException:
            return "Error: Timeout"
        except Exception as e:
            logger.error(f"General error in _get_required_grade_value_from_display: {e}", exc_info=True)
            return "Error: General"

    # --- Test Case for US09 ---
    def test_us09_change_min_approval_grade_and_verify_calculations(self):
        # Corresponds to Task 9.1
        test_name = self._testMethodName
        logger.info(f"Running test: {test_name}")

        # Scenario Data:
        # 1. Initial state: Approval grade 3.0 (default or set in _initial_setup)
        #    Add grade: 2.0, percentage: 50%. Expected required: 4.0
        # 2. Change approval grade to 4.0 via UI.
        #    With same grade (2.0, 50%), Expected required: 6.0 (which is > 5.0, so "Impossible to Approve")
        # 3. Change approval grade to 2.5 via JS (for robustness).
        #    With same grade (2.0, 50%), Expected required: 3.0

        try:
            # --- Step 1: Initial calculation with default approval grade (3.0) ---
            logger.info("Step 1: Calculation with default approval grade (3.0)")
            self._set_approval_grade_via_js("3.0") # Ensure it is 3.0
            self._add_grade_and_percentage("2.0", "50")
            self._click_calculate_and_wait_for_result_page()
            
            required_grade_step1 = self._get_required_grade_value_from_display()
            self.assertAlmostEqual(required_grade_step1, 4.0, places=1, 
                                 msg=f"Step 1: Expected required grade ~4.0 with approval 3.0. Got: {required_grade_step1}")
            logger.info(f"Step 1 Passed. Required grade with approval 3.0: {required_grade_step1}")
            
            # Navigate back to home to clear state for next calculation
            self.driver.find_element(By.CSS_SELECTOR, self.NAV_BACK_BUTTON_SELECTOR).click()
            self.wait_long.until(EC.presence_of_element_located((By.CSS_SELECTOR, self.HOME_CONTAINER_SELECTOR)))
            # Clear existing grades by resetting via JS (simpler than UI reset for this test)
            self.driver.execute_script("localStorage.removeItem('grades');")
            self.driver.refresh()
            self.wait_long.until(EC.presence_of_element_located((By.CSS_SELECTOR, self.HOME_CONTAINER_SELECTOR)))
            time.sleep(0.5)

            # --- Step 2: Change approval grade to 4.0 (via UI) and recalculate ---
            logger.info("Step 2: Changing approval grade to 4.0 via UI")
            self._set_approval_grade_in_settings_ui("4.0") # This navigates to settings, changes, and comes back home & refreshes
            
            self._add_grade_and_percentage("2.0", "50") # Same grades as before
            self._click_calculate_and_wait_for_result_page()
            
            required_grade_step2 = self._get_required_grade_value_from_display()
            # Formula: (4.0 * 100 - (2.0 * 50)) / 50 = (400 - 100) / 50 = 300 / 50 = 6.0
            # Since 6.0 > 5.0 (max grade), it should be impossible.
            self.assertEqual(required_grade_step2, "Impossible to Approve",
                             msg=f"Step 2: Expected 'Impossible to Approve' with approval 4.0. Got: {required_grade_step2}")
            logger.info(f"Step 2 Passed. Status with approval 4.0: {required_grade_step2}")

            # Navigate back and clear for next step
            self.driver.find_element(By.CSS_SELECTOR, self.NAV_BACK_BUTTON_SELECTOR).click()
            self.wait_long.until(EC.presence_of_element_located((By.CSS_SELECTOR, self.HOME_CONTAINER_SELECTOR)))
            self.driver.execute_script("localStorage.removeItem('grades');")
            self.driver.refresh()
            self.wait_long.until(EC.presence_of_element_located((By.CSS_SELECTOR, self.HOME_CONTAINER_SELECTOR)))
            time.sleep(0.5)

            # --- Step 3: Change approval grade to 2.5 (via JS) and recalculate ---
            logger.info("Step 3: Changing approval grade to 2.5 via JS")
            self._set_approval_grade_via_js("2.5") # This refreshes the page
            
            self._add_grade_and_percentage("2.0", "50") # Same grades again
            self._click_calculate_and_wait_for_result_page()
            
            required_grade_step3 = self._get_required_grade_value_from_display()
            # Formula: (2.5 * 100 - (2.0 * 50)) / 50 = (250 - 100) / 50 = 150 / 50 = 3.0
            self.assertAlmostEqual(required_grade_step3, 3.0, places=1,
                                 msg=f"Step 3: Expected required grade ~3.0 with approval 2.5. Got: {required_grade_step3}")
            logger.info(f"Step 3 Passed. Required grade with approval 2.5: {required_grade_step3}")

            logger.info(f"Test {test_name} completed successfully.")

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
