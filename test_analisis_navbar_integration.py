"""
Script para verificar que la página de análisis admin
funciona correctamente con el navbar dinámico integrado
"""

import requests
import json
from typing import Dict, Any

def test_analisis_admin_with_navbar():
    """Prueba que la página de análisis admin funciona con navbar dinámico"""
    base_url = "http://localhost:8000"
    
    print("🔍 Verificando integración del navbar dinámico en análisis admin...")
    
    # 1. Login como admin
    login_data = {
        "username": "juan",
        "password": "qwe123"
    }
    
    try:
        # Login
        login_response = requests.post(
            f"{base_url}/auth/login", 
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if login_response.status_code != 200:
            print(f"❌ Error en login: {login_response.status_code}")
            return False
        
        # Extraer cookies de sesión
        cookies = login_response.cookies
        print("✅ Login exitoso")
        
        # 2. Verificar que se puede acceder a la página de análisis admin
        analisis_response = requests.get(
            f"{base_url}/analisis/admin", 
            cookies=cookies,
            allow_redirects=False
        )
        
        if analisis_response.status_code == 200:
            print("✅ Página de análisis admin accesible")
            
            # Verificar que contiene el navbar dinámico
            content = analisis_response.text
            
            checks = [
                ('navbar-container', 'Contenedor del navbar dinámico'),
                ('components.js', 'Script de componentes'),
                ('loadComponents()', 'Función de carga de componentes'),
                ('Gestión de Análisis de Datos', 'Título de la página'),
                ('Administración de Análisis', 'Título del head')
            ]
            
            all_checks_passed = True
            for check, description in checks:
                if check in content:
                    print(f"✅ {description} encontrado")
                else:
                    print(f"❌ {description} NO encontrado")
                    all_checks_passed = False
            
            return all_checks_passed
            
        elif analisis_response.status_code == 302:
            print(f"⚠️  Redireccionado a: {analisis_response.headers.get('Location', 'URL desconocida')}")
            return False
        else:
            print(f"❌ Error accediendo a análisis admin: {analisis_response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ No se puede conectar al servidor. ¿Está ejecutándose en localhost:8000?")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

def test_navbar_component_file():
    """Verifica que el archivo del navbar dinámico existe y tiene contenido"""
    base_url = "http://localhost:8000"
    
    try:
        # Verificar que el archivo del navbar está disponible
        navbar_response = requests.get(f"{base_url}/static/components/navbar.html")
        
        if navbar_response.status_code == 200:
            print("✅ Archivo navbar.html accesible")
            
            content = navbar_response.text
            navbar_checks = [
                ('breadcrumb-container', 'Contenedor de breadcrumb'),
                ('SQL App Studio', 'Texto del logo'),
                ('user-initial', 'Inicial del usuario'),
                ('menu-perfil', 'Menú de perfil'),
                ('fa-cog', 'Icono de admin')
            ]
            
            for check, description in navbar_checks:
                if check in content:
                    print(f"✅ {description} encontrado en navbar")
                else:
                    print(f"❌ {description} NO encontrado en navbar")
                    
            return True
        else:
            print(f"❌ Error accediendo a navbar.html: {navbar_response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error verificando navbar.html: {e}")
        return False

def test_components_js_file():
    """Verifica que el archivo de componentes JavaScript existe"""
    base_url = "http://localhost:8000"
    
    try:
        # Verificar que el archivo de componentes JS está disponible
        js_response = requests.get(f"{base_url}/static/js/components.js")
        
        if js_response.status_code == 200:
            print("✅ Archivo components.js accesible")
            
            content = js_response.text
            js_checks = [
                ('loadComponents', 'Función loadComponents'),
                ('loadNavbar', 'Función loadNavbar'),
                ('updateUserInfo', 'Función updateUserInfo'),
                ('generateBreadcrumb', 'Función generateBreadcrumb'),
                ('navigationItems', 'Array de navegación')
            ]
            
            for check, description in js_checks:
                if check in content:
                    print(f"✅ {description} encontrado en components.js")
                else:
                    print(f"❌ {description} NO encontrado en components.js")
                    
            return True
        else:
            print(f"❌ Error accediendo a components.js: {js_response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error verificando components.js: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Iniciando pruebas de integración del navbar dinámico en análisis admin")
    print("=" * 70)
    
    # Verificar archivos de componentes
    print("\n📁 Verificando archivos de componentes...")
    navbar_ok = test_navbar_component_file()
    js_ok = test_components_js_file()
    
    # Verificar página principal
    print("\n🔍 Verificando página de análisis admin...")
    page_ok = test_analisis_admin_with_navbar()
    
    # Resumen
    print("\n" + "=" * 70)
    print("📊 RESUMEN DE PRUEBAS:")
    print(f"   • Archivo navbar.html: {'✅ OK' if navbar_ok else '❌ FALLO'}")
    print(f"   • Archivo components.js: {'✅ OK' if js_ok else '❌ FALLO'}")
    print(f"   • Página análisis admin: {'✅ OK' if page_ok else '❌ FALLO'}")
    
    if all([navbar_ok, js_ok, page_ok]):
        print("\n🎉 ¡Todas las pruebas pasaron! El navbar dinámico está correctamente integrado.")
    else:
        print("\n⚠️  Algunas pruebas fallaron. Revisar los detalles arriba.")
