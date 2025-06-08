def generate_crud_functions(module_name, field_names, field_types):
    module_class_name = module_name.capitalize()
    module_file_name = module_name.lower()
    
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

    code = f'''from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status
from db.models.{module_file_name} import {module_class_name}import logging

logger = logging.getLogger(__name__)

'''

    # Función create
    code += f'''def create_{module_file_name}(db: Session, {module_file_name}: {module_class_name}) -> {module_class_name}:
    """
    Crea un nuevo registro de {module_class_name} en la base de datos.
    """
    try:
        db.add({module_file_name})
        db.commit()
        db.refresh({module_file_name})
        return {module_file_name}
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al crear {module_class_name}: {{e}}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al crear el registro.")

'''

    # Función get por id
    code += f'''def get_{module_file_name}(db: Session, {primary_key}: {primary_key_python_type}) -> Optional[{module_class_name}]:
    """
    Obtiene un registro de {module_class_name} por su clave primaria.
    """
    try:
        record = db.query({module_class_name}).filter({module_class_name}.{primary_key} == {primary_key}).first()
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="{module_class_name} no encontrado.")
        return record
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener {module_class_name}: {{e}}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener el registro.")

'''

    # Función gets (obtener todos los registros)
    code += f'''def gets_{module_file_name}(db: Session) -> List[{module_class_name}]:
    """
    Obtiene una lista de todos los registros de {module_class_name}.
    """
    try:
        records = db.query({module_class_name}).all()
        return records
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener registros de {module_class_name}: {{e}}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener los registros.")

'''

    # Función delete por id
    code += f'''def delete_{module_file_name}(db: Session, {primary_key}: {primary_key_python_type}) -> {module_class_name}:
    """
    Elimina un registro de {module_class_name} por su clave primaria.
    """
    try:
        record = db.query({module_class_name}).filter({module_class_name}.{primary_key} == {primary_key}).first()
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="{module_class_name} no encontrado.")
        db.delete(record)
        db.commit()
        return record
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al eliminar {module_class_name}: {{e}}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al eliminar el registro.")

'''

    # Función update
    code += f'''def update_{module_file_name}(db: Session, {primary_key}: {primary_key_python_type}, {module_file_name}_data: dict) -> {module_class_name}:
    """
    Actualiza un registro de {module_class_name} por su clave primaria.
    """
    logger.info(f"Actualizando {module_class_name} con {primary_key} = {{ {primary_key} }}")
    try:
        record = db.query({module_class_name}).filter({module_class_name}.{primary_key} == {primary_key}).first()
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="{module_class_name} no encontrado.")

        # Actualizar los campos del registro existente
        for key, value in {module_file_name}_data.items():
            if key != '{primary_key}':  # Evitar actualizar la clave primaria
                setattr(record, key, value)

        db.commit()
        db.refresh(record)
        return record
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al actualizar {module_class_name}: {{e}}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al actualizar el registro.")

'''

    return code