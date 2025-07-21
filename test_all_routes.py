#!/usr/bin/env python3
"""Script para probar todas las rutas del sistema de obras"""

import requests

def test_all_routes():
    """Probar todas las rutas importantes del sistema"""
    print("=== PRUEBA COMPLETA DE RUTAS DEL SISTEMA ===\n")
    
    base_url = "http://127.0.0.1:8000"
    
    routes_to_test = [
        # Rutas principales
        ("/app_obras", "Dashboard principal (redirigido)"),
        ("/app_obras/dashboard", "Dashboard directo"),
        
        # Rutas de artistas
        ("/app_obras/artists/html/", "Listado de artistas"),
        ("/app_obras/artists/html/create/", "Crear artista"),
        
        # Rutas de obras
        ("/app_obras/artworks/html/", "Listado de obras"),
        ("/app_obras/artworks/html/create/", "Crear obra"),
        
        # API endpoints
        ("/app_obras/artists/", "API artistas"),
        ("/app_obras/artworks/", "API obras"),
    ]
    
    results = []
    
    for route, description in routes_to_test:
        print(f"🔗 Probando {route}...")
        print(f"   📝 {description}")
        
        try:
            response = requests.get(f"{base_url}{route}", allow_redirects=True)
            status = response.status_code
            
            if status == 200:
                print(f"   ✅ Status: {status} - OK")
                results.append((route, status, "✅ OK"))
            elif status == 302:
                location = response.headers.get('location', 'N/A')
                print(f"   🔄 Status: {status} - Redirección a {location}")
                results.append((route, status, f"🔄 Redirección"))
            else:
                print(f"   ❌ Status: {status} - Error")
                results.append((route, status, "❌ Error"))
                
        except Exception as e:
            print(f"   ❌ Error de conexión: {e}")
            results.append((route, "Error", "❌ Conexión"))
        
        print()
    
    # Resumen
    print("="*60)
    print("RESUMEN DE PRUEBAS:")
    print("="*60)
    
    for route, status, result in results:
        print(f"{result} {route} → {status}")
    
    # Estadísticas
    ok_count = sum(1 for _, _, result in results if "✅" in result)
    total_count = len(results)
    
    print(f"\n📊 ESTADÍSTICAS:")
    print(f"   ✅ Exitosas: {ok_count}/{total_count}")
    print(f"   📈 Porcentaje de éxito: {(ok_count/total_count)*100:.1f}%")
    
    if ok_count == total_count:
        print(f"\n🎉 ¡TODAS LAS RUTAS FUNCIONAN CORRECTAMENTE!")
    else:
        print(f"\n⚠️  Algunas rutas requieren atención")

if __name__ == "__main__":
    test_all_routes()
