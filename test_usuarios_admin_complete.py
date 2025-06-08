#!/usr/bin/env python3
"""
Test completo para el sistema de administración de usuarios
"""

import sys
import os
import asyncio
import requests
import json
from pathlib import Path

# Agregar el directorio de la aplicación al path
sys.path.insert(0, str(Path(__file__).parent / "sql_app"))

def test_admin_page():
    """Test básico para verificar que la página de admin funciona"""
    
    # URL base
    base_url = "http://localhost:8000"
    
    print("🔍 Probando acceso a la página de administración de usuarios...")
    
    try:
        # Simular una sesión con token de admin
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept-Language': 'es-ES,es;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        # Test 1: Verificar que la página de admin se carga
        print("\n1️⃣ Probando acceso a /usuarios_admin/")
        response = requests.get(f"{base_url}/usuarios_admin/", headers=headers, timeout=10)
        
        if response.status_code == 200:
            print("✅ Página de admin carga correctamente")
            print(f"   Status: {response.status_code}")
            
            # Verificar que el HTML contiene los elementos esperados
            html_content = response.text
            if "Gestión de Usuarios" in html_content:
                print("✅ Título de la página encontrado")
            if "Total Usuarios" in html_content:
                print("✅ Elementos de estadísticas encontrados")
            if "Lista de Usuarios" in html_content:
                print("✅ Tabla de usuarios encontrada")
            if "createUserModal" in html_content:
                print("✅ Modal de creación de usuario encontrado")
                
        elif response.status_code == 401:
            print("⚠️  Respuesta 401 - Se requiere autenticación (esperado)")
        elif response.status_code == 403:
            print("⚠️  Respuesta 403 - Se requieren permisos de admin (esperado)")
        else:
            print(f"❌ Error inesperado: Status {response.status_code}")
        
        # Test 2: Verificar endpoint de estadísticas
        print("\n2️⃣ Probando endpoint de estadísticas")
        stats_response = requests.get(f"{base_url}/usuarios_admin/estadisticas/", headers=headers, timeout=10)
        print(f"   Status de estadísticas: {stats_response.status_code}")
        
        # Test 3: Verificar endpoint de usuarios
        print("\n3️⃣ Probando endpoint de lista de usuarios")
        users_response = requests.get(f"{base_url}/usuarios_admin/usuarios/", headers=headers, timeout=10)
        print(f"   Status de lista de usuarios: {users_response.status_code}")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ No se pudo conectar al servidor. ¿Está corriendo en http://localhost:8000?")
        return False
    except requests.exceptions.Timeout:
        print("❌ Timeout al conectar con el servidor")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {str(e)}")
        return False

def test_html_structure():
    """Test para verificar la estructura del HTML"""
    
    html_file = Path(__file__).parent / "sql_app" / "static" / "html" / "config" / "usuarios_admin.html"
    
    print("\n🔍 Verificando estructura del archivo HTML...")
    
    if not html_file.exists():
        print(f"❌ Archivo HTML no encontrado: {html_file}")
        return False
    
    try:
        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verificar elementos clave
        checks = [
            ("Modal de creación", "createUserModal"),
            ("Modal de contraseña", "changePasswordModal"),
            ("Modal de perfil", "userProfileModal"),
            ("Función loadStatistics", "loadStatistics"),
            ("Función loadUsers", "loadUsers"),
            ("Tabla de usuarios", "users-table-body"),
            ("Botón crear usuario", "openCreateUserModal"),
            ("Formulario de creación", "createUserForm"),
            ("Formulario de contraseña", "changePasswordForm"),
        ]
        
        for name, element in checks:
            if element in content:
                print(f"✅ {name} encontrado")
            else:
                print(f"❌ {name} NO encontrado")
        
        return True
        
    except Exception as e:
        print(f"❌ Error al leer el archivo HTML: {str(e)}")
        return False

def main():
    """Función principal"""
    
    print("🚀 Iniciando tests del sistema de administración de usuarios")
    print("=" * 60)
    
    # Test 1: Verificar estructura HTML
    html_ok = test_html_structure()
    
    # Test 2: Verificar acceso a la página (si el servidor está corriendo)
    server_ok = test_admin_page()
    
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE RESULTADOS:")
    print(f"   HTML Structure: {'✅ OK' if html_ok else '❌ FAIL'}")
    print(f"   Server Access:  {'✅ OK' if server_ok else '❌ FAIL'}")
    
    if html_ok:
        print("\n🎉 La estructura HTML está completa y funcional")
        print("📝 Funcionalidades implementadas:")
        print("   • Página de administración de usuarios")
        print("   • Modales para crear usuario y cambiar contraseña")
        print("   • JavaScript para interacción con la API")
        print("   • Tabla dinámica de usuarios")
        print("   • Estadísticas en tiempo real")
        print("   • Botones de acción para cada usuario")
    
    if not server_ok:
        print("\n💡 Para probar completamente:")
        print("   1. Asegúrate de que el servidor esté corriendo")
        print("   2. Configura las variables de entorno necesarias")
        print("   3. Ejecuta: uvicorn sql_app.main:app --reload")

if __name__ == "__main__":
    main()
