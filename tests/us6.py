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

class US06Tests(unittest.TestCase):
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
    
    # Selector for US06 - Final Estimated Status
    FINAL_STATUS_DISPLAY_SELECTOR = "p.result__card-final" # Updated selector based on result.jsx (p class="result__card-final")

    # Selectors needed for setting up scenarios (from US05, though not directly tested here)
    REQUIRED_GRADE_DISPLAY_SELECTOR = "p.result__card-needed" 
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

        on_result_page = False
        try:
            if self.driver.find_element(By.CSS_SELECTOR, self.RESULT_PAGE_CONTAINER_SELECTOR).is_displayed():
                on_result_page = True
        except NoSuchElementException:
            on_result_page = False

        if on_result_page:
            logger.info("Currently on result page, navigating back to home to add grades.")
            try:
                nav_back_button = self.wait_short.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, self.NAV_BACK_BUTTON_SELECTOR))
                )
            except TimeoutException:
                try:
                    nav_back_button = self.wait_long.until(
                        EC.element_to_be_clickable((By.XPATH, self.NAV_BACK_BUTTON_XPATH))
                    )
                except TimeoutException:
                    nav_bar = self.wait_long.until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "nav.nav-bar"))
                    )
                    nav_buttons = nav_bar.find_elements(By.TAG_NAME, "button")
                    if nav_buttons:
                        nav_back_button = nav_buttons[0]
                    else:
                        self._take_screenshot("no_buttons_in_nav_bar_add_grade")
                        self.fail("No buttons found in nav bar when trying to navigate back")
            nav_back_button.click()
            self.wait_long.until(EC.presence_of_element_located((By.CSS_SELECTOR, self.HOME_CONTAINER_SELECTOR)))
            time.sleep(0.5)

        grade_rows = self.driver.find_elements(By.CSS_SELECTOR, self.GRADES_LIST_ITEM_SELECTOR)
        need_new_row = True
        if grade_rows:
            last_row = grade_rows[-1]
            try:
                grade_input = last_row.find_element(By.CSS_SELECTOR, self.GRADE_INPUT_SELECTOR)
                percentage_input = last_row.find_element(By.CSS_SELECTOR, self.PERCENTAGE_INPUT_SELECTOR)
                if not grade_input.get_attribute("value") and not percentage_input.get_attribute("value"):
                    need_new_row = False
            except NoSuchElementException:
                need_new_row = True
        
        if need_new_row or not grade_rows:
            add_button = self.wait_long.until(EC.element_to_be_clickable((By.CSS_SELECTOR, self.ADD_GRADE_BUTTON_SELECTOR)))
            add_button.click()
            time.sleep(0.5)
            grade_rows = self.driver.find_elements(By.CSS_SELECTOR, self.GRADES_LIST_ITEM_SELECTOR)
            if not grade_rows:
                self._take_screenshot("failed_to_add_grade_row")
                self.fail("Failed to add grade row")
        
        last_row = grade_rows[-1]
        try:
            grade_input_element = last_row.find_element(By.CSS_SELECTOR, self.GRADE_INPUT_SELECTOR)
            percentage_input_element = last_row.find_element(By.CSS_SELECTOR, self.PERCENTAGE_INPUT_SELECTOR)
            
            grade_input_element.clear()
            grade_input_element.send_keys(str(grade))
            percentage_input_element.clear()
            percentage_input_element.send_keys(str(percentage))
            
            add_button = self.wait_long.until(EC.element_to_be_clickable((By.CSS_SELECTOR, self.ADD_GRADE_BUTTON_SELECTOR)))
            add_button.click()
            time.sleep(0.5)
        except NoSuchElementException as e:
            self._take_screenshot("input_elements_not_found")
            self.fail(f"Input elements not found: {e}")
            
    def _click_calculate_and_wait_for_result_page(self):
        calculate_button = self.wait_long.until(EC.element_to_be_clickable((By.CSS_SELECTOR, self.CALCULATE_BUTTON_SELECTOR)))
        calculate_button.click()
        self.wait_long.until(EC.presence_of_element_located((By.CSS_SELECTOR, self.RESULT_PAGE_CONTAINER_SELECTOR)))
        logger.info("Clicked 'Calcular' and result page container is present.")

    def _get_final_status_message(self):
        """Extracts and returns the final estimated status message from the result page."""
        raw_text = ""
        try:
            self.wait_long.until(EC.presence_of_element_located((By.CSS_SELECTOR, self.RESULT_PAGE_CONTAINER_SELECTOR)))
            
            status_element = self.wait_long.until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, self.FINAL_STATUS_DISPLAY_SELECTOR))
            )
            time.sleep(0.2) # Allow text to stabilize
            raw_text = status_element.text.strip()
            logger.info(f"Raw final status message text: '{raw_text}'")

            if not raw_text:
                logger.warning("Final status message text is empty.")
                self._take_screenshot("empty_final_status_message")
                return "Error: Empty Value"
            
            # Expected values: "Aprobado", "En riesgo", "No aprueba"
            return raw_text

        except TimeoutException:
            logger.error(f"Timeout waiting for final status display: {self.FINAL_STATUS_DISPLAY_SELECTOR}")
            self._take_screenshot("final_status_timeout")
            return "Error: Timeout"
        except Exception as e:
            logger.error(f"Error getting final status message: {e}", exc_info=True)
            self._take_screenshot("get_final_status_error")
            return "Error: General"

    # --- Test Cases for US06 Task 6.3 ---

    def test_us06_verify_final_status_aprobado(self):
        # Scenario "Aprobado": Input grades leading to an "already approved" state (Task 5.3).
        # Verify the status displays "Aprobado".
        # Grades: Grade: "4.0", Percentage: "80%". Approval grade: 3.0
        test_name = self._testMethodName
        logger.info(f"Running test: {test_name}")
        try:
            self._add_grade_and_percentage("4.0", "80")
            self._click_calculate_and_wait_for_result_page()
            
            final_status = self._get_final_status_message()
            self.assertEqual(final_status, "Aprobado", f"Test {test_name}: Expected 'Aprobado', got '{final_status}'")
            logger.info(f"Test {test_name} passed. Final status: {final_status}")

        except AssertionError as e:
            logger.error(f"AssertionError in {test_name}: {e}", exc_info=True)
            self._take_screenshot(f"{test_name}_assertion_error")
            self.fail(f"AssertionError in {test_name}: {e}")
        except Exception as e:
            logger.error(f"Exception in {test_name}: {e}", exc_info=True)
            self._take_screenshot(f"{test_name}_exception")
            self.fail(f"Exception in {test_name}: {e}")

    def test_us06_verify_final_status_en_riesgo(self):
        # Scenario "En riesgo": Input grades leading to a "required grade" that is achievable (Task 5.1).
        # Verify the status displays "En riesgo".
        # Grades: Grade: "2.0", Percentage: "50%". Approval grade: 3.0. (Requires 4.0)
        test_name = self._testMethodName
        logger.info(f"Running test: {test_name}")
        try:
            self._add_grade_and_percentage("2.0", "50")
            self._click_calculate_and_wait_for_result_page()

            final_status = self._get_final_status_message()
            self.assertEqual(final_status, "En riesgo", f"Test {test_name}: Expected 'En riesgo', got '{final_status}'")
            logger.info(f"Test {test_name} passed. Final status: {final_status}")

        except AssertionError as e:
            logger.error(f"AssertionError in {test_name}: {e}", exc_info=True)
            self._take_screenshot(f"{test_name}_assertion_error")
            self.fail(f"AssertionError in {test_name}: {e}")
        except Exception as e:
            logger.error(f"Exception in {test_name}: {e}", exc_info=True)
            self._take_screenshot(f"{test_name}_exception")
            self.fail(f"Exception in {test_name}: {e}")

    def test_us06_verify_final_status_no_aprueba(self):
        # Scenario "No aprueba": Input grades leading to an "impossible to approve" state (Task 5.2).
        # Verify the status displays "No aprueba".
        # Grades: Grade: "1.0", Percentage: "80%". Approval grade: 3.0. (Requires 11.0)
        test_name = self._testMethodName
        logger.info(f"Running test: {test_name}")
        try:
            self._add_grade_and_percentage("1.0", "80")
            self._click_calculate_and_wait_for_result_page()

            final_status = self._get_final_status_message()
            self.assertEqual(final_status, "No aprueba", f"Test {test_name}: Expected 'No aprueba', got '{final_status}'")
            logger.info(f"Test {test_name} passed. Final status: {final_status}")

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
