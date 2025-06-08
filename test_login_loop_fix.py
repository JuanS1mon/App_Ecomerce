#!/usr/bin/env python3
# Test final para verificar que el bucle de redirección está resuelto

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

def test_login_flow_complete():
    """
    Test completo del flujo de login sin bucles
    """
    print("🔍 Testing complete login flow to verify no redirect loops")
    
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
        
        # Step 1: Navigate to login page
        login_url = "http://localhost:8000/loginpage"
        print(f"📍 Step 1: Navigating to login page: {login_url}")
        driver.get(login_url)
        
        # Wait for page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "form_common"))
        )
        print("✅ Login page loaded successfully")
        
        # Step 2: Fill and submit login form
        username_field = driver.find_element(By.ID, "username")
        password_field = driver.find_element(By.ID, "password")
        
        username_field.clear()
        username_field.send_keys("testuser")
        
        password_field.clear()
        password_field.send_keys("Test123456")
        
        print("📝 Step 2: Form fields populated")
        
        # Submit the form
        submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        print("🚀 Step 3: Submitting login form...")
        submit_button.click()
        
        # Step 3: Wait for login processing and redirection
        print("⏳ Step 4: Waiting for login processing and redirection...")
        time.sleep(5)
        
        # Step 4: Check final URL
        final_url = driver.current_url
        print(f"📍 Step 5: Final URL after login: {final_url}")
        
        # Step 5: Analyze result
        if "login" in final_url.lower():
            print("❌ FAILED: Still on login page - possible loop or login failure")
            
            # Check for error messages
            try:
                body_text = driver.find_element(By.TAG_NAME, "body").text
                if "error" in body_text.lower() or "incorrecto" in body_text.lower():
                    print("   └─ Reason: Login credentials rejected")
                else:
                    print("   └─ Reason: Possible redirect loop")
                return "FAILED"
            except:
                return "FAILED"
                
        elif "admin" in final_url or final_url.endswith("/") or "index" in final_url:
            print("🎉 SUCCESS: Successfully redirected to admin/dashboard page")
            
            # Wait a bit more to see if there are any additional redirects (loop detection)
            print("🔍 Step 6: Monitoring for redirect loops...")
            time.sleep(3)
            
            loop_check_url = driver.current_url
            if loop_check_url != final_url:
                print(f"❌ REDIRECT LOOP DETECTED: URL changed from {final_url} to {loop_check_url}")
                return "LOOP_DETECTED"
            else:
                print("✅ No redirect loops detected - URL remains stable")
                return "SUCCESS"
        else:
            print(f"❓ UNCLEAR: Unexpected final URL: {final_url}")
            return "UNCLEAR"
        
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return "ERROR"
        
    finally:
        if driver:
            print("🔧 Closing browser...")
            driver.quit()

def test_direct_admin_access():
    """
    Test accessing /admin directly to verify no loops
    """
    print("\n🔍 Testing direct access to /admin page")
    
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    driver = None
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.set_window_size(1200, 800)
        
        admin_url = "http://localhost:8000/admin"
        print(f"📍 Accessing admin page directly: {admin_url}")
        driver.get(admin_url)
        
        # Wait for page load
        time.sleep(3)
        
        # Check if redirected to login (expected for unauthenticated user)
        current_url = driver.current_url
        print(f"📍 Current URL: {current_url}")
        
        if "login" in current_url:
            print("✅ Correctly redirected to login page (user not authenticated)")
            return "EXPECTED_REDIRECT"
        elif "admin" in current_url:
            print("✅ Admin page loaded (user was already authenticated)")
            return "AUTHENTICATED_ACCESS"
        else:
            print(f"❓ Unexpected URL: {current_url}")
            return "UNEXPECTED"
            
    except Exception as e:
        print(f"❌ Direct admin test failed: {e}")
        return "ERROR"
        
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    print("🧪 Complete Login Flow Test - Loop Detection")
    print("="*60)
    
    # Test 1: Complete login flow
    login_result = test_login_flow_complete()
    
    # Test 2: Direct admin access
    admin_result = test_direct_admin_access()
    
    print("\n" + "="*60)
    print("📊 FINAL RESULTS:")
    print(f"   Login Flow Test: {login_result}")
    print(f"   Direct Admin Access: {admin_result}")
    
    if login_result == "SUCCESS":
        print("\n🎉 ¡PROBLEMA DEL BUCLE RESUELTO!")
        print("   ✅ El login funciona correctamente")
        print("   ✅ No hay bucles de redirección")
        print("   ✅ La redirección a /admin funciona")
    elif login_result == "LOOP_DETECTED":
        print("\n❌ BUCLE DE REDIRECCIÓN AÚN PRESENTE")
        print("   Se necesita más investigación para eliminar el bucle")
    elif login_result == "FAILED":
        print("\n❌ EL LOGIN FALLÓ")
        print("   Verificar credenciales o configuración del servidor")
    else:
        print(f"\n❓ RESULTADO INCIERTO: {login_result}")
        print("   Se requiere verificación manual")
    
    print("🏁 Test completed")
