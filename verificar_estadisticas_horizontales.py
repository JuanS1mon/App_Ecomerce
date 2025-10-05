#!/usr/bin/env python3
"""
Script para verificar las estadísticas horizontales y los datos
"""

import requests
import time

def verificar_estadisticas_horizontales():
    """Verifica que las estadísticas se muestren correctamente en formato horizontal"""
    
    print("🔄 VERIFICANDO ESTADÍSTICAS HORIZONTALES")
    print("="*50)
    
    base_url = "http://127.0.0.1:8000"
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJqdWFuIiwiZXhwIjoxNzU5MjA4MDA4fQ.nxCd4imnk0UQJn0J59mn7QiCGf1e20Fg9wFxpzCI2As"
    
    cookies = {'access_token': token}
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    # 1. Verificar estructura HTML
    print("1. 📄 Verificando estructura HTML...")
    try:
        response = requests.get(f"{base_url}/usuarios_admin/", cookies=cookies, headers=headers)
        if response.status_code == 200:
            html = response.text
            print("   ✅ Página carga correctamente")
            
            # Verificar que no hay duplicados
            total_users_count = html.count('id="total-users"')
            active_users_count = html.count('id="active-users"')
            admin_users_count = html.count('id="admin-users"')
            total_roles_count = html.count('id="total-roles"')
            
            print(f"   📊 IDs únicos verificados:")
            print(f"      • total-users: {total_users_count} {'✅' if total_users_count == 1 else '❌ DUPLICADO'}")
            print(f"      • active-users: {active_users_count} {'✅' if active_users_count == 1 else '❌ DUPLICADO'}")
            print(f"      • admin-users: {admin_users_count} {'✅' if admin_users_count == 1 else '❌ DUPLICADO'}")
            print(f"      • total-roles: {total_roles_count} {'✅' if total_roles_count == 1 else '❌ DUPLICADO'}")
            
            # Verificar grid horizontal
            if "grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4" in html:
                print("   ✅ Grid horizontal implementado (4 columnas)")
            else:
                print("   ❌ Grid horizontal NO encontrado")
                
            # Verificar panel-surface (tema)
            panel_count = html.count('panel-surface')
            print(f"   🎨 Paneles con tema: {panel_count} {'✅' if panel_count >= 4 else '❌'}")
            
        else:
            print(f"   ❌ Error cargando página: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    # 2. Verificar APIs
    print("\n2. 🔌 Verificando APIs...")
    try:
        # API de usuarios
        users_response = requests.get(f"{base_url}/usuarios_admin/usuarios-con-detalles/", 
                                    cookies=cookies, headers=headers)
        if users_response.status_code == 200:
            usuarios = users_response.json()
            print(f"   ✅ API usuarios: {len(usuarios)} usuarios")
        else:
            print(f"   ❌ API usuarios error: {users_response.status_code}")
        
        # API de estadísticas
        stats_response = requests.get(f"{base_url}/usuarios_admin/estadisticas-avanzadas/", 
                                    cookies=cookies, headers=headers)
        if stats_response.status_code == 200:
            stats = stats_response.json()
            resumen = stats.get('resumen', {})
            print("   ✅ API estadísticas funciona:")
            print(f"      • Total: {resumen.get('total_usuarios', 'N/A')}")
            print(f"      • Activos: {resumen.get('usuarios_activos', 'N/A')}")
            print(f"      • Admins: {resumen.get('total_administradores', 'N/A')}")
            print(f"      • Roles: {resumen.get('total_roles', 'N/A')}")
        else:
            print(f"   ❌ API estadísticas error: {stats_response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error APIs: {e}")
    
    print("\n" + "="*50)
    print("✨ RESULTADO ESPERADO:")
    print("• Las 4 tarjetas de estadísticas deben mostrarse en UNA FILA horizontal")
    print("• No deben aparecer guiones '-' sino números reales")
    print("• Cada tarjeta debe tener su icono y gradiente")
    print("• El diseño debe ser responsivo (mobile: 1 col, tablet: 2 cols, desktop: 4 cols)")
    
    print("\n🎮 PARA VERIFICAR MANUALMENTE:")
    print("1. Ve a: http://127.0.0.1:8000/usuarios_admin/")
    print("2. Las estadísticas deben estar en la parte superior en formato horizontal")
    print("3. No debe haber tarjetas duplicadas o mal posicionadas")
    print("4. Los números deben cargarse automáticamente (no '-')")

if __name__ == "__main__":
    verificar_estadisticas_horizontales()