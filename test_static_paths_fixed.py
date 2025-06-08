#!/usr/bin/env python3
"""
Script de verificación para comprobar que todos los endpoints 
funcionan correctamente después de la corrección de rutas estáticas.
"""

import requests
import time

def test_endpoint(url, description):
    """Prueba un endpoint y reporta el resultado"""
    try:
        response = requests.get(url)
        status = response.status_code
        size = len(response.content)
        
        if status == 200:
            print(f"✅ {description}: OK (Status: {status}, Size: {size} bytes)")
            return True
        else:
            print(f"❌ {description}: Error (Status: {status})")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ {description}: Error de conexión - {e}")
        return False

def main():
    """Función principal de pruebas"""
    base_url = "http://127.0.0.1:8000"
    
    print("🔍 Verificando endpoints después de la corrección de rutas...")
    print(f"🌐 URL base: {base_url}")
    print("-" * 60)
    
    # Lista de endpoints a probar
    endpoints = [
        ("/", "Página principal"),
        ("/loginpage", "Página de login"),
        ("/admin", "Panel de administración"),
        ("/docs", "Documentación Swagger"),
        ("/redoc", "Documentación ReDoc"),
    ]
    
    success_count = 0
    total_count = len(endpoints)
    
    for endpoint, description in endpoints:
        url = f"{base_url}{endpoint}"
        if test_endpoint(url, description):
            success_count += 1
        time.sleep(0.5)  # Pausa breve entre pruebas
    
    print("-" * 60)
    print(f"📊 Resumen: {success_count}/{total_count} endpoints funcionando correctamente")
    
    if success_count == total_count:
        print("🎉 ¡Todas las pruebas pasaron! El problema de rutas estáticas está resuelto.")
    else:
        print("⚠️  Algunos endpoints aún tienen problemas.")
    
    return success_count == total_count

if __name__ == "__main__":
    main()
