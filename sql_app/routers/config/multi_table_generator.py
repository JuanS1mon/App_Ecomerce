# ============================================================================
# MULTI_TABLE_GENERATOR.PY - GENERADOR PARA SISTEMAS MULTI-TABLA (FASE 1)
# ============================================================================
"""
Generador especializado para crear modelos y servicios con múltiples tablas relacionadas.
Fase 1: Soporte básico para 2 tablas con relaciones one-to-many y many-to-one.
"""

import os
from typing import Dict, Any, List, Optional
from pathlib import Path
from .generator_config import (
    MultiTableServiceConfig, TableConfig, FieldConfig, RelationshipConfig,
    GENERATOR_CONFIG, MULTI_TABLE_VALIDATOR
)
from .generator_logger import main_logger, GenerationSession
from .generator_factory import BaseGenerator

class MultiTableModelGenerator(BaseGenerator):
    """Generador de modelos SQLAlchemy con relaciones"""
    
    def __init__(self):
        super().__init__('multi_table_models')
        self.logger = main_logger
    
    def generate_content(self, module_name: str, field_names: List[str], field_types: List[str]) -> str:
        """Implementación requerida por BaseGenerator - no usada en multi-tabla"""
        raise NotImplementedError("Use generate_related_models() para generación multi-tabla")
    
    def get_file_path(self, module_name: str) -> str:
        """Implementación requerida por BaseGenerator - no usada en multi-tabla"""
        raise NotImplementedError("Use generate_related_models() para generación multi-tabla")
    
    def generate_related_models(self, service_config: MultiTableServiceConfig) -> Dict[str, Any]:
        """Generar modelos con relaciones para todas las tablas"""
        try:
            with GenerationSession(service_config.service_name, "modelos multi-tabla", self.logger) as session:
                
                # Validar configuración
                errors = MULTI_TABLE_VALIDATOR.validate_service_config(service_config)
                if errors:
                    return {"success": False, "errors": errors}
                
                generated_files = []
                
                # Generar archivo de modelos consolidado
                models_content = self._generate_models_file(service_config)
                models_file_path = self._save_models_file(service_config.service_name, models_content)
                
                if models_file_path:
                    generated_files.append(models_file_path)
                    session.add_generated_file(models_file_path)
                
                # Generar archivo __init__.py para el módulo
                init_content = self._generate_init_file(service_config)
                init_file_path = self._save_init_file(service_config.service_name, init_content)
                
                if init_file_path:
                    generated_files.append(init_file_path)
                    session.add_generated_file(init_file_path)
                
                return {
                    "success": True,
                    "generated_files": generated_files,
                    "service_name": service_config.service_name,
                    "tables_count": len(service_config.tables),
                    "relationships_count": len(service_config.relationships)
                }
                
        except Exception as e:
            self.logger.log_generation_error(e, "generación de modelos multi-tabla")
            return {"success": False, "error": str(e)}
    
    def _generate_models_file(self, service_config: MultiTableServiceConfig) -> str:
        """Generar el contenido del archivo de modelos"""
        
        # Header del archivo
        content = f'''# ============================================================================
# MODELOS MULTI-TABLA: {service_config.service_name.upper()}
# ============================================================================
"""
{service_config.description}

Modelos generados automáticamente con relaciones:
{chr(10).join(f"- {table.name}: {len(table.fields)} campos" for table in service_config.tables)}

Relaciones definidas: {len(service_config.relationships)}
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sql_app.db.database import Base
from datetime import datetime

'''
        
        # Generar cada modelo
        for table in service_config.tables:
            model_content = self._generate_single_model(table, service_config)
            content += model_content + "\n\n"
        
        # Agregar comentario final
        content += f'''# ============================================================================
# FIN DE MODELOS PARA: {service_config.service_name.upper()}
# ============================================================================
'''
        
        return content
    
    def _generate_single_model(self, table: TableConfig, service_config: MultiTableServiceConfig) -> str:
        """Generar un modelo individual"""
        
        model_name = table.get_model_name()
        
        # Inicio de la clase
        content = f'''class {model_name}(Base):
    """
    Modelo para {table.name}
    {table.description or f"Tabla generada automáticamente para {service_config.service_name}"}
    """
    __tablename__ = "{table.name}"
    
'''
        
        # Generar campos
        for field in table.fields:
            field_definition = self._generate_field_definition(field)
            content += f"    {field.name} = {field_definition}\n"
        
        # Agregar relaciones
        relationships = [rel for rel in service_config.relationships 
                        if rel.from_table == table.name or rel.to_table == table.name]
        
        if relationships:
            content += "\n    # Relaciones\n"
            for rel in relationships:
                if rel.from_table == table.name:
                    # Esta tabla es el origen de la relación
                    rel_definition = self._generate_relationship_definition(rel, service_config, is_origin=True)
                    content += f"    {rel.relationship_name} = {rel_definition}\n"
                elif rel.to_table == table.name and rel.back_populates:
                    # Esta tabla es el destino, generar back_populates si existe
                    rel_definition = self._generate_relationship_definition(rel, service_config, is_origin=False)
                    if rel_definition:
                        content += f"    {rel.back_populates} = {rel_definition}\n"
        
        # Método __repr__
        pk_field = table.get_primary_key_field()
        pk_name = pk_field.name if pk_field else "id"
        
        content += f'''
    def __repr__(self):
        return f"<{model_name}({pk_name}={{self.{pk_name}}})">\n'''
        
        return content
    
    def _generate_field_definition(self, field: FieldConfig) -> str:
        """Generar definición de un campo"""
        return field.get_column_definition()
    
    def _generate_relationship_definition(self, rel: RelationshipConfig, 
                                        service_config: MultiTableServiceConfig, 
                                        is_origin: bool) -> str:
        """Generar definición de una relación"""
        
        if is_origin:
            # Relación desde esta tabla hacia otra
            to_table = service_config.get_table_by_name(rel.to_table)
            to_model_name = to_table.get_model_name() if to_table else rel.to_table.title()
            
            if rel.relationship_type == "one_to_many":
                return f'relationship("{to_model_name}", back_populates="{rel.back_populates}")'
            elif rel.relationship_type == "many_to_one":
                return f'relationship("{to_model_name}", back_populates="{rel.back_populates}")'
            elif rel.relationship_type == "one_to_one":
                return f'relationship("{to_model_name}", back_populates="{rel.back_populates}", uselist=False)'
        else:
            # Back reference desde la tabla destino
            from_table = service_config.get_table_by_name(rel.from_table)
            from_model_name = from_table.get_model_name() if from_table else rel.from_table.title()
            
            if rel.relationship_type == "one_to_many":
                return f'relationship("{from_model_name}", back_populates="{rel.relationship_name}")'
            elif rel.relationship_type == "many_to_one":
                return f'relationship("{from_model_name}", back_populates="{rel.relationship_name}", uselist=False)'
            elif rel.relationship_type == "one_to_one":
                return f'relationship("{from_model_name}", back_populates="{rel.relationship_name}")'
        
        return ""
    
    def _generate_init_file(self, service_config: MultiTableServiceConfig) -> str:
        """Generar archivo __init__.py para el módulo"""
        
        imports = []
        for table in service_config.tables:
            model_name = table.get_model_name()
            imports.append(f"from .{service_config.service_name}_models import {model_name}")
        
        content = f'''# ============================================================================
# INIT - MÓDULO {service_config.service_name.upper()}
# ============================================================================
"""
Módulo multi-tabla: {service_config.service_name}
{service_config.description}

Modelos disponibles:
{chr(10).join(f"- {table.get_model_name()}" for table in service_config.tables)}
"""

{chr(10).join(imports)}

__all__ = [{", ".join(f'"{table.get_model_name()}"' for table in service_config.tables)}]
'''
        
        return content
    
    def _save_models_file(self, service_name: str, content: str) -> Optional[str]:
        """Guardar archivo de modelos"""
        try:
            # Crear directorio del servicio
            service_dir = os.path.join(GENERATOR_CONFIG.paths.services, service_name)
            Path(service_dir).mkdir(parents=True, exist_ok=True)
            
            # Guardar archivo de modelos
            models_file = os.path.join(service_dir, f"{service_name}_models.py")
            with open(models_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.logger.log_file_operation("creación de modelos multi-tabla", models_file, True)
            return models_file
            
        except Exception as e:
            self.logger.log_file_operation("creación de modelos multi-tabla", "error", False)
            raise e
    
    def _save_init_file(self, service_name: str, content: str) -> Optional[str]:
        """Guardar archivo __init__.py"""
        try:
            service_dir = os.path.join(GENERATOR_CONFIG.paths.services, service_name)
            init_file = os.path.join(service_dir, "__init__.py")
            
            with open(init_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.logger.log_file_operation("creación de __init__.py", init_file, True)
            return init_file
            
        except Exception as e:
            self.logger.log_file_operation("creación de __init__.py", "error", False)
            raise e


class MultiTableCRUDGeneratorV2(BaseGenerator):
    """Generador de operaciones CRUD para sistemas multi-tabla"""
    
    def __init__(self):
        super().__init__('multi_table_crud')
        self.logger = main_logger
    
    def generate_content(self, module_name: str, field_names: List[str], field_types: List[str]) -> str:
        """Implementación requerida por BaseGenerator - no usada en multi-tabla"""
        raise NotImplementedError("Use generate_related_crud() para generación multi-tabla")
    
    def get_file_path(self, module_name: str) -> str:
        """Implementación requerida por BaseGenerator - no usada en multi-tabla"""
        raise NotImplementedError("Use generate_related_crud() para generación multi-tabla")
    
    def generate_related_crud_NEW_VERSION(self, service_config: MultiTableServiceConfig) -> Dict[str, Any]:
        """Generar operaciones CRUD con queries relacionadas - ESTRUCTURA COMPLETA POR TABLA"""
        
        # ESCRIBIR A UN ARCHIVO PARA CONFIRMAR QUE SE EJECUTA
        with open('C:\\GENERADOR_LOG.txt', 'w') as f:
            f.write(f"NUEVA VERSION EJECUTANDOSE - {service_config.service_name}")
        
        # PRUEBA DIRECTA: Retornar inmediatamente para verificar que este método se ejecuta
        return {
            "success": True,
            "message": "🚀 NUEVA VERSIÓN DEL GENERADOR EJECUTÁNDOSE",
            "generated_files": ["ARCHIVO_DE_PRUEBA"],
            "service_name": service_config.service_name,
            "tables_generated": len(service_config.tables)
        }
    
    def _generate_complete_table_structure(self, table: TableConfig, service_config: MultiTableServiceConfig) -> List[str]:
        """Generar estructura completa para una tabla: model, route, schema, service, __init__"""
        generated_files = []
        
        # Crear directorio de la tabla
        table_dir = os.path.join(GENERATOR_CONFIG.paths.services, service_config.service_name, table.name)
        Path(table_dir).mkdir(parents=True, exist_ok=True)
        
        # 1. Generar modelo individual
        model_content = self._generate_table_model(table, service_config)
        model_file = os.path.join(table_dir, f"model_{table.name}.py")
        self._save_file(model_file, model_content, f"modelo para {table.name}")
        generated_files.append(model_file)
        
        # 2. Generar schema individual
        schema_content = self._generate_table_schema(table, service_config)
        schema_file = os.path.join(table_dir, f"schema_{table.name}.py")
        self._save_file(schema_file, schema_content, f"schema para {table.name}")
        generated_files.append(schema_file)
        
        # 3. Generar service individual (CRUD)
        service_content = self._generate_table_service(table, service_config)
        service_file = os.path.join(table_dir, f"service_{table.name}.py")
        self._save_file(service_file, service_content, f"service para {table.name}")
        generated_files.append(service_file)
        
        # 4. Generar router individual
        route_content = self._generate_table_router(table, service_config)
        route_file = os.path.join(table_dir, f"route_{table.name}.py")
        self._save_file(route_file, route_content, f"router para {table.name}")
        generated_files.append(route_file)
        
        # 5. Generar __init__.py para la tabla
        init_content = self._generate_table_init(table, service_config)
        init_file = os.path.join(table_dir, "__init__.py")
        self._save_file(init_file, init_content, f"__init__.py para {table.name}")
        generated_files.append(init_file)
        
        return generated_files
    
    def _generate_table_model(self, table: TableConfig, service_config: MultiTableServiceConfig) -> str:
        """Generar modelo individual para una tabla"""
        model_name = table.get_model_name()
        
        content = f'''# ============================================================================
# MODELO: {table.name.upper()}
# ============================================================================
"""
Modelo para {table.name}
Parte del servicio: {service_config.service_name}
{table.description or f"Tabla generada automáticamente"}
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey
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
            field_definition = field.get_column_definition()
            content += f"    {field.name} = {field_definition}\n"
        
        # Agregar relaciones
        relationships = [rel for rel in service_config.relationships 
                        if rel.from_table == table.name or rel.to_table == table.name]
        
        if relationships:
            content += "\n    # Relaciones\n"
            for rel in relationships:
                if rel.from_table == table.name:
                    # Esta tabla es el origen de la relación
                    rel_definition = self._generate_relationship_definition(rel, service_config, is_origin=True)
                    content += f"    {rel.relationship_name} = {rel_definition}\n"
                elif rel.to_table == table.name and rel.back_populates:
                    # Esta tabla es el destino, generar back_populates si existe
                    rel_definition = self._generate_relationship_definition(rel, service_config, is_origin=False)
                    if rel_definition:
                        content += f"    {rel.back_populates} = {rel_definition}\n"
        
        # Método __repr__
        pk_field = table.get_primary_key_field()
        pk_name = pk_field.name if pk_field else "id"
        
        content += f'''
    def __repr__(self):
        return f"<{model_name}({pk_name}={{self.{pk_name}}})">\n'''
        
        return content
    
    def _generate_table_schema(self, table: TableConfig, service_config: MultiTableServiceConfig) -> str:
        """Generar schema Pydantic para una tabla"""
        model_name = table.get_model_name()
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

class {base_name}Base(BaseModel):
    """Schema base para {table.name}"""
'''
        
        # Campos para el schema base (sin ID y campos auto-generados)
        for field in table.fields:
            if not field.primary_key and not field.auto_increment:
                field_type = self._get_pydantic_type(field)
                optional = "Optional[" + field_type + "] = None" if field.nullable else field_type
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
            field_type = self._get_pydantic_type(field)
            optional = "Optional[" + field_type + "] = None" if field.nullable else field_type
            content += f"    {field.name}: {optional}\n"
        
        content += f'''

# Alias para compatibilidad
{base_name} = {base_name}InDB
'''
        
        return content
    
    def _generate_table_service(self, table: TableConfig, service_config: MultiTableServiceConfig) -> str:
        """Generar service (CRUD) para una tabla"""
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
    
    def _generate_table_router(self, table: TableConfig, service_config: MultiTableServiceConfig) -> str:
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
    
    def _generate_table_init(self, table: TableConfig, service_config: MultiTableServiceConfig) -> str:
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
    
    def _get_pydantic_type(self, field: FieldConfig) -> str:
        """Convertir tipo de campo a tipo Pydantic"""
        type_mapping = {
            'integer': 'int',
            'int': 'int',
            'string': 'str',
            'str': 'str',
            'text': 'str',
            'float': 'float',
            'decimal': 'float',
            'boolean': 'bool',
            'bool': 'bool',
            'datetime': 'datetime',
            'date': 'datetime',
            'time': 'datetime'
        }
        return type_mapping.get(field.field_type, 'str')
    
    def _save_file(self, file_path: str, content: str, description: str) -> bool:
        """Guardar archivo con logging"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            self.logger.log_file_operation(f"creación de {description}", file_path, True)
            return True
        except Exception as e:
            self.logger.log_file_operation(f"creación de {description}", file_path, False)
            raise e
    
    def _generate_table_crud(self, table: TableConfig, service_config: MultiTableServiceConfig) -> str:
        """Generar operaciones CRUD para una tabla específica"""
        
        model_name = table.get_model_name()
        pk_field = table.get_primary_key_field()
        pk_name = pk_field.name if pk_field else "id"
        pk_type = "int" if pk_field and pk_field.field_type in ["integer", "int"] else "str"
        
        content = f'''# ============================================================================
# CRUD PARA TABLA: {table.name.upper()}
# ============================================================================
"""
Operaciones CRUD para {table.name}
Parte del servicio multi-tabla: {service_config.service_name}
"""

from sqlalchemy.orm import Session
from typing import List, Optional
from ..{service_config.service_name}_models import {model_name}

class {model_name}CRUD:
    """Operaciones CRUD para {model_name}"""
    
    def create(self, db: Session, **kwargs) -> {model_name}:
        """Crear nuevo registro de {table.name}"""
        db_obj = {model_name}(**kwargs)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def get(self, db: Session, {pk_name}: {pk_type}) -> Optional[{model_name}]:
        """Obtener {table.name} por {pk_name}"""
        return db.query({model_name}).filter({model_name}.{pk_name} == {pk_name}).first()
    
    def get_all(self, db: Session, skip: int = 0, limit: int = 100) -> List[{model_name}]:
        """Obtener todos los registros de {table.name}"""
        return db.query({model_name}).offset(skip).limit(limit).all()
    
    def update(self, db: Session, {pk_name}: {pk_type}, **kwargs) -> Optional[{model_name}]:
        """Actualizar {table.name}"""
        db_obj = self.get(db, {pk_name})
        if db_obj:
            for key, value in kwargs.items():
                if hasattr(db_obj, key):
                    setattr(db_obj, key, value)
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

# Instancia global
{table.name}_crud = {model_name}CRUD()
'''
        
        return content
    
    def _generate_relationship_operations(self, service_config: MultiTableServiceConfig) -> str:
        """Generar operaciones especiales para relaciones"""
        
        content = f'''# ============================================================================
# OPERACIONES RELACIONADAS: {service_config.service_name.upper()}
# ============================================================================
"""
Operaciones especializadas para queries con múltiples tablas relacionadas
Servicio: {service_config.service_name}
"""

from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from ..{service_config.service_name}_models import *

class {service_config.service_name.title()}RelationOperations:
    """Operaciones que involucran múltiples tablas relacionadas"""
    
'''
        
        # Generar operaciones específicas según las relaciones
        for rel in service_config.relationships:
            if rel.relationship_type == "one_to_many":
                content += self._generate_one_to_many_operations(rel, service_config)
            elif rel.relationship_type == "many_to_one":
                content += self._generate_many_to_one_operations(rel, service_config)
        
        content += f'''
# Instancia global
{service_config.service_name}_relations = {service_config.service_name.title()}RelationOperations()
'''
        
        return content
    
    def _generate_one_to_many_operations(self, rel: RelationshipConfig, 
                                       service_config: MultiTableServiceConfig) -> str:
        """Generar operaciones para relación one-to-many"""
        
        from_table = service_config.get_table_by_name(rel.from_table)
        to_table = service_config.get_table_by_name(rel.to_table)
        
        from_model = from_table.get_model_name()
        to_model = to_table.get_model_name()
        
        from_pk = from_table.get_primary_key_field()
        from_pk_name = from_pk.name if from_pk else "id"
        from_pk_type = "int" if from_pk and from_pk.field_type in ["integer", "int"] else "str"
        
        content = f'''
    def get_{rel.from_table}_with_{rel.relationship_name}(self, db: Session, {from_pk_name}: {from_pk_type}) -> Optional[{from_model}]:
        """Obtener {rel.from_table} con todos sus {rel.relationship_name}"""
        return db.query({from_model}).options(
            joinedload({from_model}.{rel.relationship_name})
        ).filter({from_model}.{from_pk_name} == {from_pk_name}).first()
    
    def get_{rel.relationship_name}_by_{rel.from_table}(self, db: Session, {from_pk_name}: {from_pk_type}) -> List[{to_model}]:
        """Obtener todos los {rel.relationship_name} de un {rel.from_table} específico"""
        return db.query({to_model}).filter({to_model}.{rel.to_field} == {from_pk_name}).all()
'''
        
        return content
    
    def _generate_many_to_one_operations(self, rel: RelationshipConfig,
                                       service_config: MultiTableServiceConfig) -> str:
        """Generar operaciones para relación many-to-one"""
        
        from_table = service_config.get_table_by_name(rel.from_table)
        to_table = service_config.get_table_by_name(rel.to_table)
        
        from_model = from_table.get_model_name()
        to_model = to_table.get_model_name()
        
        content = f'''
    def get_{rel.from_table}_with_{rel.relationship_name}(self, db: Session) -> List[{from_model}]:
        """Obtener todos los {rel.from_table} con su {rel.relationship_name} asociado"""
        return db.query({from_model}).options(
            joinedload({from_model}.{rel.relationship_name})
        ).all()
'''
        
        return content
    
    def _save_relations_file(self, service_name: str, content: str) -> Optional[str]:
        """Guardar archivo de operaciones relacionadas en el directorio raíz del servicio"""
        try:
            service_dir = os.path.join(GENERATOR_CONFIG.paths.services, service_name)
            Path(service_dir).mkdir(parents=True, exist_ok=True)
            
            relations_file = os.path.join(service_dir, "relations.py")
            with open(relations_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.logger.log_file_operation("creación de operaciones relacionadas", relations_file, True)
            return relations_file
            
        except Exception as e:
            self.logger.log_file_operation("creación de operaciones relacionadas", "error", False)
            raise e


# ============================================================================
# FACTORY PARA GENERADORES MULTI-TABLA
# ============================================================================

class MultiTableGeneratorFactory:
    """Factory para crear generadores multi-tabla"""
    
    @staticmethod
    def create_generator(generator_type: str) -> BaseGenerator:
        """Crear generador especializado para multi-tabla"""
        
        generators = {
            'models': MultiTableModelGenerator,
            'crud': MultiTableCRUDGeneratorV2,
        }
        
        generator_class = generators.get(generator_type)
        if not generator_class:
            raise ValueError(f"Tipo de generador multi-tabla no soportado: {generator_type}")
        
        return generator_class()

# Instancia global
multi_table_factory = MultiTableGeneratorFactory()
