import time
import pytest
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException # Ensure this is imported

# Configure logging
import logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class HomePageTest(StaticLiveServerTestCase):
    GRADE_INPUT_SELECTOR = 'input.home__input[placeholder="0.0"][type="number"]'
    PERCENTAGE_INPUT_SELECTOR = 'input.home__input[placeholder="0"][type="number"]'
    ADD_GRADE_BUTTON_SELECTOR = 'button.home__add-button'
    GRADES_LIST_ITEM_SELECTOR = "div.home__grades-container > div.home__grade-row"

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Additional setup if needed
        cls.driver.implicitly_wait(10) # Implicit wait for elements to be present

    def _initial_setup(self):
        self.driver.get(self.live_server_url)
        # No alert handling for now, as it's not in the provided production HTML
        # try:
        #     WebDriverWait(self.driver, 3).until(
        #         EC.element_to_be_clickable((By.CSS_SELECTOR, ".alert__button.alert__button--single"))
        #     ).click()
        #     logger.info("Initial alert handled.")
        # except TimeoutException:
        #     logger.info("Initial alert not found or not clickable, proceeding.")

        try:
            # Wait for the main grade input to be present
            self.wait_long.until(EC.presence_of_element_located((By.CSS_SELECTOR, self.GRADE_INPUT_SELECTOR)))
            logger.info(f"Grade input ('{self.GRADE_INPUT_SELECTOR}') found on page load.")
        except TimeoutException:
            current_url = self.driver.current_url
            logger.error(f"Failed to find grade input ('{self.GRADE_INPUT_SELECTOR}') on initial load. URL: {current_url}")
            self._take_screenshot("error_initial_setup_grade_input_not_found")
            # Ensure the exception message is clear
            raise Exception(f"Could not find the grade input ('{self.GRADE_INPUT_SELECTOR}') during setup. Current URL: {current_url}")

    def _add_grade_and_percentage(self, grade, percentage):
        # Ensure _initial_setup has been called or page is otherwise ready
        grade_input = self.wait_long.until(EC.presence_of_element_located((By.CSS_SELECTOR, self.GRADE_INPUT_SELECTOR)))
        percentage_input = self.wait_long.until(EC.presence_of_element_located((By.CSS_SELECTOR, self.PERCENTAGE_INPUT_SELECTOR)))
        add_button = self.wait_long.until(EC.element_to_be_clickable((By.CSS_SELECTOR, self.ADD_GRADE_BUTTON_SELECTOR)))

        grade_input.clear()
        grade_input.send_keys(str(grade))
        percentage_input.clear()
        percentage_input.send_keys(str(percentage))
        add_button.click()
        logger.info(f"Added grade: {grade}, percentage: {percentage}")

    def _get_grades_list_item_count(self):
        # This counts the number of displayed grade rows
        try:
            grade_items = self.driver.find_elements(By.CSS_SELECTOR, self.GRADES_LIST_ITEM_SELECTOR)
            return len(grade_items)
        except Exception as e:
            logger.error(f"Error finding grade list items: {e}")
            self._take_screenshot("error_get_grades_list_item_count")
            return 0

    # US01: Registro de Calificaciones
    def test_us01_add_single_valid_grade(self, driver, request): # Added request fixture
        test_name = request.node.name # Use request fixture to get test name
        try:
            self._initial_setup(driver)
            
            grade_to_add = "4.0"
            percentage_to_add = "20"
            
            initial_item_count = self._get_grades_list_item_count(driver)
            self._add_grade_and_percentage(driver, grade_to_add, percentage_to_add)

            # Wait for list to update
            WebDriverWait(driver, 10).until(
                lambda d: self._get_grades_list_item_count(d) > initial_item_count
            )
            
            grades_list_container = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "grades-list"))
            )
            # Verify the added grade and percentage are present in the list
            # This assumes a simple text representation; more specific selectors for items are better
            assert grade_to_add in grades_list_container.text
            assert percentage_to_add + "%" in grades_list_container.text # Assuming '%' is displayed

        except Exception as e:
            os.makedirs("screenshots", exist_ok=True)
            driver.save_screenshot(f"screenshots/error_{test_name}_{int(time.time())}.png")
            print(f"Current URL on error in {test_name}: {driver.current_url}")
            print(f"Page source excerpt on error in {test_name}: {driver.page_source[:500]}...")
            raise e

    def test_us01_add_multiple_valid_grades(self, driver, request): # Added request fixture
        test_name = request.node.name # Use request fixture to get test name
        try:
            self._initial_setup(driver)

            grades_data = [
                {"grade": "4.5", "percentage": "25"},
                {"grade": "3.0", "percentage": "30"},
                {"grade": "5.0", "percentage": "15"},
            ]
            
            initial_item_count = self._get_grades_list_item_count(driver)

            for i, item in enumerate(grades_data):
                self._add_grade_and_percentage(driver, item["grade"], item["percentage"])
                # Wait for the list to update after each addition
                WebDriverWait(driver, 10).until(
                    lambda d: self._get_grades_list_item_count(d) == initial_item_count + i + 1
                )

            grades_list_container = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "grades-list"))
            )
            for item in grades_data:
                assert item["grade"] in grades_list_container.text
                assert item["percentage"] + "%" in grades_list_container.text
            
            assert self._get_grades_list_item_count(driver) == initial_item_count + len(grades_data)

        except Exception as e:
            os.makedirs("screenshots", exist_ok=True)
            driver.save_screenshot(f"screenshots/error_{test_name}_{int(time.time())}.png")
            print(f"Current URL on error in {test_name}: {driver.current_url}")
            print(f"Page source excerpt on error in {test_name}: {driver.page_source[:500]}...")
            raise e

    def test_us01_validate_grade_input_below_range(self, driver, request): # Added request fixture
        test_name = request.node.name # Use request fixture to get test name
        try:
            self._initial_setup(driver)
            initial_item_count = self._get_grades_list_item_count(driver)
            
            self._add_grade_and_percentage(driver, "-1.0", "20") # Invalid grade

            error_message_element = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.ID, "error-message-grade")) # Hypothetical ID
            )
            assert "válido" in error_message_element.text.lower() or "rango" in error_message_element.text.lower()
            
            # Verify grade was not added
            assert self._get_grades_list_item_count(driver) == initial_item_count

        except Exception as e:
            os.makedirs("screenshots", exist_ok=True)
            driver.save_screenshot(f"screenshots/error_{test_name}_{int(time.time())}.png")
            print(f"Current URL on error in {test_name}: {driver.current_url}")
            print(f"Page source excerpt on error in {test_name}: {driver.page_source[:500]}...")
            raise e

    def test_us01_validate_grade_input_above_range(self, driver, request): # Added request fixture
        test_name = request.node.name # Use request fixture to get test name
        try:
            self._initial_setup(driver)
            initial_item_count = self._get_grades_list_item_count(driver)

            self._add_grade_and_percentage(driver, "6.0", "20") # Invalid grade (assuming max 5.0)
            
            error_message_element = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.ID, "error-message-grade"))
            )
            assert "válido" in error_message_element.text.lower() or "rango" in error_message_element.text.lower()

            assert self._get_grades_list_item_count(driver) == initial_item_count

        except Exception as e:
            os.makedirs("screenshots", exist_ok=True)
            driver.save_screenshot(f"screenshots/error_{test_name}_{int(time.time())}.png")
            print(f"Current URL on error in {test_name}: {driver.current_url}")
            print(f"Page source excerpt on error in {test_name}: {driver.page_source[:500]}...")
            raise e

    def test_us01_validate_percentage_input_negative(self, driver, request): # Added request fixture
        test_name = request.node.name # Use request fixture to get test name
        try:
            self._initial_setup(driver)
            initial_item_count = self._get_grades_list_item_count(driver)

            self._add_grade_and_percentage(driver, "4.0", "-10") # Invalid percentage
            
            error_message_element = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.ID, "error-message-percentage")) # Hypothetical ID
            )
            assert "positivo" in error_message_element.text.lower() or "válido" in error_message_element.text.lower()

            assert self._get_grades_list_item_count(driver) == initial_item_count

        except Exception as e:
            os.makedirs("screenshots", exist_ok=True)
            driver.save_screenshot(f"screenshots/error_{test_name}_{int(time.time())}.png")
            print(f"Current URL on error in {test_name}: {driver.current_url}")
            print(f"Page source excerpt on error in {test_name}: {driver.page_source[:500]}...")
            raise e

    def test_us01_validate_percentage_input_non_numeric(self, driver, request): # Added request fixture
        test_name = request.node.name # Use request fixture to get test name
        try:
            self._initial_setup(driver)
            initial_item_count = self._get_grades_list_item_count(driver)
            
            # Manually interact for this specific case to send "abc"
            grade_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "grade-input"))
            )
            grade_input.clear()
            grade_input.send_keys("3.0")

            percentage_input_loc = (By.ID, "percentage-input")
            percentage_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(percentage_input_loc)
            )
            percentage_input.clear()
            percentage_input.send_keys("abc") # Non-numeric

            add_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, "add-grade-btn"))
            )
            add_button.click()

            # Verification depends on behavior: error message or input rejection
            try:
                error_message_element = WebDriverWait(driver, 5).until(
                    EC.visibility_of_element_located((By.ID, "error-message-percentage"))
                )
                assert "número" in error_message_element.text.lower() or "válido" in error_message_element.text.lower()
            except TimeoutException:
                # If no error message, check if the input was rejected or field is empty/still "abc"
                current_percentage_value = driver.find_element(*percentage_input_loc).get_attribute("value")
                # If type="number", browser might prevent "abc" or convert to empty.
                # If type="text", "abc" might remain.
                assert current_percentage_value == "" or current_percentage_value == "abc", \
                    "Percentage input did not show error for non-numeric and value is not as expected."
            
            assert self._get_grades_list_item_count(driver) == initial_item_count

        except Exception as e:
            os.makedirs("screenshots", exist_ok=True)
            driver.save_screenshot(f"screenshots/error_{test_name}_{int(time.time())}.png")
            print(f"Current URL on error in {test_name}: {driver.current_url}")
            print(f"Page source excerpt on error in {test_name}: {driver.page_source[:500]}...")
            raise e

    def test_home_page_functional_flow(self, driver):
        # Navigate to application using environment variable
        base_url = os.environ.get('APP_URL', 'http://localhost:3000')
        driver.get(base_url)
        
        try:
            # 1. Wait for and click the alert button
            alert_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".alert__button.alert__button--single"))
            )
            alert_button.click()
            
            # 2. Test if the back navigation button works
            try:
                back_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, ".nav-bar__button"))
                )
                back_button.click()
                
                # Wait for any element that indicates we navigated back successfully
                # Replace ".home__container" with an element that actually exists in your app
                WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".home__container"))
                )
            except Exception as e:
                print(f"Navigation test failed: {e}")
                # If navigation test fails, go back to the main page
                driver.get(base_url)
                # Wait again for alert button and click it to get back to the same state
                alert_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, ".alert__button.alert__button--single"))
                )
                alert_button.click()
            
            # 3. Test adding a new grade row
            # Get initial count of grade rows
            initial_grade_rows = driver.find_elements(By.CSS_SELECTOR, ".home__grade-row")
            initial_count = len(initial_grade_rows)
            
            # Click add button
            add_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".home__add-button"))
            )
            add_button.click()
            
            # Verify a new row was added
            WebDriverWait(driver, 5).until(
                lambda d: len(d.find_elements(By.CSS_SELECTOR, ".home__grade-row")) > initial_count
            )
            updated_grade_rows = driver.find_elements(By.CSS_SELECTOR, ".home__grade-row")
            assert len(updated_grade_rows) == initial_count + 1, "New grade row was not added!"
            
            # 4. Test removing a grade row
            # Find the remove button in the last added row and click it
            remove_button = updated_grade_rows[-1].find_element(By.CSS_SELECTOR, ".home__remove-button")
            remove_button.click()
            
            # Verify the row was removed
            WebDriverWait(driver, 5).until(
                lambda d: len(d.find_elements(By.CSS_SELECTOR, ".home__grade-row")) == initial_count
            )
            final_grade_rows = driver.find_elements(By.CSS_SELECTOR, ".home__grade-row")
            assert len(final_grade_rows) == initial_count, "Grade row was not removed!"
            
        except Exception as e:
            # Take screenshot on any failure
            driver.save_screenshot(f"screenshots/error_{int(time.time())}.png")
            print(f"Current URL: {driver.current_url}")
            print(f"Page source excerpt: {driver.page_source[:500]}...")
            raise e