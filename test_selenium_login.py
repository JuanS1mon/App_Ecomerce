#!/usr/bin/env python3
"""
Script para probar el JavaScript del navegador usando Selenium
"""

import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys

def test_login_with_selenium():
    """Probar el login usando Selenium para simular exactamente el navegador"""
    
    print("🧪 PROBANDO LOGIN CON SELENIUM")
    print("=" * 50)
    
    # Configurar opciones de Chrome
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-web-security")
    chrome_options.add_argument("--allow-running-insecure-content")
    # No headless para ver qué pasa
    # chrome_options.add_argument("--headless")
    
    driver = None
    
    try:
        # Inicializar el driver
        print("🚀 Iniciando Chrome...")
        driver = webdriver.Chrome(options=chrome_options)
        
        # Ir a la página de test simple
        test_url = "http://localhost:8000/static/test_login_simple.html"
        print(f"📍 Navegando a: {test_url}")
        driver.get(test_url)
        
        # Esperar a que cargue
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "testForm"))
        )
        print("✅ Página cargada")
        
        # Rellenar el formulario
        username_field = driver.find_element(By.ID, "username")
        password_field = driver.find_element(By.ID, "password")
        
        print("📝 Llenando formulario...")
        username_field.clear()
        username_field.send_keys("testuser")
        password_field.clear()
        password_field.send_keys("Test123456")
        
        # Obtener logs de consola antes del submit
        print("📊 Logs de consola antes del submit:")
        logs = driver.get_log('browser')
        for log in logs:
            print(f"  {log['level']}: {log['message']}")
        
        # Hacer submit
        submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        print("🚀 Haciendo submit del formulario...")
        submit_button.click()
        
        # Esperar respuesta
        print("⏳ Esperando respuesta...")
        time.sleep(3)
        
        # Obtener logs de consola después del submit
        print("📊 Logs de consola después del submit:")
        logs = driver.get_log('browser')
        for log in logs:
            print(f"  {log['level']}: {log['message']}")
        
        # Verificar el resultado
        try:
            result_div = driver.find_element(By.ID, "result")
            if result_div.is_displayed():
                result_text = result_div.text
                print(f"📋 Resultado mostrado:")
                print(f"  {result_text}")
                
                if "Login Exitoso" in result_text:
                    print("✅ LOGIN EXITOSO EN EL NAVEGADOR!")
                    return True
                else:
                    print("❌ LOGIN FALLÓ EN EL NAVEGADOR")
                    return False
            else:
                print("⚠️  Div de resultado no visible")
                
        except Exception as e:
            print(f"❌ Error al obtener resultado: {e}")
        
        # Esperar un poco más para observar
        print("⏳ Esperando para observar...")
        time.sleep(5)
        
        return False
        
    except Exception as e:
        print(f"❌ Error en la prueba: {e}")
        return False
    
    finally:
        if driver:
            print("🔚 Cerrando navegador...")
            driver.quit()

def test_original_login_page():
    """Probar también la página original de login"""
    
    print("\n🧪 PROBANDO PÁGINA ORIGINAL DE LOGIN")
    print("=" * 50)
    
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-web-security")
    
    driver = None
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        
        # Ir a la página original
        login_url = "http://localhost:8000/loginpage"
        print(f"📍 Navegando a: {login_url}")
        driver.get(login_url)
        
        # Esperar a que cargue
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "form_common"))
        )
        print("✅ Página original cargada")
        
        # Rellenar el formulario
        username_field = driver.find_element(By.ID, "username")
        password_field = driver.find_element(By.ID, "password")
        
        print("📝 Llenando formulario...")
        username_field.clear()
        username_field.send_keys("testuser")
        password_field.clear()
        password_field.send_keys("Test123456")
        
        # Obtener logs antes del submit
        print("📊 Logs antes del submit:")
        try:
            logs = driver.get_log('browser')
            for log in logs:
                print(f"  {log['level']}: {log['message']}")
        except:
            print("  No se pudieron obtener logs")
        
        # Hacer submit
        submit_button = driver.find_element(By.ID, "submit_button")
        print("🚀 Haciendo submit del formulario original...")
        submit_button.click()
        
        # Esperar respuesta
        print("⏳ Esperando respuesta...")
        time.sleep(5)
        
        # Obtener logs después del submit
        print("📊 Logs después del submit:")
        try:
            logs = driver.get_log('browser')
            for log in logs:
                print(f"  {log['level']}: {log['message']}")
        except:
            print("  No se pudieron obtener logs")
        
        # Verificar URL actual
        current_url = driver.current_url
        print(f"📍 URL actual: {current_url}")
        
        if current_url != login_url:
            print("✅ REDIRECCIÓN EXITOSA - Login funcionó!")
            return True
        else:
            print("❌ No hubo redirección - Login falló")
            
            # Verificar si hay mensajes de error
            try:
                error_element = driver.find_element(By.ID, "message")
                if error_element.text:
                    print(f"📋 Mensaje de error: {error_element.text}")
            except:
                print("  No se encontró mensaje de error")
            
            return False
        
    except Exception as e:
        print(f"❌ Error en la prueba: {e}")
        return False
    
    finally:
        if driver:
            print("🔚 Cerrando navegador...")
            driver.quit()

if __name__ == "__main__":
    print("🧪 PRUEBAS DE LOGIN CON SELENIUM")
    print("=" * 60)
    
    # Verificar que Selenium esté disponible
    try:
        from selenium import webdriver
        print("✅ Selenium disponible")
    except ImportError:
        print("❌ Selenium no está instalado. Instalando...")
        import subprocess
        subprocess.run(["pip", "install", "selenium"])
        from selenium import webdriver
    
    # Probar página simple
    simple_success = test_login_with_selenium()
    
    # Probar página original
    original_success = test_original_login_page()
    
    print(f"\n📊 RESULTADOS:")
    print(f"✅ Página simple: {'ÉXITO' if simple_success else 'FALLO'}")
    print(f"✅ Página original: {'ÉXITO' if original_success else 'FALLO'}")
    
    if simple_success and not original_success:
        print(f"\n🔍 CONCLUSIÓN: El problema está en la página original de login")
    elif not simple_success and not original_success:
        print(f"\n🔍 CONCLUSIÓN: Hay un problema general con el JavaScript")
    elif simple_success and original_success:
        print(f"\n🎉 CONCLUSIÓN: ¡Todo funciona correctamente!")
    else:
        print(f"\n🤔 CONCLUSIÓN: Resultados inesperados")
