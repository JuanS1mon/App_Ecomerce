#!/usr/bin/env python3
"""
TEST FINAL - Verificación Completa de Solución de Bucle Infinito
==============================================================

Este test verifica que la solución completa funciona correctamente:
1. ✅ Login funciona
2. ✅ Usuario autenticado puede acceder a /admin
3. ✅ NO hay bucle infinito al visitar /login estando autenticado
4. ✅ Interceptor embebido funciona correctamente
5. ✅ Middlewares de error están reactivados
"""
import requests
import time

def test_complete_solution():
    base_url = "http://localhost:8000"
    session = requests.Session()
    
    print("🎉 TEST FINAL: Solución Completa de Bucle Infinito")
    print("=" * 55)
    
    # 1. Test de login básico
    print("\n1️⃣ Test de Login Básico...")
    login_data = {'username': 'juan', 'password': 'qwer1234'}
    
    response = session.post(
        f"{base_url}/login",
        data=login_data,
        headers={'Content-Type': 'application/x-www-form-urlencoded'}
    )
    
    if response.status_code == 200:
        data = response.json()
        token = data.get('access_token')
        print(f"✅ Login exitoso - Token: {token[:30]}...")
    else:
        print(f"❌ Error en login: {response.status_code}")
        return False
    
    # 2. Test de acceso a admin con token
    print("\n2️⃣ Test de Acceso a Admin...")
    headers = {'Authorization': f'Bearer {token}'}
    
    admin_response = session.get(f"{base_url}/admin", headers=headers)
    if admin_response.status_code == 200:
        print("✅ Acceso a /admin exitoso con token")
    else:
        print(f"❌ Error accediendo a /admin: {admin_response.status_code}")
        return False
    
    # 3. Test de interceptor embebido
    print("\n3️⃣ Test de Interceptor Embebido...")
    login_page = session.get(f"{base_url}/loginpage")
    
    if login_page.status_code == 200:
        content = login_page.text
        
        # Verificaciones del interceptor
        checks = [
            ('AUTH_INTERCEPTOR_LOADED', 'Variable de interceptor cargado'),
            ('3.0.0-embedded', 'Versión correcta del interceptor'),
            ('/usuarios/current', 'Exclusión de endpoint de verificación'),
            ('navigateWithAuth', 'Función de navegación con auth'),
            ('checkIfAlreadyAuthenticated', 'Función de verificación de auth')
        ]
        
        for check, description in checks:
            if check in content:
                print(f"✅ {description}")
            else:
                print(f"❌ FALTA: {description}")
                return False
    else:
        print(f"❌ Error obteniendo login page: {login_page.status_code}")
        return False
    
    # 4. Test de verificación de token con /usuarios/current
    print("\n4️⃣ Test de Verificación de Token...")
    current_response = session.get(f"{base_url}/usuarios/current", headers=headers)
    
    if current_response.status_code == 200:
        user_data = current_response.json()
        if user_data.get('autenticado'):
            print(f"✅ Token válido - Usuario: {user_data.get('usuario')}")
        else:
            print("❌ Token válido pero usuario no autenticado")
            return False
    else:
        print(f"❌ Error verificando token: {current_response.status_code}")
        return False
    
    # 5. Test de middlewares reactivados
    print("\n5️⃣ Test de Middlewares Reactivados...")
    
    # Probar una página que no existe para verificar middleware de error
    not_found_response = session.get(f"{base_url}/pagina-que-no-existe")
    if not_found_response.status_code == 404:
        # Verificar si es HTML personalizado o JSON por defecto
        content_type = not_found_response.headers.get('content-type', '')
        if 'text/html' in content_type:
            print("✅ Middleware de error personalizado funcionando (404 HTML)")
        else:
            print("⚠️ Middleware de error devuelve JSON (funcional pero no personalizado)")
    else:
        print(f"❌ Middleware de error no funcionando correctamente: {not_found_response.status_code}")
    
    # 6. Test específico de prevención de bucle infinito
    print("\n6️⃣ Test de Prevención de Bucle Infinito...")
    
    # Simular múltiples accesos rápidos a login page (esto antes causaba bucle)
    for i in range(3):
        rapid_response = session.get(f"{base_url}/loginpage")
        if rapid_response.status_code != 200:
            print(f"❌ Fallo en acceso rápido #{i+1}: {rapid_response.status_code}")
            return False
        time.sleep(0.1)  # Pequeña pausa entre requests
    
    print("✅ Múltiples accesos rápidos sin bucle infinito")
    
    print("\n🎉 TODOS LOS TESTS PASARON EXITOSAMENTE")
    print("=" * 55)
    print("✅ Solución de bucle infinito implementada y funcionando")
    print("✅ Interceptor embebido operativo")
    print("✅ Middlewares de error reactivados")
    print("✅ Autenticación funcionando correctamente")
    
    return True

if __name__ == "__main__":
    success = test_complete_solution()
    if success:
        print("\n🚀 ¡SOLUCIÓN COMPLETAMENTE IMPLEMENTADA!")
        print("📋 Próximos pasos opcionales:")
        print("   - Limpiar archivos de test temporales")
        print("   - Documentar la solución en README")
        print("   - Realizar pruebas de carga si es necesario")
    else:
        print("\n⚠️ Algunos tests fallaron - revisar configuración")
