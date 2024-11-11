from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status
from db.models.pruebat1 import Pruebat1

def create_pruebat1(db: Session, pruebat1: Pruebat1):
    try:
        db.add(pruebat1)
        db.commit()
        db.refresh(pruebat1)
        return pruebat1
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

def get_pruebat1(db: Session, campot1: int):
    try:
        record = db.query(Pruebat1).filter(Pruebat1.campot1 == campot1).first()
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="pruebat1 no encontrado")
        return record
    except SQLAlchemyError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

def gets_pruebat1(db: Session):
    try:
        records = db.query(Pruebat1).all()
        return records
    except SQLAlchemyError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

def delete_pruebat1(db: Session, campot1: int):
    try:
        record = db.query(Pruebat1).filter(Pruebat1.campot1 == campot1).first()
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="pruebat1 no encontrado")
        db.delete(record)
        db.commit()
        return record
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

def update_pruebat1(db: Session, campot1: int, pruebat1_data: dict):
    print(f"Actualizando pruebat1 con campot1 = {campot1}")
    try:
        # Obtener el registro existente
        record = db.query(Pruebat1).filter(Pruebat1.campot1 == campot1).first()
        print(record)
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="pruebat1 no encontrado")

        # Actualizar los campos del registro existente
        for key, value in pruebat1_data.items():
            if key != 'campot1':  # Opcional: evitar actualizar la clave primaria
                setattr(record, key, value)

        db.commit()
        db.refresh(record)
        return record
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))