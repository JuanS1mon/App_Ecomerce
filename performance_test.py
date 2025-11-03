import time
import requests

def test_performance():
    base_url = "http://localhost:8000"

    print("🚀 Probando performance de carga de productos")
    print("=" * 50)

    # Test 1: Carga inicial de productos
    print("\n📊 Test 1: Carga inicial de productos")
    start_time = time.time()
    try:
        response = requests.get(f"{base_url}/ecomerce/productos/tienda")
        load_time = time.time() - start_time
        print(f"   Tiempo de carga: {load_time:.2f}s")
        print(f"   Status: {response.status_code}")
        print(f"   Tamaño respuesta: {len(response.text)} caracteres")

        # Contar productos en el HTML
        product_count = response.text.count('product-card')
        print(f"   Productos encontrados: {product_count}")

    except Exception as e:
        print(f"   ❌ Error: {e}")

    # Test 2: API de productos
    print("\n📊 Test 2: API de productos")
    start_time = time.time()
    try:
        response = requests.get(f"{base_url}/ecomerce/api/productos/publicos")
        api_time = time.time() - start_time
        print(f"   Tiempo API: {api_time:.2f}s")
        print(f"   Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            product_count = len(data) if isinstance(data, list) else 0
            print(f"   Productos en API: {product_count}")
            if product_count > 0:
                print(f"   Primer producto: {data[0].get('nombre', 'N/A')[:30]}...")

    except Exception as e:
        print(f"   ❌ Error: {e}")

    # Test 3: Búsqueda
    print("\n📊 Test 3: Búsqueda de productos")
    search_terms = ["teclado", "mouse", "audifonos", "laptop"]
    for term in search_terms:
        start_time = time.time()
        try:
            response = requests.get(f"{base_url}/ecomerce/api/productos/publicos?search={term}")
            search_time = time.time() - start_time
            if response.status_code == 200:
                data = response.json()
                count = len(data) if isinstance(data, list) else 0
                print(f"   '{term}': {count} resultados ({search_time:.2f}s)")
            else:
                print(f"   ❌ Búsqueda '{term}': Error {response.status_code}")
        except Exception as e:
            print(f"   ❌ Búsqueda '{term}': {e}")

    # Test 4: Filtrado por categoría
    print("\n📊 Test 4: Filtrado por categoría")
    for cat_id in range(1, 6):  # Categorías 1-5
        start_time = time.time()
        try:
            response = requests.get(f"{base_url}/ecomerce/api/productos/publicos?categoria={cat_id}")
            filter_time = time.time() - start_time
            if response.status_code == 200:
                data = response.json()
                count = len(data) if isinstance(data, list) else 0
                print(f"   Categoría {cat_id}: {count} productos ({filter_time:.2f}s)")
            else:
                print(f"   ❌ Categoría {cat_id}: Error {response.status_code}")
        except Exception as e:
            print(f"   ❌ Categoría {cat_id}: {e}")

    print("\n" + "=" * 50)
    print("✅ Tests de performance completados")
    print("\n💡 Recomendaciones para mejorar performance:")
    print("   • Implementar paginación si hay muchos productos")
    print("   • Agregar índices en búsquedas frecuentes")
    print("   • Considerar cache para productos populares")
    print("   • Optimizar imágenes de productos")

if __name__ == "__main__":
    test_performance()