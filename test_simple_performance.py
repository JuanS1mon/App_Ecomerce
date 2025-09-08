#!/usr/bin/env python3
"""
PRUEBA SIMPLE DE RENDIMIENTO ASYNC
Comparación directa entre servicios optimizados y originales
"""

import asyncio
import aiohttp
import time
import statistics
import json

async def test_endpoint_performance(url: str, name: str, iterations: int = 5):
    """Prueba un endpoint y mide su rendimiento"""
    print(f"\n🧪 Probando: {name}")
    print(f"   URL: {url}")
    
    response_times = []
    errors = 0
    
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
        for i in range(iterations):
            start_time = time.time()
            try:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        response_time = (time.time() - start_time) * 1000
                        response_times.append(response_time)
                        print(f"   Iteración {i+1}: {response_time:.1f}ms ✅")
                    else:
                        errors += 1
                        print(f"   Iteración {i+1}: Error {response.status} ❌")
            except Exception as e:
                errors += 1
                print(f"   Iteración {i+1}: Excepción {str(e)[:50]} ❌")
    
    if response_times:
        avg_time = statistics.mean(response_times)
        min_time = min(response_times)
        max_time = max(response_times)
        
        print(f"   📊 Resultados:")
        print(f"      • Promedio: {avg_time:.1f}ms")
        print(f"      • Mínimo: {min_time:.1f}ms")
        print(f"      • Máximo: {max_time:.1f}ms")
        print(f"      • Éxito: {len(response_times)}/{iterations}")
        
        return {
            "name": name,
            "url": url,
            "avg_ms": round(avg_time, 1),
            "min_ms": round(min_time, 1),
            "max_ms": round(max_time, 1),
            "success_rate": len(response_times) / iterations,
            "errors": errors
        }
    else:
        print(f"   ❌ Todas las pruebas fallaron")
        return {
            "name": name,
            "url": url,
            "errors": errors,
            "success_rate": 0
        }

async def test_concurrent_load(url: str, name: str, concurrent_requests: int = 10):
    """Prueba carga concurrente"""
    print(f"\n🔄 Prueba de Concurrencia: {name}")
    print(f"   Requests simultáneos: {concurrent_requests}")
    
    start_time = time.time()
    
    async def single_request(session, request_id):
        try:
            async with session.get(f"{url}?req_id={request_id}") as response:
                return {
                    "status": response.status,
                    "success": response.status == 200,
                    "request_id": request_id
                }
        except Exception as e:
            return {
                "status": "error",
                "success": False,
                "error": str(e),
                "request_id": request_id
            }
    
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=15)) as session:
        tasks = [single_request(session, i) for i in range(concurrent_requests)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
    
    total_time = (time.time() - start_time) * 1000
    successful = len([r for r in results if isinstance(r, dict) and r.get("success")])
    
    print(f"   📊 Resultados concurrencia:")
    print(f"      • Tiempo total: {total_time:.1f}ms")
    print(f"      • Exitosos: {successful}/{concurrent_requests}")
    print(f"      • Requests/segundo: {concurrent_requests / (total_time / 1000):.1f}")
    
    return {
        "name": f"{name}_concurrent",
        "total_time_ms": round(total_time, 1),
        "successful": successful,
        "total": concurrent_requests,
        "rps": round(concurrent_requests / (total_time / 1000), 1)
    }

async def main():
    """Función principal de pruebas"""
    print("🚀 PRUEBA SIMPLE DE RENDIMIENTO ASYNC")
    print("=" * 50)
    
    # Endpoints a probar
    test_endpoints = [
        ("http://localhost:8000/health", "Sistema Original (puerto 8000)"),
        ("http://localhost:8001/core/health", "Core Service Optimizado (puerto 8001)"),
        ("http://localhost:8001/core/health/detailed", "Core Service Detallado (puerto 8001)"),
    ]
    
    results = []
    
    # Pruebas individuales
    print("\n📊 FASE 1: PRUEBAS INDIVIDUALES")
    print("-" * 40)
    
    for url, name in test_endpoints:
        result = await test_endpoint_performance(url, name)
        results.append(result)
    
    # Pruebas de concurrencia (solo endpoints que funcionaron)
    print("\n🔄 FASE 2: PRUEBAS DE CONCURRENCIA")
    print("-" * 40)
    
    working_endpoints = [(url, name) for url, name in test_endpoints 
                        if any(r["name"] == name and r.get("success_rate", 0) > 0 for r in results)]
    
    concurrent_results = []
    for url, name in working_endpoints:
        concurrent_result = await test_concurrent_load(url, name, 5)
        concurrent_results.append(concurrent_result)
    
    # Reporte final
    print("\n" + "=" * 50)
    print("📋 REPORTE FINAL DE RENDIMIENTO")
    print("=" * 50)
    
    print("\n🚀 RENDIMIENTO INDIVIDUAL:")
    print(f"{'Servicio':<30} {'Promedio':<10} {'Éxito':<8}")
    print("-" * 50)
    for result in results:
        if result.get("success_rate", 0) > 0:
            name = result["name"][:28]
            avg = f"{result['avg_ms']}ms"
            success = f"{result['success_rate']*100:.0f}%"
            print(f"{name:<30} {avg:<10} {success:<8}")
        else:
            name = result["name"][:28]
            print(f"{name:<30} {'ERROR':<10} {'0%':<8}")
    
    if concurrent_results:
        print("\n🔄 RENDIMIENTO CONCURRENTE:")
        print(f"{'Servicio':<30} {'Req/s':<8} {'Éxito':<8}")
        print("-" * 50)
        for result in concurrent_results:
            name = result["name"].replace("_concurrent", "")[:28]
            rps = result["rps"]
            success = f"{result['successful']}/{result['total']}"
            print(f"{name:<30} {rps:<8} {success:<8}")
    
    # Conclusiones
    print("\n💡 CONCLUSIONES:")
    
    # Encontrar el servicio más rápido
    working_results = [r for r in results if r.get("success_rate", 0) > 0]
    if working_results:
        fastest = min(working_results, key=lambda x: x["avg_ms"])
        print(f"   ✅ Servicio más rápido: {fastest['name']} ({fastest['avg_ms']}ms)")
        
        # Comparar con original si existe
        original = next((r for r in working_results if "Original" in r["name"]), None)
        optimized = next((r for r in working_results if "Optimizado" in r["name"]), None)
        
        if original and optimized:
            improvement = ((original["avg_ms"] - optimized["avg_ms"]) / original["avg_ms"]) * 100
            if improvement > 0:
                print(f"   🚀 Mejora de rendimiento: {improvement:.1f}% más rápido")
            else:
                print(f"   📊 Diferencia de rendimiento: {abs(improvement):.1f}%")
    
    # Guardar resultados
    all_results = {
        "individual": results,
        "concurrent": concurrent_results,
        "timestamp": time.time()
    }
    
    with open("performance_test_results.json", "w") as f:
        json.dump(all_results, f, indent=2)
    
    print(f"\n📁 Resultados guardados en: performance_test_results.json")
    print("\n🏁 Pruebas completadas!")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n❌ Pruebas interrumpidas")
    except Exception as e:
        print(f"\n💥 Error: {e}")
    
    input("\nPresiona Enter para continuar...")
