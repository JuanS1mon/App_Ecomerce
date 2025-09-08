#!/usr/bin/env python3
"""
Script de Migración Automatizada a Microservicios
Migra de un monolito a arquitectura de microservicios
"""

import os
import sys
import subprocess
import time
import json
import requests
from pathlib import Path
from typing import Dict, List, Any

class MicroservicesMigrator:
    def __init__(self, base_path: str = None):
        self.base_path = Path(base_path or os.getcwd())
        self.services = {
            "core": {"port": 8001, "path": "microservices/core-service"},
            "stock": {"port": 8002, "path": "microservices/stock-service"},
            "obras": {"port": 8003, "path": "microservices/obras-service"},
            "tickets": {"port": 8004, "path": "microservices/tickets-service"}
        }
        self.status = {}
        
    def log(self, message: str, level: str = "INFO"):
        """Log con formato"""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")
        
    def run_command(self, command: str, cwd: str = None) -> bool:
        """Ejecutar comando y manejar errores"""
        try:
            cwd = cwd or str(self.base_path)
            self.log(f"Ejecutando: {command} en {cwd}")
            result = subprocess.run(
                command, 
                shell=True, 
                cwd=cwd, 
                capture_output=True, 
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                self.log(f"✅ Comando exitoso: {command}")
                return True
            else:
                self.log(f"❌ Error en comando: {command}", "ERROR")
                self.log(f"STDOUT: {result.stdout}", "ERROR")
                self.log(f"STDERR: {result.stderr}", "ERROR")
                return False
                
        except subprocess.TimeoutExpired:
            self.log(f"⏰ Timeout en comando: {command}", "ERROR")
            return False
        except Exception as e:
            self.log(f"💥 Excepción en comando {command}: {str(e)}", "ERROR")
            return False
    
    def check_service_health(self, service: str, timeout: int = 30) -> bool:
        """Verificar salud de un servicio"""
        port = self.services[service]["port"]
        health_url = f"http://localhost:{port}/{service}/health"
        
        self.log(f"🔍 Verificando salud de {service} en {health_url}")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                response = requests.get(health_url, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    self.log(f"✅ {service} service está saludable: {data}")
                    self.status[service] = "healthy"
                    return True
            except requests.exceptions.RequestException:
                pass
            
            time.sleep(2)
        
        self.log(f"❌ {service} service no responde después de {timeout}s", "ERROR")
        self.status[service] = "unhealthy"
        return False
    
    def stop_existing_services(self):
        """Detener servicios existentes"""
        self.log("🛑 Deteniendo servicios existentes...")
        
        # Detener servicios Python
        for service in self.services:
            port = self.services[service]["port"]
            # Buscar procesos en el puerto específico
            self.run_command(f"taskkill /F /IM python.exe 2>nul || echo 'No Python processes'")
            self.run_command(f"netstat -ano | findstr :{port} && taskkill /F /PID (netstat -ano | findstr :{port} | awk '{{print $5}}') 2>nul || echo 'Port {port} libre'")
        
        # Detener Docker si está corriendo
        self.run_command("docker-compose -f docker-compose.microservices.yml down 2>nul || echo 'Docker no estaba corriendo'")
        
        time.sleep(3)
        self.log("✅ Servicios detenidos")
    
    def start_individual_services(self):
        """Iniciar servicios individuales"""
        self.log("🚀 Iniciando servicios individuales...")
        
        for service_name, config in self.services.items():
            service_path = self.base_path / config["path"]
            port = config["port"]
            
            self.log(f"🔄 Iniciando {service_name} service en puerto {port}")
            
            # Cambiar al directorio del servicio e iniciar
            if service_path.exists():
                # Usar PowerShell para iniciar en background
                cmd = f'Start-Process -FilePath "python" -ArgumentList "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "{port}", "--reload" -WorkingDirectory "{service_path}" -WindowStyle Hidden'
                
                if self.run_command(f'powershell -Command "{cmd}"'):
                    self.log(f"🚀 {service_name} iniciado en background")
                    time.sleep(3)  # Dar tiempo para que inicie
                else:
                    self.log(f"❌ Error iniciando {service_name}", "ERROR")
            else:
                self.log(f"❌ No existe directorio: {service_path}", "ERROR")
    
    def verify_services(self):
        """Verificar que todos los servicios estén corriendo"""
        self.log("🔍 Verificando servicios...")
        
        all_healthy = True
        for service in self.services:
            if not self.check_service_health(service):
                all_healthy = False
        
        return all_healthy
    
    def start_docker_services(self):
        """Iniciar servicios con Docker Compose"""
        self.log("🐳 Iniciando servicios con Docker...")
        
        # Verificar que Docker esté disponible
        if not self.run_command("docker --version"):
            self.log("❌ Docker no está disponible", "ERROR")
            return False
        
        # Construir e iniciar servicios
        if self.run_command("docker-compose -f docker-compose.microservices.yml up --build -d"):
            self.log("✅ Servicios Docker iniciados")
            
            # Esperar a que los servicios estén listos
            self.log("⏳ Esperando que los servicios estén listos...")
            time.sleep(30)
            
            return self.verify_docker_services()
        else:
            self.log("❌ Error iniciando servicios Docker", "ERROR")
            return False
    
    def verify_docker_services(self):
        """Verificar servicios Docker"""
        self.log("🔍 Verificando servicios Docker...")
        
        # Verificar contenedores
        if self.run_command("docker-compose -f docker-compose.microservices.yml ps"):
            # Verificar health de servicios
            time.sleep(10)  # Dar tiempo adicional
            return self.verify_services()
        
        return False
    
    def generate_migration_report(self):
        """Generar reporte de migración"""
        report = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "migration_status": "completed" if all(status == "healthy" for status in self.status.values()) else "partial",
            "services": {}
        }
        
        for service, config in self.services.items():
            report["services"][service] = {
                "port": config["port"],
                "status": self.status.get(service, "unknown"),
                "health_url": f"http://localhost:{config['port']}/{service}/health",
                "docs_url": f"http://localhost:{config['port']}/{service}/docs"
            }
        
        # Guardar reporte
        report_path = self.base_path / "migration_report.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        self.log(f"📊 Reporte de migración guardado: {report_path}")
        return report
    
    def print_dashboard_info(self):
        """Mostrar información del dashboard"""
        self.log("📊 Dashboard de Control:")
        self.log("   Dashboard HTML: microservices/dashboard.html")
        self.log("   Abrir en navegador: file:///c:/Users/PCJuan/Desktop/sql_app/microservices/dashboard.html")
        self.log("")
        self.log("🔗 URLs de los Servicios:")
        for service, config in self.services.items():
            port = config["port"]
            self.log(f"   {service.title()} Service:")
            self.log(f"     - Health: http://localhost:{port}/{service}/health")
            self.log(f"     - Docs:   http://localhost:{port}/{service}/docs")
        self.log("")
        
    def migrate_to_microservices(self, use_docker: bool = False):
        """Proceso completo de migración"""
        self.log("🚀 INICIANDO MIGRACIÓN A MICROSERVICIOS")
        self.log("=" * 50)
        
        try:
            # Paso 1: Detener servicios existentes
            self.stop_existing_services()
            
            # Paso 2: Iniciar servicios
            if use_docker:
                success = self.start_docker_services()
            else:
                self.start_individual_services()
                success = self.verify_services()
            
            # Paso 3: Generar reporte
            report = self.generate_migration_report()
            
            # Paso 4: Mostrar resultado
            if success:
                self.log("🎉 MIGRACIÓN COMPLETADA EXITOSAMENTE!")
                self.print_dashboard_info()
            else:
                self.log("⚠️  MIGRACIÓN COMPLETADA CON ADVERTENCIAS", "WARNING")
                self.log("   Algunos servicios pueden no estar completamente operativos")
            
            self.log("=" * 50)
            return success
            
        except Exception as e:
            self.log(f"💥 ERROR EN MIGRACIÓN: {str(e)}", "ERROR")
            return False

def main():
    """Función principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Migración automatizada a microservicios")
    parser.add_argument("--docker", action="store_true", help="Usar Docker Compose")
    parser.add_argument("--path", type=str, help="Ruta base del proyecto")
    
    args = parser.parse_args()
    
    migrator = MicroservicesMigrator(args.path)
    success = migrator.migrate_to_microservices(use_docker=args.docker)
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
