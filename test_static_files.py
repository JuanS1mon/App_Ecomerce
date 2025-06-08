#!/usr/bin/env python3
"""
Script para probar que los archivos estáticos sean accesibles
y que las rutas funcionen correctamente
"""

import os
import sys

def test_static_files():
    """Verifica que los archivos HTML estáticos existan"""
    print("🔍 Verificando archivos estáticos...")
    
    # Directorio de archivos estáticos
    static_dir = "sql_app/static"
    
    # Lista de archivos HTML críticos
    critical_files = [
        "login.html",
        "register.html", 
        "index.html",
        "terminos.html",
        "privacidad.html",
        "activation.html"
    ]
    
    print(f"📁 Directorio estático: {os.path.abspath(static_dir)}")
    print(f"📂 Directorio de trabajo actual: {os.getcwd()}")
    
    # Verificar si el directorio existe
    if not os.path.exists(static_dir):
        print(f"❌ ERROR: El directorio {static_dir} no existe")
        return False
    
    all_good = True
    
    # Verificar cada archivo
    for file_name in critical_files:
        file_path = os.path.join(static_dir, file_name)
        if os.path.exists(file_path):
            file_size = os.path.getsize(file_path)
            print(f"✅ {file_name} - OK ({file_size} bytes)")
        else:
            print(f"❌ {file_name} - NO ENCONTRADO")
            all_good = False
    
    # Verificar archivos en el directorio
    print(f"\n📋 Archivos en {static_dir}:")
    try:
        files = os.listdir(static_dir)
        for f in sorted(files):
            if f.endswith('.html'):
                print(f"   📄 {f}")
    except Exception as e:
        print(f"❌ Error listando archivos: {e}")
        all_good = False
    
    return all_good

def test_paths():
    """Prueba las rutas relativas que usa la aplicación"""
    print("\n🛣️  Probando rutas...")
    
    test_paths = [
        "sql_app/static/login.html",
        "sql_app/static/register.html",
        "sql_app/static/index.html"
    ]
    
    for path in test_paths:
        if os.path.exists(path):
            print(f"✅ {path} - OK")
        else:
            print(f"❌ {path} - NO ENCONTRADO")
            # Intentar encontrar alternativas
            print(f"   🔍 Buscando alternativas...")
            basename = os.path.basename(path)
            for root, dirs, files in os.walk("."):
                if basename in files:
                    found_path = os.path.join(root, basename)
                    print(f"   📍 Encontrado en: {found_path}")

if __name__ == "__main__":
    print("🚀 Iniciando test de archivos estáticos...")
    
    if test_static_files():
        print("\n✅ Todos los archivos críticos encontrados!")
    else:
        print("\n❌ Faltan algunos archivos críticos")
    
    test_paths()
    
    print(f"\n📊 Resumen:")
    print(f"   Directorio actual: {os.getcwd()}")
    print(f"   Python: {sys.version}")
    print(f"   OS: {os.name}")
