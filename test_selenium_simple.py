#!/usr/bin/env python3
# Simplified automated browser test using Selenium to debug login issue

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

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
    
    driver = None
    
    try:
        # Initialize Chrome driver
        driver = webdriver.Chrome(options=chrome_options)
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
        time.sleep(3)
        
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
            
            # Check if login was successful
            if "Login Exitoso" in result_content or "✅" in result_content:
                print("🎉 LOGIN WAS SUCCESSFUL!")
            elif "Error" in result_content or "❌" in result_content:
                print("❌ LOGIN FAILED!")
            else:
                print("❓ LOGIN RESULT UNCLEAR")
                
        except Exception as e:
            print(f"❌ Could not get result div: {e}")
        
        # Get browser console logs
        print("\n🔍 Browser console logs:")
        try:
            for log_entry in driver.get_log('browser'):
                print(f"  {log_entry['level']}: {log_entry['message']}")
        except Exception as e:
            print(f"❌ Could not get console logs: {e}")
        
        print("\n✅ Test completed successfully")
        
        # Keep browser open for manual inspection
        print("🔍 Browser will stay open for 10 seconds for manual inspection...")
        time.sleep(10)
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        if driver:
            print("🔧 Closing browser...")
            driver.quit()

if __name__ == "__main__":
    print("🧪 Selenium Login Test - Simplified")
    print("="*60)
    test_isolated_login()
    print("🏁 Test finished")
