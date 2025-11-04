#!/usr/bin/env python3
"""
Script de diagnóstico para identificar qué módulo está causando el cierre automático del servidor
"""
import sys
import os
import time

def test_import(module_name, description):
    """Prueba importar un módulo y mide el tiempo"""
    print(f"🔍 Probando importar: {description} ({module_name})")
    start_time = time.time()

    try:
        __import__(module_name)
        end_time = time.time()
        duration = end_time - start_time
        print(f"✅ Módulo {module_name} importado correctamente en {duration:.3f}s")
        return True
    except Exception as e:
        end_time = time.time()
        duration = end_time - start_time
        print(f"❌ Error importando {module_name}: {e} ({duration:.3f}s)")
        return False

def test_fastapi_app():
    """Prueba crear una aplicación FastAPI básica"""
    print("🔍 Probando crear aplicación FastAPI básica...")
    try:
        from fastapi import FastAPI
        app = FastAPI()
        print("✅ Aplicación FastAPI básica creada correctamente")
        return True
    except Exception as e:
        print(f"❌ Error creando aplicación FastAPI: {e}")
        return False

def test_main_imports():
    """Prueba importar los módulos principales de main.py uno por uno"""
    print("\n" + "="*60)
    print("🧪 PRUEBA DE IMPORTACIONES PRINCIPALES")
    print("="*60)

    # Lista de imports principales de main.py
    imports_to_test = [
        ("config", "Configuración"),
        ("app_settings", "Configuración de aplicación"),
        ("logging_config", "Configuración de logging"),
        ("db.database", "Base de datos"),
        ("utils.templates", "Templates"),
        ("middleware.custom", "Middleware custom"),
        ("security.jwt_auth", "JWT Auth"),
        ("exception_handlers", "Manejadores de excepciones"),
    ]

    failed_imports = []

    for module, description in imports_to_test:
        if not test_import(module, description):
            failed_imports.append(module)

    if failed_imports:
        print(f"\n❌ {len(failed_imports)} módulos fallaron al importar:")
        for module in failed_imports:
            print(f"  - {module}")
    else:
        print("\n✅ Todos los módulos principales se importaron correctamente")

    return len(failed_imports) == 0

def test_router_imports():
    """Prueba importar los routers principales"""
    print("\n" + "="*60)
    print("🧪 PRUEBA DE IMPORTACIONES DE ROUTERS")
    print("="*60)

    # Lista de routers principales
    routers_to_test = [
        ("routers.auth", "Router de autenticación"),
        ("routers.usuarios", "Router de usuarios"),
        ("routers.carrito", "Router de carrito"),
        ("routers.static_pages", "Router de páginas estáticas"),
        ("routers.frontend_pages", "Router de páginas frontend"),
        ("routers.ecommerce_auth", "Router de auth ecommerce"),
    ]

    failed_routers = []

    for module, description in routers_to_test:
        if not test_import(module, description):
            failed_routers.append(module)

    if failed_routers:
        print(f"\n❌ {len(failed_routers)} routers fallaron al importar:")
        for router in failed_routers:
            print(f"  - {router}")
    else:
        print("\n✅ Todos los routers principales se importaron correctamente")

    return len(failed_routers) == 0

def test_database_connection():
    """Prueba la conexión a la base de datos"""
    print("\n" + "="*60)
    print("🧪 PRUEBA DE CONEXIÓN A BASE DE DATOS")
    print("="*60)

    try:
        from db.database import engine
        from sqlalchemy import text

        # Intentar hacer una consulta simple
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1 as test"))
            row = result.fetchone()
            if row and row[0] == 1:
                print("✅ Conexión a base de datos exitosa")
                return True
            else:
                print("❌ Consulta de prueba falló")
                return False

    except Exception as e:
        print(f"❌ Error conectando a base de datos: {e}")
        return False

def main():
    print("🔬 DIAGNÓSTICO DEL SERVIDOR FASTAPI")
    print("Identificando la causa del cierre automático")
    print("="*60)

    # Prueba básica de FastAPI
    if not test_fastapi_app():
        print("\n❌ FastAPI básico falló. Problema con la instalación.")
        return

    # Prueba imports principales
    main_ok = test_main_imports()

    # Prueba routers
    routers_ok = test_router_imports()

    # Prueba base de datos
    db_ok = test_database_connection()

    print("\n" + "="*60)
    print("📊 RESULTADOS DEL DIAGNÓSTICO:")
    print(f"  FastAPI básico: ✅ OK")
    print(f"  Imports principales: {'✅ OK' if main_ok else '❌ FALLÓ'}")
    print(f"  Routers: {'✅ OK' if routers_ok else '❌ FALLÓ'}")
    print(f"  Base de datos: {'✅ OK' if db_ok else '❌ FALLÓ'}")

    if main_ok and routers_ok and db_ok:
        print("\n🤔 Todos los componentes funcionan individualmente.")
        print("💡 El problema podría estar en la interacción entre componentes")
        print("💡 o en el código de inicialización del servidor.")
        print("\n🔧 Sugerencias:")
        print("  1. Revisar el lifespan en main.py")
        print("  2. Verificar middlewares")
        print("  3. Probar ejecutar con menos routers")
        print("  4. Revisar logs de uvicorn con --log-level debug")
    else:
        print("\n❌ Algunos componentes fallan. Revisar los detalles arriba.")

if __name__ == "__main__":
    main()