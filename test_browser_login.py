import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

def test_browser_login():
    print("🚀 INICIANDO TEST DE LOGIN EN NAVEGADOR")
    
    # Configurar Chrome con más debugging
    chrome_options = Options()
    chrome_options.add_argument("--headless=false")  # Mostrar navegador
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--remote-debugging-port=9222")
    chrome_options.add_experimental_option("detach", True)  # Mantener navegador abierto
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        # Navegar a la página de login
        login_url = "http://localhost:8000/loginpage"
        print(f"📍 Navegando a: {login_url}")
        driver.get(login_url)
        
        # Esperar a que la página se cargue
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "form_common")))
        print("✅ Página de login cargada")
        
        # Verificar que el formulario existe
        form = driver.find_element(By.ID, "form_common")
        print(f"✅ Formulario encontrado: {form.tag_name}")
        
        # Completar credenciales
        username_field = driver.find_element(By.ID, "username")
        password_field = driver.find_element(By.ID, "password")
        
        username_field.clear()
        username_field.send_keys("testuser")
        password_field.clear()
        password_field.send_keys("Test123456")
        
        print("✅ Credenciales completadas")
        
        # Verificar URL antes del submit
        print(f"📍 URL antes del submit: {driver.current_url}")
        
        # Enviar formulario
        submit_button = driver.find_element(By.ID, "submit_button")
        print("📍 Haciendo click en submit...")
        submit_button.click()
        
        # Esperar un poco para ver qué pasa
        time.sleep(3)
        
        # Verificar URL después del submit
        current_url = driver.current_url
        print(f"📍 URL después del submit: {current_url}")
        
        # Verificar si hay algún mensaje en la página
        try:
            message_element = driver.find_element(By.ID, "message")
            message_text = message_element.text
            if message_text:
                print(f"📝 Mensaje en página: {message_text}")
        except:
            print("📝 No hay mensajes visibles")
        
        # Verificar console logs del navegador
        logs = driver.get_log('browser')
        if logs:
            print("📋 Console logs del navegador:")
            for log in logs[-10:]:  # Últimos 10 logs
                print(f"   {log['level']}: {log['message']}")
        
        # Verificar si se redirigió
        if "admin" in current_url:
            print("✅ Redirección exitosa a admin")
            return True
        elif current_url == login_url:
            print("❌ No se redirigió - permanece en login")
            return False
        else:
            print(f"❓ Redirigió a una URL inesperada: {current_url}")
            return False
            
    except Exception as e:
        print(f"❌ Error durante el test: {str(e)}")
        return False
    
    finally:
        print("🔍 Navegador permanecerá abierto para inspección manual...")
        input("Presiona Enter para cerrar el navegador...")
        driver.quit()

if __name__ == "__main__":
    test_browser_login()
