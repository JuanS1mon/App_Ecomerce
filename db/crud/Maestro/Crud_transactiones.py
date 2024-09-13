from sqlalchemy.orm import Session
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException,status

def create_transactiones(db: Session, id: int, producto_id: int, cantidad: float, transaction_tipo: str, transaction_date: str, usuario_id: int, created_at: str, updated_at: str):
    try:
        sql = text("""INSERT INTO transactiones (id, producto_id, cantidad, transaction_tipo, transaction_date, usuario_id, created_at, updated_at)
OUTPUT INSERTED.id AS id, INSERTED.producto_id AS producto_id, INSERTED.cantidad AS cantidad, INSERTED.transaction_tipo AS transaction_tipo, INSERTED.transaction_date AS transaction_date, INSERTED.usuario_id AS usuario_id, INSERTED.created_at AS created_at, INSERTED.updated_at AS updated_at
VALUES (COALESCE((SELECT MAX(id) FROM transactiones), 0) + 1, :producto_id, :cantidad, :transaction_tipo, :transaction_date, :usuario_id, :created_at, :updated_at)""")
        sql = db.execute(sql.params(id=id, producto_id=producto_id, cantidad=cantidad, transaction_tipo=transaction_tipo, transaction_date=transaction_date, usuario_id=usuario_id, created_at=created_at, updated_at=updated_at))
        result = sql.fetchall()
        db.commit()
        return [{'id': row[0], 'producto_id': row[1], 'cantidad': row[2], 'transaction_tipo': row[3], 'transaction_date': row[4], 'usuario_id': row[5], 'created_at': row[6], 'updated_at': row[7]} for row in result] if result else None 
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail="SQL: No se pudo guardar registro en transactiones, intentelo de nuevo")

def get_transactiones(db: Session, id: int):
    try:
        if id is not None:
            query = text("SELECT id, producto_id, cantidad, transaction_tipo, transaction_date, usuario_id, created_at, updated_at FROM transactiones WHERE id = :id")
            sql = db.execute(query.params(id=id))
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="transactiones no encontrado")
        result = sql.fetchall()
        return [{'id': row[0], 'producto_id': row[1], 'cantidad': row[2], 'transaction_tipo': row[3], 'transaction_date': row[4], 'usuario_id': row[5], 'created_at': row[6], 'updated_at': row[7]} for row in result] if result else None 
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=" SQL: No se pudo obtener dato de transactiones, intentelo de nuevo")

def gets_transactiones(db: Session):
    try:
        query = text("SELECT id, producto_id, cantidad, transaction_tipo, transaction_date, usuario_id, created_at, updated_at FROM transactiones")
        sql = db.execute(query)
        result = sql.fetchall()
        return [{'id': row[0], 'producto_id': row[1], 'cantidad': row[2], 'transaction_tipo': row[3], 'transaction_date': row[4], 'usuario_id': row[5], 'created_at': row[6], 'updated_at': row[7]} for row in result] if result else None 
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=" SQL: No se pudo obtener dato de transactiones, intentelo de nuevo")

def delete_transactiones(db: Session, id: int):
    try:
        query = text("""DELETE FROM transactiones
 OUTPUT DELETED.id AS id, DELETED.producto_id AS producto_id, DELETED.cantidad AS cantidad, DELETED.transaction_tipo AS transaction_tipo, DELETED.transaction_date AS transaction_date, DELETED.usuario_id AS usuario_id, DELETED.created_at AS created_at, DELETED.updated_at AS updated_at WHERE id = :id  """)
        sql = db.execute(query.params(id=id))
        result = sql.fetchall()
        db.commit()
        return [{'id': row[0], 'producto_id': row[1], 'cantidad': row[2], 'transaction_tipo': row[3], 'transaction_date': row[4], 'usuario_id': row[5], 'created_at': row[6], 'updated_at': row[7]} for row in result] if result else None
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=404, detail="No se pudo eliminar")

def get_transactiones_producto_id(db: Session, producto_id: str):
    try:
        if producto_id is not None:
            query = text("SELECT id, producto_id, cantidad, transaction_tipo, transaction_date, usuario_id, created_at, updated_at FROM transactiones WHERE producto_id LIKE :producto_id")
            sql = db.execute(query.params(producto_id='%' + producto_id + '%'))
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="transactiones no encontrado")
        result = sql.fetchall()
        if not result:
            return None
        return [{'id': row[0], 'producto_id': row[1], 'cantidad': row[2], 'transaction_tipo': row[3], 'transaction_date': row[4], 'usuario_id': row[5], 'created_at': row[6], 'updated_at': row[7]} for row in result] if result else None
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=str(e))

def update_transactiones(db: Session, id: int, producto_id: int, cantidad: float, transaction_tipo: str, transaction_date: str, usuario_id: int, created_at: str, updated_at: str):
    try:
        query = text("""UPDATE transactiones SET producto_id = :producto_id, cantidad = :cantidad, transaction_tipo = :transaction_tipo, transaction_date = :transaction_date, usuario_id = :usuario_id, created_at = :created_at, updated_at = :updated_at
OUTPUT INSERTED.id AS id, INSERTED.producto_id AS producto_id, INSERTED.cantidad AS cantidad, INSERTED.transaction_tipo AS transaction_tipo, INSERTED.transaction_date AS transaction_date, INSERTED.usuario_id AS usuario_id, INSERTED.created_at AS created_at, INSERTED.updated_at AS updated_at
WHERE id = :id""")
        sql = db.execute(query.params(id=id, producto_id=producto_id, cantidad=cantidad, transaction_tipo=transaction_tipo, transaction_date=transaction_date, usuario_id=usuario_id, created_at=created_at, updated_at=updated_at))
        result = sql.fetchall()
        db.commit()
        return [{'id': row[0], 'producto_id': row[1], 'cantidad': row[2], 'transaction_tipo': row[3], 'transaction_date': row[4], 'usuario_id': row[5], 'created_at': row[6], 'updated_at': row[7]} for row in result] if result else None
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f" Route: descripcion no se pudo actualizar el codigo {codigo} en Familias ")

