from sqlalchemy.orm import Session
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException,status

def create_inventarios(db: Session, id: int, producto_id: int, cantidad_fisica: float, inventario_date: str, notas: str, created_at: str, updated_at: str):
    try:
        sql = text("""INSERT INTO inventarios (id, producto_id, cantidad_fisica, inventario_date, notas, created_at, updated_at)
OUTPUT INSERTED.id AS id, INSERTED.producto_id AS producto_id, INSERTED.cantidad_fisica AS cantidad_fisica, INSERTED.inventario_date AS inventario_date, INSERTED.notas AS notas, INSERTED.created_at AS created_at, INSERTED.updated_at AS updated_at
VALUES (COALESCE((SELECT MAX(id) FROM inventarios), 0) + 1, :producto_id, :cantidad_fisica, :inventario_date, :notas, :created_at, :updated_at)""")
        sql = db.execute(sql.params(id=id, producto_id=producto_id, cantidad_fisica=cantidad_fisica, inventario_date=inventario_date, notas=notas, created_at=created_at, updated_at=updated_at))
        result = sql.fetchall()
        db.commit()
        return [{'id': row[0], 'producto_id': row[1], 'cantidad_fisica': row[2], 'inventario_date': row[3], 'notas': row[4], 'created_at': row[5], 'updated_at': row[6]} for row in result] if result else None 
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail="SQL: No se pudo guardar registro en inventarios, intentelo de nuevo")

def get_inventarios(db: Session, id: int):
    try:
        if id is not None:
            query = text("SELECT id, producto_id, cantidad_fisica, inventario_date, notas, created_at, updated_at FROM inventarios WHERE id = :id")
            sql = db.execute(query.params(id=id))
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="inventarios no encontrado")
        result = sql.fetchall()
        return [{'id': row[0], 'producto_id': row[1], 'cantidad_fisica': row[2], 'inventario_date': row[3], 'notas': row[4], 'created_at': row[5], 'updated_at': row[6]} for row in result] if result else None 
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=" SQL: No se pudo obtener dato de inventarios, intentelo de nuevo")

def gets_inventarios(db: Session):
    try:
        query = text("SELECT id, producto_id, cantidad_fisica, inventario_date, notas, created_at, updated_at FROM inventarios")
        sql = db.execute(query)
        result = sql.fetchall()
        return [{'id': row[0], 'producto_id': row[1], 'cantidad_fisica': row[2], 'inventario_date': row[3], 'notas': row[4], 'created_at': row[5], 'updated_at': row[6]} for row in result] if result else None 
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=" SQL: No se pudo obtener dato de inventarios, intentelo de nuevo")

def delete_inventarios(db: Session, id: int):
    try:
        query = text("""DELETE FROM inventarios
 OUTPUT DELETED.id AS id, DELETED.producto_id AS producto_id, DELETED.cantidad_fisica AS cantidad_fisica, DELETED.inventario_date AS inventario_date, DELETED.notas AS notas, DELETED.created_at AS created_at, DELETED.updated_at AS updated_at WHERE id = :id  """)
        sql = db.execute(query.params(id=id))
        result = sql.fetchall()
        db.commit()
        return [{'id': row[0], 'producto_id': row[1], 'cantidad_fisica': row[2], 'inventario_date': row[3], 'notas': row[4], 'created_at': row[5], 'updated_at': row[6]} for row in result] if result else None
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=404, detail="No se pudo eliminar")

def get_inventarios_producto_id(db: Session, producto_id: str):
    try:
        if producto_id is not None:
            query = text("SELECT id, producto_id, cantidad_fisica, inventario_date, notas, created_at, updated_at FROM inventarios WHERE producto_id LIKE :producto_id")
            sql = db.execute(query.params(producto_id='%' + producto_id + '%'))
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="inventarios no encontrado")
        result = sql.fetchall()
        if not result:
            return None
        return [{'id': row[0], 'producto_id': row[1], 'cantidad_fisica': row[2], 'inventario_date': row[3], 'notas': row[4], 'created_at': row[5], 'updated_at': row[6]} for row in result] if result else None
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=str(e))

def update_inventarios(db: Session, id: int, producto_id: int, cantidad_fisica: float, inventario_date: str, notas: str, created_at: str, updated_at: str):
    try:
        query = text("""UPDATE inventarios SET producto_id = :producto_id, cantidad_fisica = :cantidad_fisica, inventario_date = :inventario_date, notas = :notas, created_at = :created_at, updated_at = :updated_at
OUTPUT INSERTED.id AS id, INSERTED.producto_id AS producto_id, INSERTED.cantidad_fisica AS cantidad_fisica, INSERTED.inventario_date AS inventario_date, INSERTED.notas AS notas, INSERTED.created_at AS created_at, INSERTED.updated_at AS updated_at
WHERE id = :id""")
        sql = db.execute(query.params(id=id, producto_id=producto_id, cantidad_fisica=cantidad_fisica, inventario_date=inventario_date, notas=notas, created_at=created_at, updated_at=updated_at))
        result = sql.fetchall()
        db.commit()
        return [{'id': row[0], 'producto_id': row[1], 'cantidad_fisica': row[2], 'inventario_date': row[3], 'notas': row[4], 'created_at': row[5], 'updated_at': row[6]} for row in result] if result else None
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f" Route: descripcion no se pudo actualizar el codigo {codigo} en Familias ")

