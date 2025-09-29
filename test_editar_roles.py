#!/usr/bin/env python3
"""Script para crear usuario de prueba y probar edición de roles"""

import requests
import json

def test_crear_usuario_y_editar_roles():
    """Crear usuario test y probar cambio de roles"""
    base_url = "http://localhost:8000"
    
    print("🔐 === LOGIN COMO ADMIN ===")
    
    # Login para obtener token
    login_data = {
        "username": "juan",
        "password": "123456"
    }
    
    try:
        login_response = requests.post(f"{base_url}/token", data=login_data)
        print(f"Login Status: {login_response.status_code}")
        
        if login_response.status_code == 200:
            token_data = login_response.json()
            token = token_data.get("access_token")
            print(f"✅ Token obtenido")
            
            # 1. Crear usuario test
            print("\n👤 === CREANDO USUARIO TEST ===")
            nuevo_usuario = {
                "usuario": "test",
                "nombre": "Usuario Test",
                "email": "test@example.com",
                "password": "test123",
                "activo": True
            }
            
            crear_response = requests.post(
                f"{base_url}/usuarios_admin/usuarios/",
                json=nuevo_usuario,
                params={"token": token}
            )
            
            print(f"Crear Usuario Status: {crear_response.status_code}")
            if crear_response.status_code == 200:
                usuario_creado = crear_response.json()
                print(f"✅ Usuario creado: {usuario_creado}")
                user_id = usuario_creado.get("id")
                
                # 2. Asignar rol "manager" al usuario test
                print(f"\n🏷️ === ASIGNANDO ROL MANAGER AL USUARIO {user_id} ===")
                roles_data = {
                    "roles": ["manager"]
                }
                
                asignar_response = requests.put(
                    f"{base_url}/usuarios_admin/usuarios/{user_id}/roles",
                    json=roles_data,
                    params={"token": token}
                )
                
                print(f"Asignar Roles Status: {asignar_response.status_code}")
                if asignar_response.status_code == 200:
                    resultado = asignar_response.json()
                    print(f"✅ Roles asignados: {resultado}")
                    
                    # 3. Verificar los roles del usuario
                    print(f"\n👀 === VERIFICANDO ROLES DEL USUARIO ===")
                    usuarios_response = requests.get(
                        f"{base_url}/usuarios_admin/usuarios-con-detalles/",
                        params={"token": token, "search": "test"}
                    )
                    
                    if usuarios_response.status_code == 200:
                        usuarios = usuarios_response.json()
                        usuario_test = next((u for u in usuarios if u['usuario'] == 'test'), None)
                        if usuario_test:
                            print(f"✅ Usuario test encontrado con roles: {usuario_test['roles']}")
                            
                            # 4. Cambiar el rol a "tecnico"
                            print(f"\n🔄 === CAMBIANDO ROL A TECNICO ===")
                            nuevos_roles_data = {
                                "roles": ["tecnico"]
                            }
                            
                            cambiar_response = requests.put(
                                f"{base_url}/usuarios_admin/usuarios/{user_id}/roles",
                                json=nuevos_roles_data,
                                params={"token": token}
                            )
                            
                            print(f"Cambiar Roles Status: {cambiar_response.status_code}")
                            if cambiar_response.status_code == 200:
                                resultado_cambio = cambiar_response.json()
                                print(f"✅ Roles cambiados: {resultado_cambio}")
                                
                                # Verificar el cambio
                                print(f"\n🔍 === VERIFICANDO CAMBIO DE ROLES ===")
                                verificar_response = requests.get(
                                    f"{base_url}/usuarios_admin/usuarios-con-detalles/",
                                    params={"token": token, "search": "test"}
                                )
                                
                                if verificar_response.status_code == 200:
                                    usuarios_actualizados = verificar_response.json()
                                    usuario_actualizado = next((u for u in usuarios_actualizados if u['usuario'] == 'test'), None)
                                    if usuario_actualizado:
                                        print(f"✅ Usuario test actualizado con roles: {usuario_actualizado['roles']}")
                                        
                                        if "tecnico" in usuario_actualizado['roles']:
                                            print("🎉 ¡ÉXITO! El cambio de roles funciona correctamente")
                                        else:
                                            print("❌ ERROR: El rol no se actualizó correctamente")
                            else:
                                print(f"❌ Error cambiando roles: {cambiar_response.text}")
                        else:
                            print("❌ Usuario test no encontrado")
                    else:
                        print(f"❌ Error verificando usuarios: {usuarios_response.text}")
                else:
                    print(f"❌ Error asignando roles: {asignar_response.text}")
            else:
                print(f"❌ Error creando usuario: {crear_response.text}")
        else:
            print(f"❌ Error en login: {login_response.text}")
            
    except Exception as e:
        print(f"❌ Error en prueba: {e}")

if __name__ == "__main__":
    test_crear_usuario_y_editar_roles()