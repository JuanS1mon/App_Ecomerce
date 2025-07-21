"""
Script para verificar que el navbar blanco funciona en la página de análisis
"""

def test_navbar_white_integration():
    """Verifica que la integración del navbar blanco esté correcta"""
    
    print("🔍 Verificando integración del navbar blanco...")
    
    # Verificar archivo HTML de análisis admin
    try:
        with open("sql_app/static/html/analisis_admin.html", "r", encoding="utf-8") as f:
            content = f.read()
            
        checks = [
            ("navbar-white.html", "Referencia al navbar blanco"),
            ("loadWhiteNavbar", "Función de carga del navbar blanco"),
            ("navbar-container", "Contenedor del navbar"),
            ("loadComponents", "Fallback al navbar dinámico")
        ]
        
        all_ok = True
        for check, description in checks:
            if check in content:
                print(f"✅ {description} encontrado")
            else:
                print(f"❌ {description} NO encontrado")
                all_ok = False
                
        return all_ok
        
    except Exception as e:
        print(f"❌ Error leyendo archivo: {e}")
        return False

def test_navbar_white_file():
    """Verifica que el archivo del navbar blanco existe y tiene contenido correcto"""
    
    print("\n📁 Verificando archivo navbar-white.html...")
    
    try:
        with open("sql_app/static/components/navbar-white.html", "r", encoding="utf-8") as f:
            content = f.read()
            
        checks = [
            ("bg-white", "Fondo blanco"),
            ("sticky top-0", "Posición fija"),
            ("shadow-md", "Sombra"),
            ("SQL App Studio", "Texto del logo"),
            ("breadcrumb-container", "Contenedor de breadcrumb"),
            ("menu-perfil", "Menú de perfil"),
            ("generateBreadcrumb", "Función de breadcrumb"),
            ("updateUserInfo", "Función de actualización de usuario")
        ]
        
        all_ok = True
        for check, description in checks:
            if check in content:
                print(f"✅ {description} encontrado")
            else:
                print(f"❌ {description} NO encontrado")
                all_ok = False
                
        return all_ok
        
    except Exception as e:
        print(f"❌ Error leyendo archivo navbar-white.html: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Verificando implementación del navbar blanco")
    print("=" * 60)
    
    file_ok = test_navbar_white_file()
    integration_ok = test_navbar_white_integration()
    
    print("\n" + "=" * 60)
    print("📊 RESUMEN:")
    print(f"   • Archivo navbar-white.html: {'✅ OK' if file_ok else '❌ FALLO'}")
    print(f"   • Integración en analisis_admin.html: {'✅ OK' if integration_ok else '❌ FALLO'}")
    
    if all([file_ok, integration_ok]):
        print("\n🎉 ¡Navbar blanco implementado correctamente!")
        print("💡 Características del navbar blanco:")
        print("   • Fondo blanco con sombra sutil")
        print("   • Posición fija en la parte superior (sticky)")
        print("   • Breadcrumb dinámico estilo explorador")
        print("   • Menú de usuario con dropdown")
        print("   • Enlaces de navegación principales")
        print("   • Fecha actual actualizada automáticamente")
        print(f"\n🌐 Accede a: http://127.0.0.1:8000/analisis/admin")
    else:
        print("\n⚠️  Hay algunos problemas en la implementación.")
