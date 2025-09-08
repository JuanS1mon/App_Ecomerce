# Imports de bibliotecas estándar
import logging

# Imports de terceros
from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

# Imports del proyecto
from ...schemas.config.Usuarios import UserDB

# Configura el logger
logger = logging.getLogger(__name__)

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
            raise HTTPException(status_code=400, detail="Error de integridad al crear usuario.")
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error interno al crear usuario.")

def get_usuario(db: Session, codigo: int = None, usuario: str = None):
    try:
        if codigo:
            sql = text("SELECT codigo, usuario, nombre, clave, mail, activo FROM Usuarios WHERE codigo = :codigo")
            result = db.execute(sql, {"codigo": codigo})
        elif usuario:
            sql = text("SELECT codigo, usuario, nombre, clave, mail, activo FROM Usuarios WHERE usuario = :usuario")
            result = db.execute(sql, {"usuario": usuario})
        else:
            raise HTTPException(status_code=400, detail="Debe proporcionar código o usuario")
        
        rows = result.fetchall()
        return [{"codigo": row[0], "usuario": row[1], "nombre": row[2], "clave": row[3], "mail": row[4], "activo": row[5]} for row in rows]
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Error interno al obtener usuario")

def gets_usuarios(db: Session):
    try:
        sql = text("SELECT codigo, usuario, nombre, clave, mail, activo FROM Usuarios")
        result = db.execute(sql)
        rows = result.fetchall()
        return [{"codigo": row[0], "usuario": row[1], "nombre": row[2], "clave": row[3], "mail": row[4], "activo": row[5]} for row in rows]
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Error interno al obtener usuarios")

def delete_usuario(db: Session, codigo: int):
    try:
        sql = text("DELETE FROM Usuarios WHERE codigo = :codigo")
        result = db.execute(sql, {"codigo": codigo})
        db.commit()
        return result.rowcount > 0  # True if deleted, False if not found
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error interno al eliminar usuario")

def update_usuario(db: Session, codigo: int, usuario: str, clave: str, nombre: str, email: str):
    try:
        sql = text("""UPDATE Usuarios 
                     SET usuario = :usuario, clave = :clave, nombre = :nombre, mail = :email 
                     OUTPUT INSERTED.codigo AS codigo, INSERTED.Usuario AS Usuario, INSERTED.nombre AS Nombre, INSERTED.mail AS mail
                     WHERE codigo = :codigo""")
        result = db.execute(sql, {"codigo": codigo, "usuario": usuario, "clave": clave, "nombre": nombre, "email": email})
        rows = result.fetchall()
        db.commit()
        return [{"codigo": row[0], "usuario": row[1], "nombre": row[2], "email": row[3]} for row in rows]
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=400, detail="No se pudo actualizar el usuario")

def user_pass(db: Session, username: str, password: str):
    """Verifica las credenciales del usuario y retorna el hash de la contraseña si es válido"""
    try:
        from ...Services.security.security import verificar_clave
        
        # Consulta para obtener el hash de la contraseña
        sql = text("SELECT clave FROM Usuarios WHERE usuario = :usuario AND activo = 1")
        result = db.execute(sql, {"usuario": username}).first()
        
        if result and verificar_clave(password, result[0]):
            return result[0]  # Retorna el hash de la contraseña
        else:
            return False
    except Exception as e:
        logger.error(f"Error en user_pass: {str(e)}")
        return False

def update_usuario_activate(db: Session, usuario: str):
    try:
        sql = text("""UPDATE Usuarios SET activo = 1 
                     OUTPUT INSERTED.codigo AS codigo, INSERTED.Usuario AS Usuario, INSERTED.nombre AS Nombre, INSERTED.mail AS mail
                     WHERE usuario = :usuario""")
        result = db.execute(sql, {"usuario": usuario})
        rows = result.fetchall()
        db.commit()
        return [{"codigo": row[0], "usuario": row[1], "nombre": row[2], "email": row[3]} for row in rows]
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=400, detail="No se pudo actualizar el usuario")

def assign_role_to_user(db: Session, user_id: int, role_id: int):
    """Asigna un rol a un usuario usando SQL nativo"""
    try:
        # Primero verificamos si el usuario y el rol existen
        user_result = db.execute(
            text("SELECT codigo FROM Usuarios WHERE codigo = :codigo"),
            {"codigo": user_id}
        ).first()
        
        if not user_result:
            logger.warning(f"Usuario con ID {user_id} no encontrado")
            return False
        
        role_result = db.execute(
            text("SELECT id FROM roles WHERE id = :id"),
            {"id": role_id}
        ).first()
        
        if not role_result:
            logger.warning(f"Rol con ID {role_id} no encontrado")
            return False
        
        # Verificamos si la relación ya existe para evitar duplicados
        existing = db.execute(
            text("SELECT 1 FROM usuario_roles WHERE usuario_id = :user_id AND rol_id = :role_id"),
            {"user_id": user_id, "role_id": role_id}
        ).first()
        
        if existing:
            return True  # La relación ya existe, no hacemos nada
        
        # Insertamos la nueva relación
        db.execute(
            text("INSERT INTO usuario_roles (usuario_id, rol_id) VALUES (:user_id, :role_id)"),
            {"user_id": user_id, "role_id": role_id}
        )
        
        db.commit()
        logger.info(f"Rol {role_id} asignado al usuario {user_id}")
        return True
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al asignar rol: {str(e)}")
        return False

def remove_role_from_user(db: Session, user_id: int, role_id: int):
    """Remueve un rol de un usuario usando SQL nativo"""
    try:
        result = db.execute(
            text("DELETE FROM usuario_roles WHERE usuario_id = :user_id AND rol_id = :role_id"),
            {"user_id": user_id, "role_id": role_id}
        )
        
        deleted = result.rowcount > 0
        db.commit()
        
        if deleted:
            logger.info(f"Rol {role_id} removido del usuario {user_id}")
        else:
            logger.warning(f"No se encontró la relación usuario {user_id} - rol {role_id}")
            
        return deleted
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al remover rol: {str(e)}")
        return False

def has_role(db: Session, user_id: int, role_name: str):
    """Verifica si un usuario tiene un rol específico usando SQL nativo"""
    try:
        result = db.execute(
            text("""
                SELECT 1 FROM usuario_roles ur
                JOIN roles r ON ur.rol_id = r.id
                WHERE ur.usuario_id = :user_id AND r.nombre = :role_name
            """),
            {"user_id": user_id, "role_name": role_name}
        ).first()
        
        return result is not None
    except SQLAlchemyError as e:
        logger.error(f"Error al verificar rol: {str(e)}")
        return False

def get_user_roles(db: Session, user_id: int):
    """Obtiene todos los roles de un usuario usando SQL nativo"""
    try:
        result = db.execute(
            text("""
                SELECT r.id, r.nombre, r.descripcion 
                FROM roles r
                JOIN usuario_roles ur ON r.id = ur.rol_id
                WHERE ur.usuario_id = :user_id
            """),
            {"user_id": user_id}
        )
        
        roles = []
        for row in result:
            roles.append({
                "id": row[0],
                "nombre": row[1],
                "descripcion": row[2]
            })
        
        return roles
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener roles del usuario: {str(e)}")
        return []

def user_has_role(db: Session, user_id: int, role_name: str):
    """Verifica si un usuario tiene un rol específico"""
    try:
        result = db.execute(
            text("""
                SELECT 1 FROM usuario_roles ur
                JOIN roles r ON ur.rol_id = r.id
                WHERE ur.usuario_id = :user_id AND r.nombre = :role_name
            """),
            {"user_id": user_id, "role_name": role_name}
        ).first()
        
        return result is not None
    except SQLAlchemyError as e:
        logger.error(f"Error al verificar rol: {str(e)}")
        return False

def get_user_from_db(db: Session, username: str):
    """Obtiene un usuario con sus roles usando SQL directo para evitar problemas con nombres de tablas"""
    try:
        # Realizar la consulta a la tabla Usuarios usando SQL crudo
        user_result = db.execute(
            text("SELECT top(1) codigo, usuario, nombre, mail, activo, clave FROM Usuarios WHERE usuario = :usuario"),
            {"usuario": username}
        ).first()
        
        if not user_result:
            logger.warning(f"Usuario no encontrado: {username}")
            return None
        
        # Obtener los roles del usuario
        roles_result = db.execute(
            text("""
                SELECT r.id, r.nombre, r.descripcion
                FROM roles r
                JOIN usuario_roles ur ON r.id = ur.rol_id
                WHERE ur.usuario_id = :user_id
            """),
            {"user_id": user_result.codigo}
        )
        
        roles = []
        for role_row in roles_result:
            roles.append({
                "id": role_row[0],
                "nombre": role_row[1],
                "descripcion": role_row[2]
            })
        
        # Crear un diccionario con los datos del usuario
        user_data = {
            "codigo": user_result.codigo,
            "usuario": user_result.usuario,
            "nombre": user_result.nombre,
            "mail": user_result.mail,
            "activo": user_result.activo,
            "clave": user_result.clave,
            "roles": roles
        }
        
        logger.info(f"Usuario obtenido correctamente: {username}")
        return user_data
        
    except Exception as e:
        logger.error(f"Error al obtener usuario con roles: {str(e)}")
        return None

def create_role(db: Session, nombre: str, descripcion: str = None):
    """Crea un nuevo rol"""
    try:
        # Verificar si el rol ya existe
        existing = db.execute(
            text("SELECT id FROM roles WHERE nombre = :nombre"),
            {"nombre": nombre}
        ).first()
        
        if existing:
            logger.warning(f"El rol '{nombre}' ya existe")
            return None
        
        # Crear el nuevo rol
        result = db.execute(
            text("INSERT INTO roles (nombre, descripcion) OUTPUT INSERTED.id, INSERTED.nombre, INSERTED.descripcion VALUES (:nombre, :descripcion)"),
            {"nombre": nombre, "descripcion": descripcion}
        ).first()
        
        db.commit()
        logger.info(f"Rol '{nombre}' creado exitosamente")
        
        return {
            "id": result[0],
            "nombre": result[1],
            "descripcion": result[2]
        }
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al crear rol: {str(e)}")
        return None

def get_role_by_name(db: Session, nombre: str):
    """Obtiene un rol por su nombre"""
    try:
        result = db.execute(
            text("SELECT id, nombre, descripcion FROM roles WHERE nombre = :nombre"),
            {"nombre": nombre}
        ).first()
        
        if result:
            return {
                "id": result[0],
                "nombre": result[1],
                "descripcion": result[2]
            }
        else:
            return None
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener rol: {str(e)}")
        return None

def get_all_roles(db: Session, skip: int = 0, limit: int = 100):
    """Obtiene todos los roles"""
    try:
        result = db.execute(
            text("SELECT id, nombre, descripcion FROM roles ORDER BY nombre OFFSET :skip ROWS FETCH NEXT :limit ROWS ONLY"),
            {"skip": skip, "limit": limit}
        )
        
        roles = []
        for row in result:
            roles.append({
                "id": row[0],
                "nombre": row[1],
                "descripcion": row[2]
            })
        
        return roles
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener roles: {str(e)}")
        return []

def delete_role(db: Session, role_id: int):
    """Elimina un rol"""
    try:
        # Primero eliminar todas las relaciones con usuarios
        db.execute(
            text("DELETE FROM usuario_roles WHERE rol_id = :role_id"),
            {"role_id": role_id}
        )
        
        # Luego eliminar el rol
        result = db.execute(
            text("DELETE FROM roles WHERE id = :role_id"),
            {"role_id": role_id}
        )
        
        deleted = result.rowcount > 0
        db.commit()
        return deleted
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al eliminar rol: {str(e)}")
        return False
