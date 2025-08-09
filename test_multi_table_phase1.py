# ============================================================================
# TEST SISTEMA MULTI-TABLA (FASE 1)
# ============================================================================
"""
Tests para verificar el funcionamiento del sistema multi-tabla básico.
Fase 1: Soporte para 2 tablas con relaciones one-to-many y many-to-one.
"""

import os
import sys
import json
import tempfile
import shutil
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Imports del sistema
from sql_app.routers.config.generator_config import (
    MultiTableServiceConfig, TableConfig, FieldConfig, RelationshipConfig,
    MULTI_TABLE_VALIDATOR
)
from sql_app.routers.config.multi_table_generator import (
    MultiTableModelGenerator, MultiTableCRUDGenerator, multi_table_factory
)

def test_phase1_basic_configuration():
    """Test 1: Configuración básica de 2 tablas relacionadas"""
    print("🧪 Test 1: Configuración básica multi-tabla...")
    
    try:
        # Crear configuración de ejemplo: Autores y Libros
        autor_fields = [
            FieldConfig(name="id", field_type="integer", primary_key=True, auto_increment=True, nullable=False),
            FieldConfig(name="nombre", field_type="string", max_length=100, nullable=False),
            FieldConfig(name="email", field_type="string", max_length=150, unique=True),
            FieldConfig(name="fecha_creacion", field_type="datetime", default_value="now()")
        ]
        
        libro_fields = [
            FieldConfig(name="id", field_type="integer", primary_key=True, auto_increment=True, nullable=False),
            FieldConfig(name="titulo", field_type="string", max_length=200, nullable=False),
            FieldConfig(name="isbn", field_type="string", max_length=20, unique=True),
            FieldConfig(name="autor_id", field_type="integer", foreign_key="autores.id", nullable=False),
            FieldConfig(name="fecha_publicacion", field_type="date"),
            FieldConfig(name="precio", field_type="decimal")
        ]
        
        autores_table = TableConfig(
            name="autores",
            fields=autor_fields,
            description="Tabla de autores"
        )
        
        libros_table = TableConfig(
            name="libros", 
            fields=libro_fields,
            description="Tabla de libros"
        )
        
        # Definir relación one-to-many
        relationship = RelationshipConfig(
            relationship_type="one_to_many",
            from_table="autores",
            from_field="id",
            to_table="libros",
            to_field="autor_id",
            relationship_name="libros",
            back_populates="autor"
        )
        
        # Crear configuración del servicio
        service_config = MultiTableServiceConfig(
            service_name="biblioteca_test",
            description="Sistema de prueba para biblioteca",
            tables=[autores_table, libros_table],
            relationships=[relationship],
            generate_crud_for_all=True,
            generate_relationship_endpoints=True
        )
        
        # Validar configuración
        errors = MULTI_TABLE_VALIDATOR.validate_service_config(service_config)
        
        if errors:
            print(f"❌ Errores de validación: {errors}")
            return False
        
        print("✅ Configuración básica válida")
        print(f"   - Servicio: {service_config.service_name}")
        print(f"   - Tablas: {len(service_config.tables)}")
        print(f"   - Relaciones: {len(service_config.relationships)}")
        return True
        
    except Exception as e:
        print(f"❌ Error en configuración básica: {str(e)}")
        return False

def test_phase1_model_generation():
    """Test 2: Generación de modelos relacionados"""
    print("\n🧪 Test 2: Generación de modelos...")
    
    try:
        # Usar la misma configuración del test anterior
        service_config = create_test_service_config()
        
        # Crear directorio temporal para las pruebas
        temp_dir = tempfile.mkdtemp()
        original_services_path = os.environ.get('SERVICES_PATH')
        
        # Cambiar temporalmente la ruta de servicios
        from sql_app.routers.config.generator_config import GENERATOR_CONFIG
        original_path = GENERATOR_CONFIG.paths.services
        GENERATOR_CONFIG.paths.services = temp_dir
        
        try:
            # Generar modelos
            model_generator = MultiTableModelGenerator()
            result = model_generator.generate_related_models(service_config)
            
            if not result["success"]:
                print(f"❌ Error generando modelos: {result.get('error', 'Error desconocido')}")
                return False
            
            # Verificar archivos generados
            expected_files = [
                os.path.join(temp_dir, "biblioteca_test", "biblioteca_test_models.py"),
                os.path.join(temp_dir, "biblioteca_test", "__init__.py")
            ]
            
            for file_path in expected_files:
                if not os.path.exists(file_path):
                    print(f"❌ Archivo esperado no encontrado: {file_path}")
                    return False
            
            # Verificar contenido del modelo
            models_file = expected_files[0]
            with open(models_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Verificar que contiene las clases esperadas
            if "class Autores(Base):" not in content:
                print("❌ Clase Autores no encontrada en el modelo")
                return False
            
            if "class Libros(Base):" not in content:
                print("❌ Clase Libros no encontrada en el modelo")
                return False
            
            # Verificar relaciones
            if "relationship(" not in content:
                print("❌ Relaciones no encontradas en el modelo")
                return False
            
            print("✅ Modelos generados correctamente")
            print(f"   - Archivos: {len(result['generated_files'])}")
            print(f"   - Tablas procesadas: {result['tables_count']}")
            return True
            
        finally:
            # Restaurar configuración original
            GENERATOR_CONFIG.paths.services = original_path
            
            # Limpiar directorio temporal
            shutil.rmtree(temp_dir, ignore_errors=True)
            
    except Exception as e:
        print(f"❌ Error en generación de modelos: {str(e)}")
        return False

def test_phase1_crud_generation():
    """Test 3: Generación de operaciones CRUD relacionadas"""
    print("\n🧪 Test 3: Generación de CRUDs...")
    
    try:
        service_config = create_test_service_config()
        
        # Crear directorio temporal
        temp_dir = tempfile.mkdtemp()
        
        from sql_app.routers.config.generator_config import GENERATOR_CONFIG
        original_path = GENERATOR_CONFIG.paths.services
        GENERATOR_CONFIG.paths.services = temp_dir
        
        try:
            # Generar CRUDs
            crud_generator = MultiTableCRUDGenerator()
            result = crud_generator.generate_related_crud(service_config)
            
            if not result["success"]:
                print(f"❌ Error generando CRUDs: {result.get('error', 'Error desconocido')}")
                return False
            
            # Verificar archivos CRUD generados
            expected_crud_files = [
                os.path.join(temp_dir, "biblioteca_test", "crud", "autores_crud.py"),
                os.path.join(temp_dir, "biblioteca_test", "crud", "libros_crud.py"),
                os.path.join(temp_dir, "biblioteca_test", "crud", "relations.py")
            ]
            
            for file_path in expected_crud_files:
                if not os.path.exists(file_path):
                    print(f"❌ Archivo CRUD esperado no encontrado: {file_path}")
                    return False
            
            # Verificar contenido de operaciones relacionadas
            relations_file = expected_crud_files[2]
            with open(relations_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if "get_autores_with_libros" not in content:
                print("❌ Operación relacionada 'get_autores_with_libros' no encontrada")
                return False
            
            print("✅ CRUDs generados correctamente")
            print(f"   - Archivos CRUD: {len(result['generated_files'])}")
            return True
            
        finally:
            GENERATOR_CONFIG.paths.services = original_path
            shutil.rmtree(temp_dir, ignore_errors=True)
            
    except Exception as e:
        print(f"❌ Error en generación de CRUDs: {str(e)}")
        return False

def test_phase1_json_to_config():
    """Test 4: Conversión de JSON a configuración"""
    print("\n🧪 Test 4: Conversión JSON a configuración...")
    
    try:
        # JSON de ejemplo
        json_data = {
            "service_name": "ecommerce_test",
            "description": "Sistema de ecommerce de prueba",
            "tables": [
                {
                    "name": "usuarios",
                    "description": "Tabla de usuarios",
                    "fields": [
                        {"name": "id", "field_type": "integer", "primary_key": True, "auto_increment": True, "nullable": False},
                        {"name": "username", "field_type": "string", "max_length": 50, "unique": True, "nullable": False},
                        {"name": "email", "field_type": "string", "max_length": 100, "unique": True}
                    ]
                },
                {
                    "name": "productos",
                    "description": "Tabla de productos",
                    "fields": [
                        {"name": "id", "field_type": "integer", "primary_key": True, "auto_increment": True, "nullable": False},
                        {"name": "nombre", "field_type": "string", "max_length": 100, "nullable": False},
                        {"name": "precio", "field_type": "decimal"},
                        {"name": "usuario_id", "field_type": "integer", "foreign_key": "usuarios.id"}
                    ]
                }
            ],
            "relationships": [
                {
                    "relationship_type": "one_to_many",
                    "from_table": "usuarios",
                    "from_field": "id",
                    "to_table": "productos",
                    "to_field": "usuario_id",
                    "relationship_name": "productos",
                    "back_populates": "usuario"
                }
            ],
            "generate_crud_for_all": True,
            "generate_relationship_endpoints": True
        }
        
        # Importar función de conversión
        from sql_app.routers.config.Generar import create_service_config_from_json
        
        # Convertir JSON a configuración
        service_config = create_service_config_from_json(json_data)
        
        # Verificar conversión
        if service_config.service_name != "ecommerce_test":
            print("❌ Nombre del servicio no coincide")
            return False
        
        if len(service_config.tables) != 2:
            print(f"❌ Número de tablas incorrecto: {len(service_config.tables)}")
            return False
        
        if len(service_config.relationships) != 1:
            print(f"❌ Número de relaciones incorrecto: {len(service_config.relationships)}")
            return False
        
        # Validar configuración convertida
        errors = MULTI_TABLE_VALIDATOR.validate_service_config(service_config)
        if errors:
            print(f"❌ Configuración convertida no válida: {errors}")
            return False
        
        print("✅ Conversión JSON exitosa")
        print(f"   - Servicio: {service_config.service_name}")
        print(f"   - Tablas convertidas: {len(service_config.tables)}")
        print(f"   - Relaciones convertidas: {len(service_config.relationships)}")
        return True
        
    except Exception as e:
        print(f"❌ Error en conversión JSON: {str(e)}")
        return False

def test_phase1_factory_pattern():
    """Test 5: Factory pattern para generadores multi-tabla"""
    print("\n🧪 Test 5: Factory pattern multi-tabla...")
    
    try:
        # Probar creación de generadores
        model_generator = multi_table_factory.create_generator('models')
        crud_generator = multi_table_factory.create_generator('crud')
        
        if not isinstance(model_generator, MultiTableModelGenerator):
            print("❌ Factory no creó correctamente el generador de modelos")
            return False
        
        if not isinstance(crud_generator, MultiTableCRUDGenerator):
            print("❌ Factory no creó correctamente el generador de CRUD")
            return False
        
        # Probar tipo inválido
        try:
            invalid_generator = multi_table_factory.create_generator('invalid_type')
            print("❌ Factory debería haber lanzado error para tipo inválido")
            return False
        except ValueError:
            pass  # Comportamiento esperado
        
        print("✅ Factory pattern funcionando correctamente")
        return True
        
    except Exception as e:
        print(f"❌ Error en factory pattern: {str(e)}")
        return False

def create_test_service_config() -> MultiTableServiceConfig:
    """Crear configuración de servicio de prueba"""
    
    # Campos para autores
    autor_fields = [
        FieldConfig(name="id", field_type="integer", primary_key=True, auto_increment=True, nullable=False),
        FieldConfig(name="nombre", field_type="string", max_length=100, nullable=False),
        FieldConfig(name="email", field_type="string", max_length=150, unique=True)
    ]
    
    # Campos para libros
    libro_fields = [
        FieldConfig(name="id", field_type="integer", primary_key=True, auto_increment=True, nullable=False),
        FieldConfig(name="titulo", field_type="string", max_length=200, nullable=False),
        FieldConfig(name="autor_id", field_type="integer", foreign_key="autores.id", nullable=False)
    ]
    
    # Tablas
    autores_table = TableConfig(name="autores", fields=autor_fields)
    libros_table = TableConfig(name="libros", fields=libro_fields)
    
    # Relación
    relationship = RelationshipConfig(
        relationship_type="one_to_many",
        from_table="autores",
        from_field="id",
        to_table="libros",
        to_field="autor_id",
        relationship_name="libros",
        back_populates="autor"
    )
    
    return MultiTableServiceConfig(
        service_name="biblioteca_test",
        description="Sistema de prueba",
        tables=[autores_table, libros_table],
        relationships=[relationship]
    )

def run_all_phase1_tests():
    """Ejecutar todos los tests de la Fase 1"""
    print("=" * 70)
    print("🚀 EJECUTANDO TESTS DE FASE 1 - SISTEMA MULTI-TABLA")
    print("=" * 70)
    
    tests = [
        ("Configuración básica", test_phase1_basic_configuration),
        ("Generación de modelos", test_phase1_model_generation),
        ("Generación de CRUDs", test_phase1_crud_generation),
        ("Conversión JSON", test_phase1_json_to_config),
        ("Factory pattern", test_phase1_factory_pattern)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                print(f"💥 Test '{test_name}' FALLÓ")
        except Exception as e:
            print(f"💥 Test '{test_name}' EXCEPCIÓN: {str(e)}")
    
    print("\n" + "=" * 70)
    print(f"📊 RESULTADOS FINALES: {passed}/{total} tests pasaron")
    
    if passed == total:
        print("🎉 ¡TODOS LOS TESTS DE FASE 1 PASARON!")
        print("✅ Sistema multi-tabla básico funcionando correctamente")
    else:
        print(f"❌ {total - passed} tests fallaron")
        print("🔧 Revisa la implementación antes de continuar")
    
    print("=" * 70)
    
    return passed == total

if __name__ == "__main__":
    success = run_all_phase1_tests()
    sys.exit(0 if success else 1)
