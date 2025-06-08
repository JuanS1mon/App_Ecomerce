#!/usr/bin/env python3
"""
Test del Interceptor de Autenticación - Solución Bucle Infinito
===============================================================

Este script verifica que el interceptor JavaScript esté funcionando correctamente
para resolver el problema del bucle infinito de login.

Casos de prueba:
1. ✅ Login normal funciona
2. ✅ Usuario autenticado puede acceder a /admin con token
3. ✅ No hay bucle infinito cuando se visita /login estando autenticado
4. ✅ El interceptor está cargando en las páginas
"""

import requests
import json
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

class InfiniteLoopTester:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        
        # Configurar reintentos para conexiones robustas
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        self.results = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "tests": {},
            "interceptor_verification": {},
            "summary": {}
        }
    
    def log(self, message):
        """Log con timestamp"""
        timestamp = time.strftime("%H:%M:%S")
        print(f"[{timestamp}] {message}")
    
    def test_1_login_functionality(self):
        """Test 1: Verificar que el login básico funciona"""
        self.log("🧪 TEST 1: Verificando funcionalidad de login...")
        
        try:
            # Intentar login
            login_data = {
                'username': 'juan',
                'password': 'qwer1234'
            }
            
            response = self.session.post(
                f"{self.base_url}/login",
                data=login_data,
                headers={'Content-Type': 'application/x-www-form-urlencoded'}
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'access_token' in data:
                    self.log("✅ Login exitoso - Token recibido")
                    self.results["tests"]["login_functionality"] = {
                        "status": "PASS",
                        "token_received": True,
                        "response_status": response.status_code
                    }
                    return data['access_token']
                else:
                    self.log("❌ Login falló - No se recibió token")
                    self.results["tests"]["login_functionality"] = {
                        "status": "FAIL",
                        "reason": "No token in response",
                        "response": data
                    }
            else:
                self.log(f"❌ Login falló - Status: {response.status_code}")
                self.results["tests"]["login_functionality"] = {
                    "status": "FAIL",
                    "response_status": response.status_code,
                    "response_text": response.text[:500]
                }
                
        except Exception as e:
            self.log(f"❌ Error en test de login: {e}")
            self.results["tests"]["login_functionality"] = {
                "status": "ERROR",
                "error": str(e)
            }
        
        return None
    
    def test_2_admin_access_with_token(self, token):
        """Test 2: Verificar acceso a /admin con token de Authorization"""
        self.log("🧪 TEST 2: Verificando acceso a /admin con token de Authorization...")
        
        if not token:
            self.log("⚠️ No hay token para probar acceso a admin")
            self.results["tests"]["admin_access_with_token"] = {
                "status": "SKIP",
                "reason": "No token available"
            }
            return
        
        try:
            # Probar acceso a /admin con header Authorization
            headers = {
                'Authorization': f'Bearer {token}',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
            }
            
            response = self.session.get(f"{self.base_url}/admin", headers=headers, allow_redirects=False)
            
            if response.status_code == 200:
                self.log("✅ Acceso a /admin exitoso con token Authorization")
                self.results["tests"]["admin_access_with_token"] = {
                    "status": "PASS",
                    "response_status": response.status_code,
                    "content_length": len(response.text)
                }
            elif response.status_code in [301, 302, 307, 308]:
                self.log(f"⚠️ /admin redirige (Status: {response.status_code}) - Verificando destino...")
                location = response.headers.get('Location', 'N/A')
                self.log(f"📍 Redirección a: {location}")
                
                if 'login' in location.lower():
                    self.log("❌ Redirige a login - Token rechazado")
                    self.results["tests"]["admin_access_with_token"] = {
                        "status": "FAIL",
                        "reason": "Redirects to login despite valid token",
                        "redirect_location": location,
                        "response_status": response.status_code
                    }
                else:
                    self.log("✅ Redirección válida (no a login)")
                    self.results["tests"]["admin_access_with_token"] = {
                        "status": "PASS",
                        "response_status": response.status_code,
                        "redirect_location": location
                    }
            else:
                self.log(f"❌ Error en acceso a /admin: {response.status_code}")
                self.results["tests"]["admin_access_with_token"] = {
                    "status": "FAIL",
                    "response_status": response.status_code,
                    "response_text": response.text[:500]
                }
                
        except Exception as e:
            self.log(f"❌ Error en test de admin: {e}")
            self.results["tests"]["admin_access_with_token"] = {
                "status": "ERROR",
                "error": str(e)
            }
    
    def test_3_interceptor_files_exist(self):
        """Test 3: Verificar que los archivos del interceptor son accesibles"""
        self.log("🧪 TEST 3: Verificando archivos del interceptor...")
        
        # Verificar que auth-interceptor.js es accesible
        try:
            response = self.session.get(f"{self.base_url}/static/js/auth-interceptor.js")
            
            if response.status_code == 200:
                content = response.text
                if 'navigateWithAuth' in content and 'AUTH_CONFIG' in content:
                    self.log("✅ Interceptor de autenticación accesible y válido")
                    self.results["interceptor_verification"]["interceptor_file"] = {
                        "status": "PASS",
                        "size": len(content),
                        "has_navigate_function": True,
                        "has_config": True
                    }
                else:
                    self.log("⚠️ Interceptor accesible pero contenido inválido")
                    self.results["interceptor_verification"]["interceptor_file"] = {
                        "status": "WARN",
                        "reason": "Missing key functions",
                        "size": len(content)
                    }
            else:
                self.log(f"❌ Interceptor no accesible: {response.status_code}")
                self.results["interceptor_verification"]["interceptor_file"] = {
                    "status": "FAIL",
                    "response_status": response.status_code
                }
                
        except Exception as e:
            self.log(f"❌ Error verificando interceptor: {e}")
            self.results["interceptor_verification"]["interceptor_file"] = {
                "status": "ERROR",
                "error": str(e)
            }
    
    def test_4_login_page_includes_interceptor(self):
        """Test 4: Verificar que login.html incluye el interceptor"""
        self.log("🧪 TEST 4: Verificando que login.html incluye el interceptor...")
        
        try:
            response = self.session.get(f"{self.base_url}/loginpage")
            
            if response.status_code == 200:
                content = response.text
                if 'auth-interceptor.js' in content:
                    self.log("✅ Login page incluye el interceptor")
                    self.results["interceptor_verification"]["login_page_includes_interceptor"] = {
                        "status": "PASS",
                        "has_interceptor_script": True
                    }
                else:
                    self.log("❌ Login page NO incluye el interceptor")
                    self.results["interceptor_verification"]["login_page_includes_interceptor"] = {
                        "status": "FAIL",
                        "reason": "auth-interceptor.js not found in login page"
                    }
            else:
                self.log(f"❌ No se pudo cargar login page: {response.status_code}")
                self.results["interceptor_verification"]["login_page_includes_interceptor"] = {
                    "status": "FAIL",
                    "response_status": response.status_code
                }
                
        except Exception as e:
            self.log(f"❌ Error verificando login page: {e}")
            self.results["interceptor_verification"]["login_page_includes_interceptor"] = {
                "status": "ERROR",
                "error": str(e)
            }
    
    def test_5_no_infinite_loop_simulation(self, token):
        """Test 5: Simular acceso a /login siendo ya autenticado"""
        self.log("🧪 TEST 5: Simulando acceso a /login con usuario autenticado...")
        
        if not token:
            self.log("⚠️ No hay token para probar bucle infinito")
            self.results["tests"]["no_infinite_loop"] = {
                "status": "SKIP",
                "reason": "No token available"
            }
            return
        
        try:
            # Simular que un usuario autenticado va a /login
            # Esto debe redirigir a admin sin crear un bucle
            
            redirect_count = 0
            max_redirects = 5
            current_url = f"{self.base_url}/loginpage"
            
            self.session.cookies.clear()  # Usar solo el token, no cookies
            
            while redirect_count < max_redirects:
                self.log(f"📍 Intento {redirect_count + 1}: Accediendo a {current_url}")
                
                headers = {
                    'Authorization': f'Bearer {token}',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
                }
                
                response = self.session.get(current_url, headers=headers, allow_redirects=False)
                
                if response.status_code in [301, 302, 307, 308]:
                    location = response.headers.get('Location', '')
                    self.log(f"🔄 Redirección {response.status_code} a: {location}")
                    
                    if location == current_url or '/login' in location:
                        self.log("🚨 ¡BUCLE INFINITO DETECTADO!")
                        self.results["tests"]["no_infinite_loop"] = {
                            "status": "FAIL",
                            "reason": "Infinite loop detected",
                            "redirect_count": redirect_count + 1,
                            "loop_url": location
                        }
                        return
                    
                    current_url = location if location.startswith('http') else f"{self.base_url}{location}"
                    redirect_count += 1
                    
                elif response.status_code == 200:
                    self.log(f"✅ Llegamos a destino final: {current_url}")
                    if '/admin' in current_url or 'admin' in response.text:
                        self.log("✅ No hay bucle infinito - Usuario redirigido correctamente")
                        self.results["tests"]["no_infinite_loop"] = {
                            "status": "PASS",
                            "redirect_count": redirect_count,
                            "final_url": current_url
                        }
                    else:
                        self.log("⚠️ Destino inesperado pero no hay bucle")
                        self.results["tests"]["no_infinite_loop"] = {
                            "status": "WARN",
                            "reason": "Unexpected destination",
                            "final_url": current_url,
                            "redirect_count": redirect_count
                        }
                    return
                    
                else:
                    self.log(f"❌ Error HTTP: {response.status_code}")
                    self.results["tests"]["no_infinite_loop"] = {
                        "status": "FAIL",
                        "reason": f"HTTP Error {response.status_code}",
                        "redirect_count": redirect_count
                    }
                    return
            
            self.log("⚠️ Demasiadas redirecciones (posible bucle)")
            self.results["tests"]["no_infinite_loop"] = {
                "status": "FAIL",
                "reason": "Too many redirects",
                "redirect_count": redirect_count
            }
            
        except Exception as e:
            self.log(f"❌ Error en test de bucle infinito: {e}")
            self.results["tests"]["no_infinite_loop"] = {
                "status": "ERROR",
                "error": str(e)
            }
    
    def run_all_tests(self):
        """Ejecutar todos los tests"""
        self.log("🚀 INICIANDO TESTS DEL INTERCEPTOR DE AUTENTICACIÓN")
        self.log("=" * 60)
        
        # Test 1: Login
        token = self.test_1_login_functionality()
        
        # Test 2: Admin access
        self.test_2_admin_access_with_token(token)
        
        # Test 3: Interceptor files
        self.test_3_interceptor_files_exist()
        
        # Test 4: Login page includes interceptor
        self.test_4_login_page_includes_interceptor()
        
        # Test 5: No infinite loop
        self.test_5_no_infinite_loop_simulation(token)
        
        # Generar resumen
        self.generate_summary()
        
        return self.results
    
    def generate_summary(self):
        """Generar resumen de resultados"""
        self.log("\n" + "=" * 60)
        self.log("📊 RESUMEN DE RESULTADOS")
        self.log("=" * 60)
        
        passed = 0
        failed = 0
        errors = 0
        warnings = 0
        skipped = 0
        
        all_tests = {**self.results["tests"], **self.results["interceptor_verification"]}
        
        for test_name, result in all_tests.items():
            status = result.get("status", "UNKNOWN")
            if status == "PASS":
                passed += 1
                self.log(f"✅ {test_name}: PASSED")
            elif status == "FAIL":
                failed += 1
                reason = result.get("reason", "Unknown reason")
                self.log(f"❌ {test_name}: FAILED - {reason}")
            elif status == "ERROR":
                errors += 1
                error = result.get("error", "Unknown error")
                self.log(f"🚨 {test_name}: ERROR - {error}")
            elif status == "WARN":
                warnings += 1
                reason = result.get("reason", "Unknown warning")
                self.log(f"⚠️ {test_name}: WARNING - {reason}")
            elif status == "SKIP":
                skipped += 1
                self.log(f"⏭️ {test_name}: SKIPPED")
        
        self.results["summary"] = {
            "total": len(all_tests),
            "passed": passed,
            "failed": failed,
            "errors": errors,
            "warnings": warnings,
            "skipped": skipped,
            "success_rate": f"{(passed / len(all_tests)) * 100:.1f}%" if all_tests else "0%"
        }
        
        self.log(f"\n📈 ESTADÍSTICAS:")
        self.log(f"   Total: {len(all_tests)}")
        self.log(f"   ✅ Passed: {passed}")
        self.log(f"   ❌ Failed: {failed}")
        self.log(f"   🚨 Errors: {errors}")
        self.log(f"   ⚠️  Warnings: {warnings}")
        self.log(f"   ⏭️  Skipped: {skipped}")
        self.log(f"   📊 Success Rate: {self.results['summary']['success_rate']}")
        
        if failed == 0 and errors == 0:
            self.log("\n🎉 ¡TODOS LOS TESTS CRÍTICOS PASARON!")
            self.log("🔒 El interceptor de autenticación está funcionando correctamente")
        else:
            self.log(f"\n⚠️ HAY {failed + errors} PROBLEMAS QUE REQUIEREN ATENCIÓN")

def main():
    tester = InfiniteLoopTester()
    
    try:
        results = tester.run_all_tests()
        
        # Guardar resultados
        with open('test_interceptor_results.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Resultados guardados en: test_interceptor_results.json")
        
    except KeyboardInterrupt:
        print("\n🛑 Tests interrumpidos por el usuario")
    except Exception as e:
        print(f"\n❌ Error general en tests: {e}")

if __name__ == "__main__":
    main()
