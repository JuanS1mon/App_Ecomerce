# ============================================================================
# ENDPOINT TEMPORAL PARA PROBAR GENERADOR OPTIMIZADO
# ============================================================================
"""
Endpoint temporal para probar el nuevo generador optimizado sin tocar el código principal
"""

from fastapi import APIRouter, Request
import json

router = APIRouter(
    prefix="/generar-optimizado",
    tags=["generador-optimizado"]
)

@router.post("/test")
async def test_generador_optimizado(request: Request):
    """Endpoint para probar el generador optimizado"""
    
    try:
        # Obtener JSON del request
        json_data = await request.json()
        
        # Importar el generador optimizado
        from .generador_async_optimizado import generar_estructura_completa_optimizada
        from .Generar import create_service_config_from_json, auto_fix_relationships
        
        # Convertir JSON a configuración
        service_config = create_service_config_from_json(json_data)
        
        # Auto-corregir relaciones
        service_config = auto_fix_relationships(service_config)
        
        # Generar usando el nuevo sistema optimizado
        result = generar_estructura_completa_optimizada(service_config)
        
        if result["success"]:
            return {
                "success": True,
                "message": f"🚀 GENERADOR OPTIMIZADO: Servicio '{service_config.service_name}' generado con async/await inteligente",
                "generated_files": result["generated_files"],
                "files_count": len(result["generated_files"]),
                "optimizations_applied": {
                    "async_await_intelligent": True,
                    "complexity_based_decisions": True,
                    "performance_optimized": True
                }
            }
        else:
            return {
                "success": False,
                "message": "Error en el generador optimizado",
                "error": result.get("error")
            }
            
    except Exception as e:
        return {
            "success": False,
            "message": f"Error: {str(e)}"
        }

@router.get("/example")
async def get_optimized_example():
    """Obtener ejemplo para el generador optimizado"""
    
    example = {
        "service_name": "sistema_ventas_optimizado",
        "description": "Sistema de ventas con async/await optimizado",
        "tables": [
            {
                "name": "clientes",
                "description": "Tabla simple de clientes",
                "fields": [
                    {"name": "id", "field_type": "integer", "primary_key": True, "auto_increment": True},
                    {"name": "nombre", "field_type": "string", "max_length": 100},
                    {"name": "email", "field_type": "string", "max_length": 150, "unique": True}
                ]
            },
            {
                "name": "productos",
                "description": "Tabla compleja de productos",
                "fields": [
                    {"name": "id", "field_type": "integer", "primary_key": True, "auto_increment": True},
                    {"name": "nombre", "field_type": "string", "max_length": 200},
                    {"name": "descripcion", "field_type": "text"},
                    {"name": "precio", "field_type": "decimal"},
                    {"name": "categoria", "field_type": "string", "max_length": 50},
                    {"name": "stock", "field_type": "integer"},
                    {"name": "especificaciones", "field_type": "json"},
                    {"name": "fecha_creacion", "field_type": "datetime"}
                ]
            },
            {
                "name": "ventas",
                "description": "Tabla muy compleja de ventas",
                "fields": [
                    {"name": "id", "field_type": "integer", "primary_key": True, "auto_increment": True},
                    {"name": "numero_venta", "field_type": "string", "max_length": 50, "unique": True},
                    {"name": "cliente_id", "field_type": "integer", "foreign_key": "clientes.id"},
                    {"name": "producto_id", "field_type": "integer", "foreign_key": "productos.id"},
                    {"name": "cantidad", "field_type": "integer"},
                    {"name": "precio_unitario", "field_type": "decimal"},
                    {"name": "descuento", "field_type": "decimal"},
                    {"name": "total", "field_type": "decimal"},
                    {"name": "fecha_venta", "field_type": "datetime"},
                    {"name": "estado", "field_type": "string", "max_length": 20},
                    {"name": "metodo_pago", "field_type": "string", "max_length": 30},
                    {"name": "notas", "field_type": "text"},
                    {"name": "datos_adicionales", "field_type": "json"}
                ]
            }
        ],
        "relationships": [
            {
                "relationship_type": "one_to_many",
                "from_table": "clientes",
                "from_field": "id",
                "to_table": "ventas",
                "to_field": "cliente_id",
                "relationship_name": "ventas",
                "back_populates": "cliente"
            },
            {
                "relationship_type": "one_to_many",
                "from_table": "productos",
                "from_field": "id",
                "to_table": "ventas",
                "to_field": "producto_id",
                "relationship_name": "ventas",
                "back_populates": "producto"
            }
        ],
        "generate_crud_for_all": True,
        "generate_relationship_endpoints": True
    }
    
    return {
        "success": True,
        "example": example,
        "description": "Ejemplo optimizado que demuestra async/await inteligente",
        "expected_behavior": {
            "clientes": {
                "complexity": "BAJA",
                "get_by_id": "SYNC (operación simple)",
                "create_update_delete": "ASYNC (operaciones de escritura)",
                "list": "ASYNC (puede ser grande)"
            },
            "productos": {
                "complexity": "ALTA",
                "all_operations": "ASYNC (tabla compleja con muchos campos)",
                "additional_endpoints": "count, bulk_create, search avanzado"
            },
            "ventas": {
                "complexity": "MUY ALTA",
                "all_operations": "ASYNC (tabla muy compleja con relaciones)",
                "background_tasks": "limpieza después de eliminar",
                "additional_endpoints": "reportes, analytics, bulk operations"
            }
        },
        "instructions": [
            "1. Usa este JSON como base para probar el generador optimizado",
            "2. Envía el JSON al endpoint POST /generar-optimizado/test",
            "3. El sistema aplicará async/await inteligentemente",
            "4. Revisa los archivos generados para ver las optimizaciones"
        ]
    }
