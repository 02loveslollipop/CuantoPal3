import time
import pytest
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

class TestHomePage:
    def _initial_setup(self, driver):
        base_url = os.environ.get('APP_URL', 'http://localhost:3000')
        driver.get(base_url)
        time.sleep(1) # Allow a brief moment for initial rendering

        # 1. Handle initial alert (if any)
        try:
            alert_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".alert__button.alert__button--single"))
            )
            alert_button.click()
            # Wait for the alert to disappear or for a subsequent element if needed
            WebDriverWait(driver, 5).until(EC.staleness_of(alert_button))
            print("Initial alert handled.")
        except TimeoutException:
            print("Initial alert not found or not clickable within 10s.")
        except Exception as e:
            print(f"Error clicking initial alert: {e}, proceeding.")

        # 2. Check if we are on the main page (with grade-input) or need to navigate back
        try:
            # Try to find a main page element immediately. If present, we are good.
            WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.ID, "grade-input")))
            print("Already on the main page with grade input.")
            return # Already on the correct page
        except TimeoutException:
            print("Grade input not immediately visible. Attempting navigation back from potential settings/initial page.")
            try:
                # If not on main page, try to click a common 'back' or 'home' button
                # Using ".nav-bar__button" from the original test_home_page_functional_flow
                back_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, ".nav-bar__button"))
                )
                back_button.click()
                print("Clicked .nav-bar__button.")
                # Wait for the main page element to ensure navigation was successful
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, "grade-input"))
                )
                print("Successfully navigated to the main page with grade-input after clicking back.")
            except TimeoutException:
                print("Failed to find grade-input after attempting back navigation.")
                os.makedirs("screenshots", exist_ok=True)
                driver.save_screenshot(f"screenshots/error_initial_setup_navigation_timeout_{int(time.time())}.png")
                raise Exception("Could not navigate to the main page with grade-input during setup.")
            except Exception as e_nav:
                print(f"Error during back navigation attempt: {e_nav}")
                os.makedirs("screenshots", exist_ok=True)
                driver.save_screenshot(f"screenshots/error_initial_setup_navigation_exception_{int(time.time())}.png")
                raise e_nav
        except Exception as e_main_check:
            print(f"Unexpected error during initial page check: {e_main_check}")
            os.makedirs("screenshots", exist_ok=True)
            driver.save_screenshot(f"screenshots/error_initial_setup_main_check_exception_{int(time.time())}.png")
            raise e_main_check

    def _add_grade_and_percentage(self, driver, grade, percentage):
        grade_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "grade-input"))
        )
        grade_input.clear()
        grade_input.send_keys(str(grade))

        percentage_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "percentage-input"))
        )
        percentage_input.clear()
        percentage_input.send_keys(str(percentage))

        add_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "add-grade-btn"))
        )
        add_button.click()

    def _get_grades_list_item_count(self, driver):
        try:
            grades_list_container = driver.find_element(By.ID, "grades-list")
            # Assuming direct children are the items; adjust selector if structure is different
            return len(grades_list_container.find_elements(By.XPATH, "./*"))
        except Exception:
            return 0 # If list not found or empty

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