from sqlalchemy.orm import Session
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from db.schemas.config.Usuarios import UserDB
import logging

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
            raise HTTPException(status_code=403, detail="No se pudo crear el usuario debido a un error de integridad.")
    except Exception as e:
        db.rollback()
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
            # Obtener los roles del usuario
            roles_result = db.execute(
                text("""
                    SELECT r.id, r.nombre, r.descripcion
                    FROM roles r
                    JOIN usuario_roles ur ON r.id = ur.role_id
                    WHERE ur.usuario_id = :user_id
                """),
                {"user_id": result.codigo}
            )
            
            roles = [
                {"id": role[0], "nombre": role[1], "descripcion": role[2]} 
                for role in roles_result
            ]
            
            # Crear un objeto UserDB con los datos obtenidos
            user = UserDB(
                codigo=result.codigo,
                usuario=result.usuario,
                nombre=result.nombre,
                mail=result.mail,
                activo=result.activo,
                clave=result.clave,
                roles=roles
            )
            return user
        else:
            return None
    except Exception as e:
        # Manejar posibles excepciones
        logger.error(f"Error al obtener usuario con roles: {str(e)}")
        return None
def assign_role_to_user(db: Session, user_id: int, role_id: int):
    """Asigna un rol a un usuario usando SQL nativo"""
    try:
        # Primero verificamos si el usuario y el rol existen
        user_result = db.execute(
            text("SELECT codigo FROM Usuarios WHERE codigo = :codigo"),
            {"codigo": user_id}
        ).first()
        
        role_result = db.execute(
            text("SELECT id FROM roles WHERE id = :id"),
            {"id": role_id}
        ).first()
        
        if not user_result or not role_result:
            return False
        
        # Verificamos si la relación ya existe para evitar duplicados
        existing = db.execute(
            text("SELECT 1 FROM usuario_roles WHERE usuario_id = :user_id AND role_id = :role_id"),
            {"user_id": user_id, "role_id": role_id}
        ).first()
        
        if existing:
            return True  # La relación ya existe, no hacemos nada
        
        # Insertamos la nueva relación
        db.execute(
            text("INSERT INTO usuario_roles (usuario_id, role_id) VALUES (:user_id, :role_id)"),
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
    """Elimina un rol de un usuario usando SQL nativo"""
    try:
        # Eliminar la relación
        result = db.execute(
            text("DELETE FROM usuario_roles WHERE usuario_id = :user_id AND role_id = :role_id"),
            {"user_id": user_id, "role_id": role_id}
        )
        
        # Verificar si se eliminó algo (rows_affected)
        deleted = result.rowcount > 0
        db.commit()
        
        if deleted:
            logger.info(f"Rol {role_id} eliminado del usuario {user_id}")
        
        return deleted
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al eliminar rol: {str(e)}")
        return False

def has_role(db: Session, user_id: int, role_name: str):
    """Verifica si un usuario tiene un rol específico usando SQL nativo"""
    try:
        # Consulta que verifica si el usuario tiene el rol específico
        result = db.execute(
            text("""
                SELECT 1
                FROM usuario_roles ur
                JOIN roles r ON ur.role_id = r.id
                WHERE ur.usuario_id = :user_id AND r.nombre = :role_name
            """),
            {"user_id": user_id, "role_name": role_name}
        ).first()
        
        return result is not None
    except SQLAlchemyError as e:
        logger.error(f"Error al verificar rol: {str(e)}")
        return False

def get_user_roles(db: Session, user_id: int):
    """Obtiene todos los roles de un usuario con manejo de errores mejorado"""
    try:
        # Intentar primero con la tabla UsuariosRol
        try:
            result = db.execute(
                text("""
                    SELECT r.id, r.nombre, r.descripcion
                    FROM Roles r
                    JOIN UsuariosRol ur ON r.id = ur.rol_id
                    WHERE ur.usuario_id = :user_id
                """),
                {"user_id": user_id}
            )
            
            roles = result.fetchall()
            if roles:
                logger.info(f"Roles obtenidos con tabla 'UsuariosRol' para usuario_id {user_id}")
                return [{"id": role[0], "nombre": role[1], "descripcion": role[2]} for role in roles]
        except Exception as e1:
            logger.warning(f"Error al intentar obtener roles con tabla 'UsuariosRol': {str(e1)}")
        
        # Si falla, intentar con la tabla usuario_roles
        try:
            result = db.execute(
                text("""
                    SELECT r.id, r.nombre, r.descripcion
                    FROM Roles r
                    JOIN usuario_roles ur ON r.id = ur.role_id
                    WHERE ur.usuario_id = :user_id
                """),
                {"user_id": user_id}
            )
            
            roles = result.fetchall()
            if roles:
                logger.info(f"Roles obtenidos con tabla 'usuario_roles' para usuario_id {user_id}")
                return [{"id": role[0], "nombre": role[1], "descripcion": role[2]} for role in roles]
        except Exception as e2:
            logger.warning(f"Error al intentar obtener roles con tabla 'usuario_roles': {str(e2)}")
        
        # Si ninguna consulta funcionó, verificar si el usuario es admin por ID
        if user_id == 1:  # Generalmente el primer usuario es admin
            logger.info(f"Asignando rol admin por defecto para usuario_id {user_id}")
            return [{"id": 1, "nombre": "admin", "descripcion": "Administrador del sistema"}]
        
        # Si no, devolver rol de usuario por defecto
        logger.info(f"Asignando rol usuario por defecto para usuario_id {user_id}")
        return [{"id": 2, "nombre": "usuario", "descripcion": "Usuario estándar"}]
        
    except Exception as e:
        logger.error(f"Error al obtener roles del usuario: {str(e)}")
        return []


def user_has_role(db: Session, user_id: int, role_name: str):
    """Verifica si un usuario tiene un rol específico usando SQL nativo"""
    try:
        # Consulta que verifica si el usuario tiene el rol específico
        result = db.execute(
            text("""
                SELECT 1
                FROM usuario_roles ur
                JOIN roles r ON ur.role_id = r.id
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
        
        # Crear diccionario con los datos del usuario
        user_dict = {
            "codigo": user_result.codigo,
            "usuario": user_result.usuario,
            "nombre": user_result.nombre,
            "mail": user_result.mail,
            "activo": user_result.activo,
            "clave": user_result.clave,
        }
        
        # Obtener roles directamente para evitar dependencia en get_user_roles
        try:
            # Probar diferentes nombres de tabla para diagnóstico
            roles = None
            
            # Intentar con UsuariosRol (nombre más probable según errores anteriores)
            try:
                roles_result = db.execute(
                    text("""
                        SELECT r.id, r.nombre, r.descripcion
                        FROM Roles r
                        JOIN UsuariosRol ur ON r.id = ur.rol_id
                        WHERE ur.usuario_id = :user_id
                    """),
                    {"user_id": user_result.codigo}
                )
                roles = [{"id": role[0], "nombre": role[1], "descripcion": role[2]} for role in roles_result]
                logger.info(f"Roles obtenidos con tabla 'UsuariosRol' para usuario {username}: {len(roles)} roles")
            except Exception as e1:
                logger.warning(f"Error al intentar obtener roles con tabla 'UsuariosRol': {str(e1)}")
                
                # Si falla, intentar con usuario_roles
                try:
                    roles_result = db.execute(
                        text("""
                            SELECT r.id, r.nombre, r.descripcion
                            FROM Roles r
                            JOIN usuario_roles ur ON r.id = ur.role_id
                            WHERE ur.usuario_id = :user_id
                        """),
                        {"user_id": user_result.codigo}
                    )
                    roles = [{"id": role[0], "nombre": role[1], "descripcion": role[2]} for role in roles_result]
                    logger.info(f"Roles obtenidos con tabla 'usuario_roles' para usuario {username}: {len(roles)} roles")
                except Exception as e2:
                    logger.warning(f"Error al intentar obtener roles con tabla 'usuario_roles': {str(e2)}")
            
            # Si ningún intento funcionó, crear roles por defecto
            if roles is None:
                # Si ambas consultas fallan, asignar el rol por defecto
                if username.lower() in ['admin', 'administrator', 'administrador']:
                    roles = [{"id": 1, "nombre": "admin", "descripcion": "Administrador del sistema"}]
                    logger.info(f"Asignando rol de admin por defecto a {username}")
                else:
                    roles = [{"id": 2, "nombre": "usuario", "descripcion": "Usuario estándar"}]
                    logger.info(f"Asignando rol de usuario por defecto a {username}")
            
            user_dict["roles"] = roles
            
            # Determinar rol principal
            if roles:
                # Buscar primero el rol de admin si existe
                admin_role = next((r for r in roles if r["nombre"].lower() == "admin"), None)
                if admin_role:
                    user_dict["rol_principal"] = "admin"
                else:
                    # Usar el primer rol como principal
                    user_dict["rol_principal"] = roles[0]["nombre"]
            else:
                user_dict["rol_principal"] = "usuario"
                
        except Exception as e:
            logger.error(f"Error al procesar roles: {str(e)}")
            # En caso de error en cualquier parte, asignar rol por defecto
            if username.lower() in ['admin', 'administrator', 'administrador']:
                user_dict["roles"] = [{"id": 1, "nombre": "admin", "descripcion": "Administrador del sistema"}]
                user_dict["rol_principal"] = "admin"
            else:
                user_dict["roles"] = [{"id": 2, "nombre": "usuario", "descripcion": "Usuario estándar"}]
                user_dict["rol_principal"] = "usuario"
        
        logger.info(f"Usuario obtenido correctamente: {username}, rol principal: {user_dict.get('rol_principal')}")
        return user_dict
        
    except Exception as e:
        logger.error(f"Error general al obtener usuario: {str(e)}")
        return None


def create_role(db: Session, nombre: str, descripcion: str = None):
    """Crea un nuevo rol"""
    try:
        result = db.execute(
            text("""
                INSERT INTO roles (nombre, descripcion)
                OUTPUT INSERTED.id, INSERTED.nombre, INSERTED.descripcion
                VALUES (:nombre, :descripcion)
            """),
            {"nombre": nombre, "descripcion": descripcion}
        )
        
        row = result.first()
        db.commit()
        
        return {"id": row[0], "nombre": row[1], "descripcion": row[2]}
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al crear rol: {str(e)}")
        raise HTTPException(status_code=400, detail=f"No se pudo crear el rol: {str(e)}")

def get_role_by_name(db: Session, nombre: str):
    """Obtiene un rol por su nombre"""
    try:
        result = db.execute(
            text("SELECT id, nombre, descripcion FROM roles WHERE nombre = :nombre"),
            {"nombre": nombre}
        ).first()
        
        if not result:
            return None
        
        return {"id": result[0], "nombre": result[1], "descripcion": result[2]}
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
        
        roles = result.fetchall()
        return [{"id": role[0], "nombre": role[1], "descripcion": role[2]} for role in roles]
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener roles: {str(e)}")
        return []

def delete_role(db: Session, role_id: int):
    """Elimina un rol"""
    try:
        # Primero eliminar todas las relaciones con usuarios
        db.execute(
            text("DELETE FROM usuario_roles WHERE role_id = :role_id"),
            {"role_id": role_id}
        )
        
        # Luego eliminar el rol
        result = db.execute(
            text("DELETE FROM roles WHERE id = :role_id"),
            {"role_id": role_id}
        )
        
        if result.rowcount == 0:
            return False
        
        db.commit()
        return True
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al eliminar rol: {str(e)}")
        raise HTTPException(status_code=400, detail=f"No se pudo eliminar el rol: {str(e)}")