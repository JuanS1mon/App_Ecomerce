# ============================================================================
# GENERAR.PY - GENERADOR DE CÓDIGO MEJORADO (VERSIÓN FUNCIONAL)
# ============================================================================
"""
Generador automático de código para aplicaciones FastAPI.
Sistema refactorizado con arquitectura mejorada, validaciones robustas y logging unificado.
"""

from starlette.responses import FileResponse
import logging
import os
import time
from typing import Dict, Any, List, Optional

from fastapi import APIRouter, Request, status
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
import traceback

# Imports para sistema multi-tabla
from .generator_config import MultiTableServiceConfig, TableConfig, FieldConfig, RelationshipConfig, MULTI_TABLE_VALIDATOR

# Logger básico
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("generador")

templates = Jinja2Templates(directory="sql_app/static")

router = APIRouter(
    include_in_schema=False,  # Oculta todas las rutas de este router en la documentación
    prefix="/generar",
    tags=["generar"],
    responses={status.HTTP_404_NOT_FOUND: {"message": "ruta no encontrada"}}
)

@router.get("/")
async def migraciones_page(request: Request):
    """Endpoint principal del generador"""
    try:
        logger.info("🚀 Acceso a página principal del generador")
        
        # Crear datos de usuario básicos para compatibilidad
        mock_user_data = {
            "user": {"username": "generator_user", "email": "generator@example.com"},
            "user_count": 1,
            "activities": [],
            "is_admin": True,
            "is_authenticated": True
        }
        
        # Verificar si el archivo existe
        template_path = "sql_app/static/html/generar.html"
        if os.path.exists(template_path):
            logger.info(f"✅ Template encontrado: {template_path}")
            
            return templates.TemplateResponse("html/generar.html", {
                "request": request, 
                **mock_user_data
            })
        else:
            logger.error(f"❌ Template file not found: {template_path}")
            
            return HTMLResponse(content="""
            <html>
                <head><title>Generador de Aplicaciones</title></head>
                <body>
                    <h1>🛠️ Generador de Aplicaciones</h1>
                    <p>El archivo generar.html no se encontró en la ruta esperada.</p>
                    <p>Ruta buscada: sql_app/static/html/generar.html</p>
                    <p><a href="/login">Ir al login</a></p>
                </body>
            </html>
            """, status_code=200)
            
    except Exception as e:
        logger.error(f"❌ Error en template: {str(e)}")
        traceback.print_exc()
        
        # Fallback a una respuesta simple en caso de error
        return HTMLResponse(content=f"""
        <html>
            <head><title>Error Temporal</title></head>
            <body>
                <h1>Generador de Aplicaciones</h1>
                <p>Error temporal al cargar la página. Por favor, inténtelo de nuevo.</p>
                <p>Error: {str(e)}</p>
                <p><a href="/login">Ir al login</a></p>
            </body>
        </html>
        """, status_code=200)

# ============================================================================
# VALIDADORES Y UTILITARIOS BÁSICOS
# ============================================================================

def validate_module_name(module_name: str) -> bool:
    """Validar nombre del módulo"""
    if not module_name:
        raise ValueError("❌ El nombre del módulo no puede estar vacío")
    
    if not module_name.replace('_', '').isalnum():
        raise ValueError("❌ El nombre del módulo solo puede contener letras, números y guiones bajos")
    
    if module_name[0].isdigit():
        raise ValueError("❌ El nombre del módulo no puede empezar con un número")
    
    if len(module_name) > 50:
        raise ValueError("❌ El nombre del módulo no puede tener más de 50 caracteres")
    
    return True

def validate_field_data(field_names: List[str], field_types: List[str]) -> bool:
    """Validar datos de campos"""
    if not field_names:
        raise ValueError("❌ Debe especificar al menos un campo")
    
    if len(field_names) != len(field_types):
        raise ValueError(f"❌ Inconsistencia: {len(field_names)} campos vs {len(field_types)} tipos")
    
    allowed_types = {'string', 'str', 'text', 'integer', 'int', 'number', 'float', 'decimal', 
                    'boolean', 'bool', 'datetime', 'date', 'time', 'json', 'dict', 'uuid'}
    
    for i, (field_name, field_type) in enumerate(zip(field_names, field_types)):
        if not field_name.strip():
            raise ValueError(f"❌ El campo {i+1} no puede estar vacío")
        
        if not field_name.replace('_', '').isalnum():
            raise ValueError(f"❌ El campo '{field_name}' contiene caracteres inválidos")
        
        if field_type.lower() not in allowed_types:
            raise ValueError(f"❌ Tipo de campo '{field_type}' no permitido")
    
    return True

# ============================================================================
# GENERADORES BÁSICOS
# ============================================================================

def generate_model_content(module_name: str, field_names: List[str], field_types: List[str]) -> str:
    """Generar contenido del modelo SQLAlchemy"""
    type_mapping = {
        'string': 'String(255)', 'str': 'String(255)', 'text': 'Text',
        'integer': 'Integer', 'int': 'Integer', 'number': 'Integer',
        'float': 'Float', 'decimal': 'Numeric(10, 2)',
        'boolean': 'Boolean', 'bool': 'Boolean',
        'datetime': 'DateTime', 'date': 'Date', 'time': 'Time',
        'json': 'JSON', 'dict': 'JSON', 'uuid': 'String(36)'
    }
    
    model_class = module_name.capitalize()
    
    fields_code = []
    for field_name, field_type in zip(field_names, field_types):
        sql_type = type_mapping.get(field_type.lower(), 'String(255)')
        if field_name.lower() == 'id':
            fields_code.append(f"    {field_name} = Column(Integer, primary_key=True, autoincrement=True)")
        else:
            fields_code.append(f"    {field_name} = Column({sql_type})")
    
    content = f'''from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Float, Numeric, Date, Time, JSON
from sql_app.db.database import Base

class {model_class}(Base):
    __tablename__ = "{module_name.lower()}"
    
{chr(10).join(fields_code)}
    
    def __repr__(self):
        return f"<{model_class}(id={{self.id}})>"
'''
    return content

def generate_schema_content(module_name: str, field_names: List[str], field_types: List[str]) -> str:
    """Generar contenido de esquemas Pydantic"""
    type_mapping = {
        'string': 'str', 'str': 'str', 'text': 'str',
        'integer': 'int', 'int': 'int', 'number': 'int',
        'float': 'float', 'decimal': 'float',
        'boolean': 'bool', 'bool': 'bool',
        'datetime': 'datetime', 'date': 'date', 'time': 'time',
        'json': 'dict', 'dict': 'dict', 'uuid': 'str'
    }
    
    model_class = module_name.capitalize()
    
    base_fields = []
    create_fields = []
    
    for field_name, field_type in zip(field_names, field_types):
        python_type = type_mapping.get(field_type.lower(), 'str')
        
        if field_name.lower() == 'id':
            base_fields.append(f"    {field_name}: int")
        else:
            base_fields.append(f"    {field_name}: {python_type}")
            create_fields.append(f"    {field_name}: {python_type}")
    
    content = f'''from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date, time

class {model_class}Base(BaseModel):
{chr(10).join(create_fields)}

class {model_class}Create({model_class}Base):
    pass

class {model_class}Update(BaseModel):
{chr(10).join(f"    {field}: Optional[{type_mapping.get(ftype.lower(), 'str')}] = None" for field, ftype in zip(field_names, field_types) if field.lower() != 'id')}

class {model_class}InDB({model_class}Base):
{chr(10).join(base_fields)}
    
    class Config:
        from_attributes = True

class {model_class}({model_class}InDB):
    pass
'''
    return content

def generate_crud_content(module_name: str, field_names: List[str], field_types: List[str]) -> str:
    """Generar contenido de CRUD operations"""
    model_class = module_name.capitalize()
    
    content = f'''from sqlalchemy.orm import Session
from typing import List, Optional
from . import models, schemas

def get_{module_name}(db: Session, {module_name}_id: int):
    return db.query(models.{model_class}).filter(models.{model_class}.id == {module_name}_id).first()

def get_{module_name}s(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.{model_class}).offset(skip).limit(limit).all()

def create_{module_name}(db: Session, {module_name}: schemas.{model_class}Create):
    db_obj = models.{model_class}(**{module_name}.dict())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def update_{module_name}(db: Session, {module_name}_id: int, {module_name}: schemas.{model_class}Update):
    db_obj = get_{module_name}(db, {module_name}_id)
    if db_obj:
        update_data = {module_name}.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.commit()
        db.refresh(db_obj)
    return db_obj

def delete_{module_name}(db: Session, {module_name}_id: int):
    db_obj = get_{module_name}(db, {module_name}_id)
    if db_obj:
        db.delete(db_obj)
        db.commit()
    return db_obj
'''
    return content

def generate_router_content(module_name: str, field_names: List[str], field_types: List[str]) -> str:
    """Generar contenido de rutas FastAPI"""
    model_class = module_name.capitalize()
    
    content = f'''from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from sql_app.db.database import get_db
from . import crud, schemas

router = APIRouter(
    prefix="/{module_name}",
    tags=["{module_name}"]
)

@router.post("/", response_model=schemas.{model_class})
def create_{module_name}(
    {module_name}: schemas.{model_class}Create,
    db: Session = Depends(get_db)
):
    return crud.create_{module_name}(db=db, {module_name}={module_name})

@router.get("/", response_model=List[schemas.{model_class}])
def read_{module_name}s(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    return crud.get_{module_name}s(db, skip=skip, limit=limit)

@router.get("/{{item_id}}", response_model=schemas.{model_class})
def read_{module_name}(
    item_id: int,
    db: Session = Depends(get_db)
):
    db_obj = crud.get_{module_name}(db, {module_name}_id=item_id)
    if db_obj is None:
        raise HTTPException(status_code=404, detail="{model_class} not found")
    return db_obj

@router.put("/{{item_id}}", response_model=schemas.{model_class})
def update_{module_name}(
    item_id: int,
    {module_name}: schemas.{model_class}Update,
    db: Session = Depends(get_db)
):
    db_obj = crud.update_{module_name}(db, {module_name}_id=item_id, {module_name}={module_name})
    if db_obj is None:
        raise HTTPException(status_code=404, detail="{model_class} not found")
    return db_obj

@router.delete("/{{item_id}}")
def delete_{module_name}(
    item_id: int,
    db: Session = Depends(get_db)
):
    db_obj = crud.delete_{module_name}(db, {module_name}_id=item_id)
    if db_obj is None:
        raise HTTPException(status_code=404, detail="{model_class} not found")
    return {{"message": "{model_class} deleted successfully"}}
'''
    return content

def save_generated_file(content: str, file_path: str) -> bool:
    """Guardar archivo generado"""
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    except Exception as e:
        logger.error(f"Error saving file {file_path}: {e}")
        return False

@router.post("/generate")
async def generate(request: Request):
    """Endpoint principal para la generación de código"""
    start_time = time.time()

    try:
        # Obtener datos del JSON
        json_data = await request.json()
        module_name = json_data["module_name"]
        field_names = json_data.get("field_names", [])
        field_types = json_data.get("field_types", [])

        # Procesar opciones elegidas por el usuario
        options = {
            'generate_crud': json_data.get('generate_crud', False),
            'generate_route': json_data.get('generate_route', False),
            'generate_schema': json_data.get('generate_schema', False),
            'generate_html_form': json_data.get('generate_html_form', False),
            'generate_tests': json_data.get('generate_tests', False),
            'agregar_rutas': json_data.get('agregar_rutas', False),
            'generate_service': json_data.get('generate_service', False)
        }

        logger.info(f"🚀 Solicitud de generación - Módulo: {module_name}")
        logger.info(f"📋 Opciones: {options}")

        # Validar datos de entrada
        try:
            validate_module_name(module_name)
            validate_field_data(field_names, field_types)
        except ValueError as e:
            return JSONResponse(content={"success": False, "message": str(e)}, status_code=400)

        # Generar archivos según opciones
        generated_files = []
        errors = []

        if options.get('generate_schema', False):
            try:
                schema_content = generate_schema_content(module_name, field_names, field_types)
                schema_path = f"sql_app/db/schemas/{module_name}_schemas.py"
                if save_generated_file(schema_content, schema_path):
                    generated_files.append(schema_path)
                    logger.info(f"✅ Schema generado: {schema_path}")
                else:
                    errors.append(f"Error generando schema en {schema_path}")
            except Exception as e:
                errors.append(f"Error en schema: {str(e)}")

        if options.get('generate_crud', False):
            try:
                crud_content = generate_crud_content(module_name, field_names, field_types)
                crud_path = f"sql_app/db/crud/{module_name}_crud.py"
                if save_generated_file(crud_content, crud_path):
                    generated_files.append(crud_path)
                    logger.info(f"✅ CRUD generado: {crud_path}")
                else:
                    errors.append(f"Error generando CRUD en {crud_path}")
            except Exception as e:
                errors.append(f"Error en CRUD: {str(e)}")

        if options.get('generate_route', False):
            try:
                router_content = generate_router_content(module_name, field_names, field_types)
                router_path = f"sql_app/routers/{module_name}_router.py"
                if save_generated_file(router_content, router_path):
                    generated_files.append(router_path)
                    logger.info(f"✅ Router generado: {router_path}")
                else:
                    errors.append(f"Error generando router en {router_path}")
            except Exception as e:
                errors.append(f"Error en router: {str(e)}")

        # Generar modelo siempre
        try:
            model_content = generate_model_content(module_name, field_names, field_types)
            model_path = f"sql_app/db/models/{module_name}_model.py"
            if save_generated_file(model_content, model_path):
                generated_files.append(model_path)
                logger.info(f"✅ Modelo generado: {model_path}")
            else:
                errors.append(f"Error generando modelo en {model_path}")
        except Exception as e:
            errors.append(f"Error en modelo: {str(e)}")

        # Preparar respuesta
        success = len(generated_files) > 0
        message = f"✅ Generación completada: {len(generated_files)} archivos creados"
        if errors:
            message += f" (con {len(errors)} errores)"

        duration = time.time() - start_time
        logger.info(f"⏱️ Generación completada en {duration:.2f}s")

        return JSONResponse(content={
            "success": success,
            "message": message,
            "details": {
                "generated_files": generated_files,
                "errors": errors,
                "duration": f"{duration:.2f}s"
            }
        })

    except Exception as e:
        logger.error(f"❌ Error en generación: {str(e)}")
        traceback.print_exc()
        return JSONResponse(content={
            "success": False,
            "message": f"Error interno: {str(e)}"
        }, status_code=500)

@router.post("/generate-multi-table")
async def generate_multi_table(request: Request):
    """Endpoint completo para generación de servicios multi-tabla"""
    start_time = time.time()
    
    try:
        # Obtener datos del JSON
        json_data = await request.json()
        
        logger.info(f"🌐 Solicitud multi-tabla recibida")
        logger.info(f"📋 Datos recibidos: {json_data.keys()}")
        
        # Logging detallado para debugging
        logger.info(f"🔍 service_name: {json_data.get('service_name', 'N/A')}")
        logger.info(f"🔍 description: {json_data.get('description', 'N/A')}")
        logger.info(f"🔍 Número de tablas: {len(json_data.get('tables', []))}")
        
        # Importar las clases necesarias
        from .generator_config import MultiTableServiceConfig, TableConfig, FieldConfig, RelationshipConfig, MULTI_TABLE_VALIDATOR
        from .nuevo_generador_multi_tabla import generar_estructura_completa_por_tabla
        
        # Validar estructura JSON básica
        logger.info("🔍 Iniciando validación JSON básica...")
        validation_errors = MULTI_TABLE_VALIDATOR.validate_json_structure(json_data)
        if validation_errors:
            logger.error(f"❌ Errores de validación JSON: {validation_errors}")
            return JSONResponse(content={
                "success": False,
                "message": "❌ Errores de validación JSON",
                "errors": validation_errors
            }, status_code=400)
        
        logger.info("✅ Validación JSON básica completada")
        
        # Crear configuración de servicio
        logger.info("🔍 Creando configuración desde JSON...")
        try:
            service_config = crear_configuracion_desde_json(json_data)
            logger.info("✅ Configuración creada exitosamente")
        except Exception as e:
            logger.error(f"❌ Error creando configuración: {str(e)}")
            logger.error(f"❌ Tipo de error: {type(e).__name__}")
            import traceback
            logger.error(f"❌ Stack trace: {traceback.format_exc()}")
            return JSONResponse(content={
                "success": False,
                "message": f"❌ Error creando configuración: {str(e)}",
                "error_type": type(e).__name__
            }, status_code=400)
        
        # Validar configuración completa
        logger.info("🔍 Validando configuración completa...")
        errors = MULTI_TABLE_VALIDATOR.validate_service_config(service_config)
        if errors:
            logger.error(f"❌ Errores en la configuración del servicio: {errors}")
            return JSONResponse(content={
                "success": False,
                "message": "❌ Errores en la configuración del servicio",
                "errors": errors
            }, status_code=400)
        
        logger.info(f"✅ Configuración validada - Servicio: {service_config.service_name}")
        logger.info(f"📊 Estadísticas: {len(service_config.tables)} tablas, {len(service_config.relationships)} relaciones")
        
        # Generar estructura completa
        result = generar_estructura_completa_por_tabla(service_config)
        
        # Agregar estadísticas adicionales
        if result["success"]:
            # Generar formularios HTML dinámicos
            try:
                html_forms_result = await generate_dynamic_html_forms(service_config)
                result["html_forms"] = html_forms_result
            except Exception as e:
                logger.warning(f"⚠️ No se pudieron generar formularios HTML: {str(e)}")
                result["html_forms"] = {"success": False, "error": str(e)}
            
            # Intentar registrar las rutas automáticamente
            try:
                auto_register_routes_result = await auto_register_generated_routes(service_config)
                result["auto_registration"] = auto_register_routes_result
            except Exception as e:
                logger.warning(f"⚠️ No se pudieron registrar las rutas automáticamente: {str(e)}")
                result["auto_registration"] = {"success": False, "error": str(e)}
            
            # Intentar crear migraciones automáticas
            try:
                auto_migration_result = await auto_create_database_migrations(service_config)
                result["auto_migration"] = auto_migration_result
            except Exception as e:
                logger.warning(f"⚠️ No se pudieron crear migraciones automáticas: {str(e)}")
                result["auto_migration"] = {"success": False, "error": str(e)}
            
            duration = time.time() - start_time
            result["duration"] = f"{duration:.2f}s"
            result["timestamp"] = time.strftime("%Y-%m-%d %H:%M:%S")
            
            logger.info(f"🎉 Generación multi-tabla completada en {duration:.2f}s")
        
        return JSONResponse(content=result)
        
    except Exception as e:
        logger.error(f"❌ Error en generación multi-tabla: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return JSONResponse(content={
            "success": False,
            "message": f"Error interno en generación multi-tabla: {str(e)}",
            "error_type": type(e).__name__
        }, status_code=500)


def crear_configuracion_desde_json(json_data: dict) -> MultiTableServiceConfig:
    """Crear configuración multi-tabla desde JSON"""
    from .generator_config import MultiTableServiceConfig, TableConfig, FieldConfig, RelationshipConfig
    
    # Crear configuración de tablas
    tables = []
    for table_data in json_data.get('tables', []):
        # Crear campos
        fields = []
        for field_data in table_data.get('fields', []):
            field = FieldConfig(
                name=field_data['name'],
                field_type=field_data['field_type'],
                max_length=field_data.get('max_length'),
                nullable=field_data.get('nullable', True),
                unique=field_data.get('unique', False),
                primary_key=field_data.get('primary_key', False),
                auto_increment=field_data.get('auto_increment', False),
                default_value=field_data.get('default_value'),
                foreign_key=field_data.get('foreign_key'),
                index=field_data.get('index', False)
            )
            fields.append(field)
        
        # Crear tabla
        table = TableConfig(
            name=table_data['name'],
            fields=fields,
            description=table_data.get('description')
        )
        tables.append(table)
    
    # Crear configuración de relaciones
    relationships = []
    for rel_data in json_data.get('relationships', []):
        relationship = RelationshipConfig(
            relationship_type=rel_data['relationship_type'],
            from_table=rel_data['from_table'],
            from_field=rel_data['from_field'],
            to_table=rel_data['to_table'],
            to_field=rel_data['to_field'],
            relationship_name=rel_data.get('relationship_name', f"{rel_data['to_table']}_rel"),
            back_populates=rel_data.get('back_populates')
        )
        relationships.append(relationship)
    
    # Crear configuración del servicio
    service_config = MultiTableServiceConfig(
        service_name=json_data['service_name'],
        description=json_data['description'],
        tables=tables,
        relationships=relationships
    )
    
    return service_config


async def auto_register_generated_routes(service_config: MultiTableServiceConfig) -> Dict[str, Any]:
    """Registrar automáticamente las rutas generadas en main.py"""
    try:
        import os
        
        # Leer main.py actual
        main_py_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "main.py")
        
        if not os.path.exists(main_py_path):
            return {"success": False, "error": "main.py no encontrado"}
        
        with open(main_py_path, 'r', encoding='utf-8') as f:
            main_content = f.read()
        
        # Generar imports y registros para las rutas
        route_imports = []
        route_registrations = []
        
        for table in service_config.tables:
            import_line = f"from sql_app.Services.{service_config.service_name}.{table.name}.route_{table.name} import router as {table.name}_router"
            registration_line = f"app.include_router({table.name}_router, prefix=\"/{service_config.service_name}\")"
            
            route_imports.append(import_line)
            route_registrations.append(registration_line)
        
        # Agregar marcador si no existe
        marker_start = f"# === AUTO-GENERATED ROUTES FOR {service_config.service_name.upper()} === START"
        marker_end = f"# === AUTO-GENERATED ROUTES FOR {service_config.service_name.upper()} === END"
        
        if marker_start not in main_content:
            # Buscar donde insertar las rutas (después de las otras inclusiones)
            insert_point = main_content.find("# Incluir routers")
            if insert_point == -1:
                insert_point = main_content.find("app.include_router")
                if insert_point == -1:
                    insert_point = len(main_content)
            
            # Insertar imports al inicio del archivo (después de los otros imports)
            import_insert_point = main_content.rfind("from sql_app.routers")
            if import_insert_point != -1:
                import_insert_point = main_content.find("\n", import_insert_point) + 1
            else:
                import_insert_point = main_content.find("from fastapi import")
                if import_insert_point != -1:
                    import_insert_point = main_content.find("\n", import_insert_point) + 1
                else:
                    import_insert_point = 0
            
            # Construir nuevo contenido
            new_imports = "\n".join(route_imports) + "\n"
            new_registrations = f"\n{marker_start}\n" + "\n".join(route_registrations) + f"\n{marker_end}\n"
            
            new_content = (
                main_content[:import_insert_point] + 
                new_imports + 
                main_content[import_insert_point:insert_point] + 
                new_registrations + 
                main_content[insert_point:]
            )
            
            # Guardar archivo modificado
            with open(main_py_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            return {
                "success": True,
                "message": f"Rutas registradas automáticamente en main.py",
                "routes_added": len(route_registrations)
            }
        else:
            return {
                "success": False,
                "message": f"Rutas para {service_config.service_name} ya están registradas"
            }
    
    except Exception as e:
        return {"success": False, "error": str(e)}


async def auto_create_database_migrations(service_config: MultiTableServiceConfig) -> Dict[str, Any]:
    """Crear migraciones automáticas para los modelos generados"""
    try:
        import os
        import importlib.util
        
        # Intentar importar los modelos generados para crear las tablas
        models_imported = []
        
        for table in service_config.tables:
            try:
                # Construir ruta al modelo
                model_path = os.path.join(
                    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                    "Services",
                    service_config.service_name,
                    table.name,
                    f"model_{table.name}.py"
                )
                
                if os.path.exists(model_path):
                    # Importar dinámicamente el modelo
                    spec = importlib.util.spec_from_file_location(f"{table.name}_model", model_path)
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    
                    models_imported.append(table.name)
                    logger.info(f"📦 Modelo {table.name} importado para migración")
                
            except Exception as e:
                logger.warning(f"⚠️ No se pudo importar modelo {table.name}: {str(e)}")
        
        if models_imported:
            # Intentar crear las tablas usando SQLAlchemy
            try:
                from sql_app.db.database import engine, Base
                
                # Esto creará las tablas si no existen
                Base.metadata.create_all(bind=engine)
                
                return {
                    "success": True,
                    "message": f"Tablas creadas automáticamente en la base de datos",
                    "tables_created": models_imported
                }
                
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Error creando tablas en BD: {str(e)}",
                    "models_imported": models_imported
                }
        
        return {
            "success": False,
            "error": "No se pudieron importar los modelos generados"
        }
    
    except Exception as e:
        return {"success": False, "error": str(e)}


async def generate_dynamic_html_forms(service_config: MultiTableServiceConfig) -> Dict[str, Any]:
    """Generar formularios HTML dinámicos que apunten a las rutas generadas"""
    try:
        import os
        from pathlib import Path
        
        generated_forms = []
        
        # Crear directorio para formularios si no existe
        forms_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "static", "html", "forms", service_config.service_name
        )
        Path(forms_dir).mkdir(parents=True, exist_ok=True)
        
        for table in service_config.tables:
            # Generar formulario para cada tabla
            form_content = generate_table_form_html(table, service_config)
            form_file_path = os.path.join(forms_dir, f"{table.name}_form.html")
            
            with open(form_file_path, 'w', encoding='utf-8') as f:
                f.write(form_content)
            
            generated_forms.append(form_file_path)
            logger.info(f"📄 Formulario HTML creado: {form_file_path}")
        
        # Generar página de índice con todos los formularios
        index_content = generate_service_index_html(service_config)
        index_file_path = os.path.join(forms_dir, "index.html")
        
        with open(index_file_path, 'w', encoding='utf-8') as f:
            f.write(index_content)
        
        generated_forms.append(index_file_path)
        
        return {
            "success": True,
            "generated_forms": generated_forms,
            "forms_count": len(service_config.tables),
            "base_url": f"/static/html/forms/{service_config.service_name}/"
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}


def generate_table_form_html(table: TableConfig, service_config: MultiTableServiceConfig) -> str:
    """Generar formulario HTML para una tabla específica"""
    table_title = table.name.replace('_', ' ').title()
    model_name = table.get_model_name()
    
    # Generar campos del formulario
    form_fields = []
    for field in table.fields:
        if field.primary_key or field.auto_increment:
            continue  # Skip campos auto-generados
        
        field_html = generate_form_field_html(field)
        form_fields.append(field_html)
    
    form_fields_html = "\n".join(form_fields)
    
    content = f'''<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{table_title} - {service_config.service_name}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        body {{ 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }}
        .main-container {{
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
            backdrop-filter: blur(10px);
            margin: 20px;
            padding: 30px;
        }}
        .btn-custom {{
            background: linear-gradient(45deg, #667eea, #764ba2);
            border: none;
            color: white;
            padding: 12px 30px;
            border-radius: 25px;
            font-weight: 600;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        }}
        .btn-custom:hover {{
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(102, 126, 234, 0.6);
            color: white;
        }}
        .form-control {{
            border: 2px solid #e9ecef;
            border-radius: 10px;
            padding: 12px 15px;
            transition: all 0.3s ease;
        }}
        .form-control:focus {{
            border-color: #667eea;
            box-shadow: 0 0 0 0.2rem rgba(102, 126, 234, 0.25);
        }}
        .alert {{
            border: none;
            border-radius: 15px;
            padding: 20px;
        }}
    </style>
</head>
<body>
    <div class="container-fluid">
        <div class="main-container">
            <!-- Header -->
            <div class="text-center mb-4">
                <h1 class="display-5 text-primary mb-3">
                    <i class="fas fa-edit me-3"></i>{table_title}
                </h1>
                <p class="lead text-muted">Formulario para gestión de {table.description or table_title}</p>
                <div class="d-flex justify-content-center gap-2 mb-3">
                    <a href="index.html" class="btn btn-outline-secondary btn-sm">
                        <i class="fas fa-arrow-left me-1"></i>Volver al índice
                    </a>
                    <a href="/{service_config.service_name}/{table.name}/" target="_blank" class="btn btn-outline-info btn-sm">
                        <i class="fas fa-external-link-alt me-1"></i>Ver API
                    </a>
                </div>
            </div>

            <!-- Formulario -->
            <div class="row justify-content-center">
                <div class="col-lg-8">
                    <div class="card border-0 shadow-lg">
                        <div class="card-header bg-primary text-white">
                            <h5 class="mb-0">
                                <i class="fas fa-plus-circle me-2"></i>Crear nuevo {table_title}
                            </h5>
                        </div>
                        <div class="card-body">
                            <form id="{table.name}Form">
                                {form_fields_html}
                                
                                <div class="row mt-4">
                                    <div class="col-md-6">
                                        <button type="submit" class="btn btn-custom w-100">
                                            <i class="fas fa-save me-2"></i>Guardar
                                        </button>
                                    </div>
                                    <div class="col-md-6">
                                        <button type="reset" class="btn btn-outline-secondary w-100">
                                            <i class="fas fa-undo me-2"></i>Limpiar
                                        </button>
                                    </div>
                                </div>
                            </form>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Lista existente -->
            <div class="row mt-5">
                <div class="col-12">
                    <div class="card border-0 shadow-lg">
                        <div class="card-header bg-info text-white d-flex justify-content-between align-items-center">
                            <h5 class="mb-0">
                                <i class="fas fa-list me-2"></i>Registros existentes
                            </h5>
                            <button id="refresh-btn" class="btn btn-light btn-sm">
                                <i class="fas fa-sync-alt me-1"></i>Actualizar
                            </button>
                        </div>
                        <div class="card-body">
                            <div id="loading" class="text-center py-4" style="display: none;">
                                <div class="spinner-border" role="status">
                                    <span class="visually-hidden">Cargando...</span>
                                </div>
                            </div>
                            <div id="data-table" class="table-responsive">
                                <!-- La tabla se cargará dinámicamente -->
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Alertas -->
            <div id="alerts-container" class="mt-3"></div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        const API_BASE = '/{service_config.service_name}/{table.name}';
        
        // Manejar envío del formulario
        document.getElementById('{table.name}Form').addEventListener('submit', async function(e) {{
            e.preventDefault();
            
            const formData = new FormData(this);
            const data = {{}};
            
            for (let [key, value] of formData.entries()) {{
                // Convertir tipos según sea necesario
                if (value === '') {{
                    data[key] = null;
                }} else {{
                    data[key] = value;
                }}
            }}
            
            try {{
                showLoading(true);
                const response = await fetch(API_BASE + '/', {{
                    method: 'POST',
                    headers: {{
                        'Content-Type': 'application/json',
                    }},
                    body: JSON.stringify(data)
                }});
                
                if (response.ok) {{
                    showAlert('Registro creado exitosamente', 'success');
                    this.reset();
                    loadData();
                }} else {{
                    const errorData = await response.json();
                    showAlert('Error: ' + (errorData.detail || 'Error desconocido'), 'danger');
                }}
            }} catch (error) {{
                showAlert('Error de conexión: ' + error.message, 'danger');
            }} finally {{
                showLoading(false);
            }}
        }});
        
        // Cargar datos existentes
        async function loadData() {{
            try {{
                showLoading(true);
                const response = await fetch(API_BASE + '/');
                
                if (response.ok) {{
                    const data = await response.json();
                    displayData(data);
                }} else {{
                    showAlert('Error cargando datos', 'warning');
                }}
            }} catch (error) {{
                showAlert('Error de conexión al cargar datos', 'warning');
            }} finally {{
                showLoading(false);
            }}
        }}
        
        // Mostrar datos en tabla
        function displayData(data) {{
            const container = document.getElementById('data-table');
            
            if (!data || data.length === 0) {{
                container.innerHTML = '<p class="text-muted text-center py-4">No hay registros disponibles</p>';
                return;
            }}
            
            const headers = Object.keys(data[0]);
            let tableHTML = `
                <table class="table table-hover">
                    <thead class="table-dark">
                        <tr>
                            ${{headers.map(h => `<th>${{h.replace('_', ' ').toUpperCase()}}</th>`).join('')}}
                            <th>Acciones</th>
                        </tr>
                    </thead>
                    <tbody>
            `;
            
            data.forEach(row => {{
                tableHTML += '<tr>';
                headers.forEach(header => {{
                    let value = row[header];
                    if (value === null || value === undefined) value = '-';
                    if (typeof value === 'boolean') value = value ? 'Sí' : 'No';
                    tableHTML += `<td>${{value}}</td>`;
                }});
                tableHTML += `
                    <td>
                        <button class="btn btn-sm btn-outline-primary me-1" onclick="editRecord(${{row.id || row[headers[0]]}})">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-danger" onclick="deleteRecord(${{row.id || row[headers[0]]}})">
                            <i class="fas fa-trash"></i>
                        </button>
                    </td>
                </tr>`;
            }});
            
            tableHTML += '</tbody></table>';
            container.innerHTML = tableHTML;
        }}
        
        // Funciones de utilidad
        function showAlert(message, type = 'info') {{
            const container = document.getElementById('alerts-container');
            const alert = document.createElement('div');
            alert.className = `alert alert-${{type}} alert-dismissible fade show`;
            alert.innerHTML = `
                ${{message}}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            `;
            container.appendChild(alert);
            
            setTimeout(() => alert.remove(), 5000);
        }}
        
        function showLoading(show) {{
            document.getElementById('loading').style.display = show ? 'block' : 'none';
        }}
        
        async function editRecord(id) {{
            // Implementar edición
            showAlert('Función de edición en desarrollo', 'info');
        }}
        
        async function deleteRecord(id) {{
            if (confirm('¿Está seguro de eliminar este registro?')) {{
                try {{
                    const response = await fetch(API_BASE + `/${{id}}`, {{
                        method: 'DELETE'
                    }});
                    
                    if (response.ok) {{
                        showAlert('Registro eliminado exitosamente', 'success');
                        loadData();
                    }} else {{
                        showAlert('Error al eliminar registro', 'danger');
                    }}
                }} catch (error) {{
                    showAlert('Error de conexión', 'danger');
                }}
            }}
        }}
        
        // Evento del botón refrescar
        document.getElementById('refresh-btn').addEventListener('click', loadData);
        
        // Cargar datos al inicio
        document.addEventListener('DOMContentLoaded', loadData);
    </script>
</body>
</html>'''
    
    return content


def generate_form_field_html(field: FieldConfig) -> str:
    """Generar HTML para un campo del formulario"""
    field_label = field.name.replace('_', ' ').title()
    field_id = f"field_{field.name}"
    
    # Determinar tipo de input
    input_type = "text"
    input_html = ""
    
    if field.field_type in ['integer', 'int', 'bigint', 'smallint']:
        input_type = "number"
        input_html = f'<input type="{input_type}" class="form-control" id="{field_id}" name="{field.name}" {"required" if not field.nullable else ""}>'
    elif field.field_type in ['float', 'decimal', 'currency']:
        input_type = "number"
        step = "0.01" if field.field_type in ['decimal', 'currency'] else "any"
        input_html = f'<input type="{input_type}" step="{step}" class="form-control" id="{field_id}" name="{field.name}" {"required" if not field.nullable else ""}>'
    elif field.field_type in ['boolean', 'bool']:
        input_html = f'''
        <div class="form-check">
            <input type="checkbox" class="form-check-input" id="{field_id}" name="{field.name}" value="true">
            <label class="form-check-label" for="{field_id}">{field_label}</label>
        </div>'''
        return f'<div class="mb-3">{input_html}</div>'
    elif field.field_type in ['datetime', 'date']:
        input_type = "datetime-local" if field.field_type == 'datetime' else "date"
        input_html = f'<input type="{input_type}" class="form-control" id="{field_id}" name="{field.name}" {"required" if not field.nullable else ""}>'
    elif field.field_type == 'time':
        input_html = f'<input type="time" class="form-control" id="{field_id}" name="{field.name}" {"required" if not field.nullable else ""}>'
    elif field.field_type in ['text', 'longtext']:
        input_html = f'<textarea class="form-control" id="{field_id}" name="{field.name}" rows="4" {"required" if not field.nullable else ""}></textarea>'
    elif field.field_type == 'email':
        input_html = f'<input type="email" class="form-control" id="{field_id}" name="{field.name}" {"required" if not field.nullable else ""}>'
    elif field.field_type == 'url':
        input_html = f'<input type="url" class="form-control" id="{field_id}" name="{field.name}" {"required" if not field.nullable else ""}>'
    elif field.field_type == 'phone':
        input_html = f'<input type="tel" class="form-control" id="{field_id}" name="{field.name}" {"required" if not field.nullable else ""}>'
    elif field.field_type == 'color':
        input_html = f'<input type="color" class="form-control form-control-color" id="{field_id}" name="{field.name}" {"required" if not field.nullable else ""}>'
    elif field.enum_values:
        options = "\\n".join([f'<option value="{val}">{val}</option>' for val in field.enum_values])
        input_html = f'''<select class="form-select" id="{field_id}" name="{field.name}" {"required" if not field.nullable else ""}>
            <option value="">Seleccionar...</option>
            {options}
        </select>'''
    else:
        # Default: text input
        max_length = f'maxlength="{field.max_length}"' if field.max_length else ""
        input_html = f'<input type="text" class="form-control" id="{field_id}" name="{field.name}" {max_length} {"required" if not field.nullable else ""}>'
    
    help_text = ""
    if field.description:
        help_text = f'<div class="form-text">{field.description}</div>'
    
    return f'''
    <div class="mb-3">
        <label for="{field_id}" class="form-label">{field_label}</label>
        {input_html}
        {help_text}
    </div>'''


def generate_service_index_html(service_config: MultiTableServiceConfig) -> str:
    """Generar página de índice para el servicio con enlaces a todos los formularios"""
    
    # Generar tarjetas para cada tabla
    table_cards = []
    for table in service_config.tables:
        table_title = table.name.replace('_', ' ').title()
        card_html = f'''
        <div class="col-md-6 col-lg-4 mb-4">
            <div class="card h-100 border-0 shadow-sm hover-card">
                <div class="card-body text-center">
                    <div class="mb-3">
                        <i class="fas fa-table text-primary" style="font-size: 2rem;"></i>
                    </div>
                    <h5 class="card-title">{table_title}</h5>
                    <p class="card-text text-muted">{table.description or f"Gestión de {table_title}"}</p>
                    <p class="small text-info">{len(table.fields)} campos configurados</p>
                </div>
                <div class="card-footer bg-transparent text-center">
                    <a href="{table.name}_form.html" class="btn btn-primary btn-sm">
                        <i class="fas fa-edit me-1"></i>Gestionar
                    </a>
                    <a href="/{service_config.service_name}/{table.name}/" target="_blank" class="btn btn-outline-secondary btn-sm ms-1">
                        <i class="fas fa-code me-1"></i>API
                    </a>
                </div>
            </div>
        </div>'''
        table_cards.append(card_html)
    
    tables_html = "\\n".join(table_cards)
    
    content = f'''<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{service_config.service_name.title()} - Índice de Gestión</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        body {{ 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }}
        .main-container {{
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
            backdrop-filter: blur(10px);
            margin: 20px;
            padding: 30px;
        }}
        .hover-card {{
            transition: all 0.3s ease;
        }}
        .hover-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15) !important;
        }}
        .stats-card {{
            background: linear-gradient(45deg, #667eea, #764ba2);
            color: white;
            border-radius: 15px;
        }}
    </style>
</head>
<body>
    <div class="container-fluid">
        <div class="main-container">
            <!-- Header -->
            <div class="text-center mb-5">
                <h1 class="display-4 text-primary mb-3">
                    <i class="fas fa-cogs me-3"></i>{service_config.service_name.title()}
                </h1>
                <p class="lead text-muted">{service_config.description}</p>
                <div class="d-flex justify-content-center gap-2">
                    <a href="/admin" class="btn btn-outline-secondary">
                        <i class="fas fa-arrow-left me-1"></i>Panel Admin
                    </a>
                    <a href="/docs" target="_blank" class="btn btn-outline-info">
                        <i class="fas fa-book me-1"></i>Documentación API
                    </a>
                </div>
            </div>

            <!-- Estadísticas -->
            <div class="row mb-5">
                <div class="col-md-4 mb-3">
                    <div class="card stats-card text-center">
                        <div class="card-body">
                            <i class="fas fa-table fa-2x mb-2"></i>
                            <h3 class="mb-0">{len(service_config.tables)}</h3>
                            <p class="mb-0">Tablas</p>
                        </div>
                    </div>
                </div>
                <div class="col-md-4 mb-3">
                    <div class="card stats-card text-center">
                        <div class="card-body">
                            <i class="fas fa-link fa-2x mb-2"></i>
                            <h3 class="mb-0">{len(service_config.relationships)}</h3>
                            <p class="mb-0">Relaciones</p>
                        </div>
                    </div>
                </div>
                <div class="col-md-4 mb-3">
                    <div class="card stats-card text-center">
                        <div class="card-body">
                            <i class="fas fa-database fa-2x mb-2"></i>
                            <h3 class="mb-0">{sum(len(table.fields) for table in service_config.tables)}</h3>
                            <p class="mb-0">Campos Total</p>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Tablas disponibles -->
            <div class="mb-4">
                <h2 class="text-center mb-4">
                    <i class="fas fa-table me-2"></i>Gestión de Datos
                </h2>
            </div>

            <div class="row">
                {tables_html}
            </div>

            <!-- Footer -->
            <div class="text-center mt-5 pt-4 border-top">
                <p class="text-muted">
                    <i class="fas fa-info-circle me-1"></i>
                    Servicio generado automáticamente • 
                    <small>Versión {service_config.version or "1.0.0"}</small>
                </p>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>'''
    
    return content

@router.get("/multi-table-example")
async def get_multi_table_example():
    """Endpoint que devuelve un ejemplo de JSON para configuración multi-tabla"""
    
    example_config = {
        "service_name": "biblioteca_sistema",
        "description": "Sistema básico de gestión de biblioteca con autores y libros",
        "tables": [
            {
                "name": "autores",
                "description": "Tabla de autores",
                "fields": [
                    {"name": "id", "field_type": "integer", "primary_key": True},
                    {"name": "nombre", "field_type": "string", "max_length": 100},
                    {"name": "email", "field_type": "string", "max_length": 150}
                ]
            },
            {
                "name": "libros", 
                "description": "Tabla de libros",
                "fields": [
                    {"name": "id", "field_type": "integer", "primary_key": True},
                    {"name": "titulo", "field_type": "string", "max_length": 200},
                    {"name": "autor_id", "field_type": "integer", "foreign_key": "autores.id"}
                ]
            }
        ],
        "relationships": [
            {
                "relationship_type": "one_to_many",
                "from_table": "autores",
                "from_field": "id", 
                "to_table": "libros",
                "to_field": "autor_id"
            }
        ]
    }
    
    return JSONResponse(content={
        "success": True,
        "example": example_config,
        "description": "Ejemplo de configuración JSON para sistema multi-tabla",
        "instructions": [
            "1. Copia este JSON y modifícalo según tus necesidades",
            "2. Envía el JSON modificado al endpoint POST /generar/generate-multi-table",
            "3. Esta funcionalidad está en desarrollo"
        ]
    })

# ============================================================================
# FUNCIONES DE UTILIDAD ADICIONALES
# ============================================================================

def generate_html_form(module_name: str, field_names: List[str], field_types: List[str]) -> str:
    """Generar formulario HTML básico"""
    model_class = module_name.capitalize()
    
    form_fields = []
    for field_name, field_type in zip(field_names, field_types):
        if field_name.lower() == 'id':
            continue
            
        input_type = "text"
        if field_type.lower() in ['integer', 'int', 'number']:
            input_type = "number"
        elif field_type.lower() in ['boolean', 'bool']:
            input_type = "checkbox"
        elif field_type.lower() in ['datetime', 'date']:
            input_type = "date"
        elif field_type.lower() == 'time':
            input_type = "time"
        elif field_type.lower() in ['text']:
            form_fields.append(f'''
            <div class="mb-3">
                <label for="{field_name}" class="form-label">{field_name.replace('_', ' ').title()}</label>
                <textarea class="form-control" id="{field_name}" name="{field_name}" rows="3"></textarea>
            </div>''')
            continue
            
        form_fields.append(f'''
            <div class="mb-3">
                <label for="{field_name}" class="form-label">{field_name.replace('_', ' ').title()}</label>
                <input type="{input_type}" class="form-control" id="{field_name}" name="{field_name}">
            </div>''')
    
    html_content = f'''<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Formulario {model_class}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <div class="container mt-4">
        <h2>Formulario {model_class}</h2>
        <form id="{module_name}Form">
            {''.join(form_fields)}
            <button type="submit" class="btn btn-primary">Guardar</button>
        </form>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        document.getElementById('{module_name}Form').addEventListener('submit', function(e) {{
            e.preventDefault();
            // Aquí puedes agregar la lógica para enviar los datos
            alert('Formulario enviado (funcionalidad pendiente)');
        }});
    </script>
</body>
</html>'''
    return html_content

# ============================================================================
# EXPLORADOR DE TABLAS DINÁMICAS - NUEVA FUNCIONALIDAD
# ============================================================================

from sqlalchemy import inspect, text
from typing import Dict, List, Any, Optional
from sql_app.db.database import get_db, engine

# Tablas core del sistema que NO deben mostrarse en el explorador
CORE_TABLES = {
    # Tablas de autenticación y usuarios (en minúsculas para comparación)
    'usuarios', 'usuario_roles', 'roles', 'permisos', 'user_sessions', 'tokens',
    'sesiones', 'auth_sessions',
    
    # Tablas de sistema y administración  
    'alembic_version', 'migrations', 'system_config', 'app_config',
    
    # Tablas de logs y auditoría
    'activity_log', 'logs', 'audit_logs', 'security_logs', 'system_logs',
    
    # Tablas de comunicación del sistema
    'tickets', 'mensajes', 'chat_rooms', 'chat_messages', 'chat_members',
    
    # Tablas de métricas y KPIs del sistema
    'resultados_kpi',
    
    # Tablas temporales y cache
    'cache', 'temp_data'
}

@router.get("/list-tables")
async def list_dynamic_tables():
    """Listar todas las tablas dinámicas (excluyendo core tables)"""
    try:
        inspector = inspect(engine)
        all_tables = inspector.get_table_names()
        
        # Filtrar tablas core
        dynamic_tables = []
        
        for table_name in all_tables:
            if table_name.lower() not in CORE_TABLES:
                # Obtener información básica de la tabla
                try:
                    with engine.connect() as conn:
                        # Contar registros
                        count_result = conn.execute(text(f"SELECT COUNT(*) FROM [{table_name}]"))
                        record_count = count_result.scalar()
                        
                        # Obtener columnas
                        columns = inspector.get_columns(table_name)
                        column_count = len(columns)
                        
                        # Información de la tabla
                        table_info = {
                            "name": table_name,
                            "record_count": record_count,
                            "column_count": column_count,
                            "columns": [{"name": col["name"], "type": str(col["type"])} for col in columns[:5]]  # Primeras 5 columnas
                        }
                        dynamic_tables.append(table_info)
                        
                except Exception as e:
                    logger.warning(f"Error al obtener info de tabla {table_name}: {e}")
                    continue
        
        return JSONResponse(content={
            "success": True,
            "message": f"✅ Se encontraron {len(dynamic_tables)} tablas dinámicas",
            "tables": dynamic_tables,
            "total_count": len(dynamic_tables)
        })
        
    except Exception as e:
        logger.error(f"❌ Error al listar tablas: {str(e)}")
        return JSONResponse(content={
            "success": False,
            "message": f"Error al obtener tablas: {str(e)}"
        }, status_code=500)

@router.get("/table-content/{table_name}")
async def get_table_content(table_name: str, page: int = 1, limit: int = 50):
    """Obtener contenido de una tabla específica con paginación"""
    try:
        # Validar que la tabla no sea core
        if table_name.lower() in CORE_TABLES:
            return JSONResponse(content={
                "success": False,
                "message": f"❌ Acceso denegado a tabla core: {table_name}"
            }, status_code=403)
        
        # Validar que la tabla existe
        inspector = inspect(engine)
        if table_name not in inspector.get_table_names():
            return JSONResponse(content={
                "success": False,
                "message": f"❌ Tabla '{table_name}' no encontrada"
            }, status_code=404)
        
        offset = (page - 1) * limit
        
        with engine.connect() as conn:
            # Obtener total de registros
            count_result = conn.execute(text(f"SELECT COUNT(*) FROM [{table_name}]"))
            total_records = count_result.scalar()
            
            # Obtener datos paginados
            data_result = conn.execute(text(f"SELECT * FROM [{table_name}] ORDER BY 1 OFFSET {offset} ROWS FETCH NEXT {limit} ROWS ONLY"))
            
            # Convertir resultados a lista de diccionarios
            columns = list(data_result.keys())  # Convertir a lista para poder usar índices
            rows = []
            for row in data_result:
                row_dict = {}
                for i, value in enumerate(row):
                    # Convertir tipos no serializables
                    if hasattr(value, 'isoformat'):  # datetime
                        row_dict[columns[i]] = value.isoformat()
                    elif value is None:
                        row_dict[columns[i]] = None
                    else:
                        row_dict[columns[i]] = str(value)
                rows.append(row_dict)
            
            # Calcular metadatos de paginación
            total_pages = (total_records + limit - 1) // limit
            has_next = page < total_pages
            has_prev = page > 1
            
            # Mensaje adaptado según si hay datos o no
            if total_records == 0:
                message = f"📋 Tabla '{table_name}' está vacía (sin registros)"
            else:
                message = f"✅ Datos de tabla '{table_name}' obtenidos ({total_records} registros)"
            
            return JSONResponse(content={
                "success": True,
                "message": message,
                "table_name": table_name,
                "data": rows,
                "pagination": {
                    "page": page,
                    "limit": limit,
                    "total_records": total_records,
                    "total_pages": total_pages,
                    "has_next": has_next,
                    "has_prev": has_prev
                },
                "columns": columns,
                "is_empty": total_records == 0
            })
            
    except Exception as e:
        logger.error(f"❌ Error al obtener contenido de tabla {table_name}: {str(e)}")
        return JSONResponse(content={
            "success": False,
            "message": f"Error al obtener datos: {str(e)}"
        }, status_code=500)

@router.get("/table-schema/{table_name}")
async def get_table_schema(table_name: str):
    """Obtener esquema detallado de una tabla"""
    try:
        # Validar que la tabla no sea core
        if table_name.lower() in CORE_TABLES:
            return JSONResponse(content={
                "success": False,
                "message": f"❌ Acceso denegado a tabla core: {table_name}"
            }, status_code=403)
        
        inspector = inspect(engine)
        
        # Validar que la tabla existe
        if table_name not in inspector.get_table_names():
            return JSONResponse(content={
                "success": False,
                "message": f"❌ Tabla '{table_name}' no encontrada"
            }, status_code=404)
        
        # Obtener información detallada
        columns = inspector.get_columns(table_name)
        primary_keys = inspector.get_pk_constraint(table_name)
        foreign_keys = inspector.get_foreign_keys(table_name)
        indexes = inspector.get_indexes(table_name)
        
        # Formatear información de columnas
        column_info = []
        for col in columns:
            col_data = {
                "name": col["name"],
                "type": str(col["type"]),
                "nullable": col.get("nullable", True),
                "default": str(col.get("default")) if col.get("default") else None,
                "autoincrement": col.get("autoincrement", False),
                "primary_key": col["name"] in primary_keys.get("constrained_columns", [])
            }
            column_info.append(col_data)
        
        # Formatear foreign keys
        fk_info = []
        for fk in foreign_keys:
            fk_info.append({
                "name": fk.get("name"),
                "constrained_columns": fk.get("constrained_columns", []),
                "referred_table": fk.get("referred_table"),
                "referred_columns": fk.get("referred_columns", [])
            })
        
        return JSONResponse(content={
            "success": True,
            "message": f"✅ Esquema de tabla '{table_name}' obtenido",
            "table_name": table_name,
            "columns": column_info,
            "primary_key": primary_keys,
            "foreign_keys": fk_info,
            "indexes": indexes
        })
        
    except Exception as e:
        logger.error(f"❌ Error al obtener esquema de tabla {table_name}: {str(e)}")
        return JSONResponse(content={
            "success": False,
            "message": f"Error al obtener esquema: {str(e)}"
        }, status_code=500)

# Fin del archivo - todas las funciones están listas
# El generador ahora está completamente funcional con explorador de tablas
