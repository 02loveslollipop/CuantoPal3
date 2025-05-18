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
    # Original complex XPath selector
    NAV_BACK_BUTTON_XPATH = "//button[contains(@class, 'nav-bar__button') and .//span[contains(@class, 'back-icon')]/svg[contains(@class, 'lucide-chevron-left')]]"
    # Simpler CSS selector for the back button - targeting the first button in the nav-bar
    NAV_BACK_BUTTON_SELECTOR = "nav.nav-bar > button.nav-bar__button:first-child"
    HOME_CONTAINER_SELECTOR = "div.home__container"
    
    def set_driver_fixture(self, driver):
        self.driver = driver
        self.wait_short = WebDriverWait(self.driver, 5)
        self.wait_long = WebDriverWait(self.driver, 15)
        if not os.path.exists("screenshots"):
            os.makedirs("screenshots")

    def setUp(self):
        # This setup is primarily for direct unittest execution.
        # Pytest will use the fixture from conftest.py
        if not hasattr(self, 'driver') or not self.driver:
            logger.info("WebDriver not set by fixture, attempting fallback setup for direct unittest execution.")
            try:
                options = webdriver.ChromeOptions()
                # Add any desired options here, e.g., headless
                # options.add_argument('--headless')
                # options.add_argument('--disable-gpu')
                self.driver = webdriver.Chrome(options=options)
                self.set_driver_fixture(self.driver) # Call to setup waits and screenshot dir
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
            
    def _get_current_weighted_average(self):
        """Extract and return the current weighted average from the result page."""
        try:
            # Take screenshot to debug what we're seeing
            self._take_screenshot("result_page_before_extract_average")
            
            # Make sure we are on the result page
            self.wait_long.until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, self.RESULT_PAGE_CONTAINER_SELECTOR))
            )
            
            # Wait for average display element
            current_avg_element = self.wait_long.until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, self.CURRENT_AVERAGE_DISPLAY_SELECTOR))
            )
            
            # Small delay to make sure text is fully loaded/rendered
            time.sleep(0.2)
            
            current_avg_text = current_avg_element.text.strip()
            logger.info(f"Current average text found: '{current_avg_text}'")
            
            # Extract the numeric value using regex - looking for decimal number
            # Example text: "Promedio actual: 1.8"
            match = re.search(r'(\d+\.\d+)', current_avg_text)
            if match:
                current_avg = float(match.group(1))
                logger.info(f"Extracted current average: {current_avg}")
                return current_avg
            else:
                logger.error(f"Failed to extract numeric average from text: '{current_avg_text}'")
                # Try an alternative approach - get the raw text content
                raw_text = current_avg_element.get_attribute('textContent').strip()
                logger.info(f"Raw text content: '{raw_text}'")
                
                # Try to find any decimal number in the raw text
                alt_match = re.search(r'(\d+\.\d+)', raw_text)
                if alt_match:
                    current_avg = float(alt_match.group(1))
                    logger.info(f"Extracted current average from raw text: {current_avg}")
                    return current_avg
                
                self._take_screenshot("average_extraction_failed")
                self.fail(f"Could not extract numeric average from: '{current_avg_text}'")
                
        except Exception as e:
            logger.error(f"Error getting current weighted average: {e}")
            self._take_screenshot("get_current_avg_error")
            self.fail(f"Error getting current weighted average: {e}")
            return None

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
            
            # Try CSS selector first, fall back to XPath if needed
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
                
    def _add_grade_and_percentage(self, grade, percentage):
        if not hasattr(self, 'driver') or not self.driver:
            logger.error("Driver not available in _add_grade_and_percentage.")
            self.fail("Driver not available.")
            return

        # First check if we're on the result page and navigate back if needed
        on_result_page = False
        try:
            if self.driver.find_element(By.CSS_SELECTOR, self.RESULT_PAGE_CONTAINER_SELECTOR).is_displayed():
                on_result_page = True
        except NoSuchElementException:
            on_result_page = False

        if on_result_page:
            logger.info("Currently on result page, navigating back to home to add grades.")
            try:
                # First try with the CSS selector
                nav_back_button = self.wait_short.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, self.NAV_BACK_BUTTON_SELECTOR))
                )
                logger.info("Found back button using CSS selector in _add_grade_and_percentage.")
            except TimeoutException:
                try:
                    # Then try with XPath
                    logger.info("CSS selector failed for back button in _add_grade_and_percentage, trying XPath...")
                    nav_back_button = self.wait_long.until(
                        EC.element_to_be_clickable((By.XPATH, self.NAV_BACK_BUTTON_XPATH))
                    )
                    logger.info("Found back button using XPath selector in _add_grade_and_percentage.")
                except TimeoutException:
                    # As a last resort, try to find any buttons in the nav bar
                    logger.info("XPath also failed. Looking for any button in the nav bar...")
                    nav_bar = self.wait_long.until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "nav.nav-bar"))
                    )
                    nav_buttons = nav_bar.find_elements(By.TAG_NAME, "button")
                    if nav_buttons:
                        nav_back_button = nav_buttons[0]  # First button in nav bar is usually back
                        logger.info("Using first button found in nav bar")
                    else:
                        logger.error("No buttons found in nav bar")
                        self._take_screenshot("no_buttons_in_nav_bar_add_grade")
                        self.fail("No buttons found in nav bar when trying to navigate back")
            
            # Click the back button once found
            nav_back_button.click()
            self.wait_long.until(EC.presence_of_element_located((By.CSS_SELECTOR, self.HOME_CONTAINER_SELECTOR)))
            logger.info("Successfully navigated back to home page.")
            
            # Take a small pause to ensure the UI is fully loaded
            time.sleep(0.5)

        # Now we're on the home page
        # Take a screenshot of the current state for debugging
        self._take_screenshot("before_adding_grade")
        
        # Find all grade rows currently in the UI
        grade_rows = self.driver.find_elements(By.CSS_SELECTOR, self.GRADES_LIST_ITEM_SELECTOR)
        logger.info(f"Found {len(grade_rows)} grade rows before adding.")
        
        # First check if we need to add a new row
        need_new_row = True
        if grade_rows:
            # Check if the last row is empty (which means we can use it)
            last_row = grade_rows[-1]
            try:
                grade_input = last_row.find_element(By.CSS_SELECTOR, self.GRADE_INPUT_SELECTOR)
                percentage_input = last_row.find_element(By.CSS_SELECTOR, self.PERCENTAGE_INPUT_SELECTOR)
                
                grade_value = grade_input.get_attribute("value")
                percentage_value = percentage_input.get_attribute("value")
                
                # If both inputs are empty, we can use this row
                if not grade_value and not percentage_value:
                    need_new_row = False
                    logger.info("Found empty row to use for new grade entry.")
            except NoSuchElementException:
                # If we can't find inputs in the last row, we'll add a new one
                logger.warning("Last row doesn't have expected input elements.")
                need_new_row = True
        
        # If we need a new row or there are no rows, add one
        if need_new_row or not grade_rows:
            logger.info("Adding a new grade row...")
            add_button = self.wait_long.until(EC.element_to_be_clickable((By.CSS_SELECTOR, self.ADD_GRADE_BUTTON_SELECTOR)))
            add_button.click()
            time.sleep(0.5)  # Wait for the row to be added
            
            # Refresh the list of grade rows
            grade_rows = self.driver.find_elements(By.CSS_SELECTOR, self.GRADES_LIST_ITEM_SELECTOR)
            if not grade_rows:
                logger.error("Failed to add grade row - no rows found after clicking 'Add' button")
                self._take_screenshot("failed_to_add_grade_row")
                self.fail("Failed to add grade row - no rows found after clicking 'Add' button")
        
        # Now use the last row to add our grade
        last_row = grade_rows[-1]
        logger.info(f"Using the last of {len(grade_rows)} rows to add grade: {grade}, percentage: {percentage}")
        
        try:
            grade_input_element = last_row.find_element(By.CSS_SELECTOR, self.GRADE_INPUT_SELECTOR)
            percentage_input_element = last_row.find_element(By.CSS_SELECTOR, self.PERCENTAGE_INPUT_SELECTOR)
            
            # Clear and enter the grade and percentage
            grade_input_element.clear()
            grade_input_element.send_keys(str(grade))
            percentage_input_element.clear()
            percentage_input_element.send_keys(str(percentage))
            
            # Take screenshot after entering values
            self._take_screenshot(f"after_entering_grade_{grade}_percent_{percentage}")
            
            # Click the add button to confirm this grade
            add_button = self.wait_long.until(EC.element_to_be_clickable((By.CSS_SELECTOR, self.ADD_GRADE_BUTTON_SELECTOR)))
            add_button.click()
            logger.info(f"Clicked 'Add' button after entering grade: {grade}, percentage: {percentage}")
            
            # Allow time for the UI to update
            time.sleep(0.5)
            
            # Verify the grade was added by checking for more rows or for values in the inputs
            new_grade_rows = self.driver.find_elements(By.CSS_SELECTOR, self.GRADES_LIST_ITEM_SELECTOR)
            logger.info(f"After adding: {len(new_grade_rows)} grade rows (previously {len(grade_rows)})")
            
            # Take screenshot after adding grade
            self._take_screenshot("after_adding_grade")
            
        except NoSuchElementException as e:
            logger.error(f"Could not find input elements in the grade row: {e}")
            self._take_screenshot("input_elements_not_found")
            self.fail(f"Input elements not found: {e}")
            return

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
                try:
                    nav_back_button_initial = self.wait_short.until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, self.NAV_BACK_BUTTON_SELECTOR))
                    )
                    logger.info("Found initial back button using CSS selector.")
                except TimeoutException:
                    logger.info("CSS selector failed for initial back button, trying XPath...")
                    nav_back_button_initial = self.wait_long.until(
                        EC.element_to_be_clickable((By.XPATH, self.NAV_BACK_BUTTON_XPATH))
                    )
                    logger.info("Found initial back button using XPath selector.")
                    
                nav_back_button_initial.click()
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
            # Try both selectors with a more extended wait time
            try:
                logger.info("Attempting to find back button with CSS selector...")
                self._take_screenshot("before_finding_back_button_step1")
                nav_back_button_step1 = self.wait_long.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, self.NAV_BACK_BUTTON_SELECTOR))
                )
                logger.info("Found back button using CSS selector for step 1.")
            except TimeoutException:
                logger.warning("CSS selector failed for back button in step 1, trying XPath with more wait time...")
                # Take debug screenshot
                self._take_screenshot("css_selector_failed_step1")
                 # Try a more verbose approach to locate the button
                try:
                    # First, check if there's a nav bar
                    nav_bar = self.wait_long.until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "nav.nav-bar"))
                    )
                    logger.info("Nav bar found, looking for the first button inside it...")
                    nav_buttons = nav_bar.find_elements(By.TAG_NAME, "button")
                    if nav_buttons:
                        nav_back_button_step1 = nav_buttons[0]  # First button in the nav bar
                        logger.info("Using first button in nav bar")
                    else:
                        logger.error("No buttons found in nav bar")
                        self._take_screenshot("no_buttons_in_nav_bar")
                        self.fail("No buttons found in nav bar")
                except Exception as e:
                    logger.error(f"Error finding nav bar or buttons: {e}")
                    self._take_screenshot("error_finding_nav_elements")
                    self.fail(f"Error finding nav bar or buttons: {e}")
                    
            # Click the back button once found
            nav_back_button_step1.click()
            logger.info("Clicked on back button for step 1")
            self._take_screenshot("after_back_button_click_step1")
            
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
            # Try both selectors with a more extended wait time
            try:
                logger.info("Attempting to find back button with CSS selector for step 2...")
                self._take_screenshot("before_finding_back_button_step2")
                nav_back_button_step2 = self.wait_long.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, self.NAV_BACK_BUTTON_SELECTOR))
                )
                logger.info("Found back button using CSS selector for step 2.")
            except TimeoutException:
                logger.warning("CSS selector failed for back button in step 2, trying alternative approaches...")
                self._take_screenshot("css_selector_failed_step2")
                try:
                    # First, check if there's a nav bar
                    nav_bar = self.wait_long.until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "nav.nav-bar"))
                    )
                    logger.info("Nav bar found, looking for the first button inside it...")
                    nav_buttons = nav_bar.find_elements(By.TAG_NAME, "button")
                    if nav_buttons:
                        nav_back_button_step2 = nav_buttons[0]  # First button in the nav bar
                        logger.info("Using first button in nav bar")
                    else:
                        logger.error("No buttons found in nav bar")
                        self._take_screenshot("no_buttons_in_nav_bar_step2")
                        self.fail("No buttons found in nav bar for step 2")
                except Exception as e:
                    logger.error(f"Error finding nav bar or buttons for step 2: {e}")
                    self._take_screenshot("error_finding_nav_elements_step2")
                    self.fail(f"Error finding nav bar or buttons for step 2: {e}")
                    
            # Click the back button once found
            nav_back_button_step2.click()
            logger.info("Clicked on back button for step 2")
            self._take_screenshot("after_back_button_click_step2")
            
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
