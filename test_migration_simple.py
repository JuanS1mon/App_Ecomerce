#!/usr/bin/env python3
"""
Script de prueba simplificado para el sistema de migraciones
"""
import requests
import time
import os
import json

# Configuración
SERVER_URL = "http://127.0.0.1:8000"
TEST_FILE = "test_file_200mb_800000_rows.xlsx"
USERNAME = "juan"
PASSWORD = "123456"

class MigrationTester:
    def __init__(self):
        self.session = requests.Session()
        
    def login(self):
        """Autenticar usuario"""
        login_data = {
            "username": USERNAME,
            "password": PASSWORD
        }
        
        try:
            response = self.session.post(f"{SERVER_URL}/auth/login", data=login_data)
            
            if response.status_code == 200:
                print("✅ Login exitoso")
                return True
            else:
                print(f"❌ Error en login: {response.status_code}")
                print(f"   Respuesta: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error en login: {str(e)}")
            return False
            
    def upload_file(self):
        """Subir archivo de prueba"""
        if not os.path.exists(TEST_FILE):
            print(f"❌ Archivo de prueba no encontrado: {TEST_FILE}")
            return None
            
        print(f"📤 Subiendo archivo: {TEST_FILE}")
        print(f"📊 Tamaño: {os.path.getsize(TEST_FILE) / (1024*1024):.1f} MB")
        
        try:
            # Preparar archivos y datos
            files = {
                'file': (TEST_FILE, open(TEST_FILE, 'rb'), 
                        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            }
            
            data = {
                'nombreMigracion': 'test_paralelo_system'
            }
            
            response = self.session.post(f"{SERVER_URL}/migraciones/upload_migracion_file",
                                       files=files, data=data)
            
            files['file'][1].close()  # Cerrar archivo
            
            print(f"📡 Status de respuesta: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    result = response.json()
                    print("✅ Archivo subido exitosamente")
                    print(f"   Task ID: {result.get('task_id', 'N/A')}")
                    return result.get('task_id')
                except:
                    print("✅ Archivo subido exitosamente (respuesta sin JSON)")
                    return "upload_success"
            else:
                print(f"❌ Error en upload: {response.status_code}")
                print(f"   Respuesta: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error en upload: {str(e)}")
            return None
            
    def monitor_progress(self, task_id):
        """Monitorear progreso de la migración"""
        if not task_id:
            print("❌ No hay task_id para monitorear")
            return
            
        print(f"📊 Monitoreando progreso para task_id: {task_id}")
        
        start_time = time.time()
        last_status = None
        check_count = 0
        
        try:
            while check_count < 30:  # Máximo 30 intentos (1 minuto)
                try:
                    response = self.session.get(f"{SERVER_URL}/migraciones/progress/{task_id}")
                    
                    if response.status_code == 200:
                        try:
                            progress = response.json()
                            
                            current_status = progress.get('status', 'desconocido')
                            
                            # Mostrar actualizaciones
                            elapsed = time.time() - start_time
                            
                            print(f"\n⏱️  Tiempo transcurrido: {elapsed:.1f}s")
                            print(f"📈 Estado: {current_status}")
                            print(f"📊 Progreso: {progress.get('progress_percentage', 0):.1f}%")
                            
                            # Información de procesamiento paralelo
                            if 'total_chunks' in progress:
                                print(f"🔄 Chunks: {progress.get('processed_chunks', 0)}/{progress.get('total_chunks', 0)}")
                                print(f"💾 Memoria: {progress.get('memory_usage', 0):.1f} MB")
                                print(f"⚡ Velocidad: {progress.get('processing_speed', 0):.0f} filas/seg")
                                print(f"⏳ Tiempo estimado: {progress.get('estimated_time_remaining', 0):.1f}s")
                            
                            # Verificar si completó
                            if current_status in ['completado', 'completado con errores', 'error']:
                                print(f"\n🏁 Procesamiento finalizado: {current_status}")
                                
                                if progress.get('errors'):
                                    print("❌ Errores encontrados:")
                                    for error in progress['errors']:
                                        print(f"   - {error}")
                                else:
                                    print("✅ Sin errores")
                                    
                                total_time = time.time() - start_time
                                print(f"⏱️  Tiempo total: {total_time:.1f}s")
                                break
                                
                        except json.JSONDecodeError:
                            print(f"⚠️  Respuesta no es JSON válido: {response.text[:200]}")
                            
                    elif response.status_code == 404:
                        print(f"⚠️  Task ID no encontrado o procesamiento no iniciado aún")
                    else:
                        print(f"❌ Error consultando progreso: {response.status_code}")
                        print(f"   Respuesta: {response.text[:200]}")
                        
                except requests.exceptions.RequestException as e:
                    print(f"⚠️  Error de conexión: {str(e)}")
                    
                check_count += 1
                time.sleep(2)  # Esperar 2 segundos
                
            if check_count >= 30:
                print("\n⏰ Tiempo límite de monitoreo alcanzado")
                
        except Exception as e:
            print(f"❌ Error monitoreando progreso: {str(e)}")

def main():
    """Función principal de prueba"""
    print("🧪 PRUEBA DEL SISTEMA DE MIGRACIONES CON PROCESAMIENTO PARALELO")
    print("=" * 70)
    
    tester = MigrationTester()
    
    try:
        # Login
        if not tester.login():
            return
            
        # Upload file
        task_id = tester.upload_file()
        
        # Monitor progress
        if task_id:
            tester.monitor_progress(task_id)
        else:
            print("❌ No se pudo obtener task_id para monitorear")
            
    finally:
        print("\n🔚 Prueba completada")

if __name__ == "__main__":
    main()