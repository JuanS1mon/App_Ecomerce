# ============================================================================
# GENERADOR_ASYNC_OPTIMIZADO.PY
# ============================================================================
"""
Versión mejorada del generador que usa async/await inteligentemente
"""

import os
from typing import Dict, Any, List, Optional
from pathlib import Path
from .generator_config import MultiTableServiceConfig, TableConfig, FieldConfig, RelationshipConfig, GENERATOR_CONFIG
from .generator_logger import main_logger

class AsyncDecisionEngine:
    """Motor de decisión para determinar cuándo usar async/await"""
    
    @staticmethod
    def should_use_async(operation: str, table: TableConfig, service_config: MultiTableServiceConfig) -> bool:
        """Determinar si una operación debe ser async"""
        
        # Reglas por tipo de operación
        async_operations = {
            "create": True,      # ✅ Siempre async - operaciones DB complejas
            "update": True,      # ✅ Siempre async - operaciones DB complejas
            "delete": True,      # ✅ Siempre async - pueden tener cascadas
            "list": True,        # ✅ Siempre async - listas pueden ser grandes
            "search": True,      # ✅ Siempre async - consultas complejas
            "bulk": True,        # ✅ Siempre async - operaciones masivas
        }
        
        # Operaciones que dependen de la complejidad
        complexity_dependent = {
            "get_by_id": False,  # Por defecto sync para gets simples
            "count": False,      # Por defecto sync para conteos
            "exists": False,     # Por defecto sync para verificaciones
        }
        
        # Si está en la lista de siempre async
        if operation in async_operations:
            return True
            
        # Si está en las dependientes de complejidad
        if operation in complexity_dependent:
            return AsyncDecisionEngine._is_complex_table(table, service_config)
            
        # Por defecto async para operaciones no definidas
        return True
    
    @staticmethod
    def _is_complex_table(table: TableConfig, service_config: MultiTableServiceConfig) -> bool:
        """Determinar si una tabla es compleja"""
        
        # Factores de complejidad
        factors = 0
        
        # Muchos campos
        if len(table.fields) > 5:
            factors += 1
            
        # Tiene relaciones
        table_relationships = [rel for rel in service_config.relationships 
                             if rel.from_table == table.name or rel.to_table == table.name]
        if table_relationships:
            factors += 1
            
        # Tiene campos complejos (text, json, etc.)
        complex_types = ["text", "longtext", "json", "jsonb", "blob"]
        has_complex_fields = any(field.field_type.lower() in complex_types for field in table.fields)
        if has_complex_fields:
            factors += 1
            
        # Tabla con foreign keys
        has_foreign_keys = any(field.foreign_key for field in table.fields)
        if has_foreign_keys:
            factors += 1
            
        # Es compleja si tiene 2 o más factores
        return factors >= 2

class AsyncRouterGenerator:
    """Generador optimizado de routers con async/await inteligente"""
    
    def __init__(self):
        self.decision_engine = AsyncDecisionEngine()
    
    def generate_router(self, table: TableConfig, service_config: MultiTableServiceConfig) -> str:
        """Generar router con async/await optimizado"""
        
        model_name = table.get_model_name()
        base_name = table.name.title()
        pk_field = table.get_primary_key_field()
        pk_name = pk_field.name if pk_field else "id"
        pk_type = "int" if pk_field and pk_field.field_type in ["integer", "int"] else "str"
        
        # Determinar qué operaciones necesitan async
        create_async = self.decision_engine.should_use_async("create", table, service_config)
        list_async = self.decision_engine.should_use_async("list", table, service_config)
        get_async = self.decision_engine.should_use_async("get_by_id", table, service_config)
        update_async = self.decision_engine.should_use_async("update", table, service_config)
        delete_async = self.decision_engine.should_use_async("delete", table, service_config)
        
        content = f'''# ============================================================================
# ROUTER OPTIMIZADO: {table.name.upper()}
# ============================================================================
"""
Router FastAPI optimizado para {table.name}
Parte del servicio: {service_config.service_name}
Usa async/await inteligentemente basado en la complejidad de las operaciones
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from sql_app.db.database import get_db, get_async_db
from .service_{table.name} import {table.name}_service
from .schema_{table.name} import {base_name}, {base_name}Create, {base_name}Update

router = APIRouter(
    prefix="/{table.name}",
    tags=["{table.name}"],
    responses={{404: {{"description": "No encontrado"}}}}
)

# ============================================================================
# CREATE - {'ASYNC' if create_async else 'SYNC'}
# ============================================================================
'''
        
        # Generar endpoint CREATE
        if create_async:
            content += f'''
@router.post("/", response_model={base_name}, status_code=status.HTTP_201_CREATED)
async def create_{table.name}(
    obj_in: {base_name}Create,
    db: AsyncSession = Depends(get_async_db),
    background_tasks: BackgroundTasks = None
):
    """
    Crear nuevo {table.name}
    ✅ ASYNC - Operación de escritura optimizada para concurrencia
    """
    return await {table.name}_service.create_async(db=db, obj_in=obj_in)
'''
        else:
            content += f'''
@router.post("/", response_model={base_name}, status_code=status.HTTP_201_CREATED)
def create_{table.name}(
    obj_in: {base_name}Create,
    db: Session = Depends(get_db)
):
    """
    Crear nuevo {table.name}
    ⚡ SYNC - Operación simple sin necesidad de async
    """
    return {table.name}_service.create(db=db, obj_in=obj_in)
'''

        # Generar endpoint LIST
        content += f'''
# ============================================================================
# LIST - {'ASYNC' if list_async else 'SYNC'}
# ============================================================================
'''
        
        if list_async:
            content += f'''
@router.get("/", response_model=List[{base_name}])
async def read_{table.name}_list(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_async_db)
):
    """
    Obtener lista de {table.name}
    ✅ ASYNC - Lista optimizada para grandes volúmenes de datos
    """
    if search:
        return await {table.name}_service.search_async(db=db, query=search, skip=skip, limit=limit)
    return await {table.name}_service.get_multi_async(db=db, skip=skip, limit=limit)
'''
        else:
            content += f'''
@router.get("/", response_model=List[{base_name}])
def read_{table.name}_list(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Obtener lista de {table.name}
    ⚡ SYNC - Lista simple sin complejidad adicional
    """
    return {table.name}_service.get_multi(db=db, skip=skip, limit=limit)
'''

        # Generar endpoint GET BY ID
        content += f'''
# ============================================================================
# GET BY ID - {'ASYNC' if get_async else 'SYNC'}
# ============================================================================
'''
        
        if get_async:
            content += f'''
@router.get("/{{{pk_name}}}", response_model={base_name})
async def read_{table.name}(
    {pk_name}: {pk_type},
    include_relations: bool = False,
    db: AsyncSession = Depends(get_async_db)
):
    """
    Obtener {table.name} por {pk_name}
    ✅ ASYNC - Tabla compleja que puede beneficiarse de carga optimizada
    """
    db_obj = await {table.name}_service.get_async(
        db=db, {pk_name}={pk_name}, include_relations=include_relations
    )
    if not db_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{base_name} no encontrado"
        )
    return db_obj
'''
        else:
            content += f'''
@router.get("/{{{pk_name}}}", response_model={base_name})
def read_{table.name}(
    {pk_name}: {pk_type},
    db: Session = Depends(get_db)
):
    """
    Obtener {table.name} por {pk_name}
    ⚡ SYNC - Operación simple y rápida
    """
    db_obj = {table.name}_service.get(db=db, {pk_name}={pk_name})
    if not db_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{base_name} no encontrado"
        )
    return db_obj
'''

        # Generar endpoint UPDATE
        content += f'''
# ============================================================================
# UPDATE - {'ASYNC' if update_async else 'SYNC'}
# ============================================================================
'''
        
        if update_async:
            content += f'''
@router.put("/{{{pk_name}}}", response_model={base_name})
async def update_{table.name}(
    {pk_name}: {pk_type},
    obj_in: {base_name}Update,
    db: AsyncSession = Depends(get_async_db),
    background_tasks: BackgroundTasks = None
):
    """
    Actualizar {table.name}
    ✅ ASYNC - Actualización optimizada con posibles efectos en cascada
    """
    db_obj = await {table.name}_service.get_async(db=db, {pk_name}={pk_name})
    if not db_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{base_name} no encontrado"
        )
    return await {table.name}_service.update_async(db=db, db_obj=db_obj, obj_in=obj_in)
'''
        else:
            content += f'''
@router.put("/{{{pk_name}}}", response_model={base_name})
def update_{table.name}(
    {pk_name}: {pk_type},
    obj_in: {base_name}Update,
    db: Session = Depends(get_db)
):
    """
    Actualizar {table.name}
    ⚡ SYNC - Actualización simple
    """
    db_obj = {table.name}_service.get(db=db, {pk_name}={pk_name})
    if not db_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{base_name} no encontrado"
        )
    return {table.name}_service.update(db=db, db_obj=db_obj, obj_in=obj_in)
'''

        # Generar endpoint DELETE
        content += f'''
# ============================================================================
# DELETE - {'ASYNC' if delete_async else 'SYNC'}
# ============================================================================
'''
        
        if delete_async:
            content += f'''
@router.delete("/{{{pk_name}}}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_{table.name}(
    {pk_name}: {pk_type},
    db: AsyncSession = Depends(get_async_db),
    background_tasks: BackgroundTasks = None
):
    """
    Eliminar {table.name}
    ✅ ASYNC - Eliminación con posibles cascadas y limpieza en background
    """
    success = await {table.name}_service.delete_async(db=db, {pk_name}={pk_name})
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{base_name} no encontrado"
        )
    
    # Ejecutar limpieza en background si es necesario
    if background_tasks:
        background_tasks.add_task({table.name}_service.cleanup_after_delete, {pk_name})
'''
        else:
            content += f'''
@router.delete("/{{{pk_name}}}", status_code=status.HTTP_204_NO_CONTENT)
def delete_{table.name}(
    {pk_name}: {pk_type},
    db: Session = Depends(get_db)
):
    """
    Eliminar {table.name}
    ⚡ SYNC - Eliminación simple
    """
    success = {table.name}_service.delete(db=db, {pk_name}={pk_name})
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{base_name} no encontrado"
        )
'''

        # Agregar endpoints adicionales si es una tabla compleja
        if self.decision_engine._is_complex_table(table, service_config):
            content += f'''

# ============================================================================
# ENDPOINTS ADICIONALES PARA TABLA COMPLEJA
# ============================================================================

@router.get("/count", response_model=int)
async def count_{table.name}(
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_async_db)
):
    """Contar registros de {table.name}"""
    return await {table.name}_service.count_async(db=db, search=search)

@router.post("/bulk", response_model=List[{base_name}])
async def bulk_create_{table.name}(
    objects: List[{base_name}Create],
    db: AsyncSession = Depends(get_async_db),
    background_tasks: BackgroundTasks = None
):
    """Crear múltiples {table.name} en lote"""
    return await {table.name}_service.bulk_create_async(db=db, objects=objects)
'''

        content += '''

# ============================================================================
# HEALTH CHECK - SIEMPRE SYNC
# ============================================================================

@router.get("/health")
def health_check():
    """
    Health check del servicio
    ⚡ SYNC - Verificación simple y rápida
    """
    return {"status": "healthy", "service": "''' + table.name + '''"}
'''

        return content

def generar_estructura_completa_optimizada(service_config: MultiTableServiceConfig) -> Dict[str, Any]:
    """Función mejorada para generar estructura completa con async/await optimizado"""
    
    generated_files = []
    router_generator = AsyncRouterGenerator()
    
    try:
        # Construir ruta base
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        services_path = os.path.join(base_dir, GENERATOR_CONFIG.paths.services)
        
        print(f"🚀 GENERADOR ASYNC OPTIMIZADO - Iniciando generación")
        print(f"📊 Servicio: {service_config.service_name}")
        print(f"📋 Tablas: {len(service_config.tables)}")
        
        for table in service_config.tables:
            print(f"\n🔍 Analizando tabla: {table.name}")
            
            # Analizar complejidad
            decision_engine = AsyncDecisionEngine()
            is_complex = decision_engine._is_complex_table(table, service_config)
            
            print(f"   📊 Campos: {len(table.fields)}")
            print(f"   🔗 Relaciones: {len([r for r in service_config.relationships if r.from_table == table.name or r.to_table == table.name])}")
            print(f"   🎯 Complejidad: {'ALTA' if is_complex else 'BAJA'}")
            
            # Crear directorio
            table_dir = os.path.join(services_path, service_config.service_name, table.name)
            Path(table_dir).mkdir(parents=True, exist_ok=True)
            
            # Generar router optimizado
            router_content = router_generator.generate_router(table, service_config)
            router_file = os.path.join(table_dir, f"route_{table.name}_optimized.py")
            
            with open(router_file, 'w', encoding='utf-8') as f:
                f.write(router_content)
            
            generated_files.append(router_file)
            print(f"   ✅ Router optimizado: {router_file}")
            
            # Mostrar decisiones de async/await
            operations = ["create", "list", "get_by_id", "update", "delete"]
            for op in operations:
                uses_async = decision_engine.should_use_async(op, table, service_config)
                print(f"   {'✅ ASYNC' if uses_async else '⚡ SYNC'}: {op}")
        
        print(f"\n🎯 GENERACIÓN COMPLETADA")
        print(f"📁 Archivos generados: {len(generated_files)}")
        print(f"💡 Se aplicó async/await inteligente basado en complejidad")
        
        return {
            "success": True,
            "generated_files": generated_files,
            "message": f"✅ Router optimizado generado para {len(service_config.tables)} tablas con async/await inteligente",
            "service_name": service_config.service_name
        }
        
    except Exception as e:
        print(f"❌ Error en generación: {e}")
        return {
            "success": False,
            "error": str(e),
            "generated_files": generated_files
        }
