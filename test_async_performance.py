# ============================================================================
# SCRIPT DE COMPARACIÓN DE RENDIMIENTO ASYNC
# ============================================================================
# Herramienta para comparar el rendimiento antes y después de las optimizaciones

import asyncio
import aiohttp
import time
import statistics
from typing import List, Dict
import json

class PerformanceTester:
    def __init__(self):
        self.results = {}
    
    async def test_endpoint(self, url: str, iterations: int = 10) -> Dict:
        """Prueba un endpoint múltiples veces y mide rendimiento"""
        response_times = []
        errors = 0
        
        async with aiohttp.ClientSession() as session:
            for _ in range(iterations):
                start_time = time.time()
                try:
                    async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                        await response.json()
                        response_time = (time.time() - start_time) * 1000
                        response_times.append(response_time)
                except Exception as e:
                    errors += 1
                    print(f"Error en {url}: {e}")
        
        if response_times:
            return {
                "url": url,
                "iterations": iterations,
                "errors": errors,
                "avg_response_time_ms": round(statistics.mean(response_times), 2),
                "min_response_time_ms": round(min(response_times), 2),
                "max_response_time_ms": round(max(response_times), 2),
                "median_response_time_ms": round(statistics.median(response_times), 2),
                "success_rate": round((iterations - errors) / iterations * 100, 2)
            }
        else:
            return {
                "url": url,
                "errors": errors,
                "success_rate": 0
            }
    
    async def test_concurrent_requests(self, url: str, concurrent_users: int = 5) -> Dict:
        """Prueba capacidad de manejo de requests concurrentes"""
        start_time = time.time()
        
        async def make_request(session, user_id):
            try:
                async with session.get(f"{url}?user={user_id}") as response:
                    return await response.json()
            except Exception as e:
                return {"error": str(e)}
        
        async with aiohttp.ClientSession() as session:
            tasks = [make_request(session, i) for i in range(concurrent_users)]
            results = await asyncio.gather(*tasks, return_exceptions=True)
        
        total_time = (time.time() - start_time) * 1000
        successful = len([r for r in results if not isinstance(r, Exception) and "error" not in r])
        
        return {
            "url": url,
            "concurrent_users": concurrent_users,
            "total_time_ms": round(total_time, 2),
            "successful_requests": successful,
            "failed_requests": concurrent_users - successful,
            "avg_time_per_request_ms": round(total_time / concurrent_users, 2),
            "requests_per_second": round(concurrent_users / (total_time / 1000), 2)
        }
    
    async def run_comprehensive_test(self):
        """Ejecuta pruebas completas de rendimiento"""
        
        print("🚀 INICIANDO PRUEBAS DE RENDIMIENTO ASYNC")
        print("=" * 60)
        
        # URLs a probar
        endpoints = {
            "core_health": "http://localhost:8001/core/health",
            "core_optimized_health": "http://localhost:8001/core/health/detailed",
            "stock_health": "http://localhost:8002/stock/health", 
            "stock_articles": "http://localhost:8002/stock/articles",
            "stock_report": "http://localhost:8002/stock/inventory/report",
            "obras_health": "http://localhost:8003/obras/health",
            "obras_dashboard": "http://localhost:8003/obras/dashboard"
        }
        
        # Prueba 1: Rendimiento individual
        print("\n📊 PRUEBA 1: RENDIMIENTO INDIVIDUAL")
        print("-" * 40)
        
        for name, url in endpoints.items():
            print(f"Probando {name}...")
            result = await self.test_endpoint(url, iterations=5)
            self.results[f"individual_{name}"] = result
            print(f"  ✅ {name}: {result.get('avg_response_time_ms', 'ERROR')}ms promedio")
        
        # Prueba 2: Requests concurrentes
        print("\n🔄 PRUEBA 2: REQUESTS CONCURRENTES")
        print("-" * 40)
        
        key_endpoints = [
            ("core_health", "http://localhost:8001/core/health"),
            ("stock_articles", "http://localhost:8002/stock/articles"),
            ("obras_dashboard", "http://localhost:8003/obras/dashboard")
        ]
        
        for name, url in key_endpoints:
            print(f"Probando concurrencia en {name}...")
            result = await self.test_concurrent_requests(url, concurrent_users=10)
            self.results[f"concurrent_{name}"] = result
            print(f"  ✅ {name}: {result.get('requests_per_second', 'ERROR')} req/s")
        
        # Prueba 3: Operaciones complejas
        print("\n🎯 PRUEBA 3: OPERACIONES COMPLEJAS")
        print("-" * 40)
        
        complex_operations = [
            ("core_services_status", "http://localhost:8001/core/services/status"),
            ("stock_full_report", "http://localhost:8002/stock/inventory/report?include_metrics=true"),
        ]
        
        for name, url in complex_operations:
            print(f"Probando operación compleja: {name}...")
            result = await self.test_endpoint(url, iterations=3)
            self.results[f"complex_{name}"] = result
            print(f"  ✅ {name}: {result.get('avg_response_time_ms', 'ERROR')}ms promedio")
        
        # Generar reporte
        await self.generate_report()
    
    async def generate_report(self):
        """Genera reporte completo de rendimiento"""
        print("\n" + "=" * 60)
        print("📋 REPORTE DE RENDIMIENTO")
        print("=" * 60)
        
        # Agrupar resultados
        individual_tests = {k: v for k, v in self.results.items() if k.startswith("individual_")}
        concurrent_tests = {k: v for k, v in self.results.items() if k.startswith("concurrent_")}
        complex_tests = {k: v for k, v in self.results.items() if k.startswith("complex_")}
        
        # Reporte de pruebas individuales
        print("\n🚀 RENDIMIENTO INDIVIDUAL:")
        print("Endpoint" + " " * 25 + "Tiempo Promedio" + " " * 5 + "Éxito")
        print("-" * 60)
        for name, result in individual_tests.items():
            endpoint_name = name.replace("individual_", "")[:30]
            avg_time = result.get('avg_response_time_ms', 'ERROR')
            success = result.get('success_rate', 0)
            print(f"{endpoint_name:<30} {avg_time:>10}ms {success:>10}%")
        
        # Reporte de concurrencia
        print("\n🔄 CAPACIDAD DE CONCURRENCIA:")
        print("Endpoint" + " " * 25 + "Req/Segundo" + " " * 8 + "Éxito")
        print("-" * 60)
        for name, result in concurrent_tests.items():
            endpoint_name = name.replace("concurrent_", "")[:30]
            rps = result.get('requests_per_second', 'ERROR')
            success = result.get('successful_requests', 0)
            total = result.get('concurrent_users', 1)
            success_pct = round(success / total * 100, 1)
            print(f"{endpoint_name:<30} {rps:>10} {success_pct:>12}%")
        
        # Operaciones complejas
        print("\n🎯 OPERACIONES COMPLEJAS:")
        print("Operación" + " " * 25 + "Tiempo Promedio" + " " * 5 + "Éxito")
        print("-" * 60)
        for name, result in complex_tests.items():
            operation_name = name.replace("complex_", "")[:30]
            avg_time = result.get('avg_response_time_ms', 'ERROR')
            success = result.get('success_rate', 0)
            print(f"{operation_name:<30} {avg_time:>10}ms {success:>10}%")
        
        # Recomendaciones
        print("\n💡 RECOMENDACIONES:")
        self.generate_recommendations()
        
        # Guardar resultados
        with open('performance_results.json', 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"\n📁 Resultados guardados en: performance_results.json")
    
    def generate_recommendations(self):
        """Genera recomendaciones basadas en los resultados"""
        recommendations = []
        
        # Analizar tiempos de respuesta
        individual_tests = {k: v for k, v in self.results.items() if k.startswith("individual_")}
        avg_times = [result.get('avg_response_time_ms', 0) for result in individual_tests.values()]
        
        if avg_times:
            overall_avg = statistics.mean(avg_times)
            
            if overall_avg > 500:
                recommendations.append("⚠️  Tiempos de respuesta altos (>500ms). Considerar más optimizaciones.")
            elif overall_avg > 200:
                recommendations.append("📈 Tiempos de respuesta moderados. Hay espacio para mejoras.")
            else:
                recommendations.append("✅ Excelentes tiempos de respuesta (<200ms).")
        
        # Analizar concurrencia
        concurrent_tests = {k: v for k, v in self.results.items() if k.startswith("concurrent_")}
        rps_values = [result.get('requests_per_second', 0) for result in concurrent_tests.values()]
        
        if rps_values:
            max_rps = max(rps_values)
            
            if max_rps > 50:
                recommendations.append("🚀 Excelente capacidad de concurrencia (>50 req/s).")
            elif max_rps > 20:
                recommendations.append("📊 Buena capacidad de concurrencia. Puede escalarse más.")
            else:
                recommendations.append("⚡ Capacidad de concurrencia limitada. Revisar optimizaciones.")
        
        # Mostrar recomendaciones
        for i, rec in enumerate(recommendations, 1):
            print(f"   {i}. {rec}")
        
        # Recomendaciones específicas
        print("\n🔧 OPTIMIZACIONES ESPECÍFICAS:")
        print("   • Implementar Redis para caché")
        print("   • Usar connection pooling para DB")
        print("   • Configurar load balancing")
        print("   • Implementar rate limiting")
        print("   • Optimizar queries de base de datos")

async def main():
    """Función principal para ejecutar las pruebas"""
    tester = PerformanceTester()
    
    try:
        await tester.run_comprehensive_test()
    except KeyboardInterrupt:
        print("\n❌ Pruebas interrumpidas por el usuario")
    except Exception as e:
        print(f"\n💥 Error durante las pruebas: {e}")

if __name__ == "__main__":
    print("🔍 HERRAMIENTA DE ANÁLISIS DE RENDIMIENTO ASYNC")
    print("Asegúrate de que todos los microservicios estén ejecutándose")
    print("Puertos esperados: 8001 (Core), 8002 (Stock), 8003 (Obras)")
    print()
    
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"Error al ejecutar las pruebas: {e}")
    
    input("\nPresiona Enter para salir...")
