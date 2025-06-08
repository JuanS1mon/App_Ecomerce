#!/usr/bin/env python3
# Test final para confirmar que el login original ahora funciona

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

def test_fixed_original_login():
    """
    Test the original login page after fixing components.js issue
    """
    print("🔍 Testing FIXED original login page")
    
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
        
        # Wait for response and possible redirect
        time.sleep(5)
        
        # Check if we're still on login page or redirected
        current_url = driver.current_url
        print(f"📍 Current URL after login: {current_url}")
        
        # Get console logs to check for errors
        print("\n🔍 Browser console logs:")
        try:
            for log_entry in driver.get_log('browser'):
                print(f"  {log_entry['level']}: {log_entry['message']}")
        except Exception as e:
            print(f"❌ Could not get console logs: {e}")
        
        # Check result
        if "loginpage" in current_url or "login" in current_url:
            # Still on login page, check for error messages or success indicators
            try:
                # Look for any error or success messages
                page_text = driver.find_element(By.TAG_NAME, "body").text
                if "éxito" in page_text.lower() or "exitoso" in page_text.lower():
                    print("🎉 LOGIN SUCCESSFUL (found success message)")
                    return "SUCCESS"
                elif "error" in page_text.lower() or "incorrecto" in page_text.lower():
                    print("❌ LOGIN FAILED (found error message)")
                    return "FAILED"
                else:
                    print("❌ LOGIN FAILED (still on login page, no success message)")
                    return "FAILED"
            except:
                print("❌ LOGIN FAILED (still on login page)")
                return "FAILED"
        elif "dashboard" in current_url or current_url.endswith("/") or "admin" in current_url:
            print("🎉 LOGIN SUCCESSFUL (redirected to dashboard/admin)")
            return "SUCCESS"
        else:
            print(f"❓ UNCLEAR RESULT (unexpected URL: {current_url})")
            return "UNCLEAR"
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return "ERROR"
        
    finally:
        if driver:
            print("🔧 Closing browser...")
            driver.quit()

if __name__ == "__main__":
    print("🧪 Final Test: Fixed Original Login Page")
    print("="*50)
    
    result = test_fixed_original_login()
    
    print(f"\n📊 FINAL RESULT: {result}")
    
    if result == "SUCCESS":
        print("🎉 ¡PROBLEMA RESUELTO COMPLETAMENTE!")
        print("   El login original ahora funciona después de deshabilitar components.js")
    elif result == "FAILED":
        print("❌ El problema persiste, se necesita más investigación")
    else:
        print("❓ Resultado incierto, se requiere verificación manual")
    
    print("🏁 Test final completado")
