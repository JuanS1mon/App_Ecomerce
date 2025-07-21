#!/usr/bin/env python3
"""
Script de prueba para verificar que las APIs del dashboard funcionan correctamente
después de arreglar los problemas de columnas faltantes.
"""

import asyncio
import aiohttp
import json
from datetime import datetime

async def test_api_endpoint(session, url, method='GET', data=None):
    """
    Función helper para probar un endpoint de API
    """
    try:
        if method == 'GET':
            async with session.get(url) as response:
                result = await response.json()
                return {
                    'url': url,
                    'status': response.status,
                    'success': response.status == 200,
                    'data': result if response.status == 200 else None,
                    'error': result if response.status != 200 else None
                }
        elif method == 'POST':
            async with session.post(url, data=data) as response:
                result = await response.json()
                return {
                    'url': url,
                    'status': response.status,
                    'success': response.status == 200,
                    'data': result if response.status == 200 else None,
                    'error': result if response.status != 200 else None
                }
    except Exception as e:
        return {
            'url': url,
            'status': 'ERROR',
            'success': False,
            'data': None,
            'error': str(e)
        }

async def test_dashboard_apis():
    """
    Prueba todas las APIs del dashboard de stock
    """
    base_url = "http://localhost:8000/stock_admin/api"
    
    # Lista de endpoints a probar
    endpoints = [
        # APIs básicas
        {'url': f"{base_url}/recent-movements", 'method': 'GET'},
        {'url': f"{base_url}/search-articles?q=test&limit=5", 'method': 'GET'},
        {'url': f"{base_url}/chart-data?period=7", 'method': 'GET'},
        {'url': f"{base_url}/chart-data?period=30", 'method': 'GET'},
        {'url': f"{base_url}/chart-data?period=90", 'method': 'GET'},
        {'url': f"{base_url}/metrics", 'method': 'GET'},
        {'url': f"{base_url}/depositos-distribution", 'method': 'GET'},
        {'url': f"{base_url}/categorias-top", 'method': 'GET'},
        {'url': f"{base_url}/dashboard-summary", 'method': 'GET'},
        {'url': f"{base_url}/alerts", 'method': 'GET'},
        # Endpoint específico (puede fallar si no existe el artículo)
        {'url': f"{base_url}/stock-status/TEST001", 'method': 'GET'},
    ]
    
    print("🧪 Iniciando pruebas de APIs del Dashboard de Stock")
    print("=" * 60)
    
    async with aiohttp.ClientSession() as session:
        results = []
        
        for endpoint in endpoints:
            print(f"🔍 Probando: {endpoint['url']}")
            result = await test_api_endpoint(session, endpoint['url'], endpoint['method'])
            results.append(result)
            
            if result['success']:
                print(f"   ✅ EXITOSO - Status: {result['status']}")
                if 'articles' in str(result['data']):
                    articles_count = len(result['data'].get('articles', []))
                    print(f"      📦 Artículos encontrados: {articles_count}")
                elif 'movements' in str(result['data']):
                    movements_count = len(result['data'].get('movements', []))
                    print(f"      📋 Movimientos encontrados: {movements_count}")
                elif 'alerts' in str(result['data']):
                    alerts_count = len(result['data'].get('alerts', []))
                    print(f"      🚨 Alertas encontradas: {alerts_count}")
            else:
                print(f"   ❌ ERROR - Status: {result['status']}")
                print(f"      💬 Error: {result['error']}")
            
            print()
    
    # Resumen final
    print("📊 RESUMEN DE PRUEBAS")
    print("=" * 40)
    successful = sum(1 for r in results if r['success'])
    total = len(results)
    print(f"✅ Exitosas: {successful}/{total}")
    print(f"❌ Fallidas: {total - successful}/{total}")
    
    if successful == total:
        print("\n🎉 ¡Todas las APIs funcionan correctamente!")
    else:
        print(f"\n⚠️  {total - successful} APIs necesitan atención")
        print("\nAPIs que fallaron:")
        for result in results:
            if not result['success']:
                print(f"  - {result['url']}: {result['error']}")

async def test_dashboard_page():
    """
    Prueba que la página del dashboard se cargue correctamente
    """
    print("\n🌐 Probando página del dashboard")
    print("=" * 40)
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("http://localhost:8000/stock_admin/dashboard") as response:
                if response.status == 200:
                    content = await response.text()
                    if "Panel de Administración de Stock" in content:
                        print("✅ Dashboard carga correctamente")
                        print(f"   📄 Tamaño del contenido: {len(content)} caracteres")
                    else:
                        print("⚠️  Dashboard carga pero el contenido puede estar incompleto")
                else:
                    print(f"❌ Error al cargar dashboard - Status: {response.status}")
    except Exception as e:
        print(f"❌ Error de conexión: {e}")

if __name__ == "__main__":
    print(f"🚀 Dashboard API Test Suite - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n📝 NOTA: Asegúrate de que el servidor esté ejecutándose en localhost:8000")
    print("   Comando: uvicorn main:app --reload")
    print()
    
    # Ejecutar pruebas
    asyncio.run(test_dashboard_apis())
    asyncio.run(test_dashboard_page())
    
    print("\n🏁 Pruebas completadas")
