import pytest
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

@pytest.fixture(scope="function")
def driver():
    # Setup Chrome options
    chrome_options = Options()
    
    # Check if running in GitHub Actions
    if os.environ.get('GITHUB_ACTIONS') == 'true':
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
    
    chrome_options.add_argument('--window-size=1920,1080')
    
    # Initialize Chrome driver
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )
    
    # Create screenshots directory if it doesn't exist
    os.makedirs("screenshots", exist_ok=True)
    
    yield driver
    
    # Take screenshot on test failure
    if pytest.item and hasattr(pytest, '_funcargs'):
        test_name = pytest._funcargs.get('request', pytest._funcargs.get('fspath', pytest)).node.name
        driver.save_screenshot(f"screenshots/{test_name}.png")
    
    driver.quit()