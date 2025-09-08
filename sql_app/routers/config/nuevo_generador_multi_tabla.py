# ============================================================================
# NUEVO_GENERADOR_MULTI_TABLA.PY - VERSIÓN CORREGIDA
# ============================================================================
"""
Generador corregido que crea carpetas individuales por tabla.
"""

import os
from typing import Dict, Any, List, Optional
from pathlib import Path
from .generator_config import MultiTableServiceConfig, TableConfig, FieldConfig, RelationshipConfig, GENERATOR_CONFIG
from .generator_logger import main_logger

def generar_estructura_completa_por_tabla(service_config: MultiTableServiceConfig) -> Dict[str, Any]:
    """Función independiente para generar estructura completa por tabla"""
    
    generated_files = []
    
    try:
        # Construir ruta base correcta para Services
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))  # sql_app/
        services_path = os.path.join(base_dir, GENERATOR_CONFIG.paths.services)  # sql_app/Services/
        
        # Para cada tabla, crear su carpeta individual
        for table in service_config.tables:
            
            # Crear directorio de la tabla
            table_dir = os.path.join(services_path, service_config.service_name, table.name)
            Path(table_dir).mkdir(parents=True, exist_ok=True)
            
            print(f"🏗️ Creando directorio: {table_dir}")  # Debug para verificar
            print(f"🏗️ Creando directorio: {table_dir}")  # Debug para verificar
            
            # 1. Generar model
            model_content = generar_modelo_tabla(table, service_config)
            model_file = os.path.join(table_dir, f"model_{table.name}.py")
            with open(model_file, 'w', encoding='utf-8') as f:
                f.write(model_content)
            generated_files.append(model_file)
            print(f"📄 Modelo creado: {model_file}")
            
            # 2. Generar schema
            schema_content = generar_schema_tabla(table, service_config)
            schema_file = os.path.join(table_dir, f"schema_{table.name}.py")
            with open(schema_file, 'w', encoding='utf-8') as f:
                f.write(schema_content)
            generated_files.append(schema_file)
            print(f"📄 Schema creado: {schema_file}")
            
            # 3. Generar service
            service_content = generar_service_tabla(table, service_config)
            service_file = os.path.join(table_dir, f"service_{table.name}.py")
            with open(service_file, 'w', encoding='utf-8') as f:
                f.write(service_content)
            generated_files.append(service_file)
            print(f"📄 Service creado: {service_file}")
            
            # 4. Generar router
            router_content = generar_router_tabla(table, service_config)
            router_file = os.path.join(table_dir, f"route_{table.name}.py")
            with open(router_file, 'w', encoding='utf-8') as f:
                f.write(router_content)
            generated_files.append(router_file)
            print(f"📄 Router creado: {router_file}")
            
            # 5. Generar __init__.py
            init_content = generar_init_tabla(table, service_config)
            init_file = os.path.join(table_dir, "__init__.py")
            with open(init_file, 'w', encoding='utf-8') as f:
                f.write(init_content)
            generated_files.append(init_file)
            print(f"📄 Init creado: {init_file}")
        
        # 6. Generar route_config para todo el servicio
        route_config_content = generar_route_config_servicio(service_config)
        route_config_file = os.path.join(services_path, service_config.service_name, f"route_config_{service_config.service_name}.py")
        with open(route_config_file, 'w', encoding='utf-8') as f:
            f.write(route_config_content)
        generated_files.append(route_config_file)
        print(f"📄 Route Config creado: {route_config_file}")
        
        print(f"🎯 Generación completada: {len(generated_files)} archivos creados")
        return {
            "success": True,
            "generated_files": generated_files,
            "message": f"✅ Estructura completa generada para {len(service_config.tables)} tablas",
            "service_name": service_config.service_name
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "generated_files": generated_files
        }

def generar_modelo_tabla(table: TableConfig, service_config: MultiTableServiceConfig) -> str:
    """Generar modelo SQLAlchemy para una tabla"""
    model_name = table.get_model_name()
    
    content = f'''# ============================================================================
# MODELO: {table.name.upper()}
# ============================================================================
"""
Modelo para {table.name}
Parte del servicio: {service_config.service_name}
{table.description or f"Tabla generada automáticamente"}
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from sql_app.db.database import Base
from datetime import datetime

class {model_name}(Base):
    """
    Modelo para {table.name}
    {table.description or f"Tabla generada automáticamente para {service_config.service_name}"}
    """
    __tablename__ = "{table.name}"
    
'''
    
    # Generar campos
    for field in table.fields:
        field_def = obtener_definicion_campo(field)
        content += f"    {field.name} = {field_def}\n"
    
    # Método __repr__
    pk_field = table.get_primary_key_field()
    pk_name = pk_field.name if pk_field else "id"
    
    content += f'''
    def __repr__(self):
        return f"<{model_name}({pk_name}={{self.{pk_name}}})">\n'''
    
    return content

def obtener_definicion_campo(field: FieldConfig) -> str:
    """Convertir FieldConfig a definición SQLAlchemy"""
    type_mapping = {
        'integer': 'Integer',
        'int': 'Integer', 
        'string': 'String',
        'str': 'String',
        'text': 'Text',
        'float': 'Float',
        'decimal': 'Numeric',
        'boolean': 'Boolean',
        'bool': 'Boolean',
        'datetime': 'DateTime',
        'date': 'DateTime'
    }
    
    col_type = type_mapping.get(field.field_type, 'String')
    
    # Para String, agregar longitud
    if col_type == 'String' and field.max_length:
        col_type = f"String({field.max_length})"
    elif col_type == 'String':
        col_type = "String(255)"
    
    args = [col_type]
    
    # Clave primaria
    if field.primary_key:
        args.append("primary_key=True")
    
    # Auto incremento
    if field.auto_increment:
        args.append("autoincrement=True")
    
    # Nullable
    if not field.nullable:
        args.append("nullable=False")
    
    # Unique
    if field.unique:
        args.append("unique=True")
    
    # Foreign key
    if field.foreign_key:
        args.append(f'ForeignKey("{field.foreign_key}")')
    
    return f"Column({', '.join(args)})"

def generar_schema_tabla(table: TableConfig, service_config: MultiTableServiceConfig) -> str:
    """Generar schemas Pydantic para una tabla"""
    base_name = table.name.title()
    
    content = f'''# ============================================================================
# SCHEMAS: {table.name.upper()}
# ============================================================================
"""
Schemas Pydantic para {table.name}
Parte del servicio: {service_config.service_name}
"""

from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from decimal import Decimal

class {base_name}Base(BaseModel):
    """Schema base para {table.name}"""
'''
    
    # Campos para el schema base (sin ID y campos auto-generados)
    for field in table.fields:
        if not field.primary_key and not field.auto_increment:
            field_type = obtener_tipo_pydantic(field)
            optional = f"Optional[{field_type}] = None" if field.nullable else field_type
            content += f"    {field.name}: {optional}\n"
    
    content += f'''

class {base_name}Create({base_name}Base):
    """Schema para crear {table.name}"""
    pass

class {base_name}Update({base_name}Base):
    """Schema para actualizar {table.name}"""
    pass

class {base_name}InDB({base_name}Base):
    """Schema para {table.name} en base de datos"""
    model_config = ConfigDict(from_attributes=True)
    
'''
    
    # Agregar todos los campos para el schema InDB
    for field in table.fields:
        field_type = obtener_tipo_pydantic(field)
        optional = f"Optional[{field_type}] = None" if field.nullable else field_type
        content += f"    {field.name}: {optional}\n"
    
    content += f'''

# Alias para compatibilidad
{base_name} = {base_name}InDB
'''
    
    return content

def obtener_tipo_pydantic(field: FieldConfig) -> str:
    """Convertir tipo de campo a tipo Pydantic"""
    type_mapping = {
        'integer': 'int',
        'int': 'int',
        'string': 'str',
        'str': 'str',
        'text': 'str',
        'float': 'float',
        'decimal': 'Decimal',
        'boolean': 'bool',
        'bool': 'bool',
        'datetime': 'datetime',
        'date': 'datetime'
    }
    return type_mapping.get(field.field_type, 'str')

def generar_service_tabla(table: TableConfig, service_config: MultiTableServiceConfig) -> str:
    """Generar service CRUD para una tabla"""
    model_name = table.get_model_name()
    base_name = table.name.title()
    pk_field = table.get_primary_key_field()
    pk_name = pk_field.name if pk_field else "id"
    pk_type = "int" if pk_field and pk_field.field_type in ["integer", "int"] else "str"
    
    content = f'''# ============================================================================
# SERVICE: {table.name.upper()}
# ============================================================================
"""
Service para {table.name}
Parte del servicio: {service_config.service_name}
"""

from sqlalchemy.orm import Session
from typing import List, Optional
from .model_{table.name} import {model_name}
from .schema_{table.name} import {base_name}Create, {base_name}Update

class {base_name}Service:
    """Service para operaciones CRUD de {table.name}"""
    
    def create(self, db: Session, obj_in: {base_name}Create) -> {model_name}:
        """Crear nuevo registro de {table.name}"""
        obj_data = obj_in.model_dump()
        db_obj = {model_name}(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def get(self, db: Session, {pk_name}: {pk_type}) -> Optional[{model_name}]:
        """Obtener {table.name} por {pk_name}"""
        return db.query({model_name}).filter({model_name}.{pk_name} == {pk_name}).first()
    
    def get_multi(self, db: Session, skip: int = 0, limit: int = 100) -> List[{model_name}]:
        """Obtener múltiples registros de {table.name}"""
        return db.query({model_name}).offset(skip).limit(limit).all()
    
    def update(self, db: Session, db_obj: {model_name}, obj_in: {base_name}Update) -> {model_name}:
        """Actualizar {table.name}"""
        obj_data = obj_in.model_dump(exclude_unset=True)
        for field, value in obj_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def delete(self, db: Session, {pk_name}: {pk_type}) -> bool:
        """Eliminar {table.name}"""
        db_obj = self.get(db, {pk_name})
        if db_obj:
            db.delete(db_obj)
            db.commit()
            return True
        return False

# Instancia global del service
{table.name}_service = {base_name}Service()
'''
    
    return content

def generar_router_tabla(table: TableConfig, service_config: MultiTableServiceConfig) -> str:
    """Generar router FastAPI para una tabla"""
    model_name = table.get_model_name()
    base_name = table.name.title()
    pk_field = table.get_primary_key_field()
    pk_name = pk_field.name if pk_field else "id"
    pk_type = "int" if pk_field and pk_field.field_type in ["integer", "int"] else "str"
    
    content = f'''# ============================================================================
# ROUTER: {table.name.upper()}
# ============================================================================
"""
Router FastAPI para {table.name}
Parte del servicio: {service_config.service_name}
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from sql_app.db.database import get_db
from .service_{table.name} import {table.name}_service
from .schema_{table.name} import {base_name}, {base_name}Create, {base_name}Update

router = APIRouter(
    prefix="/{table.name}",
    tags=["{table.name}"],
    responses={{404: {{"description": "No encontrado"}}}}
)

@router.post("/", response_model={base_name}, status_code=status.HTTP_201_CREATED)
def create_{table.name}(
    obj_in: {base_name}Create,
    db: Session = Depends(get_db)
):
    """Crear nuevo {table.name}"""
    return {table.name}_service.create(db=db, obj_in=obj_in)

@router.get("/", response_model=List[{base_name}])
def read_{table.name}_list(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Obtener lista de {table.name}"""
    return {table.name}_service.get_multi(db=db, skip=skip, limit=limit)

@router.get("/{{{pk_name}}}", response_model={base_name})
def read_{table.name}(
    {pk_name}: {pk_type},
    db: Session = Depends(get_db)
):
    """Obtener {table.name} por {pk_name}"""
    db_obj = {table.name}_service.get(db=db, {pk_name}={pk_name})
    if not db_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{base_name} no encontrado"
        )
    return db_obj

@router.put("/{{{pk_name}}}", response_model={base_name})
def update_{table.name}(
    {pk_name}: {pk_type},
    obj_in: {base_name}Update,
    db: Session = Depends(get_db)
):
    """Actualizar {table.name}"""
    db_obj = {table.name}_service.get(db=db, {pk_name}={pk_name})
    if not db_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{base_name} no encontrado"
        )
    return {table.name}_service.update(db=db, db_obj=db_obj, obj_in=obj_in)

@router.delete("/{{{pk_name}}}", status_code=status.HTTP_204_NO_CONTENT)
def delete_{table.name}(
    {pk_name}: {pk_type},
    db: Session = Depends(get_db)
):
    """Eliminar {table.name}"""
    success = {table.name}_service.delete(db=db, {pk_name}={pk_name})
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{base_name} no encontrado"
        )
'''
    
    return content

def generar_init_tabla(table: TableConfig, service_config: MultiTableServiceConfig) -> str:
    """Generar __init__.py para una tabla"""
    model_name = table.get_model_name()
    base_name = table.name.title()
    
    content = f'''# ============================================================================
# INIT - {table.name.upper()}
# ============================================================================
"""
Módulo para {table.name}
Parte del servicio: {service_config.service_name}
"""

from .model_{table.name} import {model_name}
from .schema_{table.name} import {base_name}, {base_name}Create, {base_name}Update
from .service_{table.name} import {table.name}_service
from .route_{table.name} import router

__all__ = [
    "{model_name}",
    "{base_name}",
    "{base_name}Create", 
    "{base_name}Update",
    "{table.name}_service",
    "router"
]
'''
    
    return content

def generar_route_config_servicio(service_config: MultiTableServiceConfig) -> str:
    """Generar archivo route_config para todo el servicio"""
    
    # Generar imports de los routers
    imports = []
    router_includes = []
    
    for table in service_config.tables:
        import_name = f"{table.name}_router"
        imports.append(f"from sql_app.Services.{service_config.service_name}.{table.name}.route_{table.name} import router as {import_name}")
        router_includes.append(f"    app.include_router({import_name}, prefix=\"/{service_config.service_name}\")")
    
    imports_text = "\n".join(imports)
    includes_text = "\n".join(router_includes)
    
    content = f'''# ============================================================================
# ROUTE CONFIG - {service_config.service_name.upper()}
# ============================================================================
"""
Configurador de rutas para el servicio: {service_config.service_name}
{service_config.description or "Servicio generado automáticamente"}

Este archivo centraliza la configuración de todas las rutas del servicio.
"""

# Imports de terceros
from fastapi import FastAPI

# Imports del proyecto
{imports_text}

def configure_{service_config.service_name}_routes(app: FastAPI):
    """
    Configura todas las rutas relacionadas con el módulo de {service_config.service_name}
    
    Args:
        app: Instancia de FastAPI donde se registrarán las rutas
    """
    
    # Incluir todos los routers del servicio
{includes_text}
    
    return app
'''
    
    return content
