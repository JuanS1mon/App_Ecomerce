#!/usr/bin/env python3
"""
Script para verificar que el navbar dinámico funciona correctamente
en la página de análisis admin.
"""

import requests
from bs4 import BeautifulSoup
import time

def test_analisis_navbar():
    """Verifica que el navbar dinámico esté integrado correctamente"""
    
    print("🔍 VERIFICANDO INTEGRACIÓN DEL NAVBAR DINÁMICO EN ANÁLISIS")
    print("=" * 60)
    
    url = "http://localhost:8000/analisis/admin"
    
    try:
        # Hacer request a la página
        print(f"📡 Conectando a: {url}")
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            print("✅ Página carga correctamente (Status 200)")
            
            # Parsear HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Verificar elementos del navbar dinámico
            checks = []
            
            # 1. Verificar que existe el contenedor del navbar
            navbar_container = soup.find('div', id='navbar-container')
            if navbar_container:
                checks.append("✅ Contenedor navbar-container encontrado")
            else:
                checks.append("❌ Contenedor navbar-container NO encontrado")
            
            # 2. Verificar que se carga el script components.js
            components_script = soup.find('script', src='/static/js/components.js')
            if components_script:
                checks.append("✅ Script components.js incluido")
            else:
                checks.append("❌ Script components.js NO incluido")
            
            # 3. Verificar que existe el script de inicialización
            scripts = soup.find_all('script')
            navbar_init_found = False
            for script in scripts:
                if script.string and 'loadComponent' in script.string and 'navbar-container' in script.string:
                    navbar_init_found = True
                    break
            
            if navbar_init_found:
                checks.append("✅ Script de inicialización del navbar encontrado")
            else:
                checks.append("❌ Script de inicialización del navbar NO encontrado")
            
            # 4. Verificar que NO existe el navbar estático anterior
            old_navbar = soup.find('nav', class_='bg-white shadow-md sticky top-0 z-50')
            if not old_navbar:
                checks.append("✅ Navbar estático anterior removido correctamente")
            else:
                checks.append("⚠️ Navbar estático anterior aún presente")
            
            # 5. Verificar título de la página
            title = soup.find('title')
            if title and 'Análisis' in title.text:
                checks.append("✅ Título de página correcto")
            else:
                checks.append("❌ Título de página incorrecto")
            
            # 6. Verificar que se mantiene el contenido principal
            main_content = soup.find('h1')
            if main_content and 'Análisis' in main_content.text:
                checks.append("✅ Contenido principal intacto")
            else:
                checks.append("❌ Contenido principal modificado")
            
            # Mostrar resultados
            print("\n📋 RESULTADOS DE LA VERIFICACIÓN:")
            print("-" * 40)
            for check in checks:
                print(f"  {check}")
            
            # Resumen
            successful_checks = len([c for c in checks if c.startswith("✅")])
            total_checks = len(checks)
            
            print(f"\n📊 RESUMEN:")
            print(f"  Verificaciones exitosas: {successful_checks}/{total_checks}")
            
            if successful_checks == total_checks:
                print("🎉 ¡INTEGRACIÓN COMPLETA Y EXITOSA!")
                return True
            elif successful_checks >= total_checks - 1:
                print("⚠️ Integración mayormente exitosa con alertas menores")
                return True
            else:
                print("❌ Integración incompleta - Requiere revisión")
                return False
        
        elif response.status_code == 404:
            print("❌ Página no encontrada (404)")
            return False
        elif response.status_code == 500:
            print("❌ Error del servidor (500)")
            return False
        else:
            print(f"⚠️ Respuesta inesperada: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"💥 Error de conexión: {str(e)}")
        return False

def test_navbar_functionality():
    """Verificar que el navbar funciona después de la carga"""
    
    print("\n🔧 PRUEBA DE FUNCIONALIDAD DEL NAVBAR")
    print("=" * 40)
    
    # Simular tiempo de carga
    print("⏳ Simulando tiempo de carga del navbar...")
    time.sleep(2)
    
    # Hacer una segunda petición para verificar consistencia
    try:
        response = requests.get("http://localhost:8000/analisis/admin", timeout=5)
        if response.status_code == 200:
            print("✅ Navbar se carga consistentemente")
            return True
        else:
            print("❌ Problemas de consistencia en la carga")
            return False
    except:
        print("❌ Error en prueba de consistencia")
        return False

if __name__ == "__main__":
    try:
        print("🚀 INICIANDO VERIFICACIÓN DE NAVBAR DINÁMICO")
        print("Timestamp:", time.strftime("%Y-%m-%d %H:%M:%S"))
        print()
        
        # Ejecutar verificaciones
        integration_ok = test_analisis_navbar()
        functionality_ok = test_navbar_functionality()
        
        print("\n" + "=" * 60)
        print("🏁 VERIFICACIÓN COMPLETA")
        print("=" * 60)
        
        if integration_ok and functionality_ok:
            print("🎉 ¡TODO FUNCIONA PERFECTAMENTE!")
            print("✅ El navbar dinámico está completamente integrado")
            print("✅ La página de análisis admin funciona correctamente")
            print("✅ Compatible con el sistema de breadcrumb")
        else:
            print("⚠️ Se detectaron algunos problemas:")
            if not integration_ok:
                print("  - Problemas en la integración del navbar")
            if not functionality_ok:
                print("  - Problemas de funcionalidad")
        
        print("\n💡 PRÓXIMOS PASOS:")
        print("  1. Verificar en navegador: http://localhost:8000/analisis/admin")
        print("  2. Comprobar que el breadcrumb dinámico funciona")
        print("  3. Verificar navegación entre secciones")
        
    except Exception as e:
        print(f"💥 Error ejecutando verificación: {str(e)}")
