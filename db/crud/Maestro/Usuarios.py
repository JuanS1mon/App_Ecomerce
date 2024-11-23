from sqlalchemy.orm import Session
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from ...schemas.Maestro.Usuarios import UserDB


def create_usuario(db: Session, nombre: str, usuario: str, clave: str, mail: str):
    try:
        sql = text("""INSERT INTO Usuarios (
                                codigo, Usuario, nombre, Clave, mail, activo)
                                OUTPUT INSERTED.codigo AS codigo, INSERTED.Usuario AS Usuario, INSERTED.nombre AS Nombre, INSERTED.mail AS mail
                                VALUES (COALESCE((SELECT MAX(codigo) FROM Usuarios), 0) + 1, :usuario, :nombre, :clave, :mail, 0)""")
        result = db.execute(sql, {"usuario": usuario, "nombre": nombre, "clave": clave, "mail": mail})
        rows = result.fetchall()
        db.commit()
        return [{"codigo": row[0], "usuario": row[1], "nombre": row[2], "mail": row[3]} for row in rows]
    except IntegrityError as e:
        db.rollback()
        if "UQ__usuarios__" in str(e.orig):
            raise HTTPException(status_code=400, detail="El correo electrónico ya está registrado.")
        else:
            raise HTTPException(status_code=403, detail="No se pudo crear el usuario debido a un error de integridad.")
    except Exception as e:
        db.rollback()
        print(f"Error al insertar el usuario: {e}")
        raise HTTPException(status_code=403, detail="No se pudo crear el usuario.")
    
  
def get_usuario(db: Session, codigo: int = None, usuario: str = None):
    try:
        if codigo is not None:
            result = db.execute(text("SELECT top(1) codigo,usuario,Mail,activo FROM Usuarios WHERE codigo = :codigo"), {"codigo": codigo})
        elif usuario is not None:
            result = db.execute(text("SELECT top(1) codigo,usuario,Mail,activo FROM Usuarios WHERE usuario = :usuario"), {"usuario": usuario})
        else:
            # Ambos parámetros no pueden ser nulos
            raise HTTPException(status_code=400, detail="Se debe proporcionar código o usuario para la búsqueda")
        rows = result.fetchall()
        if not rows:
            return None
        return [{"codigo": row[0], "usuario": row[1],"Mail": row[2], "activo": row[3]} for row in rows]
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=400, detail="No se pudo obtener el Usuario")

def gets_usuarios(db: Session):
    try:
        result = db.execute(text("SELECT codigo,usuario,nombreCompleto,Email FROM Usuarios"))
        Modelos = result.fetchall()
        if not Modelos:
            raise HTTPException(status_code=404, detail="No se encontraron Usuarios")
        return Modelos
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=400, detail="No se pudieron obtener Usuarios")
    

def delete_usuario(db: Session, codigo: int):
    try:
        statement = text("DELETE FROM Usuarios WHERE codigo = :codigo")
        db.execute(statement.params(codigo=codigo))
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=404, detail="No se pudo eliminar")
    

def update_usuario(db: Session, codigo: int, usuario: str, clave: str, nombre: str, email: str):
    try:
        result = db.execute(text("""UPDATE Usuarios SET Usuario = :usuario, Clave = :clave, NombreCompleto = :nombre, Email = :email 
                                    OUTPUT INSERTED.Codigo,INSERTED.Usuario, INSERTED.NombreCompleto, INSERTED.Email
                                    WHERE Codigo = :codigo"""), 
                           {"codigo": codigo, "usuario": usuario, "clave": clave, "nombre": nombre, "email": email})
        rows = result.fetchall()
        db.commit()
        return [{"codigo": row[0], "usuario": row[1], "nombre": row[2], "email": row[3]} for row in rows]  # Return updated data
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=400, detail="No se pudo actualizar el usuario")
    
def user_pass(db: Session, username: str, password: str):
    if not password:
        return False
    result = db.execute(text("SELECT clave FROM Usuarios WHERE usuario = :usuario"), {"usuario": username})
    row = result.fetchone()
    if not row:
        return False
    hashed_password = row[0]  # Extrae la contraseña encriptada del objeto Row
    return {"username": username, "password": hashed_password}

def update_usuario_activate(db: Session, usuario: str):
    print(usuario, "Activando usuario")
    try:
        result = db.execute(text("""UPDATE Usuarios SET activo = 1  
                                    OUTPUT INSERTED.Codigo,INSERTED.Usuario, INSERTED.Nombre, INSERTED.mail
                                    WHERE usuario = :usuario"""), 
                                {"usuario": usuario })                      
        rows = result.fetchall()
        db.commit()
        return [{"codigo": row[0], "usuario": row[1], "nombre": row[2], "email": row[3]} for row in rows]  # Return updated data
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=400, detail="No se pudo actualizar el usuario")
    
    

def get_user_from_db(db: Session, username: str):
    try:
        # Realizar la consulta a la tabla Usuarios usando SQL crudo
        result = db.execute(
            text("SELECT top(1) codigo, usuario, nombre, mail, activo, clave FROM Usuarios WHERE usuario = :usuario"),
            {"usuario": username}
        ).first()
        
        # Verificar si se obtuvo un resultado
        if result:
            # Crear un objeto UserDB con los datos obtenidos
            user = UserDB(
                codigo=result.codigo,
                usuario=result.usuario,
                nombre=result.nombre,
                mail=result.mail,
                activo=result.activo,
                clave=result.clave
            )
            print("db:", user)
            return user
        else:
            return None
    except Exception as e:
        # Manejar posibles excepciones
        print(f"Error al obtener el usuario: {e}")
        return None