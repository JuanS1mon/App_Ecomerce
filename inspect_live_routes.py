"""
Inspeccionar las rutas actuales de la aplicación en tiempo de ejecución
"""
import requests
import json

def inspect_live_routes():
    base_url = "http://localhost:8000"
    
    print("=== INSPECCIÓN DE RUTAS EN VIVO ===")
    
    try:
        # 1. Verificar que el servidor responde
        print("1. Verificando servidor...")
        health_response = requests.get(f"{base_url}/")
        print(f"Root status: {health_response.status_code}")
        
        # 2. Probar la documentación de OpenAPI
        print("\n2. Verificando documentación...")
        docs_response = requests.get(f"{base_url}/openapi.json")
        print(f"OpenAPI status: {docs_response.status_code}")
        
        if docs_response.status_code == 200:
            openapi_data = docs_response.json()
            paths = openapi_data.get("paths", {})
            
            print(f"\nTotal rutas encontradas: {len(paths)}")
            
            # Buscar rutas relacionadas con logout/cerrar-sesion
            logout_routes = []
            for path, methods in paths.items():
                if "logout" in path.lower() or "cerrar" in path.lower() or "sesion" in path.lower():
                    logout_routes.append((path, list(methods.keys())))
            
            print("\n3. Rutas relacionadas con logout/cerrar-sesion:")
            if logout_routes:
                for route, methods in logout_routes:
                    print(f"  {route}: {methods}")
            else:
                print("  No se encontraron rutas relacionadas con logout")
            
            # Listar algunas rutas para contexto
            print("\n4. Primeras 10 rutas disponibles:")
            for i, (path, methods) in enumerate(list(paths.items())[:10]):
                print(f"  {path}: {list(methods.keys())}")
                
        # 3. Probar directamente algunos endpoints
        print("\n5. Pruebas directas de endpoints:")
        
        endpoints_to_test = [
            "/logout",
            "/cerrar-sesion", 
            "/logout-test",
            "/logout-simple"
        ]
        
        for endpoint in endpoints_to_test:
            print(f"\n  Probando POST {endpoint}:")
            try:
                response = requests.post(f"{base_url}{endpoint}")
                print(f"    Status: {response.status_code}")
                if response.status_code == 405:
                    print(f"    Allow: {response.headers.get('Allow', 'No Allow header')}")
                elif response.status_code == 404:
                    print(f"    Detalle: {response.json() if response.content else 'Sin contenido'}")
                else:
                    print(f"    Respuesta: {response.text[:100]}")
            except Exception as e:
                print(f"    Error: {e}")
        
    except requests.exceptions.ConnectionError:
        print("Error: No se pudo conectar al servidor en localhost:8000")
    except Exception as e:
        print(f"Error inesperado: {e}")

if __name__ == "__main__":
    inspect_live_routes()
