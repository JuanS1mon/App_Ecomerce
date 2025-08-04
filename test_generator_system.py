# ============================================================================
# TEST_GENERATOR_SYSTEM.PY - PRUEBAS DEL SISTEMA DE GENERACIÓN
# ============================================================================
"""
Script de prueba para verificar que el nuevo sistema de generación funciona correctamente.
"""

import sys
import os
sys.path.append('c:\\Users\\PCJuan\\Desktop\\sql_app')

def test_generator_config():
    """Probar la configuración del generador"""
    print("🧪 Probando configuración del generador...")
    
    try:
        from sql_app.routers.config.generator_config import GENERATOR_CONFIG, VALIDATOR, PATH_MANAGER
        
        print("✅ Imports exitosos")
        print(f"📁 Rutas configuradas: {GENERATOR_CONFIG.paths}")
        print(f"🔧 Tipos permitidos: {len(GENERATOR_CONFIG.allowed_field_types)} tipos")
        print(f"📝 Mapeos de tipos: {len(GENERATOR_CONFIG.field_type_mappings)} mapeos")
        
        return True
    except Exception as e:
        print(f"❌ Error en configuración: {e}")
        return False

def test_generator_validator():
    """Probar el validador"""
    print("\n🧪 Probando validador...")
    
    try:
        from sql_app.routers.config.generator_config import VALIDATOR
        
        # Probar validación de módulo
        VALIDATOR.validate_module_name("test_module")
        print("✅ Validación de nombre de módulo OK")
        
        # Probar validación de campos
        VALIDATOR.validate_field_names(["campo1", "campo2"])
        print("✅ Validación de nombres de campo OK")
        
        # Probar validación de tipos
        VALIDATOR.validate_field_types(["string", "integer"])
        print("✅ Validación de tipos de campo OK")
        
        # Probar validación completa
        options = {"generate_crud": True}
        VALIDATOR.validate_all("test_module", ["campo1"], ["string"], options)
        print("✅ Validación completa OK")
        
        return True
    except Exception as e:
        print(f"❌ Error en validador: {e}")
        return False

def test_generator_factory():
    """Probar el factory de generadores"""
    print("\n🧪 Probando factory de generadores...")
    
    try:
        from sql_app.routers.config.generator_factory import generator_factory
        
        # Listar generadores disponibles
        available = generator_factory.get_available_generators()
        print(f"✅ Generadores disponibles: {available}")
        
        # Crear un generador
        model_generator = generator_factory.create_generator('model')
        print(f"✅ Generador de modelo creado: {type(model_generator)}")
        
        return True
    except Exception as e:
        print(f"❌ Error en factory: {e}")
        return False

def test_generator_logger():
    """Probar el sistema de logging"""
    print("\n🧪 Probando sistema de logging...")
    
    try:
        from sql_app.routers.config.generator_logger import main_logger, GenerationSession
        
        # Probar logging básico
        main_logger.log_generation_start("test_module", "test")
        print("✅ Logging básico OK")
        
        # Probar sesión de generación
        with GenerationSession("test_module", "test", main_logger) as session:
            session.add_generated_file("test_file.py")
            print("✅ Sesión de generación OK")
        
        return True
    except Exception as e:
        print(f"❌ Error en logging: {e}")
        return False

def main():
    """Ejecutar todas las pruebas"""
    print("🚀 INICIANDO PRUEBAS DEL SISTEMA DE GENERACIÓN")
    print("=" * 60)
    
    tests = [
        test_generator_config,
        test_generator_validator,
        test_generator_factory,
        test_generator_logger
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Error inesperado en {test.__name__}: {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 RESULTADO: {passed}/{total} pruebas pasaron")
    
    if passed == total:
        print("🎉 ¡TODAS LAS PRUEBAS PASARON! El sistema está funcionando correctamente.")
    else:
        print("⚠️ Algunas pruebas fallaron. Revisar la configuración.")
    
    return passed == total

if __name__ == "__main__":
    main()
