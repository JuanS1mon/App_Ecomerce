#!/usr/bin/env python3
"""
Script de migración de seguridad para FastAPI
Este script ayuda a migrar gradualmente a las nuevas funciones de seguridad.
"""

import os
import sys
import shutil
from pathlib import Path
from datetime import datetime

def backup_original_files():
    """Crea copias de seguridad de los archivos originales"""
    print("🔄 Creando copias de seguridad de archivos originales...")
    
    files_to_backup = [
        "sql_app/Services/security/security.py",
        "sql_app/Services/security/rate_limit.py", 
        "sql_app/routers/usuarios.py"
    ]
    
    backup_dir = f"backup_security_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.makedirs(backup_dir, exist_ok=True)
    
    for file_path in files_to_backup:
        if os.path.exists(file_path):
            backup_path = os.path.join(backup_dir, os.path.basename(file_path))
            shutil.copy2(file_path, backup_path)
            print(f"   ✅ Respaldado: {file_path} -> {backup_path}")
        else:
            print(f"   ⚠️  Archivo no encontrado: {file_path}")
    
    print(f"📁 Respaldos guardados en: {backup_dir}")
    return backup_dir

def replace_with_improved_files():
    """Reemplaza los archivos originales con las versiones mejoradas"""
    print("🔄 Reemplazando archivos con versiones mejoradas...")
    
    replacements = [
        ("sql_app/Services/security/security_improved.py", "sql_app/Services/security/security.py"),
        ("sql_app/Services/security/rate_limit_improved.py", "sql_app/Services/security/rate_limit.py"),
        ("sql_app/routers/usuarios_improved.py", "sql_app/routers/usuarios.py")
    ]
    
    for source, destination in replacements:
        if os.path.exists(source):
            shutil.copy2(source, destination)
            print(f"   ✅ Reemplazado: {destination}")
        else:
            print(f"   ❌ Archivo mejorado no encontrado: {source}")

def install_dependencies():
    """Instala dependencias adicionales necesarias"""
    print("🔄 Instalando dependencias adicionales...")
    
    additional_deps = [
        "argon2-cffi",  # Para hashing de contraseñas mejorado
        "redis",        # Para almacenamiento de tokens revocados (opcional)
        "user-agents",  # Para análisis de user-agents
        "pydantic[email]",  # Para validación de emails mejorada
    ]
    
    for dep in additional_deps:
        try:
            os.system(f"pip install {dep}")
            print(f"   ✅ Instalado: {dep}")
        except Exception as e:
            print(f"   ⚠️  Error instalando {dep}: {e}")

def update_requirements_txt():
    """Actualiza el archivo requirements.txt con las nuevas dependencias"""
    print("🔄 Actualizando requirements.txt...")
    
    new_deps = [
        "argon2-cffi>=21.3.0",
        "redis>=4.0.0", 
        "user-agents>=2.2.0",
        "pydantic[email]>=1.10.0"
    ]
    
    requirements_file = "requirements.txt"
    
    # Leer requirements existentes
    existing_deps = set()
    if os.path.exists(requirements_file):
        with open(requirements_file, 'r') as f:
            existing_deps = set(line.strip() for line in f if line.strip() and not line.startswith('#'))
    
    # Agregar nuevas dependencias si no existen
    updated = False
    for dep in new_deps:
        dep_name = dep.split('>=')[0].split('==')[0]
        if not any(existing.startswith(dep_name) for existing in existing_deps):
            existing_deps.add(dep)
            updated = True
            print(f"   ✅ Agregado: {dep}")
    
    if updated:
        with open(requirements_file, 'w') as f:
            for dep in sorted(existing_deps):
                f.write(f"{dep}\n")
        print(f"   📝 Actualizado: {requirements_file}")
    else:
        print("   ℹ️  No se necesitaron actualizaciones en requirements.txt")

def create_env_file():
    """Crea el archivo .env si no existe"""
    print("🔄 Configurando archivo de entorno...")
    
    if not os.path.exists(".env"):
        if os.path.exists(".env.security.example"):
            shutil.copy2(".env.security.example", ".env")
            print("   ✅ Creado .env desde .env.security.example")
            print("   ⚠️  IMPORTANTE: Revise y configure las variables en .env")
        else:
            print("   ⚠️  .env.security.example no encontrado. Cree manualmente el archivo .env")
    else:
        print("   ℹ️  Archivo .env ya existe")

def validate_security_config():
    """Valida la configuración de seguridad"""
    print("🔄 Validando configuración de seguridad...")
    
    try:
        # Importar la configuración
        sys.path.append('sql_app')
        from config.security_config import security_config
        
        # Validar configuración
        is_valid = security_config.validate_config()
        
        if is_valid:
            print("   ✅ Configuración de seguridad válida")
        else:
            print("   ⚠️  Se encontraron advertencias en la configuración")
            
    except ImportError as e:
        print(f"   ❌ Error importando configuración: {e}")
    except Exception as e:
        print(f"   ❌ Error validando configuración: {e}")

def main():
    """Función principal del script de migración"""
    print("🔒 SCRIPT DE MIGRACIÓN DE SEGURIDAD")
    print("=" * 50)
    
    # Verificar que estamos en el directorio correcto
    if not os.path.exists("sql_app"):
        print("❌ Error: No se encuentra el directorio sql_app")
        print("   Ejecute este script desde el directorio raíz del proyecto")
        sys.exit(1)
    
    try:
        # Paso 1: Crear respaldos
        backup_dir = backup_original_files()
        
        # Paso 2: Instalar dependencias
        install_dependencies()
        
        # Paso 3: Actualizar requirements.txt
        update_requirements_txt()
        
        # Paso 4: Crear archivo .env
        create_env_file()
        
        # Paso 5: Reemplazar archivos (opcional)
        response = input("\n❓ ¿Desea reemplazar los archivos originales con las versiones mejoradas? [y/N]: ")
        if response.lower() in ['y', 'yes', 'sí', 's']:
            replace_with_improved_files()
        else:
            print("   ℹ️  Archivos originales no modificados")
            print("   ℹ️  Puede usar los archivos *_improved.py manualmente")
        
        # Paso 6: Validar configuración
        validate_security_config()
        
        print("\n✅ MIGRACIÓN COMPLETADA")
        print("=" * 50)
        print("📋 PRÓXIMOS PASOS:")
        print("1. Revise y configure las variables en .env")
        print("2. Teste la aplicación con las nuevas funciones de seguridad")
        print("3. Revise los logs de seguridad en logs/security.log")
        print(f"4. Los respaldos están disponibles en: {backup_dir}")
        print("\n🔐 FUNCIONES DE SEGURIDAD NUEVAS:")
        print("   • Autenticación JWT mejorada con claims adicionales")
        print("   • Rate limiting progressivo con detección de amenazas")
        print("   • Validación de contraseñas robusta")
        print("   • Logging de seguridad detallado")
        print("   • Protección contra ataques de fuerza bruta")
        print("   • Análisis de user-agents sospechosos")
        
    except Exception as e:
        print(f"\n❌ Error durante la migración: {e}")
        print("   Revise los logs y contacte al administrador del sistema")
        sys.exit(1)

if __name__ == "__main__":
    main()
