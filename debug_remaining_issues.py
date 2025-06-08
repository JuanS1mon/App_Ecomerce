#!/usr/bin/env python3
"""
Debug específico para problemas restantes
"""

import requests
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException

BASE_URL = "http://localhost:8000"

def debug_login_page_structure():
    """Debuggea la estructura de la página de login"""
    print("🔍 DEBUGGEANDO ESTRUCTURA DE LA PÁGINA DE LOGIN")
    print("=" * 60)
    
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    driver = None
    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.set_page_load_timeout(30)
        
        print("📍 Navegando a página de login...")
        driver.get(f"{BASE_URL}/loginpage")
        
        # Esperar a que la página cargue completamente
        time.sleep(3)
        
        print("📍 Página cargada, analizando estructura...")
        
        # Ver el título de la página
        print(f"Título: {driver.title}")
        
        # Ver el HTML del body
        body = driver.find_element(By.TAG_NAME, "body")
        print(f"Contenido del body (primeros 500 chars): {body.text[:500]}...")
        
        # Buscar formularios
        forms = driver.find_elements(By.TAG_NAME, "form")
        print(f"Formularios encontrados: {len(forms)}")
        
        for i, form in enumerate(forms):
            print(f"  Formulario {i+1}: ID={form.get_attribute('id')}, Action={form.get_attribute('action')}")
        
        # Buscar por diferentes IDs posibles
        possible_ids = ["loginForm", "form_common", "username", "password"]
        for element_id in possible_ids:
            try:
                element = driver.find_element(By.ID, element_id)
                print(f"✅ Encontrado elemento con ID '{element_id}': {element.tag_name}")
            except:
                print(f"❌ No encontrado elemento con ID '{element_id}'")
        
        # Buscar inputs
        inputs = driver.find_elements(By.TAG_NAME, "input")
        print(f"Inputs encontrados: {len(inputs)}")
        for i, inp in enumerate(inputs):
            print(f"  Input {i+1}: type={inp.get_attribute('type')}, name={inp.get_attribute('name')}, id={inp.get_attribute('id')}")
        
        # Verificar si hay errores JavaScript en la consola
        logs = driver.get_log('browser')
        if logs:
            print("⚠️  Errores JavaScript encontrados:")
            for log in logs[-5:]:  # Últimos 5 logs
                print(f"  {log['level']}: {log['message']}")
        else:
            print("✅ No hay errores JavaScript aparentes")
            
        return True
        
    except Exception as e:
        print(f"❌ Error debuggeando página: {e}")
        return False
    finally:
        if driver:
            driver.quit()

def debug_admin_access():
    """Debuggea el acceso a /admin con token"""
    print("\n🔍 DEBUGGEANDO ACCESO A /ADMIN")
    print("=" * 60)
    
    # Obtener token primero
    login_data = {
        "username": "testuser",
        "password": "Test123456"
    }
    
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    try:
        # Login
        response = requests.post(f"{BASE_URL}/login", data=login_data, headers=headers)
        if response.status_code != 200:
            print(f"❌ No se pudo obtener token: {response.status_code}")
            return False
        
        token = response.json().get('access_token')
        print(f"✅ Token obtenido: {token[:50]}...")
        
        # Probar diferentes formas de acceso a /admin
        test_endpoints = ["/admin", "/", "/index"]
        
        for endpoint in test_endpoints:
            print(f"\n📍 Probando endpoint: {endpoint}")
            
            # Sin token
            resp_no_token = requests.get(f"{BASE_URL}{endpoint}")
            print(f"  Sin token: {resp_no_token.status_code}")
            
            # Con token en Authorization header
            auth_headers = {"Authorization": f"Bearer {token}"}
            resp_auth = requests.get(f"{BASE_URL}{endpoint}", headers=auth_headers)
            print(f"  Con Authorization header: {resp_auth.status_code}")
            
            # Con cookies (simular navegador)
            cookies = {"access_token": token}
            resp_cookies = requests.get(f"{BASE_URL}{endpoint}", cookies=cookies)
            print(f"  Con cookies: {resp_cookies.status_code}")
            
            # Si hay redirección
            if resp_no_token.status_code in [301, 302, 307, 308]:
                print(f"  Redirección a: {resp_no_token.headers.get('Location', 'No especificado')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error debuggeando admin: {e}")
        return False

def main():
    """Ejecuta debugging específico"""
    print("🚀 DEBUGGING ESPECÍFICO DE PROBLEMAS RESTANTES")
    print("=" * 70)
    
    # Debug 1: Estructura de página de login
    login_debug = debug_login_page_structure()
    
    # Debug 2: Acceso a admin
    admin_debug = debug_admin_access()
    
    print("\n" + "=" * 70)
    print("📊 RESUMEN DE DEBUGGING:")
    print("=" * 70)
    print(f"Login Page Structure:     {'✅ OK' if login_debug else '❌ PROBLEM'}")
    print(f"Admin Access Debug:       {'✅ OK' if admin_debug else '❌ PROBLEM'}")

if __name__ == "__main__":
    main()
