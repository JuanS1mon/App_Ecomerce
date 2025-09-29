#!/usr/bin/env python3
"""
Script de prueba para el sistema de migraciones con procesamiento paralelo
"""
import asyncio
import aiohttp
import os
import time
from pathlib import Path

# Configuración
SERVER_URL = "http://127.0.0.1:8000"
TEST_FILE = "test_file_200mb_800000_rows.xlsx"
USERNAME = "juan"
PASSWORD = "123456"

class MigrationTester:
    def __init__(self):
        self.session = None
        self.auth_token = None
        
    async def create_session(self):
        """Crear sesión HTTP"""
        self.session = aiohttp.ClientSession()
        
    async def close_session(self):
        """Cerrar sesión HTTP"""
        if self.session:
            await self.session.close()
            
    async def login(self):
        """Autenticar usuario"""
        login_data = {
            "username": USERNAME,
            "password": PASSWORD
        }
        
        try:
            async with self.session.post(f"{SERVER_URL}/auth/login", 
                                       data=login_data) as response:
                if response.status == 200:
                    # Obtener token de la cookie o respuesta
                    cookies = response.cookies
                    self.auth_token = cookies.get('access_token')
                    if self.auth_token:
                        print("✅ Login exitoso")
                        return True
                    else:
                        print("❌ No se pudo obtener el token de autenticación")
                        return False
                else:
                    print(f"❌ Error en login: {response.status}")
                    text = await response.text()
                    print(f"   Respuesta: {text}")
                    return False
        except Exception as e:
            print(f"❌ Error en login: {str(e)}")
            return False
            
    async def upload_file(self):
        """Subir archivo de prueba"""
        if not os.path.exists(TEST_FILE):
            print(f"❌ Archivo de prueba no encontrado: {TEST_FILE}")
            return None
            
        print(f"📤 Subiendo archivo: {TEST_FILE}")
        print(f"📊 Tamaño: {os.path.getsize(TEST_FILE) / (1024*1024):.1f} MB")
        
        try:
            # Preparar datos del formulario
            data = aiohttp.FormData()
            data.add_field('nombreMigracion', 'test_paralelo_system')
            
            with open(TEST_FILE, 'rb') as f:
                data.add_field('file', f, 
                             filename=TEST_FILE,
                             content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                
                # Headers con autenticación
                headers = {}
                if self.auth_token:
                    headers['Cookie'] = f'access_token={self.auth_token.value}'
                
                async with self.session.post(f"{SERVER_URL}/migraciones/upload_migracion_file",
                                           data=data,
                                           headers=headers) as response:
                    
                    print(f"📡 Status de respuesta: {response.status}")
                    
                    if response.status == 200:
                        result = await response.json()
                        print("✅ Archivo subido exitosamente")
                        print(f"   Task ID: {result.get('task_id', 'N/A')}")
                        return result.get('task_id')
                    else:
                        print(f"❌ Error en upload: {response.status}")
                        text = await response.text()
                        print(f"   Respuesta: {text}")
                        return None
                        
        except Exception as e:
            print(f"❌ Error en upload: {str(e)}")
            return None
            
    async def monitor_progress(self, task_id):
        """Monitorear progreso de la migración"""
        if not task_id:
            print("❌ No hay task_id para monitorear")
            return
            
        print(f"📊 Monitoreando progreso para task_id: {task_id}")
        
        start_time = time.time()
        last_status = None
        
        try:
            while True:
                headers = {}
                if self.auth_token:
                    headers['Cookie'] = f'access_token={self.auth_token.value}'
                
                async with self.session.get(f"{SERVER_URL}/migraciones/progress/{task_id}",
                                          headers=headers) as response:
                    
                    if response.status == 200:
                        progress = await response.json()
                        
                        current_status = progress.get('status', 'desconocido')
                        
                        # Solo mostrar actualizaciones cuando hay cambios
                        if current_status != last_status or progress.get('progress_percentage', 0) % 10 == 0:
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
                            
                            last_status = current_status
                        
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
                            
                    else:
                        print(f"❌ Error consultando progreso: {response.status}")
                        break
                        
                # Esperar antes de la siguiente consulta
                await asyncio.sleep(2)
                
        except Exception as e:
            print(f"❌ Error monitoreando progreso: {str(e)}")

async def main():
    """Función principal de prueba"""
    print("🧪 PRUEBA DEL SISTEMA DE MIGRACIONES CON PROCESAMIENTO PARALELO")
    print("=" * 70)
    
    tester = MigrationTester()
    
    try:
        # Crear sesión
        await tester.create_session()
        print("✅ Sesión HTTP creada")
        
        # Login
        if not await tester.login():
            return
            
        # Upload file
        task_id = await tester.upload_file()
        
        # Monitor progress
        if task_id:
            await tester.monitor_progress(task_id)
        else:
            print("❌ No se pudo obtener task_id para monitorear")
            
    finally:
        await tester.close_session()
        print("\n🔚 Prueba completada")

if __name__ == "__main__":
    asyncio.run(main())