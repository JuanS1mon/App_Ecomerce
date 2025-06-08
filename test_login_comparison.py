#!/usr/bin/env python3
# Test the clean login page to confirm the problem source

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

def test_clean_login():
    """
    Test the clean login page (without external scripts)
    """
    print("🔍 Testing CLEAN login page (without external scripts)")
    
    # Configure Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    driver = None
    
    try:
        # Initialize Chrome driver
        driver = webdriver.Chrome(options=chrome_options)
        driver.set_window_size(1200, 800)
        
        print("✅ Browser started successfully")
        
        # Navigate to clean login page
        url = "http://localhost:8000/static/login_clean.html"
        print(f"📍 Navigating to: {url}")
        driver.get(url)
        
        # Wait for page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "loginForm"))
        )
        print("✅ Page loaded successfully")
        
        # Wait a bit for any JavaScript to initialize
        time.sleep(2)
        
        # Submit the form (pre-filled with testuser/Test123456)
        submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        print("🚀 Submitting form...")
        submit_button.click()
        
        # Wait for response
        time.sleep(3)
        
        # Get the debug logs
        logs_element = driver.find_element(By.ID, "debugLogs")
        logs_content = logs_element.text
        print(f"📋 Debug Logs:\n{logs_content}")
        
        # Check for success indicators in logs
        if "LOGIN COMPLETAMENTE EXITOSO" in logs_content:
            print("🎉 CLEAN LOGIN PAGE: SUCCESS!")
            return "SUCCESS"
        elif "Error" in logs_content or "❌" in logs_content:
            print("❌ CLEAN LOGIN PAGE: FAILED!")
            return "FAILED"
        else:
            print("❓ CLEAN LOGIN PAGE: UNCLEAR RESULT")
            return "UNCLEAR"
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return "ERROR"
        
    finally:
        if driver:
            print("🔧 Closing browser...")
            driver.quit()

def test_original_login():
    """
    Test the original login page (with external scripts)
    """
    print("🔍 Testing ORIGINAL login page (with external scripts)")
    
    # Configure Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    driver = None
    
    try:
        # Initialize Chrome driver
        driver = webdriver.Chrome(options=chrome_options)
        driver.set_window_size(1200, 800)
        
        print("✅ Browser started successfully")
        
        # Navigate to original login page
        url = "http://localhost:8000/loginpage"
        print(f"📍 Navigating to: {url}")
        driver.get(url)
        
        # Wait for page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "loginForm"))
        )
        print("✅ Page loaded successfully")
        
        # Fill in the form
        username_field = driver.find_element(By.ID, "username")
        password_field = driver.find_element(By.ID, "password")
        
        username_field.clear()
        username_field.send_keys("testuser")
        
        password_field.clear()
        password_field.send_keys("Test123456")
        
        print("📝 Form fields populated")
        
        # Wait a bit for any JavaScript to initialize
        time.sleep(2)
        
        # Submit the form
        submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        print("🚀 Submitting form...")
        submit_button.click()
        
        # Wait for response
        time.sleep(5)
        
        # Check if we're still on login page or redirected
        current_url = driver.current_url
        print(f"📍 Current URL after login: {current_url}")
        
        # Get console logs
        print("\n🔍 Browser console logs:")
        try:
            for log_entry in driver.get_log('browser'):
                print(f"  {log_entry['level']}: {log_entry['message']}")
        except Exception as e:
            print(f"❌ Could not get console logs: {e}")
        
        if "loginpage" in current_url or "login" in current_url:
            print("❌ ORIGINAL LOGIN PAGE: Still on login page - FAILED!")
            return "FAILED"
        elif "dashboard" in current_url or current_url.endswith("/"):
            print("🎉 ORIGINAL LOGIN PAGE: Redirected successfully - SUCCESS!")
            return "SUCCESS"
        else:
            print(f"❓ ORIGINAL LOGIN PAGE: Unexpected URL: {current_url}")
            return "UNCLEAR"
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return "ERROR"
        
    finally:
        if driver:
            print("🔧 Closing browser...")
            driver.quit()

if __name__ == "__main__":
    print("🧪 Comparison Test: Clean vs Original Login Pages")
    print("="*70)
    
    # Test clean page first
    clean_result = test_clean_login()
    print("\n" + "="*70)
    
    # Test original page
    original_result = test_original_login()
    print("\n" + "="*70)
    
    # Summary
    print("📊 RESULTS SUMMARY:")
    print(f"   Clean Page (no external scripts): {clean_result}")
    print(f"   Original Page (with external scripts): {original_result}")
    
    if clean_result == "SUCCESS" and original_result == "FAILED":
        print("\n🎯 CONCLUSION: External scripts are causing the login issue!")
        print("   The problem is specifically in components.js or footer.html includes")
    elif clean_result == original_result:
        print(f"\n🤔 CONCLUSION: Both pages have the same result: {clean_result}")
        print("   The issue might be elsewhere")
    else:
        print(f"\n❓ CONCLUSION: Mixed results - need further investigation")
    
    print("🏁 Comparison test finished")
