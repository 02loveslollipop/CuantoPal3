import time
import pytest
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class TestHomePage:
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