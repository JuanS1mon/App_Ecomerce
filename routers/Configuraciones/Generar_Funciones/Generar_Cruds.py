def generate_crud_functions(module_name, field_names, field_types):
    """
    Genera funciones CRUD para un módulo dado siguiendo el modelo proporcionado.
    """
    # Convertir el nombre del módulo a Capitalizado
    module_name_cap = module_name.capitalize()
    # Asumir que el primer campo es la clave primaria
    primary_key = field_names[0]
    primary_key_type = field_types[0]

    crud_code = f"""from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status
from db.models.{module_name} import {module_name_cap}

"""

    # Función create
    crud_code += f"""def create_{module_name}(db: Session, {module_name}: {module_name_cap}):
    try:
        db.add({module_name})
        db.commit()
        db.refresh({module_name})
        return {module_name}
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

"""

    # Función get
    crud_code += f"""def get_{module_name}(db: Session, {primary_key}: {primary_key_type}):
    try:
        record = db.query({module_name_cap}).filter({module_name_cap}.{primary_key} == {primary_key}).first()
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="{module_name} no encontrado")
        return record
    except SQLAlchemyError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

"""

    # Función gets
    crud_code += f"""def gets_{module_name}(db: Session):
    try:
        records = db.query({module_name_cap}).all()
        return records
    except SQLAlchemyError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

"""

    # Función delete
    crud_code += f"""def delete_{module_name}(db: Session, {primary_key}: {primary_key_type}):
    try:
        record = db.query({module_name_cap}).filter({module_name_cap}.{primary_key} == {primary_key}).first()
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="{module_name} no encontrado")
        db.delete(record)
        db.commit()
        return record
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

"""

    # Función update
    crud_code += f"""def update_{module_name}(db: Session, {primary_key}: {primary_key_type}, {module_name}_data: dict):
    print(f"Actualizando {module_name} con {primary_key} = {{{primary_key}}}")
    try:
        record = db.query({module_name_cap}).filter({module_name_cap}.{primary_key} == {primary_key}).first()
        print(record)
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="{module_name} no encontrado")

        for key, value in {module_name}_data.items():
            if key != '{primary_key}':
                setattr(record, key, value)

        db.commit()
        db.refresh(record)
        return record
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

"""

    return crud_code