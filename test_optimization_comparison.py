#!/usr/bin/env python3
"""
COMPARACIÓN DE LOS 3 ENFOQUES DE OPTIMIZACIÓN
1. Sistema Original (puerto 8000)
2. "Optimizado" con over-engineering (puerto 8001) 
3. Realmente optimizado (puerto 8005)
"""

import asyncio
import aiohttp
import time
import statistics
import json

async def compare_approaches():
    """Compara los 3 enfoques diferentes"""
    
    print("🔬 COMPARACIÓN DE ENFOQUES DE OPTIMIZACIÓN")
    print("=" * 55)
    
    # Definir los servicios a comparar
    services = [
        {
            "name": "Sistema Original",
            "url": "http://localhost:8000/health",
            "description": "Sistema monolítico original"
        },
        {
            "name": "Over-Engineered", 
            "url": "http://localhost:8001/core/health",
            "description": "Async/await con over-engineering"
        },
        {
            "name": "Realmente Optimizado",
            "url": "http://localhost:8005/core/health", 
            "description": "Async solo donde es útil"
        }
    ]
    
    results = []
    
    print("\n📊 PRUEBA 1: ENDPOINTS SIMPLES")
    print("-" * 45)
    
    # Probar endpoints simples
    for service in services:
        print(f"\n🧪 Probando: {service['name']}")
        print(f"   {service['description']}")
        
        response_times = []
        errors = 0
        
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
            for i in range(10):  # Más iteraciones para mejor precisión
                start_time = time.time()
                try:
                    async with session.get(service['url']) as response:
                        if response.status == 200:
                            await response.json()
                            response_time = (time.time() - start_time) * 1000
                            response_times.append(response_time)
                        else:
                            errors += 1
                except Exception:
                    errors += 1
        
        if response_times:
            avg_time = statistics.mean(response_times)
            min_time = min(response_times)
            max_time = max(response_times)
            
            result = {
                "service": service['name'],
                "avg_ms": round(avg_time, 2),
                "min_ms": round(min_time, 2),
                "max_ms": round(max_time, 2),
                "success_rate": len(response_times) / 10,
                "errors": errors
            }
            
            results.append(result)
            
            print(f"   ✅ Promedio: {avg_time:.1f}ms")
            print(f"   📊 Rango: {min_time:.1f}ms - {max_time:.1f}ms")
            print(f"   🎯 Éxito: {len(response_times)}/10")
        else:
            print(f"   ❌ Todas las pruebas fallaron")
    
    # Prueba de concurrencia
    print("\n🔄 PRUEBA 2: CONCURRENCIA (20 requests simultáneos)")
    print("-" * 45)
    
    concurrent_results = []
    
    for service in services:
        if any(r['service'] == service['name'] and r['success_rate'] > 0 for r in results):
            print(f"\n🧪 Concurrencia: {service['name']}")
            
            start_time = time.time()
            
            async def single_request(session, req_id):
                try:
                    async with session.get(f"{service['url']}?req={req_id}") as response:
                        return response.status == 200
                except:
                    return False
            
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=15)) as session:
                tasks = [single_request(session, i) for i in range(20)]
                responses = await asyncio.gather(*tasks, return_exceptions=True)
            
            total_time = (time.time() - start_time) * 1000
            successful = len([r for r in responses if r is True])
            
            concurrent_result = {
                "service": service['name'],
                "total_time_ms": round(total_time, 1),
                "successful": successful,
                "total": 20,
                "rps": round(20 / (total_time / 1000), 1)
            }
            
            concurrent_results.append(concurrent_result)
            
            print(f"   ⚡ Tiempo total: {total_time:.1f}ms")
            print(f"   🎯 Exitosos: {successful}/20")
            print(f"   📈 Req/segundo: {concurrent_result['rps']}")
    
    # Generar reporte comparativo
    print("\n" + "=" * 55)
    print("📋 REPORTE COMPARATIVO FINAL")
    print("=" * 55)
    
    if results:
        print("\n🚀 RENDIMIENTO INDIVIDUAL:")
        print(f"{'Servicio':<20} {'Promedio':<12} {'Mínimo':<10} {'Máximo':<10}")
        print("-" * 55)
        
        for result in sorted(results, key=lambda x: x['avg_ms']):
            name = result['service'][:18]
            avg = f"{result['avg_ms']}ms"
            min_t = f"{result['min_ms']}ms" 
            max_t = f"{result['max_ms']}ms"
            print(f"{name:<20} {avg:<12} {min_t:<10} {max_t:<10}")
    
    if concurrent_results:
        print("\n🔄 RENDIMIENTO CONCURRENTE:")
        print(f"{'Servicio':<20} {'Req/s':<10} {'Éxito':<10}")
        print("-" * 40)
        
        for result in sorted(concurrent_results, key=lambda x: x['rps'], reverse=True):
            name = result['service'][:18]
            rps = result['rps']
            success = f"{result['successful']}/{result['total']}"
            print(f"{name:<20} {rps:<10} {success:<10}")
    
    # Análisis y recomendaciones
    print("\n💡 ANÁLISIS DE RESULTADOS:")
    
    if results:
        fastest = min(results, key=lambda x: x['avg_ms'])
        slowest = max(results, key=lambda x: x['avg_ms'])
        
        print(f"   🏆 Más rápido: {fastest['service']} ({fastest['avg_ms']}ms)")
        print(f"   🐌 Más lento: {slowest['service']} ({slowest['avg_ms']}ms)")
        
        if fastest['avg_ms'] < slowest['avg_ms']:
            improvement = ((slowest['avg_ms'] - fastest['avg_ms']) / slowest['avg_ms']) * 100
            print(f"   📈 Diferencia: {improvement:.1f}% más rápido")
    
    print("\n🎯 LECCIONES APRENDIDAS:")
    print("   1. Async/await NO siempre es mejor")
    print("   2. Simplicidad > Over-engineering")
    print("   3. Medir antes de optimizar")
    print("   4. Usar async solo para I/O intensivo")
    print("   5. Menos código = menos overhead")
    
    # Guardar resultados
    all_data = {
        "individual_performance": results,
        "concurrent_performance": concurrent_results,
        "timestamp": time.time(),
        "test_conditions": {
            "individual_iterations": 10,
            "concurrent_requests": 20,
            "timeout_seconds": 10
        }
    }
    
    with open("optimization_comparison.json", "w") as f:
        json.dump(all_data, f, indent=2)
    
    print(f"\n📁 Resultados completos guardados en: optimization_comparison.json")

if __name__ == "__main__":
    try:
        asyncio.run(compare_approaches())
    except KeyboardInterrupt:
        print("\n❌ Comparación interrumpida")
    except Exception as e:
        print(f"\n💥 Error: {e}")
    
    input("\nPresiona Enter para continuar...")
