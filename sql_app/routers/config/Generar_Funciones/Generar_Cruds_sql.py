def generate_crud_functions(module_name, field_names, field_types):
    module_class_name = module_name.capitalize()
    module_file_name = module_name.lower()
    table_name = module_file_name  # Asumimos que el nombre de la tabla es el mismo que el del módulo
    
    # Determinar la clave primaria y su tipo
    primary_key = field_names[0]
    primary_key_type = field_types[0].lower()

    # Mapeo de tipos de datos SQL a Python
    type_mapping = {
        'int': 'int',
        'integer': 'int',
        'bigint': 'int',
        'smallint': 'int',
        'varchar': 'str',
        'char': 'str',
        'text': 'str',
        'float': 'float',
        'double': 'float',
        'decimal': 'float',
        'numeric': 'float',
        'bool': 'bool',
        'boolean': 'bool',
        'date': 'date',
        'datetime': 'datetime',
        # Agrega más mapeos según sea necesario
    }

    primary_key_python_type = type_mapping.get(primary_key_type, 'str')  # Por defecto 'str' si no se encuentra

    # Generamos las columnas para las consultas
    columns_list = ", ".join(field_names)
    inserted_columns = ", ".join([f"INSERTED.{field}" for field in field_names])
    deleted_columns = ", ".join([f"DELETED.{field}" for field in field_names])
    placeholders = ", ".join([f":{field}" for field in field_names])

    # Importaciones y configuración inicial
    code = f'''from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status
from sqlalchemy import text
from .model_{module_file_name} import {module_class_name}  # Corregida la importación
from typing import List, Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

'''

    # Función create con OUTPUT para SQL Server
    code += f'''def create_{module_file_name}(db: Session, {module_file_name}: {module_class_name}) -> {module_class_name}:
    """
    Crea un nuevo registro de {module_class_name} en la base de datos usando SQL directo.
    Adaptado para SQL Server usando cláusula OUTPUT.
    """
    try:
        # Preparar los datos para la consulta
        {module_file_name}_data = {{}}
        
        for field in {field_names}:
            if hasattr({module_file_name}, field):
                {module_file_name}_data[field] = getattr({module_file_name}, field)
        
        # Construir la consulta SQL INSERT con OUTPUT para SQL Server
        query = text("""
            INSERT INTO {table_name} ({columns_list})
            OUTPUT {inserted_columns}
            VALUES ({placeholders})
        """)
        
        # Ejecutar la consulta y obtener el registro insertado directamente
        result = db.execute(query, {module_file_name}_data)
        row = result.first()
        db.commit()
        
        if not row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="El registro no se pudo crear"
            )
        
        # Crear un nuevo objeto {module_class_name} con los valores devueltos
        new_{module_file_name} = {module_class_name}()
'''

    # Asignar cada columna al objeto recién creado
    for i, field in enumerate(field_names):
        code += f'''        new_{module_file_name}.{field} = row[{i}]
'''

    code += f'''        
        return new_{module_file_name}
        
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error SQL al crear {module_class_name}: {{e}}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear el registro: {{str(e)}}"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error general al crear {module_class_name}: {{e}}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error inesperado: {{str(e)}}"
        )
'''

    # Función get con acceso directo a las columnas
    code += f'''def get_{module_file_name}(db: Session, {primary_key}: {primary_key_python_type}) -> Optional[{module_class_name}]:
    """
    Obtiene un registro de {module_class_name} por su clave primaria usando SQL directo.
    """
    try:
        result = db.execute(
            text("SELECT {columns_list} FROM {table_name} WHERE {primary_key} = :{primary_key}"),
            {{"{primary_key}": {primary_key}}}
        ).first()
        
        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="{module_class_name} no encontrado.")
        
        # Crear el objeto directamente con los valores
        {module_file_name} = {module_class_name}()
'''

    # Asignar cada columna al objeto
    for i, field in enumerate(field_names):
        code += f'''        {module_file_name}.{field} = result[{i}]
'''
    
    code += f'''        
        return {module_file_name}
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener {module_class_name}: {{e}}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al obtener el registro: {{str(e)}}")
'''

    # Función gets para obtener todos los registros
    code += f'''def gets_{module_file_name}(db: Session) -> List[{module_class_name}]:
    """
    Obtiene una lista de todos los registros de {module_class_name} usando SQL directo.
    """
    try:
        result = db.execute(
            text("SELECT {columns_list} FROM {table_name}")
        )
        
        {module_file_name}s = []
        for row in result.fetchall():
            {module_file_name} = {module_class_name}()
'''

    # Asignar cada columna al objeto para cada fila
    for i, field in enumerate(field_names):
        code += f'''            {module_file_name}.{field} = row[{i}]
'''
    
    code += f'''            {module_file_name}s.append({module_file_name})
        
        return {module_file_name}s
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener registros de {module_class_name}: {{e}}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al obtener los registros: {{str(e)}}")
'''

    # Función delete con OUTPUT para SQL Server
    code += f'''def delete_{module_file_name}(db: Session, {primary_key}: {primary_key_python_type}) -> {module_class_name}:
    """
    Elimina un registro de {module_class_name} por su clave primaria usando SQL directo.
    """
    try:
        # Obtener y eliminar el registro en una sola operación usando OUTPUT
        result = db.execute(
            text("""
                DELETE FROM {table_name} 
                OUTPUT {deleted_columns}
                WHERE {primary_key} = :{primary_key}
            """),
            {{"{primary_key}": {primary_key}}}
        ).first()
        
        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="{module_class_name} no encontrado.")
        
        # Crear el objeto con los datos del registro eliminado
        deleted_{module_file_name} = {module_class_name}()
'''

    # Asignar cada columna al objeto eliminado
    for i, field in enumerate(field_names):
        code += f'''        deleted_{module_file_name}.{field} = result[{i}]
'''
    
    code += f'''        
        db.commit()
        return deleted_{module_file_name}
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al eliminar {module_class_name}: {{e}}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al eliminar el registro: {{str(e)}}")
'''

    # Función update con OUTPUT para SQL Server
    code += f'''def update_{module_file_name}(db: Session, {primary_key}: {primary_key_python_type}, {module_file_name}_data: Dict[str, Any]) -> {module_class_name}:
    """
    Actualiza un registro de {module_class_name} por su clave primaria usando SQL directo.
    """
    logger.info(f"Actualizando {module_class_name} con {primary_key} = {{{primary_key}}}")
    try:
        # Verificar que el registro existe
        result = db.execute(
            text("SELECT COUNT(*) FROM {table_name} WHERE {primary_key} = :{primary_key}"),
            {{"{primary_key}": {primary_key}}}
        ).scalar()
        
        if result == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="{module_class_name} no encontrado.")
        
        # Eliminar la clave primaria del diccionario de datos si está presente
        {module_file_name}_data_copy = {module_file_name}_data.copy()
        if '{primary_key}' in {module_file_name}_data_copy:
            del {module_file_name}_data_copy['{primary_key}']
        
        # Si no hay campos para actualizar, obtener el registro actual
        if not {module_file_name}_data_copy:
            return get_{module_file_name}(db, {primary_key})
        
        # Construir la parte SET de la consulta UPDATE
        set_clauses = []
        for field in {module_file_name}_data_copy:
            set_clauses.append(f"{{field}} = :{{field}}")
        
        set_clause_str = ", ".join(set_clauses)
        
        # Construir la consulta completa con OUTPUT
        query = text(f"""
            UPDATE {table_name}
            SET {{set_clause_str}}
            OUTPUT {inserted_columns}
            WHERE {primary_key} = :{primary_key}
        """)
        
        # Preparar los parámetros
        params = {module_file_name}_data_copy.copy()
        params['{primary_key}'] = {primary_key}
        
        # Ejecutar la consulta
        result = db.execute(query, params).first()
        db.commit()
        
        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No se pudo actualizar el {module_class_name}.")
        
        # Crear el objeto con los datos actualizados
        updated_{module_file_name} = {module_class_name}()
'''

    # Asignar cada columna al objeto actualizado
    for i, field in enumerate(field_names):
        code += f'''        updated_{module_file_name}.{field} = result[{i}]
'''
    
    code += f'''        
        return updated_{module_file_name}
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al actualizar {module_class_name}: {{e}}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al actualizar el registro: {{str(e)}}")
'''

    return code