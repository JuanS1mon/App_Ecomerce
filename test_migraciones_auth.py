#!/usr/bin/env python3
"""
Script para probar que las rutas de migraciones funcionan correctamente
con el nuevo sistema de autenticación que no requiere token en query.
"""

import requests
import json
from datetime import datetime

def test_migraciones_auth():
    """Prueba las rutas de migraciones sin token en query"""
    
    base_url = "http://localhost:8000"  # Cambia por tu URL
    
    # URLs a probar
    test_urls = [
        "/migraciones/",
        "/migraciones/admin_migraciones",
        "/migraciones/nueva_migracion",
        "/migraciones/control_migraciones",
        "/migraciones/tablas_migraciones",
        "/migraciones/check_progress",
        "/migraciones/api/stats"
    ]
    
    print("=" * 60)
    print("PRUEBA DE AUTENTICACIÓN EN RUTAS DE MIGRACIONES")
    print("=" * 60)
    print(f"Timestamp: {datetime.now()}")
    print()
    
    # Token de ejemplo (deberías usar un token válido)
    token = "tu_token_jwt_aqui"  # Reemplaza con un token válido
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # También incluir cookies si es el método de autenticación
    cookies = {
        "access_token": token
    }
    
    session = requests.Session()
    session.headers.update(headers)
    session.cookies.update(cookies)
    
    results = []
    
    for url in test_urls:
        full_url = f"{base_url}{url}"
        print(f"🔍 Probando: {url}")
        
        try:
            # Intentar con GET request
            response = session.get(full_url, timeout=10)
            
            status_code = response.status_code
            content_type = response.headers.get('content-type', '')
            
            if status_code == 200:
                print(f"  ✅ Éxito: {status_code}")
                if 'application/json' in content_type:
                    try:
                        data = response.json()
                        print(f"  📄 Respuesta JSON válida (keys: {list(data.keys()) if isinstance(data, dict) else 'lista'})")
                    except:
                        print(f"  📄 Respuesta JSON inválida")
                elif 'text/html' in content_type:
                    print(f"  📄 Respuesta HTML válida")
                else:
                    print(f"  📄 Tipo de contenido: {content_type}")
                    
            elif status_code == 401:
                print(f"  🚫 No autorizado: {status_code}")
                print(f"    - Verificar token de autenticación")
                
            elif status_code == 422:
                try:
                    error_data = response.json()
                    print(f"  ❌ Error de validación: {status_code}")
                    print(f"    - Detalles: {error_data}")
                    
                    # Verificar si es el error de token que estamos buscando
                    if 'detail' in error_data and 'errors' in error_data:
                        for error in error_data['errors']:
                            if error.get('loc') == ['query', 'token']:
                                print(f"    ⚠️  ERROR DETECTADO: Ruta todavía requiere token en query!")
                    
                except:
                    print(f"  ❌ Error de validación: {status_code} (sin detalles JSON)")
                    
            elif status_code == 404:
                print(f"  🔍 No encontrado: {status_code}")
                
            elif status_code == 500:
                print(f"  💥 Error del servidor: {status_code}")
                
            else:
                print(f"  ⚠️  Respuesta inesperada: {status_code}")
            
            results.append({
                'url': url,
                'status_code': status_code,
                'content_type': content_type,
                'success': status_code == 200,
                'auth_error': status_code == 401,
                'validation_error': status_code == 422
            })
            
        except requests.exceptions.RequestException as e:
            print(f"  💥 Error de conexión: {str(e)}")
            results.append({
                'url': url,
                'error': str(e),
                'success': False
            })
        
        print()
    
    # Resumen
    print("=" * 60)
    print("RESUMEN DE RESULTADOS")
    print("=" * 60)
    
    total_tests = len(results)
    successful = sum(1 for r in results if r.get('success', False))
    auth_errors = sum(1 for r in results if r.get('auth_error', False))
    validation_errors = sum(1 for r in results if r.get('validation_error', False))
    
    print(f"Total de pruebas: {total_tests}")
    print(f"Exitosas: {successful}")
    print(f"Errores de autorización (401): {auth_errors}")
    print(f"Errores de validación (422): {validation_errors}")
    
    if validation_errors > 0:
        print("\n⚠️  ATENCIÓN: Se detectaron errores 422 que pueden indicar")
        print("   que algunas rutas todavía requieren token en query.")
        print("   Revisar las rutas que devuelven 422.")
    
    if auth_errors > 0:
        print("\n🔑 NOTA: Errores 401 indican que necesitas un token válido")
        print("   para probar completamente. Esto es normal si no tienes")
        print("   un token de autenticación válido.")
    
    if successful == total_tests:
        print("\n🎉 ¡Todas las rutas funcionan correctamente!")
    elif validation_errors == 0:
        print("\n✅ Las rutas no tienen errores de validación de token.")
        print("   Los errores pueden ser debido a falta de autenticación válida.")
    
    return results

if __name__ == "__main__":
    try:
        results = test_migraciones_auth()
        
        # Guardar resultados en archivo
        with open("migraciones_auth_test_results.json", "w", encoding="utf-8") as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "results": results
            }, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Resultados guardados en: migraciones_auth_test_results.json")
        
    except Exception as e:
        print(f"💥 Error ejecutando pruebas: {str(e)}")
