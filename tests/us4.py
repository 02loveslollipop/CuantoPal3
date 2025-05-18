\
import unittest
import os
import time
import re # Added for parsing
import logging # Added for logging

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class US04Tests(unittest.TestCase):
    BASE_URL = "http://localhost:3000"
    GRADE_INPUT_SELECTOR = "input.home__input[placeholder='0.0'][type='number']"
    PERCENTAGE_INPUT_SELECTOR = "input.home__input[placeholder='0'][type='number']"
    ADD_GRADE_BUTTON_SELECTOR = "button.home__add-button" # General button to add a new grade entry/row
    GRADES_LIST_ITEM_SELECTOR = "div.home__grades-container > div.home__grade-row"
    CALCULATE_BUTTON_SELECTOR = "button.home__calculate-button"
    CURRENT_AVERAGE_DISPLAY_SELECTOR = "p.result__card-current"
    RESULT_PAGE_CONTAINER_SELECTOR = "div.result" 
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
        if not hasattr(self, 'driver') or not self.driver:
            logger.info("WebDriver not set by fixture, attempting fallback setup for direct unittest execution.")
            try:
                options = webdriver.ChromeOptions()
                # options.add_argument('--headless')
                # options.add_argument('--disable-gpu')
                # options.add_argument('--window-size=1920,1080')
                self.driver = webdriver.Chrome(options=options)
                self.is_driver_managed_by_fallback = True
                logger.info("Fallback WebDriver initialized for direct unittest execution.")
            except Exception as e:
                logger.error(f"Failed to initialize fallback WebDriver: {e}")
                self.fail(f"Failed to initialize fallback WebDriver: {e}")
        else:
            logger.info("WebDriver already set, likely by a pytest fixture.")
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
            
            nav_back_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, self.NAV_BACK_BUTTON_XPATH))
            )
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

    def _add_grade_and_percentage(self, grade, percentage):
        if not hasattr(self, 'driver') or not self.driver:
            logger.error("Driver not available in _add_grade_and_percentage.")
            self.fail("Driver not available.")
            return

        on_result_page = False
        try:
            # Check if the result page container is present
            if self.driver.find_element(By.CSS_SELECTOR, self.RESULT_PAGE_CONTAINER_SELECTOR).is_displayed():
                on_result_page = True
        except NoSuchElementException:
            on_result_page = False # Not on result page

        if on_result_page:
            logger.info("Currently on result page (detected by element presence), navigating back to home to add grades.")
            nav_back_button = self.wait_long.until(
                EC.element_to_be_clickable((By.XPATH, self.NAV_BACK_BUTTON_XPATH))
            )
            nav_back_button.click()
            self.wait_long.until(EC.presence_of_element_located((By.CSS_SELECTOR, self.HOME_CONTAINER_SELECTOR)))
            logger.info("Navigated back to home page.")

        grade_rows = self.driver.find_elements(By.CSS_SELECTOR, self.GRADES_LIST_ITEM_SELECTOR)
        if not grade_rows:
            logger.warning("No grade rows found. Attempting to add one by clicking the global 'Add Grade' button.")
            self._take_screenshot("no_grade_rows_found")
            try:
                # This assumes ADD_GRADE_BUTTON_SELECTOR is the button that adds a new empty row for input
                add_button_global = self.wait_long.until(EC.element_to_be_clickable((By.CSS_SELECTOR, self.ADD_GRADE_BUTTON_SELECTOR)))
                add_button_global.click()
                time.sleep(0.5) # Allow time for the row to be added dynamically
                grade_rows = self.driver.find_elements(By.CSS_SELECTOR, self.GRADES_LIST_ITEM_SELECTOR)
                if not grade_rows:
                    logger.error("Still no grade rows found after attempting to add one.")
                    self._take_screenshot("failed_to_add_initial_row")
                    self.fail("Still no grade rows found after attempting to add one.")
                    return
                logger.info(f"Successfully added an initial grade row. Now {len(grade_rows)} rows.")
            except Exception as ex:
                logger.error(f"Failed to create an initial grade row by clicking add button: {ex}", exc_info=True)
                self._take_screenshot("create_initial_row_exception")
                self.fail(f"Failed to create an initial grade row: {ex}")
                return

        last_row = grade_rows[-1]
        logger.info(f"Targeting the last of {len(grade_rows)} grade rows for input.")

        try:
            grade_input_element = last_row.find_element(By.CSS_SELECTOR, self.GRADE_INPUT_SELECTOR)
            percentage_input_element = last_row.find_element(By.CSS_SELECTOR, self.PERCENTAGE_INPUT_SELECTOR)
        except NoSuchElementException as e:
            logger.error(f"Could not find grade or percentage input in the last row: {e}")
            logger.info(f"HTML of last row: {last_row.get_attribute('outerHTML')}")
            self._take_screenshot("input_not_found_in_last_row")
            self.fail(f"Input elements not found in the last row: {e}")
            return
        
        # Assuming ADD_GRADE_BUTTON_SELECTOR is the button to confirm/add the currently entered grade,
        # not necessarily the one that creates a new blank row if that's different.
        # If the app auto-adds a new row upon filling the last one and clicking a general "add" button, this is fine.
        add_button = self.wait_long.until(EC.element_to_be_clickable((By.CSS_SELECTOR, self.ADD_GRADE_BUTTON_SELECTOR)))

        grade_input_element.clear()
        grade_input_element.send_keys(str(grade))
        percentage_input_element.clear()
        percentage_input_element.send_keys(str(percentage))
        
        add_button.click() 
        logger.info(f"Clicked 'Agregar nota' after filling grade: {grade}, percentage: {percentage} into the last available row.")
        time.sleep(0.5) # Brief pause for UI to update, e.g., adding a new empty row

    def _get_current_weighted_average(self):
        raw_text = ""
        try:
            average_element = self.wait_long.until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, self.CURRENT_AVERAGE_DISPLAY_SELECTOR))
            )
            time.sleep(0.2) 
            
            raw_text = average_element.text.strip()
            attempts = 0
            while raw_text == "" and attempts < 5: 
                logger.info(f"Average text is empty, attempt {attempts+1}/5. Waiting and retrying...")
                time.sleep(0.3)
                raw_text = average_element.text.strip()
                attempts += 1
            
            logger.info(f"Raw current weighted average text from result page: '{raw_text}'")
            if not raw_text:
                logger.warning("Current weighted average text is empty after retries on result page.")
                self._take_screenshot("empty_current_average_result_page")
                return "Error: Empty Value"

            # Regex to find a number (integer or float) after "promedio de "
            match = re.search(r"Actualmente tienes un promedio de (\d+\.?\d*|\.\d+) en el", raw_text)
            if match:
                grade_str = match.group(1)
                logger.info(f"Extracted grade string: '{grade_str}'")
                return float(grade_str)
            else:
                logger.error(f"Could not parse final grade from text: '{raw_text}'")
                self._take_screenshot("current_average_parse_error_result")
                return "Error: Parse"
        except TimeoutException:
            logger.error(f"Timeout waiting for result page elements or current weighted average display: {self.CURRENT_AVERAGE_DISPLAY_SELECTOR}")
            logger.info(f"Current URL: {self.driver.current_url}")
            # logger.info(f"Page source at timeout:\\n{self.driver.page_source[:2000]}") # Potentially too verbose
            self._take_screenshot("current_average_timeout_result_page")
            return "Error: Timeout"
        except ValueError:
            logger.error(f"Could not convert extracted grade string to float from '{raw_text}'.")
            self._take_screenshot("current_average_value_error_result")
            return "Error: Conversion"
        except Exception as e:
            logger.error(f"Error getting current weighted average from result page: {e}", exc_info=True)
            self._take_screenshot("get_current_average_error_result")
            return "Error: General"

    def test_us04_verify_calculation_of_current_weighted_average(self):
        test_name = self._testMethodName
        logger.info(f"Running test: {test_name}")

        try:
            # Ensure we start on the home page
            on_result_page_initial = False
            try:
                if self.driver.find_element(By.CSS_SELECTOR, self.RESULT_PAGE_CONTAINER_SELECTOR).is_displayed():
                    on_result_page_initial = True
            except NoSuchElementException:
                pass 

            if on_result_page_initial:
                logger.info("Initial state is result page, navigating back to home.")
                self.driver.find_element(By.XPATH, self.NAV_BACK_BUTTON_XPATH).click()
                self.wait_long.until(EC.presence_of_element_located((By.CSS_SELECTOR, self.HOME_CONTAINER_SELECTOR)))
            else:
                try:
                    self.wait_long.until(EC.presence_of_element_located((By.CSS_SELECTOR, self.HOME_CONTAINER_SELECTOR)))
                    logger.info("Confirmed: Starting on the home page.")
                except TimeoutException:
                    logger.warning("Not on home page initially and not on result page. Attempting to navigate to home via _initial_setup logic.")
                    self._initial_setup() # This should ensure we are on home or fail
                    self.wait_long.until(EC.presence_of_element_located((By.CSS_SELECTOR, self.HOME_CONTAINER_SELECTOR)))
            logger.info("Successfully ensured test starts on the Home page.")

            # --- Test Step 1: Add first grade and verify average ---
            logger.info("Adding first grade (4.5, 20%).")
            self._add_grade_and_percentage("4.5", "20")
            
            calculate_button = self.wait_long.until(EC.element_to_be_clickable((By.CSS_SELECTOR, self.CALCULATE_BUTTON_SELECTOR)))
            calculate_button.click()
            self._take_screenshot("after_1st_calculate_click")
            
            logger.info(f"Waiting for result page container '{self.RESULT_PAGE_CONTAINER_SELECTOR}' after 1st calc...")
            self.wait_long.until(EC.presence_of_element_located((By.CSS_SELECTOR, self.RESULT_PAGE_CONTAINER_SELECTOR)))
            logger.info(f"Result container present for 1st calc.")

            current_avg_1 = self._get_current_weighted_average()
            expected_avg_1 = 0.9
            self.assertEqual(current_avg_1, expected_avg_1, f"Avg after 1st grade. Expected {expected_avg_1}, got {current_avg_1}")
            logger.info(f"Average after 1st grade on result page is correct: {current_avg_1}")

            # --- Navigate back for Test Step 2 ---
            logger.info("Navigating back to home page for 2nd grade.")
            self.driver.find_element(By.XPATH, self.NAV_BACK_BUTTON_XPATH).click()
            self.wait_long.until(EC.presence_of_element_located((By.CSS_SELECTOR, self.HOME_CONTAINER_SELECTOR)))
            logger.info(f"Navigated back to home page for 2nd grade.")

            # --- Test Step 2: Add second grade and verify average ---
            logger.info("Adding second grade (3.0, 30%).")
            self._add_grade_and_percentage("3.0", "30")

            calculate_button = self.wait_long.until(EC.element_to_be_clickable((By.CSS_SELECTOR, self.CALCULATE_BUTTON_SELECTOR)))
            calculate_button.click()
            self._take_screenshot("after_2nd_calculate_click")

            logger.info(f"Waiting for result page container '{self.RESULT_PAGE_CONTAINER_SELECTOR}' after 2nd calc...")
            self.wait_long.until(EC.presence_of_element_located((By.CSS_SELECTOR, self.RESULT_PAGE_CONTAINER_SELECTOR)))
            logger.info(f"Result container present for 2nd calc.")

            current_avg_2 = self._get_current_weighted_average()
            expected_avg_2 = 1.8
            self.assertEqual(current_avg_2, expected_avg_2, f"Avg after 2nd grade. Expected {expected_avg_2}, got {current_avg_2}")
            logger.info(f"Average after 2nd grade on result page is correct: {current_avg_2}")

            # --- Navigate back for Test Step 3 ---
            logger.info("Navigating back to home page for 3rd grade.")
            self.driver.find_element(By.XPATH, self.NAV_BACK_BUTTON_XPATH).click()
            self.wait_long.until(EC.presence_of_element_located((By.CSS_SELECTOR, self.HOME_CONTAINER_SELECTOR)))
            logger.info(f"Navigated back to home page for 3rd grade.")

            # --- Test Step 3: Add third grade and verify average ---
            logger.info("Adding third grade (5.0, 50%).") # (1.8 + 5.0*0.50) = 1.8 + 2.5 = 4.3
            self._add_grade_and_percentage("5.0", "50")

            calculate_button = self.wait_long.until(EC.element_to_be_clickable((By.CSS_SELECTOR, self.CALCULATE_BUTTON_SELECTOR)))
            calculate_button.click()
            self._take_screenshot("after_3rd_calculate_click")

            logger.info(f"Waiting for result page container '{self.RESULT_PAGE_CONTAINER_SELECTOR}' after 3rd calc...")
            self.wait_long.until(EC.presence_of_element_located((By.CSS_SELECTOR, self.RESULT_PAGE_CONTAINER_SELECTOR)))
            logger.info(f"Result container present for 3rd calc.")
            
            current_avg_3 = self._get_current_weighted_average()
            expected_avg_3 = 4.3 
            self.assertEqual(current_avg_3, expected_avg_3, f"Avg after 3rd grade. Expected {expected_avg_3}, got {current_avg_3}")
            logger.info(f"Average after 3rd grade on result page is correct: {current_avg_3}")

        except AssertionError as e:
            logger.error(f"AssertionError in {test_name}: {e}", exc_info=True)
            self._take_screenshot(f"{test_name}_assertion_error")
            self.fail(f"AssertionError in {test_name}: {e}")
        except Exception as e:
            logger.error(f"Exception in {test_name}: {e}", exc_info=True)
            self._take_screenshot(f"{test_name}_exception")
            self.fail(f"Exception in {test_name}: {e}")

        logger.info(f"Test {test_name} completed successfully.")

if __name__ == '__main__':
    unittest.main(verbosity=2)
