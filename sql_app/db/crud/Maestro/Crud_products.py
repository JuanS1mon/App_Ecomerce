from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status
from db.models.products import Products

def create_products(db: Session, products: Products):
    try:
        db.add(products)
        db.commit()
        db.refresh(products)
        return products
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

def get_products(db: Session, id: int):
    try:
        record = db.query(Products).filter(Products.id == id).first()
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="products no encontrado")
        return record
    except SQLAlchemyError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

def gets_products(db: Session):
    try:
        records = db.query(Products).all()
        return records
    except SQLAlchemyError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

def delete_products(db: Session, id: int):
    try:
        record = db.query(Products).filter(Products.id == id).first()
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="products no encontrado")
        db.delete(record)
        db.commit()
        return record
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

def update_products(db: Session, id: int, products_data: dict):
    print(f"Actualizando products con id = {id}")
    try:
        record = db.query(Products).filter(Products.id == id).first()
        print(record)
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="products no encontrado")

        for key, value in products_data.items():
            if key != 'id':
                setattr(record, key, value)

        db.commit()
        db.refresh(record)
        return record
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

