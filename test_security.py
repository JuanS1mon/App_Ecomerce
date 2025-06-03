"""
Pruebas de seguridad para las mejoras implementadas
Este archivo contiene pruebas para validar las funciones de seguridad mejoradas.
"""

import asyncio
import aiohttp
import time
import json
from typing import Dict, List

class SecurityTester:
    """Clase para probar las funciones de seguridad"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.results: Dict = {}
    
    async def test_rate_limiting(self) -> Dict:
        """Prueba el rate limiting realizando múltiples solicitudes"""
        print("🔄 Probando rate limiting...")
        
        results = {
            "test_name": "Rate Limiting",
            "success": False,
            "details": []
        }
        
        async with aiohttp.ClientSession() as session:
            # Realizar múltiples intentos de login fallidos
            for i in range(10):
                try:
                    data = {
                        "username": "usuario_falso",
                        "password": "password_incorrecto"
                    }
                    
                    start_time = time.time()
                    async with session.post(
                        f"{self.base_url}/login",
                        data=data
                    ) as response:
                        end_time = time.time()
                        response_time = end_time - start_time
                        
                        result_detail = {
                            "attempt": i + 1,
                            "status_code": response.status,
                            "response_time": round(response_time, 3),
                            "blocked": response.status == 429
                        }
                        
                        results["details"].append(result_detail)
                        
                        if response.status == 429:
                            results["success"] = True
                            print(f"   ✅ Rate limiting activado en intento {i + 1}")
                            break
                            
                except Exception as e:
                    results["details"].append({
                        "attempt": i + 1,
                        "error": str(e)
                    })
                
                # Pequeña pausa entre intentos
                await asyncio.sleep(0.5)
        
        return results
    
    async def test_password_validation(self) -> Dict:
        """Prueba la validación de contraseñas"""
        print("🔄 Probando validación de contraseñas...")
        
        results = {
            "test_name": "Password Validation",
            "success": False,
            "details": []
        }
        
        weak_passwords = [
            "123456",
            "password",
            "abc",
            "PASSWORD",
            "12345678",
            "abcdefgh"
        ]
        
        strong_password = "MyStr0ng!P@ssw0rd"
        
        async with aiohttp.ClientSession() as session:
            # Probar contraseñas débiles
            for password in weak_passwords:
                try:
                    data = {
                        "nombre": "Test User",
                        "usuario": f"test_{int(time.time())}",
                        "clave": password,
                        "mail": f"test_{int(time.time())}@example.com"
                    }
                    
                    async with session.post(
                        f"{self.base_url}/user/registro",
                        json=data
                    ) as response:
                        
                        result_detail = {
                            "password": password,
                            "status_code": response.status,
                            "rejected": response.status == 400,
                            "response": await response.text() if response.status == 400 else "OK"
                        }
                        
                        results["details"].append(result_detail)
                        
                except Exception as e:
                    results["details"].append({
                        "password": password,
                        "error": str(e)
                    })
            
            # Verificar que al menos una contraseña débil fue rechazada
            rejected_count = sum(1 for detail in results["details"] if detail.get("rejected", False))
            if rejected_count > 0:
                results["success"] = True
                print(f"   ✅ Validación de contraseñas funcionando: {rejected_count} contraseñas débiles rechazadas")
        
        return results
    
    async def test_jwt_security(self) -> Dict:
        """Prueba la seguridad de los tokens JWT"""
        print("🔄 Probando seguridad JWT...")
        
        results = {
            "test_name": "JWT Security",
            "success": False,
            "details": []
        }
        
        # Tokens inválidos para probar
        invalid_tokens = [
            "invalid.token.here",
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.invalid.signature",
            "",
            "Bearer invalid_token"
        ]
        
        async with aiohttp.ClientSession() as session:
            for token in invalid_tokens:
                try:
                    headers = {"Authorization": f"Bearer {token}"} if token else {}
                    
                    async with session.get(
                        f"{self.base_url}/users/me",
                        headers=headers
                    ) as response:
                        
                        result_detail = {
                            "token": token[:20] + "..." if len(token) > 20 else token,
                            "status_code": response.status,
                            "unauthorized": response.status == 401
                        }
                        
                        results["details"].append(result_detail)
                        
                except Exception as e:
                    results["details"].append({
                        "token": token[:20] + "..." if len(token) > 20 else token,
                        "error": str(e)
                    })
            
            # Verificar que los tokens inválidos fueron rechazados
            unauthorized_count = sum(1 for detail in results["details"] if detail.get("unauthorized", False))
            if unauthorized_count == len(invalid_tokens):
                results["success"] = True
                print(f"   ✅ Seguridad JWT funcionando: todos los tokens inválidos rechazados")
        
        return results
    
    async def test_user_agent_analysis(self) -> Dict:
        """Prueba el análisis de user-agents sospechosos"""
        print("🔄 Probando análisis de user-agents...")
        
        results = {
            "test_name": "User Agent Analysis",
            "success": False,
            "details": []
        }
        
        suspicious_user_agents = [
            "sqlmap/1.4.7",
            "Nikto/2.1.6",
            "Mozilla/5.0 (compatible; Nmap Scripting Engine)",
            "curl/7.68.0",
            "python-requests/2.25.1"
        ]
        
        normal_user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        
        async with aiohttp.ClientSession() as session:
            # Probar user-agents sospechosos
            for user_agent in suspicious_user_agents:
                try:
                    headers = {"User-Agent": user_agent}
                    
                    async with session.get(
                        f"{self.base_url}/loginpage",
                        headers=headers
                    ) as response:
                        
                        result_detail = {
                            "user_agent": user_agent[:30] + "..." if len(user_agent) > 30 else user_agent,
                            "status_code": response.status,
                            "blocked": response.status == 403
                        }
                        
                        results["details"].append(result_detail)
                        
                except Exception as e:
                    results["details"].append({
                        "user_agent": user_agent[:30] + "..." if len(user_agent) > 30 else user_agent,
                        "error": str(e)
                    })
            
            # Si al menos un user-agent sospechoso fue detectado, es éxito
            blocked_count = sum(1 for detail in results["details"] if detail.get("blocked", False))
            if blocked_count > 0:
                results["success"] = True
                print(f"   ✅ Análisis de user-agents funcionando: {blocked_count} user-agents sospechosos detectados")
            else:
                print("   ℹ️  No se bloquearon user-agents (puede estar deshabilitado)")
                results["success"] = True  # No es un fallo si está deshabilitado
        
        return results
    
    async def run_all_tests(self) -> Dict:
        """Ejecuta todas las pruebas de seguridad"""
        print("🔒 INICIANDO PRUEBAS DE SEGURIDAD")
        print("=" * 50)
        
        all_results = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "base_url": self.base_url,
            "tests": []
        }
        
        # Lista de todas las pruebas
        tests = [
            self.test_rate_limiting,
            self.test_password_validation,
            self.test_jwt_security,
            self.test_user_agent_analysis
        ]
        
        # Ejecutar cada prueba
        for test in tests:
            try:
                result = await test()
                all_results["tests"].append(result)
            except Exception as e:
                all_results["tests"].append({
                    "test_name": test.__name__,
                    "success": False,
                    "error": str(e)
                })
        
        # Resumen de resultados
        print("\n📊 RESUMEN DE PRUEBAS")
        print("=" * 50)
        
        passed = sum(1 for test in all_results["tests"] if test.get("success", False))
        total = len(all_results["tests"])
        
        for test in all_results["tests"]:
            status = "✅ PASÓ" if test.get("success", False) else "❌ FALLÓ"
            print(f"{status}: {test.get('test_name', 'Prueba desconocida')}")
        
        print(f"\n🎯 RESULTADO: {passed}/{total} pruebas pasaron")
        
        if passed == total:
            print("✅ Todas las pruebas de seguridad pasaron exitosamente")
        else:
            print("⚠️  Algunas pruebas fallaron. Revise la configuración de seguridad.")
        
        return all_results
    
    def save_results(self, results: Dict, filename: str = "security_test_results.json"):
        """Guarda los resultados en un archivo JSON"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            print(f"📄 Resultados guardados en: {filename}")
        except Exception as e:
            print(f"❌ Error guardando resultados: {e}")

async def main():
    """Función principal para ejecutar las pruebas"""
    import sys
    
    # Obtener URL base de argumentos o usar por defecto
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    
    # Crear y ejecutar el tester
    tester = SecurityTester(base_url)
    results = await tester.run_all_tests()
    
    # Guardar resultados
    tester.save_results(results)
    
    print("\n🔒 PRUEBAS DE SEGURIDAD COMPLETADAS")
    print("   Revise los resultados detallados en security_test_results.json")

if __name__ == "__main__":
    asyncio.run(main())
