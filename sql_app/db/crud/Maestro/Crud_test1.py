from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status
from ...models.test1 import test1

def create_test1(db: Session, campo1: int, campo2: str, campo3: float, campo4: bool):
    try:
        new_record = test1(campo1=campo1, campo2=campo2, campo3=campo3, campo4=campo4)
        db.add(new_record)
        db.commit()
        db.refresh(new_record)
        return new_record
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

def get_test1(db: Session, campo1: int):
    try:
        record = db.query(test1).filter(test1.campo1 == campo1).first()
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="test1 no encontrado")
        return record
    except SQLAlchemyError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

def get_test1_by_campo1(db: Session, campo1: int):
    try:
        record = db.query(test1).filter(test1.campo1 == campo1).first()
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="test1 no encontrado")
        return record
    except SQLAlchemyError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

def gets_test1(db: Session):
    try:
        records = db.query(test1).all()
        return records
    except SQLAlchemyError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

def delete_test1(db: Session, campo1: int):
    try:
        record = db.query(test1).filter(test1.campo1 == campo1).first()
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="test1 no encontrado")
        db.delete(record)
        db.commit()
        return record
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

def update_test1(db: Session, campo1: int, campo2: str, campo3: float, campo4: bool):
    try:
        record = db.query(test1).filter(test1.campo1 == campo1).first()
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="test1 no encontrado")
        for key, value in locals().items():
            if key in ['campo1', 'campo2', 'campo3', 'campo4'] and value is not None:
                setattr(record, key, value)
        db.commit()
        db.refresh(record)
        return record
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))