import unittest
import os
import time
import re
import logging
import json # Added for parsing localStorage content

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class US08Tests(unittest.TestCase):
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

    # Selectors for results verification (from US4, US5, US6)
    CURRENT_AVERAGE_DISPLAY_SELECTOR = "p.result__card-current"
    REQUIRED_GRADE_DISPLAY_SELECTOR = "p.result__card-needed"
    FINAL_STATUS_DISPLAY_SELECTOR = "p.result__card-final" # Corrected based on previous step for US6

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

    def _set_approval_grade(self, approval_grade_value):
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
        if not hasattr(self, 'driver') or not self.driver:
            logger.error("Driver not available in _add_grade_and_percentage.")
            self.fail("Driver not available.")
            return

        try:
            self.wait_long.until(EC.presence_of_element_located((By.CSS_SELECTOR, self.HOME_CONTAINER_SELECTOR)))
        except TimeoutException:
            logger.error("Not on home page when trying to add grade.")
            self._take_screenshot("add_grade_not_on_home")
            self.fail("Not on home page for _add_grade_and_percentage")

        grade_rows = self.driver.find_elements(By.CSS_SELECTOR, self.GRADES_LIST_ITEM_SELECTOR)
        target_row_for_input = grade_rows[-1]

        try:
            grade_input_element = target_row_for_input.find_element(By.CSS_SELECTOR, self.GRADE_INPUT_SELECTOR)
            percentage_input_element = target_row_for_input.find_element(By.CSS_SELECTOR, self.PERCENTAGE_INPUT_SELECTOR)
            
            grade_input_element.clear()
            grade_input_element.send_keys(str(grade))
            percentage_input_element.clear()
            percentage_input_element.send_keys(str(percentage))
            logger.info(f"Entered Grade: {grade}, Percentage: {percentage} into the last row.")
            
            add_button_main = self.wait_long.until(EC.element_to_be_clickable((By.CSS_SELECTOR, self.ADD_GRADE_BUTTON_SELECTOR)))
            add_button_main.click()
            logger.info(f"Clicked main 'Add Grade' button to confirm entry.")
            time.sleep(0.5)
        except Exception as e:
            self._take_screenshot(f"error_adding_grade_percentage")
            logger.error(f"Generic error in _add_grade_and_percentage: {e}", exc_info=True)
            self.fail(f"Generic error adding grade/percentage: {e}")

    def _get_grades_from_ui(self):
        """Retrieves the current grades and percentages from the UI."""
        grades_data = []
        try:
            self.wait_long.until(EC.presence_of_element_located((By.CSS_SELECTOR, self.HOME_CONTAINER_SELECTOR)))
            grade_rows = self.driver.find_elements(By.CSS_SELECTOR, self.GRADES_LIST_ITEM_SELECTOR)
            logger.info(f"Found {len(grade_rows)} grade rows in UI for extraction.")
            for row in grade_rows:
                try:
                    grade_input = row.find_element(By.CSS_SELECTOR, self.GRADE_INPUT_SELECTOR)
                    percentage_input = row.find_element(By.CSS_SELECTOR, self.PERCENTAGE_INPUT_SELECTOR)
                    grade_value = grade_input.get_attribute("value")
                    percentage_value = percentage_input.get_attribute("value")
                    # Only add if both values are present (i.e., not an empty template row)
                    if grade_value and percentage_value:
                        grades_data.append({"grade": grade_value, "percentage": percentage_value})
                except NoSuchElementException:
                    # This might be an empty template row or a row without inputs, skip it
                    logger.info("Skipping a row during UI grade extraction, likely an empty template.")
                    continue
            logger.info(f"Extracted grades from UI: {grades_data}")
            return grades_data
        except Exception as e:
            logger.error(f"Error extracting grades from UI: {e}", exc_info=True)
            self._take_screenshot("get_grades_from_ui_error")
            return [] # Return empty list on error

    # --- Test Case for US08 ---
    def test_us08_data_persistence_on_reload(self):
        # Corresponds to Task 8.1
        test_name = self._testMethodName
        logger.info(f"Running test: {test_name}")
        try:
            # 1. Add two distinct grades
            self._add_grade_and_percentage("4.0", "30") # Grade 1
            self._add_grade_and_percentage("3.5", "30") # Grade 2
            
            # Small pause to ensure asynchronous operations like localStorage updates complete
            time.sleep(1.5) # Increased pause slightly

            # 2. Verify grades are in UI and attempt to get them from localStorage BEFORE refresh
            initial_grades_ui = self._get_grades_from_ui()
            self.assertEqual(len(initial_grades_ui), 2, f"Expected 2 grades in UI before reload, got {len(initial_grades_ui)}")

            grades_in_storage_before_reload_str = self.driver.execute_script("return localStorage.getItem('grades');")
            logger.info(f"LocalStorage 'grades' content BEFORE reload (raw string): {grades_in_storage_before_reload_str}")
            
            self.assertIsNotNone(grades_in_storage_before_reload_str, "Grades string should be in localStorage BEFORE reload.")
            
            parsed_grades_before_reload = None # Initialize to prevent unbound error
            try:
                parsed_grades_before_reload = json.loads(grades_in_storage_before_reload_str)
                logger.info(f"Parsed grades from localStorage BEFORE reload: {parsed_grades_before_reload}")
                self.assertIsInstance(parsed_grades_before_reload, list, "Parsed grades from localStorage should be a list.")
                
                actual_stored_grades = [g for g in parsed_grades_before_reload if g.get('grade') and g.get('percentage')]
                self.assertEqual(len(actual_stored_grades), 2, f"Expected 2 actual grades in localStorage BEFORE reload, found {len(actual_stored_grades)} in {parsed_grades_before_reload}")

            except json.JSONDecodeError as jde:
                logger.error(f"Failed to parse grades from localStorage BEFORE reload. Content: '{grades_in_storage_before_reload_str}'. Error: {jde}")
                self.fail(f"Grades in localStorage BEFORE reload were not valid JSON: {jde}")
            except AttributeError as ae: 
                 logger.error(f"Parsed grades from localStorage BEFORE reload had unexpected structure. Content: {parsed_grades_before_reload}. Error: {ae}")
                 self.fail(f"Parsed grades from localStorage BEFORE reload had unexpected structure: {ae}")


            # 3. Reload the page
            logger.info("Reloading the page...")
            self.driver.refresh()

            # 4. Wait for the home page to be fully loaded after refresh
            # Ensure home container is present
            self.wait_long.until(EC.presence_of_element_located((By.CSS_SELECTOR, self.HOME_CONTAINER_SELECTOR)))
            # Add a slight delay for React hydration and scripts to run, potentially re-populating from localStorage
            time.sleep(1.5) # Increased pause slightly
            logger.info("Page reloaded and home container is present.")
            
            # 5. Verify grades are still in localStorage AFTER refresh
            grades_in_storage_after_reload_str = self.driver.execute_script("return localStorage.getItem('grades');")
            logger.info(f"LocalStorage 'grades' content AFTER reload (raw string): {grades_in_storage_after_reload_str}")
            self.assertIsNotNone(grades_in_storage_after_reload_str, "Grades string should be in localStorage AFTER reload.")
            
            parsed_grades_after_reload = None # Initialize to prevent unbound error
            try:
                parsed_grades_after_reload = json.loads(grades_in_storage_after_reload_str)
                logger.info(f"Parsed grades from localStorage AFTER reload: {parsed_grades_after_reload}")
                self.assertIsInstance(parsed_grades_after_reload, list, "Parsed grades from localStorage after reload should be a list.")
                actual_stored_grades_after = [g for g in parsed_grades_after_reload if g.get('grade') and g.get('percentage')]
                self.assertEqual(len(actual_stored_grades_after), 2, f"Expected 2 actual grades in localStorage AFTER reload, found {len(actual_stored_grades_after)} in {parsed_grades_after_reload}")

            except json.JSONDecodeError as jde:
                logger.error(f"Failed to parse grades from localStorage AFTER reload. Content: '{grades_in_storage_after_reload_str}'. Error: {jde}")
                self.fail(f"Grades in localStorage AFTER reload were not valid JSON: {jde}")
            except AttributeError as ae: 
                 logger.error(f"Parsed grades from localStorage AFTER reload had unexpected structure. Content: {parsed_grades_after_reload}. Error: {ae}")
                 self.fail(f"Parsed grades from localStorage AFTER reload had unexpected structure: {ae}")

            # 6. Verify grades are correctly displayed in the UI after reload
            grades_ui_after_reload = self._get_grades_from_ui()
            logger.info(f"Grades found in UI after reload: {grades_ui_after_reload}")
            self.assertEqual(len(grades_ui_after_reload), 2, f"Expected 2 grades in UI after reload, got {len(grades_ui_after_reload)}")

            # Optional: Compare actual grade values if _get_grades_from_ui returns them
            # For simplicity, we are just checking counts here as per original test logic.
            # self.assertEqual(initial_grades_ui, grades_ui_after_reload, "Grades in UI should match before and after reload")

            logger.info(f"Test {test_name} passed. Data persistence on reload verified.")

        except AssertionError as e:
            logger.error(f"AssertionError in {test_name}: {e}", exc_info=True)
            self._take_screenshot(f"{test_name}_assertion_error")
            # Log localStorage content for debugging if persistence fails
            try:
                grades_local_storage = self.driver.execute_script("return localStorage.getItem('grades');")
                logger.info(f"LocalStorage 'grades' content on failure: {grades_local_storage}")
            except Exception as ls_e:
                logger.error(f"Could not retrieve localStorage content: {ls_e}")
            self.fail(f"AssertionError in {test_name}: {e}")
        except Exception as e:
            logger.error(f"Exception in {test_name}: {e}", exc_info=True)
            self._take_screenshot(f"{test_name}_exception")
            self.fail(f"Exception in {test_name}: {e}")

if __name__ == '__main__':
    unittest.main(verbosity=2)
