#!/usr/bin/env python3
# Automated browser test using Selenium to debug login issue

import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

def test_isolated_login():
    """
    Test the isolated login page using real browser automation
    """
    print("🔍 Starting automated browser test for isolated login page")
    
    # Configure Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-web-security")
    chrome_options.add_argument("--disable-features=VizDisplayCompositor")
    
    # Enable logging
    caps = DesiredCapabilities.CHROME
    caps['goog:loggingPrefs'] = {'browser': 'ALL', 'performance': 'ALL'}
    
    driver = None
    
    try:
        # Initialize Chrome driver
        driver = webdriver.Chrome(options=chrome_options, desired_capabilities=caps)
        driver.set_window_size(1200, 800)
        
        print("✅ Browser started successfully")
        
        # Navigate to isolated login page
        url = "http://localhost:8000/static/login_isolated.html"
        print(f"📍 Navigating to: {url}")
        driver.get(url)
        
        # Wait for page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "loginForm"))
        )
        print("✅ Page loaded successfully")
        
        # Wait a bit for any JavaScript to initialize
        time.sleep(2)
        
        # Check if form elements are present
        username_field = driver.find_element(By.ID, "username")
        password_field = driver.find_element(By.ID, "password")
        submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        
        print(f"📝 Username field value: '{username_field.get_attribute('value')}'")
        print(f"🔐 Password field value: '{password_field.get_attribute('value')}'")
        
        # Clear and set values to be sure
        username_field.clear()
        username_field.send_keys("testuser")
        
        password_field.clear()
        password_field.send_keys("Test123456")
        
        print("📝 Form fields populated")
        
        # Get initial logs from the page
        logs_element = driver.find_element(By.ID, "logs")
        initial_logs = logs_element.text
        print(f"📋 Initial page logs:\n{initial_logs}")
        
        # Submit the form
        print("🚀 Submitting form...")
        submit_button.click()
        
        # Wait for response (give it some time)
        time.sleep(5)
        
        # Get updated logs
        final_logs = logs_element.text
        print(f"📋 Final page logs:\n{final_logs}")
        
        # Check result div
        try:
            result_div = driver.find_element(By.ID, "result")
            result_content = result_div.text
            result_html = result_div.get_attribute("innerHTML")
            print(f"📊 Result content:\n{result_content}")
            print(f"📄 Result HTML:\n{result_html}")
        except Exception as e:
            print(f"❌ Could not get result div: {e}")
        
        # Get browser console logs
        print("\n🔍 Browser console logs:")
        for log_entry in driver.get_log('browser'):
            print(f"  {log_entry['level']}: {log_entry['message']}")
        
        # Get network logs if available
        print("\n🌐 Network logs:")
        try:
            for log_entry in driver.get_log('performance'):
                message = json.loads(log_entry['message'])
                if message['message']['method'] in ['Network.requestWillBeSent', 'Network.responseReceived']:
                    print(f"  {message['message']['method']}: {json.dumps(message['message']['params'], indent=2)}")
        except Exception as e:
            print(f"❌ Could not get network logs: {e}")
        
        print("\n✅ Test completed successfully")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        if driver:
            print("🔧 Closing browser...")
            driver.quit()

if __name__ == "__main__":
    print("🧪 Selenium Login Test")
    print("="*60)
    test_isolated_login()
    print("🏁 Test finished")
