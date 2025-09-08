#!/usr/bin/env python3
"""
============================================================================
SCRIPT DE MIGRACIÓN DE MONOLITO A MICROSERVICIOS
============================================================================
Este script ayuda a migrar los servicios existentes del monolito
a la nueva arquitectura de microservicios.
"""

import os
import shutil
import sys
from pathlib import Path

# Colores para output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    ENDC = '\033[0m'

def print_step(message):
    print(f"{Colors.BLUE}🔄 {message}{Colors.ENDC}")

def print_success(message):
    print(f"{Colors.GREEN}✅ {message}{Colors.ENDC}")

def print_warning(message):
    print(f"{Colors.YELLOW}⚠️ {message}{Colors.ENDC}")

def print_error(message):
    print(f"{Colors.RED}❌ {message}{Colors.ENDC}")

class MicroservicesMigrator:
    def __init__(self, source_dir=".", target_dir="microservices"):
        self.source_dir = Path(source_dir)
        self.target_dir = Path(target_dir)
        
        # Mapeo de servicios origen -> destino
        self.service_mapping = {
            # Core services
            "sql_app/Services/admin": "core-service/admin",
            "sql_app/Services/security": "core-service/security", 
            "security": "core-service/security",
            "sql_app/Services/mail": "core-service/mail",
            "sql_app/Services/chat": "core-service/chat",
            "sql_app/Services/mensajes": "core-service/mensajes",
            
            # Stock service
            "sql_app/Services/app_stock": "stock-service/app_stock",
            
            # Obras service
            "sql_app/Services/app_obras": "obras-service/app_obras",
            
            # Shared utilities
            "sql_app/middleware": "core-service/middleware",
            "sql_app/config": "core-service/config",
            "sql_app/db": "core-service/db",
        }

    def create_service_structure(self):
        """Crear estructura básica de directorios para cada servicio"""
        print_step("Creando estructura de directorios para microservicios...")
        
        services = ["core-service", "stock-service", "obras-service"]
        
        for service in services:
            service_path = self.target_dir / service
            
            # Crear directorios principales
            directories = [
                service_path,
                service_path / "routers",
                service_path / "models", 
                service_path / "schemas",
                service_path / "static",
                service_path / "templates",
                service_path / "tests",
                service_path / "config"
            ]
            
            for directory in directories:
                directory.mkdir(parents=True, exist_ok=True)
                print_success(f"Creado: {directory}")

    def copy_service_files(self, source_path, target_path):
        """Copiar archivos de un servicio manteniendo estructura"""
        if not source_path.exists():
            print_warning(f"Directorio origen no existe: {source_path}")
            return False
            
        target_path.mkdir(parents=True, exist_ok=True)
        
        try:
            if source_path.is_file():
                shutil.copy2(source_path, target_path.parent)
                print_success(f"Copiado archivo: {source_path.name}")
            else:
                shutil.copytree(source_path, target_path, dirs_exist_ok=True)
                print_success(f"Copiado directorio: {source_path} -> {target_path}")
            return True
        except Exception as e:
            print_error(f"Error copiando {source_path}: {e}")
            return False

    def migrate_services(self):
        """Migrar servicios según el mapeo definido"""
        print_step("Iniciando migración de servicios...")
        
        for source_rel, target_rel in self.service_mapping.items():
            source_path = self.source_dir / source_rel
            target_path = self.target_dir / target_rel
            
            print_step(f"Migrando: {source_rel} -> {target_rel}")
            self.copy_service_files(source_path, target_path)

    def create_init_files(self):
        """Crear archivos __init__.py necesarios"""
        print_step("Creando archivos __init__.py...")
        
        services = ["core-service", "stock-service", "obras-service"]
        
        for service in services:
            service_path = self.target_dir / service
            
            # Crear __init__.py en directorios principales
            for subdir in ["routers", "models", "schemas", "config"]:
                init_file = service_path / subdir / "__init__.py"
                init_file.touch()
                print_success(f"Creado: {init_file}")

    def create_service_configs(self):
        """Crear archivos de configuración específicos por servicio"""
        print_step("Creando configuraciones específicas por servicio...")
        
        # Configuración para Core Service
        core_config = self.target_dir / "core-service" / "config" / "settings.py"
        core_config.write_text('''"""
Configuración específica para Core Service
"""
import os
from typing import List

# Base de datos
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./core.db")

# JWT y Seguridad
SECRET_KEY = os.getenv("SECRET_KEY", "core-service-secret-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# CORS
ALLOWED_ORIGINS: List[str] = ["*"]

# Email
MAIL_USERNAME = os.getenv("MAIL_USERNAME", "")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "")
MAIL_FROM = os.getenv("MAIL_FROM", "admin@empresa.com")
MAIL_PORT = int(os.getenv("MAIL_PORT", "587"))
MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com")

# URLs de otros servicios
STOCK_SERVICE_URL = os.getenv("STOCK_SERVICE_URL", "http://stock-service:8002")
OBRAS_SERVICE_URL = os.getenv("OBRAS_SERVICE_URL", "http://obras-service:8003")
''')
        print_success(f"Creado: {core_config}")
        
        # Configuración para Stock Service
        stock_config = self.target_dir / "stock-service" / "config" / "settings.py"
        stock_config.write_text('''"""
Configuración específica para Stock Service
"""
import os

# Base de datos
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./stock.db")

# URLs de servicios
CORE_SERVICE_URL = os.getenv("CORE_SERVICE_URL", "http://core-service:8001")

# Configuración específica de stock
STOCK_CALCULATION_INTERVAL = int(os.getenv("STOCK_CALCULATION_INTERVAL", "60"))  # segundos
LOW_STOCK_THRESHOLD = int(os.getenv("LOW_STOCK_THRESHOLD", "10"))
''')
        print_success(f"Creado: {stock_config}")
        
        # Configuración para Obras Service
        obras_config = self.target_dir / "obras-service" / "config" / "settings.py"
        obras_config.write_text('''"""
Configuración específica para Obras Service
"""
import os

# Base de datos
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./obras.db")

# URLs de servicios
CORE_SERVICE_URL = os.getenv("CORE_SERVICE_URL", "http://core-service:8001")

# Configuración específica de obras
PROJECT_STATUS_OPTIONS = ["planificacion", "en_progreso", "pausado", "completado"]
TASK_PRIORITY_OPTIONS = ["baja", "normal", "alta", "urgente"]
''')
        print_success(f"Creado: {obras_config}")

    def create_migration_report(self):
        """Crear reporte de migración"""
        print_step("Generando reporte de migración...")
        
        report = f"""
# REPORTE DE MIGRACIÓN A MICROSERVICIOS
Generado: {os.popen('date').read().strip()}

## SERVICIOS MIGRADOS:

### Core Service (Puerto 8001):
- admin (Panel de administración)
- security (Autenticación y autorización)  
- mail (Sistema de correos)
- chat (Comunicación en tiempo real)
- mensajes (Sistema de mensajes/notificaciones)
- middleware (Middlewares compartidos)
- config (Configuración centralizada)
- db (Acceso a base de datos)

### Stock Service (Puerto 8002):
- app_stock (Gestión de inventario y stock)

### Obras Service (Puerto 8003):
- app_obras (Gestión de obras y proyectos)

## ESTRUCTURA CREADA:
"""
        
        # Agregar estructura de directorios al reporte
        for root, dirs, files in os.walk(self.target_dir):
            level = root.replace(str(self.target_dir), '').count(os.sep)
            indent = ' ' * 2 * level
            report += f"{indent}{os.path.basename(root)}/\n"
            subindent = ' ' * 2 * (level + 1)
            for file in files:
                report += f"{subindent}{file}\n"
        
        report += f"""

## PRÓXIMOS PASOS:

1. Revisar y adaptar el código migrado
2. Configurar variables de entorno específicas
3. Probar cada servicio independientemente
4. Configurar comunicación entre servicios
5. Ejecutar tests de integración

## COMANDOS ÚTILES:

### Iniciar servicios:
cd {self.target_dir}
./start-microservices.bat  # Windows
./start-microservices.sh   # Linux/Mac

### Ver logs:
docker-compose -f docker-compose.microservices.yml logs -f [servicio]

### Detener servicios:
./stop-microservices.bat   # Windows
./stop-microservices.sh    # Linux/Mac

"""
        
        report_file = self.target_dir / "MIGRATION_REPORT.md"
        report_file.write_text(report)
        print_success(f"Reporte guardado en: {report_file}")

    def run_migration(self):
        """Ejecutar proceso completo de migración"""
        print(f"{Colors.BLUE}🚀 INICIANDO MIGRACIÓN A MICROSERVICIOS{Colors.ENDC}")
        print("=" * 60)
        
        try:
            self.create_service_structure()
            self.migrate_services()
            self.create_init_files()
            self.create_service_configs()
            self.create_migration_report()
            
            print("\n" + "=" * 60)
            print_success("¡MIGRACIÓN COMPLETADA EXITOSAMENTE!")
            print_success(f"Los microservicios han sido creados en: {self.target_dir}")
            print_success("Revisa el archivo MIGRATION_REPORT.md para más detalles")
            print("\n📋 Próximos pasos:")
            print("1. Revisar y adaptar el código migrado")
            print("2. Ejecutar: cd microservices && ./start-microservices.bat")
            print("3. Verificar: http://localhost/health")
            
        except Exception as e:
            print_error(f"Error durante la migración: {e}")
            sys.exit(1)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Migrar monolito a microservicios")
    parser.add_argument("--source", default=".", help="Directorio origen (default: .)")
    parser.add_argument("--target", default="microservices", help="Directorio destino (default: microservices)")
    
    args = parser.parse_args()
    
    migrator = MicroservicesMigrator(args.source, args.target)
    migrator.run_migration()
