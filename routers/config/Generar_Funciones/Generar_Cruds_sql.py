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
    placeholders = ", ".join([f":{field}" for field in field_names])
    update_fields = ", ".join([f"{field} = :{field}" for field in field_names if field != primary_key])

    code = f'''from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status
from sqlalchemy import text
from db.models.{module_file_name} import {module_class_name}
from typing import List, Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

'''

    # Función create con SQL directo
    code += f'''def create_{module_file_name}(db: Session, {module_file_name}_data: Dict[str, Any]) -> {module_class_name}:
    """
    Crea un nuevo registro de {module_class_name} en la base de datos usando SQL directo.
    """
    try:
        # Construir la consulta SQL INSERT
        query = text("""
            INSERT INTO {table_name} ({columns_list})
            VALUES ({placeholders})
            RETURNING *
        """)
        
        # Ejecutar la consulta
        result = db.execute(query, {module_file_name}_data)
        db.commit()
        
        # Convertir el resultado a diccionario
        record_dict = dict(result.fetchone())
        
        # Crear y devolver una instancia del modelo
        return {module_class_name}(**record_dict)
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al crear {module_class_name}: {{e}}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al crear el registro: {{str(e)}}")

'''

    # Función get por id con SQL directo
    code += f'''def get_{module_file_name}(db: Session, {primary_key}: {primary_key_python_type}) -> Optional[{module_class_name}]:
    """
    Obtiene un registro de {module_class_name} por su clave primaria usando SQL directo.
    """
    try:
        query = text("""
            SELECT * FROM {table_name}
            WHERE {primary_key} = :{primary_key}
        """)
        
        result = db.execute(query, {{{primary_key}: {primary_key}}})
        record = result.fetchone()
        
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="{module_class_name} no encontrado.")
        
        # Convertir el resultado a diccionario y crear una instancia del modelo
        record_dict = dict(record)
        return {module_class_name}(**record_dict)
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener {module_class_name}: {{e}}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al obtener el registro: {{str(e)}}")

'''

    # Función gets (obtener todos los registros) con SQL directo
    code += f'''def gets_{module_file_name}(db: Session) -> List[{module_class_name}]:
    """
    Obtiene una lista de todos los registros de {module_class_name} usando SQL directo.
    """
    try:
        query = text("""
            SELECT * FROM {table_name}
        """)
        
        result = db.execute(query)
        records = []
        
        for row in result:
            record_dict = dict(row)
            records.append({module_class_name}(**record_dict))
        
        return records
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener registros de {module_class_name}: {{e}}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al obtener los registros: {{str(e)}}")

'''

    # Función delete por id con SQL directo
    code += f'''def delete_{module_file_name}(db: Session, {primary_key}: {primary_key_python_type}) -> Dict[str, Any]:
    """
    Elimina un registro de {module_class_name} por su clave primaria usando SQL directo.
    """
    try:
        # Primero obtenemos el registro para verificar que existe
        get_query = text("""
            SELECT * FROM {table_name}
            WHERE {primary_key} = :{primary_key}
        """)
        
        result = db.execute(get_query, {{{primary_key}: {primary_key}}})
        record = result.fetchone()
        
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="{module_class_name} no encontrado.")
        
        # Si existe, procedemos a eliminarlo
        delete_query = text("""
            DELETE FROM {table_name}
            WHERE {primary_key} = :{primary_key}
            RETURNING *
        """)
        
        result = db.execute(delete_query, {{{primary_key}: {primary_key}}})
        deleted_record = dict(result.fetchone())
        db.commit()
        
        return deleted_record
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al eliminar {module_class_name}: {{e}}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al eliminar el registro: {{str(e)}}")

'''

    # Función update con SQL directo
    code += f'''def update_{module_file_name}(db: Session, {primary_key}: {primary_key_python_type}, {module_file_name}_data: Dict[str, Any]) -> {module_class_name}:
    """
    Actualiza un registro de {module_class_name} por su clave primaria usando SQL directo.
    """
    logger.info(f"Actualizando {module_class_name} con {primary_key} = {{{primary_key}}}")
    try:
        # Primero verificamos que el registro existe
        check_query = text("""
            SELECT * FROM {table_name}
            WHERE {primary_key} = :{primary_key}
        """)
        
        result = db.execute(check_query, {{{primary_key}: {primary_key}}})
        if not result.fetchone():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="{module_class_name} no encontrado.")
        
        # Eliminar la clave primaria del diccionario de datos si está presente
        {module_file_name}_data_copy = {module_file_name}_data.copy()
        if '{primary_key}' in {module_file_name}_data_copy:
            del {module_file_name}_data_copy['{primary_key}']
        
        # Si no hay campos para actualizar, retornar el registro como está
        if not {module_file_name}_data_copy:
            get_query = text("""
                SELECT * FROM {table_name}
                WHERE {primary_key} = :{primary_key}
            """)
            result = db.execute(get_query, {{{primary_key}: {primary_key}}})
            record_dict = dict(result.fetchone())
            return {module_class_name}(**record_dict)
        
        # Construir la consulta de actualización dinámica
        set_clauses = ", ".join([f"{{field}} = :{{field}}" for field in {module_file_name}_data_copy.keys()])
        update_query = text(f"""
            UPDATE {table_name}
            SET {{set_clauses}}
            WHERE {primary_key} = :{primary_key}
            RETURNING *
        """)
        
        # Agregar la clave primaria al diccionario de parámetros
        params = {module_file_name}_data_copy.copy()
        params['{primary_key}'] = {primary_key}
        
        # Ejecutar la actualización
        result = db.execute(update_query, params)
        updated_record = result.fetchone()
        db.commit()
        
        return {module_class_name}(**dict(updated_record))
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al actualizar {module_class_name}: {{e}}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al actualizar el registro: {{str(e)}}")

'''

    return code