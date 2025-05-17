\
import unittest
import time
import os
import logging
import re # Added for parsing
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class US04Tests(unittest.TestCase):
    BASE_URL = "http://localhost:3000"
    GRADE_INPUT_SELECTOR = "input.home__input[placeholder='0.0'][type='number']"
    PERCENTAGE_INPUT_SELECTOR = "input.home__input[placeholder='0'][type='number']"
    ADD_GRADE_BUTTON_SELECTOR = "button.home__add-button"
    GRADES_LIST_ITEM_SELECTOR = "div.home__grades-container > div.home__grade-row"
    CALCULATE_BUTTON_SELECTOR = "button.home__calculate-button"
    # Updated selector for the result page based on result.jsx
    CURRENT_AVERAGE_DISPLAY_SELECTOR = "p.result__card-current"
    RESULT_PAGE_CONTAINER_SELECTOR = "div.result" # A general selector for the result page
    
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
            logger.info("Successfully navigated back to the Home page.")

        except TimeoutException:
            logger.info("First-time user alert or navigation elements not found or timed out. Assuming already on Home page or flow is different.")
            if self.HOME_CONTAINER_SELECTOR not in self.driver.page_source:
                self.driver.get(self.BASE_URL) 
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, self.HOME_CONTAINER_SELECTOR))
                )
                logger.info("Re-navigated to Home page as a fallback.")
        except Exception as e:
            logger.error(f"An unexpected error occurred during initial setup: {e}")
            self._take_screenshot("initial_setup_error")

    def _add_grade_and_percentage(self, grade, percentage):
        if not hasattr(self, 'driver') or not self.driver:
            logger.error("Driver not available in _add_grade_and_percentage.")
            self.fail("Driver not available.")
            return

        # Ensure we are on the home page before adding grades
        if "/result" in self.driver.current_url:
            logger.info("Currently on result page, navigating back to home to add grades.")
            nav_back_button = self.wait_long.until(
                EC.element_to_be_clickable((By.XPATH, self.NAV_BACK_BUTTON_XPATH))
            )
            nav_back_button.click()
            self.wait_long.until(EC.presence_of_element_located((By.CSS_SELECTOR, self.HOME_CONTAINER_SELECTOR)))
            logger.info("Navigated back to home page.")

        grade_rows = self.driver.find_elements(By.CSS_SELECTOR, self.GRADES_LIST_ITEM_SELECTOR)
        if not grade_rows: # Should not happen if app starts with one row
            logger.error("No grade rows found to add grade and percentage.")
            self._take_screenshot("no_grade_rows_found")
            # Attempt to click "Agregar nota" to see if it generates the first row
            try:
                add_button_global = self.wait_long.until(EC.element_to_be_clickable((By.CSS_SELECTOR, self.ADD_GRADE_BUTTON_SELECTOR)))
                add_button_global.click()
                time.sleep(0.5) # wait for row to be added
                grade_rows = self.driver.find_elements(By.CSS_SELECTOR, self.GRADES_LIST_ITEM_SELECTOR)
                if not grade_rows:
                    self.fail("Still no grade rows found after attempting to add one.")
                    return
            except Exception as ex:
                logger.error(f"Failed to create an initial grade row: {ex}")
                self.fail("Failed to create an initial grade row.")
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
            self.fail("Input elements not found in the last row.")
            return
        
        add_button = self.wait_long.until(EC.element_to_be_clickable((By.CSS_SELECTOR, self.ADD_GRADE_BUTTON_SELECTOR)))

        grade_input_element.clear()
        grade_input_element.send_keys(str(grade))
        percentage_input_element.clear()
        percentage_input_element.send_keys(str(percentage))
        
        add_button.click() 
        logger.info(f"Clicked 'Agregar nota' after filling grade: {grade}, percentage: {percentage} into the last available row.")
        time.sleep(0.5) 

    def _get_current_weighted_average(self):
        raw_text = ""
        try:
            # Ensure we are on the result page
            self.wait_long.until(EC.url_contains("/result"))
            self.wait_long.until(EC.presence_of_element_located((By.CSS_SELECTOR, self.RESULT_PAGE_CONTAINER_SELECTOR)))
            
            average_element = self.wait_long.until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, self.CURRENT_AVERAGE_DISPLAY_SELECTOR))
            )
            time.sleep(0.2) # give a brief moment for text to update
            
            raw_text = average_element.text.strip()
            attempts = 0
            while raw_text == "" and attempts < 5: # Retry if empty
                time.sleep(0.3)
                raw_text = average_element.text.strip()
                attempts += 1
            
            logger.info(f"Raw current weighted average text from result page: '{raw_text}'")
            if not raw_text:
                logger.warning("Current weighted average text is empty after retries on result page.")
                self._take_screenshot("empty_current_average_result_page")
                return "Error: Empty Value"

            # Parse the text: "Actualmente tienes un promedio de {finalGrade} en el {totalPercentage}% de la materia."
            match = re.search(r"Actualmente tienes un promedio de (\\d+\\.\\d+|\\d+) en el", raw_text)
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
            logger.info(f"Page source at timeout:\\n{self.driver.page_source[:2000]}")
            self._take_screenshot("current_average_timeout_result_page")
            return "Error: Timeout"
        except ValueError:
            # This might happen if grade_str is not a valid float, though regex should prevent it.
            logger.error(f"Could not convert extracted grade string to float from '{raw_text}'.")
            self._take_screenshot("current_average_value_error_result")
            return "Error: Conversion"
        except Exception as e:
            logger.error(f"Error getting current weighted average from result page: {e}")
            self._take_screenshot("get_current_average_error_result")
            return "Error: General"

    # US04: Cálculo del Promedio Ponderado Actual
    def test_us04_verify_calculation_of_current_weighted_average(self):
        test_name = self._testMethodName
        logger.info(f"Running test: {test_name}")

        try:
            # Ensure we start on the home page for adding grades
            if "/result" in self.driver.current_url:
                self.driver.find_element(By.XPATH, self.NAV_BACK_BUTTON_XPATH).click()
                self.wait_long.until(EC.presence_of_element_located((By.CSS_SELECTOR, self.HOME_CONTAINER_SELECTOR)))
            elif self.HOME_CONTAINER_SELECTOR not in self.driver.page_source:
                 self.driver.get(self.BASE_URL)
                 self._initial_setup() # Re-run setup if not on home page and not on result page

            # 1. Add first grade and verify average
            logger.info("Adding first grade (4.5, 20%).")
            self._add_grade_and_percentage("4.5", "20") # Adds and clicks "Agregar nota"
            
            calculate_button = self.wait_long.until(EC.element_to_be_clickable((By.CSS_SELECTOR, self.CALCULATE_BUTTON_SELECTOR)))
            calculate_button.click()
            logger.info("Clicked 'Calcular' button. Expecting navigation to /result.")
            
            # Wait for navigation to result page and for the average display to be ready
            self.wait_long.until(EC.url_contains("/result"))
            logger.info(f"Navigated to {self.driver.current_url}")

            current_avg_1 = self._get_current_weighted_average()
            expected_avg_1 = 0.9 # (4.5 * 20) / 100 = 90 / 100 = 0.9
            self.assertEqual(current_avg_1, expected_avg_1,
                             f"Average after 1st grade expected {expected_avg_1}, but got {current_avg_1}")
            logger.info(f"Average after 1st grade on result page is correct: {current_avg_1}")

            # Navigate back to home to add more grades
            self.driver.find_element(By.XPATH, self.NAV_BACK_BUTTON_XPATH).click()
            self.wait_long.until(EC.presence_of_element_located((By.CSS_SELECTOR, self.HOME_CONTAINER_SELECTOR)))
            logger.info("Navigated back to home page to add second grade.")

            # 2. Add second grade and verify average
            logger.info("Adding second grade (3.0, 30%).")
            self._add_grade_and_percentage("3.0", "30")

            calculate_button = self.wait_long.until(EC.element_to_be_clickable((By.CSS_SELECTOR, self.CALCULATE_BUTTON_SELECTOR))) # Re-locate button
            calculate_button.click()
            logger.info("Clicked 'Calcular' button again.")
            self.wait_long.until(EC.url_contains("/result"))
            logger.info(f"Navigated to {self.driver.current_url}")

            current_avg_2 = self._get_current_weighted_average()
            expected_avg_2 = 1.8 # (4.5 * 20 + 3.0 * 30) / 100 = (90 + 90)/100 = 1.8
            self.assertEqual(current_avg_2, expected_avg_2,
                             f"Average after 2nd grade expected {expected_avg_2}, but got {current_avg_2}")
            logger.info(f"Average after 2nd grade on result page is correct: {current_avg_2}")

            # Navigate back to home to add more grades
            self.driver.find_element(By.XPATH, self.NAV_BACK_BUTTON_XPATH).click()
            self.wait_long.until(EC.presence_of_element_located((By.CSS_SELECTOR, self.HOME_CONTAINER_SELECTOR)))
            logger.info("Navigated back to home page to add third grade.")

            # 3. Add third grade and verify average
            logger.info("Adding third grade (5.0, 50%).")
            self._add_grade_and_percentage("5.0", "50")

            calculate_button = self.wait_long.until(EC.element_to_be_clickable((By.CSS_SELECTOR, self.CALCULATE_BUTTON_SELECTOR))) # Re-locate button
            calculate_button.click()
            logger.info("Clicked 'Calcular' button again.")
            self.wait_long.until(EC.url_contains("/result"))
            logger.info(f"Navigated to {self.driver.current_url}")
            
            current_avg_3 = self._get_current_weighted_average()
            # (4.5*20 + 3.0*30 + 5.0*50)/100 = (90 + 90 + 250)/100 = 430/100 = 4.3
            expected_avg_3 = 4.3 
            self.assertEqual(current_avg_3, expected_avg_3,
                             f"Average after 3rd grade expected {expected_avg_3}, but got {current_avg_3}")
            logger.info(f"Average after 3rd grade on result page is correct: {current_avg_3}")

        except AssertionError as e:
            logger.error(f"AssertionError in {test_name}: {e}")
            self._take_screenshot(f"{test_name}_assertion_failure")
            # Log page source if average display is not found or value is unexpected
            if "current_average_timeout" in str(e).lower() or "Error: Conversion" in str(e) or "Error: Empty Value" in str(e):
                 logger.info(f"Page source at error:\\n{self.driver.page_source[:3000]}")
            raise
        except Exception as e:
            logger.error(f"An unexpected error occurred in {test_name}: {e}")
            self._take_screenshot(f"{test_name}_unexpected_error")
            logger.info(f"Page source at error:\\n{self.driver.page_source[:3000]}")
            raise

        logger.info(f"Test {test_name} completed successfully.")

if __name__ == '__main__':
    unittest.main(verbosity=2)
