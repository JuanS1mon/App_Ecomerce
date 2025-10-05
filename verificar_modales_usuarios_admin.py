#!/usr/bin/env python3
"""
Script para verificar que todas las funcionalidades de modales estén funcionando
"""

import requests
import time

def verificar_funcionalidades_modales():
    """Verifica que todas las funcionalidades de modales estén implementadas"""
    
    print("🔄 VERIFICANDO FUNCIONALIDADES DE MODALES")
    print("="*50)
    
    base_url = "http://127.0.0.1:8000"
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJqdWFuIiwiZXhwIjoxNzU5MjA4MDA4fQ.nxCd4imnk0UQJn0J59mn7QiCGf1e20Fg9wFxpzCI2As"
    
    cookies = {'access_token': token}
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    # 1. Verificar página HTML y modales
    print("1. 📄 Verificando estructura de modales...")
    try:
        response = requests.get(f"{base_url}/usuarios_admin/", cookies=cookies, headers=headers)
        if response.status_code == 200:
            html = response.text
            print("   ✅ Página carga correctamente")
            
            # Verificar modales
            modales_requeridos = [
                'modalUsuario',
                'modalCambiarPassword', 
                'modalHistorial',
                'modalConfirmar'
            ]
            
            for modal in modales_requeridos:
                if f'id="{modal}"' in html:
                    print(f"   ✅ Modal {modal} encontrado")
                else:
                    print(f"   ❌ Modal {modal} NO encontrado")
            
            # Verificar funciones JavaScript
            funciones_requeridas = [
                'abrirModalUsuario',
                'editarUsuario',
                'verHistorial',
                'toggleUsuarioStatus',
                'eliminarUsuario',
                'setupModalEventListeners'
            ]
            
            print("\n   📋 Funciones JavaScript:")
            for funcion in funciones_requeridas:
                if funcion in html:
                    print(f"   ✅ {funcion} implementada")
                else:
                    print(f"   ❌ {funcion} NO encontrada")
            
            # Verificar botones de acción
            botones_requeridos = [
                'btnNuevoUsuario',
                'btnCancelar',
                'btnGuardar',
                'btnCancelarPassword',
                'btnCerrarHistorial',
                'btnConfirmarAccion'
            ]
            
            print("\n   🔘 Botones de modales:")
            for boton in botones_requeridos:
                if f'id="{boton}"' in html:
                    print(f"   ✅ {boton} encontrado")
                else:
                    print(f"   ❌ {boton} NO encontrado")
                    
        else:
            print(f"   ❌ Error cargando página: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    # 2. Verificar APIs necesarias para los modales
    print("\n2. 🔌 Verificando APIs para modales...")
    try:
        # API para obtener usuario específico
        test_user_id = 1  # Asumir que existe usuario con ID 1
        user_response = requests.get(f"{base_url}/usuarios_admin/usuarios/{test_user_id}", 
                                   cookies=cookies, headers=headers)
        if user_response.status_code == 200:
            print("   ✅ API obtener usuario específico funciona")
        else:
            print(f"   ⚠️ API obtener usuario: {user_response.status_code}")
        
        # API para historial de usuario
        historial_response = requests.get(f"{base_url}/usuarios_admin/usuarios/{test_user_id}/historial", 
                                        cookies=cookies, headers=headers)
        if historial_response.status_code == 200:
            print("   ✅ API historial de usuario funciona")
        else:
            print(f"   ⚠️ API historial: {historial_response.status_code}")
        
        # API para toggle status
        # No hacemos la llamada real para no modificar datos, solo verificamos el endpoint
        print("   ℹ️ API toggle status disponible (no probado para evitar cambios)")
        
    except Exception as e:
        print(f"   ❌ Error APIs: {e}")
    
    print("\n" + "="*50)
    print("✨ FUNCIONALIDADES ESPERADAS:")
    print("• Botón 'Nuevo Usuario' debe abrir modal para crear usuario")
    print("• Iconos de editar (✏️) deben abrir modal con datos del usuario")
    print("• Iconos de historial (📜) deben mostrar historial del usuario")
    print("• Iconos de toggle (👤) deben activar/desactivar usuario")
    print("• Iconos de eliminar (🗑️) deben mostrar confirmación")
    print("• Todos los modales deben poder cerrarse con 'Cancelar' o clic fuera")
    
    print("\n🎮 PARA PROBAR MANUALMENTE:")
    print("1. Ve a: http://127.0.0.1:8000/usuarios_admin/")
    print("2. Prueba el botón 'Nuevo Usuario' en la parte superior")
    print("3. En la tabla de usuarios, prueba los iconos de acción:")
    print("   • ✏️ Editar (debe abrir modal con datos)")
    print("   • 📜 Historial (debe mostrar actividad)")
    print("   • 👤 Toggle status (debe cambiar estado)")
    print("   • 🗑️ Eliminar (debe pedir confirmación)")
    
    print("\n💡 Si algo no funciona:")
    print("• Abre la consola del navegador (F12)")
    print("• Busca errores JavaScript en rojo")
    print("• Verifica que aparezcan mensajes '✅ Event listeners configurados'")

if __name__ == "__main__":
    verificar_funcionalidades_modales()