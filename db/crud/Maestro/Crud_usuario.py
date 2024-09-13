from sqlalchemy.orm import Session
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException,status

def create_usuario(db: Session, id: int, username: str, email: str, password_hash: str, created_at: str, updated_at: str):
    try:
        sql = text("""INSERT INTO usuario (id, username, email, password_hash, created_at, updated_at)
OUTPUT INSERTED.id AS id, INSERTED.username AS username, INSERTED.email AS email, INSERTED.password_hash AS password_hash, INSERTED.created_at AS created_at, INSERTED.updated_at AS updated_at
VALUES (COALESCE((SELECT MAX(id) FROM usuario), 0) + 1, :username, :email, :password_hash, :created_at, :updated_at)""")
        sql = db.execute(sql.params(id=id, username=username, email=email, password_hash=password_hash, created_at=created_at, updated_at=updated_at))
        result = sql.fetchall()
        db.commit()
        return [{'id': row[0], 'username': row[1], 'email': row[2], 'password_hash': row[3], 'created_at': row[4], 'updated_at': row[5]} for row in result] if result else None 
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail="SQL: No se pudo guardar registro en usuario, intentelo de nuevo")

def get_usuario(db: Session, id: int):
    try:
        if id is not None:
            query = text("SELECT id, username, email, password_hash, created_at, updated_at FROM usuario WHERE id = :id")
            sql = db.execute(query.params(id=id))
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="usuario no encontrado")
        result = sql.fetchall()
        return [{'id': row[0], 'username': row[1], 'email': row[2], 'password_hash': row[3], 'created_at': row[4], 'updated_at': row[5]} for row in result] if result else None 
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=" SQL: No se pudo obtener dato de usuario, intentelo de nuevo")

def gets_usuario(db: Session):
    try:
        query = text("SELECT id, username, email, password_hash, created_at, updated_at FROM usuario")
        sql = db.execute(query)
        result = sql.fetchall()
        return [{'id': row[0], 'username': row[1], 'email': row[2], 'password_hash': row[3], 'created_at': row[4], 'updated_at': row[5]} for row in result] if result else None 
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=" SQL: No se pudo obtener dato de usuario, intentelo de nuevo")

def delete_usuario(db: Session, id: int):
    try:
        query = text("""DELETE FROM usuario
 OUTPUT DELETED.id AS id, DELETED.username AS username, DELETED.email AS email, DELETED.password_hash AS password_hash, DELETED.created_at AS created_at, DELETED.updated_at AS updated_at WHERE id = :id  """)
        sql = db.execute(query.params(id=id))
        result = sql.fetchall()
        db.commit()
        return [{'id': row[0], 'username': row[1], 'email': row[2], 'password_hash': row[3], 'created_at': row[4], 'updated_at': row[5]} for row in result] if result else None
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=404, detail="No se pudo eliminar")

def get_usuario_username(db: Session, username: str):
    try:
        if username is not None:
            query = text("SELECT id, username, email, password_hash, created_at, updated_at FROM usuario WHERE username LIKE :username")
            sql = db.execute(query.params(username='%' + username + '%'))
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="usuario no encontrado")
        result = sql.fetchall()
        if not result:
            return None
        return [{'id': row[0], 'username': row[1], 'email': row[2], 'password_hash': row[3], 'created_at': row[4], 'updated_at': row[5]} for row in result] if result else None
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=str(e))

def update_usuario(db: Session, id: int, username: str, email: str, password_hash: str, created_at: str, updated_at: str):
    try:
        query = text("""UPDATE usuario SET username = :username, email = :email, password_hash = :password_hash, created_at = :created_at, updated_at = :updated_at
OUTPUT INSERTED.id AS id, INSERTED.username AS username, INSERTED.email AS email, INSERTED.password_hash AS password_hash, INSERTED.created_at AS created_at, INSERTED.updated_at AS updated_at
WHERE id = :id""")
        sql = db.execute(query.params(id=id, username=username, email=email, password_hash=password_hash, created_at=created_at, updated_at=updated_at))
        result = sql.fetchall()
        db.commit()
        return [{'id': row[0], 'username': row[1], 'email': row[2], 'password_hash': row[3], 'created_at': row[4], 'updated_at': row[5]} for row in result] if result else None
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f" Route: descripcion no se pudo actualizar el codigo {codigo} en Familias ")

