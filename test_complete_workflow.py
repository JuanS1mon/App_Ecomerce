#!/usr/bin/env python3
"""
Script de prueba completa para verificar que todos los problemas del workflow de autenticación estén resueltos.
"""

import requests
import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException

BASE_URL = "http://localhost:8000"

def test_server_status():
    """Verifica que el servidor esté funcionando"""
    print("🔍 Verificando estado del servidor...")
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        print(f"✅ Servidor activo - Status: {response.status_code}")
        return True
    except Exception as e:
        print(f"❌ Error del servidor: {e}")
        return False

def test_login_endpoint():
    """Prueba directa del endpoint /login"""
    print("\n🔍 Probando endpoint /login directamente...")
    
    # El endpoint espera form data, no JSON
    login_data = {
        "username": "testuser",
        "password": "Test123456"
    }
    
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    try:
        response = requests.post(f"{BASE_URL}/login", data=login_data, headers=headers, timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Login endpoint funciona correctamente")
            print(f"Token recibido: {data.get('access_token', 'No token')[:50]}...")
            return data.get('access_token')
        else:
            print(f"❌ Error en login: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error en endpoint login: {e}")
        return None

def test_reset_password_page():
    """Verifica que la página de reset password esté disponible"""
    print("\n🔍 Verificando página de reset password...")
    try:
        response = requests.get(f"{BASE_URL}/reset-password", timeout=5)
        if response.status_code == 200:
            print("✅ Página de reset password accesible")
            return True
        else:
            print(f"❌ Error en página reset password: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error accediendo a reset password: {e}")
        return False

def test_browser_login_workflow():
    """Prueba el flujo completo de login en el navegador"""
    print("\n🔍 Probando flujo completo de login en navegador...")
    
    # Configurar Chrome para testing
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Cambiar a False para ver el navegador
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    
    driver = None
    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.set_page_load_timeout(30)
        
        # 1. Ir a la página de login
        print("   📍 Navegando a página de login...")
        driver.get(f"{BASE_URL}/loginpage")
          # Esperar a que la página cargue
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "form_common"))
        )
        print("   ✅ Página de login cargada")
          # 2. Completar formulario de login
        print("   📍 Completando formulario de login...")
        username_field = driver.find_element(By.ID, "username")
        password_field = driver.find_element(By.ID, "password")
        
        username_field.send_keys("testuser")
        password_field.send_keys("Test123456")
        
        # 3. Enviar formulario
        print("   📍 Enviando formulario de login...")
        login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        login_button.click()
        
        # 4. Esperar redirección y verificar que no hay bucle
        print("   📍 Verificando redirección sin bucle...")
        time.sleep(2)  # Dar tiempo para redirección
        
        # Verificar que llegamos a la página correcta y no hay bucle
        current_url = driver.current_url
        print(f"   📍 URL actual: {current_url}")
        
        # Verificar que no estamos en loop entre páginas
        start_time = time.time()
        url_history = [current_url]
        
        for i in range(5):  # Verificar por 5 segundos
            time.sleep(1)
            new_url = driver.current_url
            if new_url != current_url:
                url_history.append(new_url)
                current_url = new_url
                
                # Si volvemos a una URL anterior, hay bucle
                if url_history.count(new_url) > 1:
                    print(f"   ❌ BUCLE DETECTADO: {url_history}")
                    return False
        
        # Verificar que estamos en una página de admin/dashboard
        if "/admin" in current_url or "index" in current_url or "dashboard" in current_url:
            print("   ✅ Login exitoso, redirección correcta sin bucle")
            print(f"   📍 URL final: {current_url}")
            return True
        else:
            print(f"   ❌ No se redirigió correctamente. URL: {current_url}")
            return False
            
    except TimeoutException:
        print("   ❌ Timeout esperando elementos de la página")
        return False
    except Exception as e:
        print(f"   ❌ Error en prueba de navegador: {e}")
        return False
    finally:
        if driver:
            driver.quit()

def test_authenticated_access(token):
    """Prueba acceso a página protegida con token"""
    print("\n🔍 Probando acceso autenticado...")
    
    if not token:
        print("❌ No hay token disponible")
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/admin", headers=headers, timeout=10)
        if response.status_code == 200:
            print("✅ Acceso autenticado exitoso")
            return True
        else:
            print(f"❌ Error en acceso autenticado: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error probando acceso autenticado: {e}")
        return False

def main():
    """Ejecuta todas las pruebas"""
    print("🚀 INICIANDO PRUEBAS COMPLETAS DEL WORKFLOW DE AUTENTICACIÓN")
    print("=" * 60)
    
    tests_results = {}
    
    # Test 1: Estado del servidor
    tests_results['server'] = test_server_status()
    
    # Test 2: Endpoint de login
    token = None
    if tests_results['server']:
        token = test_login_endpoint()
        tests_results['login_endpoint'] = token is not None
    
    # Test 3: Página de reset password
    if tests_results['server']:
        tests_results['reset_password'] = test_reset_password_page()
    
    # Test 4: Flujo completo en navegador
    if tests_results['server']:
        tests_results['browser_workflow'] = test_browser_login_workflow()
    
    # Test 5: Acceso autenticado
    if token:
        tests_results['authenticated_access'] = test_authenticated_access(token)
    
    # Resumen final
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE RESULTADOS:")
    print("=" * 60)
    
    all_passed = True
    for test_name, result in tests_results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        test_display = test_name.replace('_', ' ').title()
        print(f"{test_display:<25} {status}")
        if not result:
            all_passed = False
    
    print("=" * 60)
    if all_passed:
        print("🎉 TODAS LAS PRUEBAS PASARON - SISTEMA FUNCIONANDO CORRECTAMENTE")
    else:
        print("⚠️  ALGUNAS PRUEBAS FALLARON - REVISAR PROBLEMAS PENDIENTES")
    
    return all_passed

if __name__ == "__main__":
    main()
