#!/usr/bin/env python3
"""
Script para capturar errores durante la importación del router
"""
import sys
import os
import logging

# Configurar logging detallado
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

sys.path.append(os.path.join(os.path.dirname(__file__), 'sql_app'))

def test_router_import_with_logging():
    print("🔍 IMPORTANDO ROUTER CON LOGGING DETALLADO")
    print("=" * 50)
    
    try:
        print("1. Configurando entorno...")
        # Asegurar que estamos en el directorio correcto
        original_cwd = os.getcwd()
        sql_app_dir = os.path.join(os.path.dirname(__file__), 'sql_app')
        os.chdir(sql_app_dir)
        print(f"   Cambiado a directorio: {os.getcwd()}")
        
        print("2. Importando router de usuarios...")
        from routers import usuarios as aut_usuario
        print(f"   ✅ Router importado exitosamente")
        print(f"   Rutas en router: {len(aut_usuario.router.routes)}")
        
        # Verificar rutas específicas
        activation_count = 0
        for route in aut_usuario.router.routes:
            if hasattr(route, 'path') and 'activar' in route.path:
                activation_count += 1
                print(f"   ✅ Ruta de activación: {route.path}")
        
        print(f"   Total rutas de activación: {activation_count}")
        
        print("3. Importando main.py desde el directorio correcto...")
        import main
        print(f"   ✅ Main importado exitosamente")
        print(f"   Rutas en main.app: {len(main.app.routes)}")
        
        # Verificar rutas de activación en main
        main_activation_count = 0
        for route in main.app.routes:
            if hasattr(route, 'path') and 'activar' in route.path:
                main_activation_count += 1
                print(f"   ✅ Ruta de activación en main: {route.path}")
        
        print(f"   Total rutas de activación en main: {main_activation_count}")
        
        # Restaurar directorio original
        os.chdir(original_cwd)
        
        if main_activation_count == activation_count and activation_count > 0:
            print("\n✅ TODO CORRECTO: Router se importa y registra correctamente")
            return True
        else:
            print(f"\n❌ PROBLEMA: Router ({activation_count}) vs Main ({main_activation_count})")
            return False
            
    except Exception as e:
        print(f"❌ ERROR DURANTE LA IMPORTACIÓN: {e}")
        import traceback
        traceback.print_exc()
        # Restaurar directorio original
        try:
            os.chdir(original_cwd)
        except:
            pass
        return False

if __name__ == "__main__":
    success = test_router_import_with_logging()
    if success:
        print("\n🎯 CONCLUSIÓN: El problema NO está en la importación")
        print("   El problema debe estar en el entorno de ejecución de uvicorn")
    else:
        print("\n🎯 CONCLUSIÓN: Hay un problema durante la importación")
