#!/usr/bin/env python3
"""
Script de verificación completa para usuarios_admin con datos y tema
"""

import requests
import re
import json

def verificacion_completa():
    """Verificación completa de funcionalidad y datos"""
    
    print("🎯 VERIFICACIÓN COMPLETA: USUARIOS ADMIN")
    print("="*55)
    
    base_url = "http://127.0.0.1:8000"
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJqdWFuIiwiZXhwIjoxNzU5MjA4MDA4fQ.nxCd4imnk0UQJn0J59mn7QiCGf1e20Fg9wFxpzCI2As"
    
    cookies = {'access_token': token}
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    resultados = {}
    
    # 1. Verificar página principal
    print("1. 🌐 Verificando página principal...")
    try:
        response = requests.get(f"{base_url}/usuarios_admin/", cookies=cookies, headers=headers)
        if response.status_code == 200:
            html = response.text
            resultados['pagina'] = True
            print("   ✅ Página carga correctamente")
            
            # Verificar elementos de tema
            tema_elementos = [
                'toggleThemeManual',
                'theme-toggle',
                '--color-',
                'data-theme'
            ]
            
            tema_ok = all(elemento in html for elemento in tema_elementos)
            resultados['tema'] = tema_ok
            print(f"   {'✅' if tema_ok else '❌'} Sistema de tema: {'Implementado' if tema_ok else 'Falta'}")
            
            # Verificar elementos de datos
            datos_elementos = [
                'users-table-body',
                'totalUsuarios',
                'cargarUsuariosInline',
                'renderizarTablaUsuarios'
            ]
            
            datos_ok = all(elemento in html for elemento in datos_elementos)
            resultados['estructura_datos'] = datos_ok
            print(f"   {'✅' if datos_ok else '❌'} Estructura de datos: {'OK' if datos_ok else 'Falta'}")
            
        else:
            resultados['pagina'] = False
            print(f"   ❌ Error: {response.status_code}")
            
    except Exception as e:
        resultados['pagina'] = False
        print(f"   ❌ Error: {e}")
    
    # 2. Verificar API de usuarios
    print("\n2. 👥 Verificando API de usuarios...")
    try:
        response = requests.get(f"{base_url}/usuarios_admin/usuarios-con-detalles/", cookies=cookies, headers=headers)
        if response.status_code == 200:
            usuarios = response.json()
            resultados['api_usuarios'] = True
            print(f"   ✅ API funciona - {len(usuarios)} usuarios encontrados")
            
            if usuarios:
                primer_usuario = usuarios[0]
                campos_requeridos = ['id', 'usuario', 'nombre', 'email', 'activo']
                campos_ok = all(campo in primer_usuario for campo in campos_requeridos)
                resultados['estructura_usuario'] = campos_ok
                print(f"   {'✅' if campos_ok else '❌'} Estructura usuario: {'OK' if campos_ok else 'Incompleta'}")
                
                # Mostrar ejemplo de usuario
                print(f"   📋 Ejemplo usuario: {primer_usuario.get('usuario', 'N/A')} - {primer_usuario.get('email', 'N/A')}")
            else:
                resultados['estructura_usuario'] = False
                print("   ⚠️ No hay usuarios en la respuesta")
                
        else:
            resultados['api_usuarios'] = False
            print(f"   ❌ Error API: {response.status_code}")
            
    except Exception as e:
        resultados['api_usuarios'] = False
        print(f"   ❌ Error: {e}")
    
    # 3. Verificar API de estadísticas
    print("\n3. 📊 Verificando API de estadísticas...")
    try:
        response = requests.get(f"{base_url}/usuarios_admin/estadisticas-avanzadas/", cookies=cookies, headers=headers)
        if response.status_code == 200:
            stats = response.json()
            resultados['api_estadisticas'] = True
            print("   ✅ API estadísticas funciona")
            
            if 'resumen' in stats:
                resumen = stats['resumen']
                print(f"   📈 Total usuarios: {resumen.get('total_usuarios', 'N/A')}")
                print(f"   📈 Usuarios activos: {resumen.get('usuarios_activos', 'N/A')}")
                print(f"   📈 Administradores: {resumen.get('total_administradores', 'N/A')}")
            else:
                print("   ⚠️ Estructura de estadísticas no esperada")
                
        else:
            resultados['api_estadisticas'] = False
            print(f"   ❌ Error API estadísticas: {response.status_code}")
            
    except Exception as e:
        resultados['api_estadisticas'] = False
        print(f"   ❌ Error: {e}")
    
    # 4. Verificar archivos estáticos
    print("\n4. 📁 Verificando archivos estáticos...")
    archivos = [
        "/static/html/usuarios/js/usuarios_admin_corregido.js",
        "/static/css/admin.css"
    ]
    
    archivos_ok = 0
    for archivo in archivos:
        try:
            response = requests.get(f"{base_url}{archivo}", headers=headers)
            if response.status_code == 200:
                archivos_ok += 1
                print(f"   ✅ {archivo}")
            else:
                print(f"   ❌ {archivo} - Error {response.status_code}")
        except:
            print(f"   ❌ {archivo} - Error de conexión")
    
    resultados['archivos_estaticos'] = archivos_ok == len(archivos)
    
    # Resumen final
    print("\n" + "="*55)
    print("📋 RESUMEN DE VERIFICACIÓN")
    print("="*55)
    
    checks = [
        ("Página principal", resultados.get('pagina', False)),
        ("Sistema de tema", resultados.get('tema', False)),
        ("Estructura de datos", resultados.get('estructura_datos', False)),
        ("API de usuarios", resultados.get('api_usuarios', False)),
        ("Estructura usuario", resultados.get('estructura_usuario', False)),
        ("API de estadísticas", resultados.get('api_estadisticas', False)),
        ("Archivos estáticos", resultados.get('archivos_estaticos', False))
    ]
    
    total_ok = sum(1 for _, ok in checks if ok)
    total_checks = len(checks)
    
    for nombre, ok in checks:
        estado = "✅" if ok else "❌"
        print(f"{estado} {nombre}")
    
    print(f"\n🎯 RESULTADO: {total_ok}/{total_checks} verificaciones exitosas")
    
    if total_ok == total_checks:
        print("🎉 ¡TODO FUNCIONA PERFECTAMENTE!")
        print("\n✨ Tu página usuarios_admin tiene:")
        print("  • 🌙 Sistema de tema claro/oscuro")
        print("  • 👥 Carga de usuarios desde API")
        print("  • 📊 Estadísticas en tiempo real")
        print("  • 🎨 Interfaz moderna y responsiva")
        print("  • 🔄 Navegación con avatar de usuario")
        
        print("\n🚀 INSTRUCCIONES DE USO:")
        print("1. Ve a: http://127.0.0.1:8000/usuarios_admin/")
        print("2. Verifica que veas la lista de usuarios")
        print("3. Usa el botón de tema (🌙/☀️) en la navbar")
        print("4. ¡Disfruta de tu panel de administración!")
        
    elif total_ok >= total_checks * 0.8:
        print("⚠️ La mayoría funciona, pero hay algunos problemas menores")
    else:
        print("❌ Hay problemas importantes que necesitan atención")
    
    return total_ok == total_checks

if __name__ == "__main__":
    verificacion_completa()