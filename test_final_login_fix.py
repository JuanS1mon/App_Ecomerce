#!/usr/bin/env python3
"""
Test final para verificar que el bucle de login ha sido solucionado
Verifica el flujo: login -> navegación con token -> acceso exitoso a admin
"""
import requests
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def test_programmatic_login_flow():
    """Test del flujo de login usando requests (simulando el interceptor)"""
    print("\n🔍 TEST PROGRAMÁTICO: Login -> Admin con token")
    print("=" * 50)
    
    base_url = "http://127.0.0.1:8000"
    
    try:
        # Paso 1: Login
        print("\n1️⃣ Realizando login...")
        login_data = {
            'username': 'juan',
            'password': 'juan123'
        }
        
        login_response = requests.post(
            f"{base_url}/login",
            data=login_data,
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            timeout=10
        )
        
        if login_response.status_code != 200:
            print(f"   ❌ Login falló: {login_response.status_code}")
            return False
            
        login_result = login_response.json()
        token = login_result.get('access_token')
        
        if not token:
            print("   ❌ No se recibió token")
            return False
            
        print(f"   ✅ Login exitoso, token recibido")
        
        # Paso 2: Acceso a admin CON token (simulando navegateWithAuth)
        print("\n2️⃣ Accediendo a /admin con token (simulando interceptor)...")
        
        admin_response = requests.get(
            f"{base_url}/admin",
            headers={
                'Authorization': f'Bearer {token}',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
            },
            allow_redirects=False,
            timeout=10
        )
        
        print(f"   Status: {admin_response.status_code}")
        
        if admin_response.status_code == 200:
            print("   ✅ Acceso exitoso a admin")
            
            # Verificar contenido
            if "Panel de Administración" in admin_response.text:
                print("   ✅ Contenido de admin correcto")
                return True
            else:
                print("   ⚠️ Respuesta inesperada en admin")
                return False
                
        elif admin_response.status_code in [301, 302, 307, 308]:
            redirect_url = admin_response.headers.get('Location', 'N/A')
            print(f"   ❌ Redirección a: {redirect_url}")
            
            if 'login' in redirect_url.lower():
                print("   ❌ PROBLEMA: Aún redirige al login")
                return False
            else:
                print("   ⚠️ Redirección inesperada")
                return False
        else:
            print(f"   ❌ Error inesperado: {admin_response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return False

def test_browser_login_flow():
    """Test del flujo completo usando navegador real"""
    print("\n🌐 TEST NAVEGADOR: Login -> Redirección automática")
    print("=" * 50)
    
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    # chrome_options.add_argument("--headless")  # Comentado para ver lo que pasa
    
    driver = None
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.set_window_size(1200, 800)
        
        # Ir a la página de login
        login_url = "http://localhost:8000/loginpage"
        print(f"📍 Accediendo a: {login_url}")
        driver.get(login_url)
        
        # Esperar a que cargue la página
        wait = WebDriverWait(driver, 10)
        
        # Buscar campos de login
        username_field = wait.until(EC.presence_of_element_located((By.ID, "username")))
        password_field = driver.find_element(By.ID, "password")
        submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        
        print("📝 Llenando formulario de login...")
        
        # Llenar formulario
        username_field.clear()
        username_field.send_keys("juan")
        
        password_field.clear()
        password_field.send_keys("juan123")
        
        # Verificar que hay token storage disponible
        driver.execute_script("console.log('🔧 Verificando localStorage antes del login...');")
        
        print("🚀 Enviando formulario...")
        submit_button.click()
        
        # Esperar redirección o respuesta
        time.sleep(5)
        
        # Verificar estado final
        current_url = driver.current_url
        print(f"📍 URL final: {current_url}")
        
        # Verificar token en localStorage
        token_in_storage = driver.execute_script("return localStorage.getItem('access_token');")
        print(f"🎫 Token en localStorage: {'✅ Presente' if token_in_storage else '❌ Ausente'}")
        
        if token_in_storage:
            token_length = len(token_in_storage) if token_in_storage else 0
            print(f"📏 Longitud del token: {token_length} caracteres")
        
        # Verificar si estamos en admin
        if "/admin" in current_url and "login" not in current_url:
            print("🎉 ¡ÉXITO! Login y redirección a admin funcionando")
            
            # Verificar contenido de la página
            try:
                admin_header = driver.find_element(By.TAG_NAME, "h1")
                if "Panel de Administración" in admin_header.text:
                    print("✅ Contenido de admin correcto")
                    return True
                else:
                    print("⚠️ Contenido inesperado en admin")
                    return False
            except:
                print("⚠️ No se pudo verificar contenido de admin")
                return False
                
        elif "login" in current_url:
            print("❌ PROBLEMA: Aún en página de login después del envío")
            
            # Verificar si hay mensajes de error
            try:
                page_text = driver.find_element(By.TAG_NAME, "body").text
                if "error" in page_text.lower() or "incorrecto" in page_text.lower():
                    print("❌ Error de autenticación detectado")
                else:
                    print("❌ Sin mensaje de error explícito")
            except:
                pass
                
            return False
        else:
            print(f"❓ URL inesperada: {current_url}")
            return False
            
    except Exception as e:
        print(f"❌ Error en test de navegador: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        if driver:
            print("🔧 Cerrando navegador...")
            driver.quit()

def main():
    print("🧪 VERIFICACIÓN FINAL DEL FIX DEL BUCLE DE LOGIN")
    print("=" * 60)
    
    # Test 1: Flujo programático
    programmatic_success = test_programmatic_login_flow()
    
    # Test 2: Flujo de navegador
    browser_success = test_browser_login_flow()
    
    # Resumen
    print("\n📊 RESUMEN DE RESULTADOS")
    print("=" * 30)
    print(f"✅ Test programático: {'PASS' if programmatic_success else 'FAIL'}")
    print(f"🌐 Test navegador: {'PASS' if browser_success else 'FAIL'}")
    
    if programmatic_success and browser_success:
        print("\n🎉 ¡BUCLE DE LOGIN SOLUCIONADO!")
        print("✅ Ambos tests pasaron exitosamente")
    else:
        print("\n❌ Aún hay problemas que resolver")
        if not programmatic_success:
            print("   - Test programático falló (problema de servidor/token)")
        if not browser_success:
            print("   - Test navegador falló (problema de frontend/interceptor)")

if __name__ == "__main__":
    main()
