#!/usr/bin/env python3
"""
PRUEBA DEL GENERADOR ASYNC OPTIMIZADO
Genera código con async/await inteligente
"""

import sys
import os

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from routers.config.generator_config import (
    MultiTableServiceConfig, TableConfig, FieldConfig, RelationshipConfig
)
from routers.config.generador_async_optimizado import (
    generar_estructura_completa_optimizada, AsyncDecisionEngine, AsyncRouterGenerator
)

def crear_config_prueba():
    """Crear configuración de prueba con diferentes tipos de tablas"""
    
    # Tabla SIMPLE - pocas columnas, sin relaciones
    tabla_simple = TableConfig(
        name="configuracion",
        description="Tabla de configuración simple",
        fields=[
            FieldConfig(name="id", field_type="integer", primary_key=True, auto_increment=True),
            FieldConfig(name="clave", field_type="string", max_length=50),
            FieldConfig(name="valor", field_type="string", max_length=200)
        ]
    )
    
    # Tabla COMPLEJA - muchas columnas, con relaciones
    tabla_compleja = TableConfig(
        name="ordenes",
        description="Tabla compleja de órdenes",
        fields=[
            FieldConfig(name="id", field_type="integer", primary_key=True, auto_increment=True),
            FieldConfig(name="numero_orden", field_type="string", max_length=50, unique=True),
            FieldConfig(name="cliente_id", field_type="integer", foreign_key="clientes.id"),
            FieldConfig(name="fecha_creacion", field_type="datetime"),
            FieldConfig(name="fecha_entrega", field_type="datetime"),
            FieldConfig(name="total", field_type="decimal"),
            FieldConfig(name="estado", field_type="string", max_length=20),
            FieldConfig(name="notas", field_type="text"),
            FieldConfig(name="datos_extra", field_type="json"),
            FieldConfig(name="activo", field_type="boolean", default_value="true")
        ]
    )
    
    # Tabla INTERMEDIA - complejidad media
    tabla_intermedia = TableConfig(
        name="productos",
        description="Tabla de productos",
        fields=[
            FieldConfig(name="id", field_type="integer", primary_key=True, auto_increment=True),
            FieldConfig(name="nombre", field_type="string", max_length=100),
            FieldConfig(name="descripcion", field_type="text"),
            FieldConfig(name="precio", field_type="decimal"),
            FieldConfig(name="categoria_id", field_type="integer", foreign_key="categorias.id"),
            FieldConfig(name="stock", field_type="integer")
        ]
    )
    
    # Relaciones
    relaciones = [
        RelationshipConfig(
            relationship_type="one_to_many",
            from_table="clientes",
            from_field="id", 
            to_table="ordenes",
            to_field="cliente_id",
            relationship_name="ordenes",
            back_populates="cliente"
        ),
        RelationshipConfig(
            relationship_type="many_to_one",
            from_table="productos",
            from_field="categoria_id",
            to_table="categorias", 
            to_field="id",
            relationship_name="categoria",
            back_populates="productos"
        )
    ]
    
    # Configuración del servicio
    service_config = MultiTableServiceConfig(
        service_name="tienda_online",
        description="Sistema de tienda online con tablas de diferentes complejidades",
        tables=[tabla_simple, tabla_intermedia, tabla_compleja],
        relationships=relaciones,
        generate_crud_for_all=True,
        generate_relationship_endpoints=True
    )
    
    return service_config

def probar_decision_engine():
    """Probar el motor de decisión de async/await"""
    
    print("🧪 PROBANDO MOTOR DE DECISIÓN ASYNC/AWAIT")
    print("=" * 50)
    
    service_config = crear_config_prueba()
    decision_engine = AsyncDecisionEngine()
    
    for tabla in service_config.tables:
        print(f"\n📋 Tabla: {tabla.name}")
        print(f"   📊 Campos: {len(tabla.fields)}")
        
        # Evaluar complejidad
        is_complex = decision_engine._is_complex_table(tabla, service_config)
        print(f"   🎯 Complejidad: {'ALTA' if is_complex else 'BAJA'}")
        
        # Evaluar operaciones
        operaciones = ["create", "list", "get_by_id", "update", "delete", "search", "count"]
        
        for op in operaciones:
            should_async = decision_engine.should_use_async(op, tabla, service_config)
            status = "✅ ASYNC" if should_async else "⚡ SYNC"
            print(f"   {status}: {op}")

def probar_generacion_router():
    """Probar la generación de routers optimizados"""
    
    print("\n🚀 PROBANDO GENERACIÓN DE ROUTERS")
    print("=" * 50)
    
    service_config = crear_config_prueba()
    router_generator = AsyncRouterGenerator()
    
    for tabla in service_config.tables:
        print(f"\n📋 Generando router para: {tabla.name}")
        
        try:
            router_code = router_generator.generate_router(tabla, service_config)
            
            # Analizar el código generado
            lines = router_code.split('\n')
            async_count = sum(1 for line in lines if 'async def' in line)
            sync_count = sum(1 for line in lines if line.strip().startswith('def ') and 'async def' not in line)
            
            print(f"   ✅ Router generado exitosamente")
            print(f"   📊 Funciones async: {async_count}")
            print(f"   📊 Funciones sync: {sync_count}")
            
            # Guardar ejemplo
            filename = f"ejemplo_router_{tabla.name}_optimizado.py"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(router_code)
            print(f"   💾 Guardado como: {filename}")
            
        except Exception as e:
            print(f"   ❌ Error generando router: {e}")

def probar_generacion_completa():
    """Probar la generación completa del servicio"""
    
    print("\n🏗️ PROBANDO GENERACIÓN COMPLETA")
    print("=" * 50)
    
    service_config = crear_config_prueba()
    
    try:
        resultado = generar_estructura_completa_optimizada(service_config)
        
        if resultado["success"]:
            print("✅ GENERACIÓN EXITOSA")
            print(f"📁 Archivos generados: {len(resultado['generated_files'])}")
            print("\n📋 Archivos creados:")
            for archivo in resultado["generated_files"]:
                print(f"   • {archivo}")
        else:
            print("❌ GENERACIÓN FALLÓ")
            print(f"Error: {resultado.get('error', 'Error desconocido')}")
            
    except Exception as e:
        print(f"❌ Error en generación: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Función principal de pruebas"""
    
    print("🔬 PRUEBAS DEL GENERADOR ASYNC OPTIMIZADO")
    print("=" * 60)
    
    try:
        # Prueba 1: Motor de decisión
        probar_decision_engine()
        
        # Prueba 2: Generación de routers
        probar_generacion_router()
        
        # Prueba 3: Generación completa
        probar_generacion_completa()
        
        print("\n🎯 TODAS LAS PRUEBAS COMPLETADAS")
        
    except Exception as e:
        print(f"\n💥 Error en las pruebas: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
    input("\nPresiona Enter para continuar...")
