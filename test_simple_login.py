import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

def test_simple_login():
    print("🚀 TESTING LOGIN SIMPLE PAGE")
    print("=" * 50)
    
    # Primero verificar que el endpoint funciona
    try:
        response = requests.get("http://localhost:8000/login-simple")
        if response.status_code == 200:
            print("✅ Página simple accesible")
        else:
            print(f"❌ Error accediendo a página simple: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False
    
    # Configurar Chrome
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        print("\n📍 Navegando a página simple...")
        driver.get("http://localhost:8000/login-simple")
        
        # Esperar que la página se cargue
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "loginForm")))
        print("✅ Página cargada correctamente")
        
        # Verificar elementos del formulario
        username_field = driver.find_element(By.ID, "username")
        password_field = driver.find_element(By.ID, "password")
        submit_btn = driver.find_element(By.ID, "submitBtn")
        
        print("✅ Elementos del formulario encontrados")
        
        # Verificar valores pre-llenados
        username_value = username_field.get_attribute("value")
        password_value = password_field.get_attribute("value")
        
        print(f"📋 Usuario pre-llenado: {username_value}")
        print(f"📋 Contraseña pre-llenada: {'***' if password_value else 'vacío'}")
        
        # Hacer click en submit
        print("\n📍 Enviando formulario...")
        submit_btn.click()
        
        # Esperar a que aparezca algún resultado
        time.sleep(3)
        
        # Verificar debug log
        debug_content = driver.find_element(By.ID, "debugContent")
        debug_text = debug_content.text
        
        print("\n📋 Debug Log del navegador:")
        print("-" * 30)
        for line in debug_text.split('\n')[-10:]:  # Últimas 10 líneas
            if line.strip():
                print(f"   {line}")
        print("-" * 30)
        
        # Verificar si hay mensaje de error o éxito
        message_div = driver.find_element(By.ID, "message")
        message_text = message_div.text
        message_display = message_div.value_of_css_property("display")
        
        if message_display != "none" and message_text:
            print(f"📝 Mensaje mostrado: {message_text}")
            
            if "exitoso" in message_text.lower() or "success" in message_text.lower():
                print("✅ Login reportado como exitoso")
                
                # Esperar redirección
                print("⏳ Esperando redirección...")
                time.sleep(2)
                
                current_url = driver.current_url
                print(f"📍 URL final: {current_url}")
                
                if "admin" in current_url:
                    print("✅ REDIRECCIÓN EXITOSA A ADMIN")
                    return True
                else:
                    print("❌ No se redirigió a admin")
                    return False
            else:
                print("❌ Error en login")
                return False
        else:
            print("❌ No se mostró ningún mensaje")
            return False
            
    except Exception as e:
        print(f"❌ Error durante el test: {str(e)}")
        
        # Capturar console logs en caso de error
        try:
            logs = driver.get_log('browser')
            if logs:
                print("\n📋 Console logs del navegador:")
                for log in logs:
                    print(f"   {log['level']}: {log['message']}")
        except:
            pass
            
        return False
    
    finally:
        print(f"\n🔍 URL final: {driver.current_url}")
        print("Cerrando navegador...")
        driver.quit()

if __name__ == "__main__":
    success = test_simple_login()
    if success:
        print("\n🎉 TEST PASSED - Login funciona correctamente")
    else:
        print("\n❌ TEST FAILED - Revisar logs para más detalles")
