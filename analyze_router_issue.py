"""
Análisis detallado del router para entender por qué cerrar-sesion devuelve 405
"""
import requests
import json

def analyze_router_issue():
    base_url = "http://localhost:8000"
    
    print("=== ANÁLISIS DETALLADO DEL PROBLEMA 405 ===")
    
    try:
        # 1. Obtener la documentación OpenAPI completa
        docs_response = requests.get(f"{base_url}/openapi.json")
        if docs_response.status_code == 200:
            openapi_data = docs_response.json()
            paths = openapi_data.get("paths", {})
            
            # Buscar todas las rutas que contienen "logout", "cerrar", "sesion"
            related_routes = {}
            for path, methods in paths.items():
                path_lower = path.lower()
                if any(keyword in path_lower for keyword in ["logout", "cerrar", "sesion", "test", "simple"]):
                    related_routes[path] = methods
            
            print("1. Rutas relacionadas encontradas en OpenAPI:")
            for path, methods in related_routes.items():
                print(f"  {path}:")
                for method, details in methods.items():
                    print(f"    {method.upper()}: {details.get('summary', 'Sin descripción')}")
            
            # 2. Verificar específicamente cerrar-sesion
            if "/cerrar-sesion" in paths:
                cerrar_sesion_info = paths["/cerrar-sesion"]
                print(f"\n2. Información de /cerrar-sesion en OpenAPI:")
                print(f"   Métodos disponibles: {list(cerrar_sesion_info.keys())}")
                
                for method, details in cerrar_sesion_info.items():
                    print(f"   {method.upper()}:")
                    print(f"     - Summary: {details.get('summary', 'N/A')}")
                    print(f"     - Description: {details.get('description', 'N/A')}")
                    print(f"     - Parameters: {len(details.get('parameters', []))}")
            else:
                print("\n2. /cerrar-sesion NO está en la documentación OpenAPI")
        
        # 3. Probar todos los métodos HTTP en cerrar-sesion
        print("\n3. Prueba de todos los métodos HTTP en /cerrar-sesion:")
        methods_to_test = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS', 'HEAD']
        
        for method in methods_to_test:
            try:
                response = requests.request(method, f"{base_url}/cerrar-sesion")
                print(f"   {method}: {response.status_code}")
                if response.status_code == 405:
                    print(f"     Allow: {response.headers.get('Allow', 'No Allow header')}")
                elif response.status_code == 200:
                    print(f"     Respuesta: {response.text[:50]}...")
            except Exception as e:
                print(f"   {method}: Error - {e}")
        
        # 4. Comparar con logout-test que funciona
        print("\n4. Comparación con /logout-test (que funciona):")
        for method in ['GET', 'POST']:
            try:
                response = requests.request(method, f"{base_url}/logout-test")
                print(f"   {method}: {response.status_code}")
                if response.status_code == 200:
                    print(f"     Respuesta: {response.text[:50]}...")
            except Exception as e:
                print(f"   {method}: Error - {e}")
        
        # 5. Verificar headers específicos
        print("\n5. Headers detallados para POST /cerrar-sesion:")
        try:
            response = requests.post(f"{base_url}/cerrar-sesion")
            print(f"   Status: {response.status_code}")
            print("   Headers:")
            for header, value in response.headers.items():
                print(f"     {header}: {value}")
        except Exception as e:
            print(f"   Error: {e}")
            
    except Exception as e:
        print(f"Error general: {e}")

if __name__ == "__main__":
    analyze_router_issue()
