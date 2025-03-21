from fastapi import HTTPException, Depends, status, Request
from sqlalchemy.orm import Session
from db.database import get_db
from db.crud.config.Usuarios import get_usuario, user_pass, get_user_from_db
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from dotenv import load_dotenv
import os
from pydantic import BaseModel
from typing import Dict, List, Optional,Union
from db.schemas.config.Usuarios import UserDB
import logging
from .rate_limit import check_rate_limit
from db.crud.config.Usuarios import has_role

# Carga las variables de entorno del archivo .env
load_dotenv()

# Configuración
SECRET = os.getenv("SECRET")
ALGORITHM = os.getenv("ALGORITHM")
REFRESH_TOKEN_DURATION = int(os.getenv("REFRESH_TOKEN_DURATION", 7 * 24 * 60))  # 7 días por defecto
ACCESS_TOKEN_DURATION = int(os.getenv("ACCESS_TOKEN_DURATION", 30))  # 30 minutos por defecto

# Configuración de logging
logger = logging.getLogger("refresh_token")

# Almacén temporal de tokens invalidados (idealmente esto debería estar en una base de datos)
# Clave: token, Valor: tiempo de expiración
revoked_tokens: Dict[str, datetime] = {}

# Modelo de datos para el token
class TokenData(BaseModel):
    username: Optional[str] = None

# Configuración de passlib
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2 = OAuth2PasswordBearer(tokenUrl="/login", auto_error=False)

# Calcular el tiempo de expiración del token
access_token_expires = timedelta(minutes=ACCESS_TOKEN_DURATION)


def encriptar_clave(clave):
    return pwd_context.hash(clave)

def verificar_clave(password: str, hashed_password: str) -> bool:
    return pwd_context.verify(password, hashed_password)

def decodifica_token(token: str):
    if not token:
        logger.warning("Intento de decodificar un token vacío")
        return None
        
    try:
        # Simplificamos la manipulación del token
        payload = jwt.decode(token, SECRET, algorithms=[ALGORITHM])
        usuario = payload.get("sub")
        return usuario
    except jwt.ExpiredSignatureError:
        logger.warning(f"Token expirado")
        return None
    except jwt.InvalidTokenError:
        logger.warning(f"Token inválido")
        return None



def crear_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_DURATION)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET, algorithm=ALGORITHM)

# Modificar la función authenticate_user:
def authenticate_user(db: Session, username: str, password: str, request: Request = None):
    """
    Autentica un usuario verificando su nombre y contraseña, y devuelve información completa.
    También obtiene los roles del usuario, manejando posibles errores con la tabla de roles.
    """
    # Verificar rate limiting si se proporciona una solicitud
    if request:
        check_rate_limit(request, username)
    
    try:    
        # Obtener información básica de autenticación
        user_info = user_pass(db, username, password)
        if not user_info:
            logger.warning(f"Intento de inicio de sesión fallido para usuario inexistente: {username}")
            return None
        
        hashed_password = user_info["password"]
        if not verificar_clave(password, hashed_password):
            logger.warning(f"Contraseña incorrecta para usuario: {username}")
            return None
        
        # Obtener información completa del usuario
        from db.models.config.usuarios import usuarios as UsuariosModel
        
        # Obtener el usuario completo de la base de datos
        user = db.query(UsuariosModel).filter(UsuariosModel.usuario == username).first()
        if not user:
            logger.warning(f"Usuario autenticado pero no encontrado en la base de datos: {username}")
            return None
        
        # Crear diccionario con datos completos del usuario
        user_dict = {
            "username": user.usuario,
            "mail": user.mail,
            "nombre": user.nombre,
            "codigo": user.codigo,
            "activo": user.activo,
            "password": hashed_password
        }
        
        # Intentar obtener roles del usuario con SQL directo (evitando problemas con la tabla)
        try:
            from sqlalchemy import text
            
            # Usar consulta SQL directa con el nombre correcto de la tabla
            # IMPORTANTE: Asegúrate de ajustar 'UsuariosRol' al nombre real en tu base de datos
            result = db.execute(text("""
                SELECT r.id, r.nombre, r.descripcion
                FROM Roles r
                JOIN UsuariosRol ur ON r.id = ur.rol_id
                WHERE ur.usuario_id = :usuario_id
            """), {"usuario_id": user.codigo})
            
            # Convertir resultados a lista de diccionarios
            roles = [{"id": row[0], "nombre": row[1], "descripcion": row[2]} for row in result]
            
            if roles:
                user_dict["roles"] = roles
                user_dict["rol_principal"] = roles[0]["nombre"]
                logger.info(f"Roles obtenidos para {username}: {[r['nombre'] for r in roles]}")
            else:
                # Si el usuario no tiene roles asignados, asignar un rol por defecto
                user_dict["roles"] = [{"id": 0, "nombre": "usuario", "descripcion": "Usuario estándar"}]
                user_dict["rol_principal"] = "usuario"
                logger.info(f"No se encontraron roles para {username}, asignando rol por defecto")
        
        except Exception as e:
            # En caso de error al obtener roles, asignar un rol por defecto
            logger.error(f"Error al obtener roles para {username}: {str(e)}")
            user_dict["roles"] = [{"id": 0, "nombre": "usuario", "descripcion": "Usuario estándar"}]
            user_dict["rol_principal"] = "usuario"
        
        logger.info(f"Usuario autenticado correctamente: {username}")
        return user_dict
        
    except Exception as e:
        logger.error(f"Error en authenticate_user: {str(e)}")
        return None

def auth_user(token: str = Depends(oauth2), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        user = get_user_from_db(db, username)
        if user is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    return user
def authenticate_user(db: Session, username: str, password: str, request: Request = None):
    """
    Autentica un usuario verificando su nombre y contraseña, y devuelve información completa.
    También obtiene los roles del usuario, manejando posibles errores con la tabla de roles.
    """
    # Verificar rate limiting si se proporciona una solicitud
    if request:
        check_rate_limit(request, username)
    
    try:    
        # Obtener información básica de autenticación
        user_info = user_pass(db, username, password)
        if not user_info:
            logger.warning(f"Intento de inicio de sesión fallido para usuario inexistente: {username}")
            return None
        
        hashed_password = user_info["password"]
        if not verificar_clave(password, hashed_password):
            logger.warning(f"Contraseña incorrecta para usuario: {username}")
            return None
        
        # Obtener información completa del usuario
        from db.models.config.usuarios import usuarios as UsuariosModel
        
        # Obtener el usuario completo de la base de datos
        user = db.query(UsuariosModel).filter(UsuariosModel.usuario == username).first()
        if not user:
            logger.warning(f"Usuario autenticado pero no encontrado en la base de datos: {username}")
            return None
        
        # Crear diccionario con datos completos del usuario
        user_dict = {
            "username": user.usuario,
            "mail": user.mail,
            "nombre": user.nombre,
            "codigo": user.codigo,
            "activo": user.activo,
            "password": hashed_password
        }
        
        # Intentar obtener roles del usuario con SQL directo (evitando problemas con la tabla)
        try:
            from sqlalchemy import text
            
            # Usar consulta SQL directa con el nombre correcto de la tabla
            # IMPORTANTE: Asegúrate de ajustar 'UsuariosRol' al nombre real en tu base de datos
            result = db.execute(text("""
                SELECT r.id, r.nombre, r.descripcion
                FROM Roles r
                JOIN UsuariosRol ur ON r.id = ur.rol_id
                WHERE ur.usuario_id = :usuario_id
            """), {"usuario_id": user.codigo})
            
            # Convertir resultados a lista de diccionarios
            roles = [{"id": row[0], "nombre": row[1], "descripcion": row[2]} for row in result]
            
            if roles:
                user_dict["roles"] = roles
                user_dict["rol_principal"] = roles[0]["nombre"]
                logger.info(f"Roles obtenidos para {username}: {[r['nombre'] for r in roles]}")
            else:
                # Si el usuario no tiene roles asignados, asignar un rol por defecto
                user_dict["roles"] = [{"id": 0, "nombre": "usuario", "descripcion": "Usuario estándar"}]
                user_dict["rol_principal"] = "usuario"
                logger.info(f"No se encontraron roles para {username}, asignando rol por defecto")
        
        except Exception as e:
            # En caso de error al obtener roles, asignar un rol por defecto
            logger.error(f"Error al obtener roles para {username}: {str(e)}")
            user_dict["roles"] = [{"id": 0, "nombre": "usuario", "descripcion": "Usuario estándar"}]
            user_dict["rol_principal"] = "usuario"
        
        logger.info(f"Usuario autenticado correctamente: {username}")
        return user_dict
        
    except Exception as e:
        logger.error(f"Error en authenticate_user: {str(e)}")
        return None

def generar_token_activacion(usuario_id):
    payload = {
        'usuario_id': usuario_id,
        'exp': datetime.utcnow() + timedelta(days=1)  # Expira en 1 día
    }
    token = jwt.encode(payload, SECRET, algorithm=ALGORITHM)
    return token

async def get_current_user(request: Request, db: Session = Depends(get_db)):
    """
    Función que autentica al usuario mediante un token JWT y devuelve siempre un objeto UserDB.
    
    Args:
        request: Objeto Request de FastAPI
        db: Sesión de base de datos
        
    Returns:
        UserDB: Objeto de usuario autenticado
        
    Raises:
        HTTPException: Si el token es inválido, expirado, o el usuario no está autorizado
    """
    # Añadir logs para depuración
    logger.info(f"Intentando autenticar usuario en ruta: {request.url.path}")
    
    # Obtener el token de la cookie
    token = request.cookies.get('access_token')
    logger.info(f"Token en cookies: {'Presente' if token else 'No encontrado'}")
    
    if not token:
        # Intentar obtener el token del encabezado Authorization
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            logger.info(f"Token extraído del header Authorization")
    
    if not token:
        logger.warning("Acceso denegado: Token no proporcionado")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token no proporcionado",
            headers={"Location": "/login"},
        )

    try:
        # Decodificar el token
        payload = jwt.decode(token, SECRET, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            logger.warning("Token inválido: no contiene username")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido",
                headers={"Location": "/login"},
            )
        
        logger.info(f"Token decodificado correctamente para usuario: {username}")
        
        # Obtener usuario de la base de datos
        user = get_user_from_db(db, username)
        if user is None:
            logger.warning(f"Usuario no encontrado en la base de datos: {username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario no encontrado",
                headers={"Location": "/login"},
            )
        
        # Convertir el usuario a objeto UserDB si es un diccionario
        if isinstance(user, dict):
            # Verificar si el usuario está activo antes de crear el objeto UserDB
            if not user.get("activo", False):
                logger.warning(f"Usuario deshabilitado (dict): {username}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Usuario deshabilitado",
                    headers={"Location": "/login"},
                )
            
            # Extraer los roles si existen
            roles_data = user.get("roles", [])
            roles = []
            
            # Convertir roles a objetos Role si son diccionarios
            for role_data in roles_data:
                if isinstance(role_data, dict):
                    from db.schemas.config.Usuarios import Role
                    roles.append(Role(**role_data))
                else:
                    roles.append(role_data)
            
            # Convertir el diccionario user a un objeto UserDB
            user_db = UserDB(
                codigo=user.get("codigo"),
                usuario=user.get("usuario"),
                nombre=user.get("nombre"),
                mail=user.get("mail"),
                telefono=user.get("telefono"),
                direccion=user.get("direccion"),
                fecha_nacimiento=user.get("fecha_nacimiento"),
                activo=user.get("activo", True),
                roles=roles
            )
            user = user_db
        else:
            # Ya es un objeto pero verificamos si tiene el atributo activo
            if hasattr(user, "activo") and not user.activo:
                logger.warning(f"Usuario deshabilitado (object): {username}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Usuario deshabilitado",
                    headers={"Location": "/login"},
                )
        
        logger.info(f"Usuario autenticado correctamente: {username}")
        return user
    except jwt.ExpiredSignatureError:
        logger.warning(f"Token expirado")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="La sesión ha expirado. Por favor, inicie sesión nuevamente.",
            headers={"Location": "/login"},
        )
    except JWTError as e:
        logger.warning(f"Error al decodificar token: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token inválido: {str(e)}",
            headers={"Location": "/login"},
        )

async def get_authenticated_user(
    request: Request = None, 
    token: str = Depends(oauth2), 
    db: Session = Depends(get_db)
):
    # Añadir logging para depuración
    logger.info(f"Intentando autenticar usuario. Token desde OAuth2: {bool(token)}")
    if request:
        cookies = request.cookies.get('access_token')
        auth_header = request.headers.get('Authorization')
        logger.info(f"Request disponible. Token en cookies: {bool(cookies)}, Token en header: {bool(auth_header and auth_header.startswith('Bearer '))}")

    # Obtener el token primero desde OAuth2, luego de cookies o headers
    actual_token = token
    
    if not actual_token and request:
        # Obtener de cookie
        actual_token = request.cookies.get('access_token')
        
        if not actual_token:
            # Obtener de header Authorization
            auth_header = request.headers.get('Authorization')
            if auth_header and auth_header.startswith('Bearer '):
                actual_token = auth_header.split(' ')[1]
    
    if not actual_token:
        logger.warning("Acceso denegado: Token no proporcionado")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token no proporcionado",
            headers={"Location": "/loginpage"},
        )

    try:
        # Decodificar el token
        payload = jwt.decode(actual_token, SECRET, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            logger.warning("Acceso denegado: Token inválido (sin username)")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido",
                headers={"Location": "/loginpage"},
            )
        
        # Obtener usuario de la base de datos
        user = get_user_from_db(db, username)
        if user is None:
            logger.warning(f"Acceso denegado: Usuario no encontrado: {username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario no encontrado",
                headers={"Location": "/loginpage"},
            )
        
        # Convertir el usuario a objeto UserDB si es un diccionario
        if isinstance(user, dict):
            # Extraer los roles si existen
            roles = user.get("roles", [])
            
            # Convertir el diccionario user a un objeto UserDB
            user_db = UserDB(
                codigo=user.get("codigo"),
                usuario=user.get("usuario"),
                nombre=user.get("nombre"),
                mail=user.get("mail"),
                telefono=user.get("telefono"),
                direccion=user.get("direccion"),
                fecha_nacimiento=user.get("fecha_nacimiento"),
                activo=user.get("activo", True),
                roles=roles
            )
            user = user_db
        
        # Verificar si el usuario está activo
        if not user.activo:
            logger.warning(f"Acceso denegado: Usuario deshabilitado: {username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario deshabilitado",
                headers={"Location": "/loginpage"},
            )
        
        logger.info(f"Usuario autenticado correctamente: {username}")
        return user
    except JWTError as e:
        logger.warning(f"Acceso denegado: Token inválido: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token inválido: {str(e)}",
            headers={"Location": "/loginpage"},
        )
# Verificar si un usuario tiene un rol específico
def user_has_role(user, role_name: str) -> bool:
    """Verifica si un usuario tiene un rol específico"""
    if not user:
        return False
        
    # Si el usuario es un diccionario
    if isinstance(user, dict):
        if "roles" not in user or not user["roles"]:
            return False
        return any(role.get("nombre") == role_name for role in user["roles"])
    
    # Si el usuario es un objeto
    if hasattr(user, "roles"):
        if not user.roles:
            return False
            
        # Si los roles son diccionarios
        if user.roles and isinstance(user.roles[0], dict):
            return any(role.get("nombre") == role_name for role in user.roles)
        # Si los roles son objetos con propiedad 'nombre'
        elif user.roles and hasattr(user.roles[0], "nombre"):
            return any(role.nombre == role_name for role in user.roles)
        # Si son objetos pero sin propiedad 'nombre' reconocible
        else:
            return any(getattr(role, "nombre", None) == role_name for role in user.roles)
    
    return False



# Verificar si un usuario tiene alguno de los roles especificados
def user_has_any_role(user, role_names: list) -> bool:
    """Verifica si un usuario tiene alguno de los roles especificados"""
    if not user:
        return False
        
    # Si el usuario es un diccionario
    if isinstance(user, dict):
        if "roles" not in user or not user["roles"]:
            return False
        return any(role.get("nombre") in role_names for role in user["roles"])
    
    # Si el usuario es un objeto
    if hasattr(user, "roles"):
        if not user.roles:
            return False
            
        # Si los roles son diccionarios
        if user.roles and isinstance(user.roles[0], dict):
            return any(role.get("nombre") in role_names for role in user.roles)
        # Si los roles son objetos con propiedad 'nombre'
        elif user.roles and hasattr(user.roles[0], "nombre"):
            return any(role.nombre in role_names for role in user.roles)
        # Si son objetos pero sin propiedad 'nombre' reconocible
        else:
            return any(getattr(role, "nombre", None) in role_names for role in user.roles)
    
    return False


# Verificar si un usuario tiene alguno de los roles especificados
def user_has_any_role(user, role_names: list) -> bool:
    """Verifica si un usuario tiene alguno de los roles especificados"""
    if not user or "roles" not in user:
        return False
    return any(role["nombre"] in role_names for role in user["roles"])


# Dependencia para requerir un rol específico
async def require_role(role_name: str, user = Depends(get_current_user)):
    """Dependencia que requiere que el usuario tenga un rol específico"""
    if not user_has_role(user, role_name):
        # Extraer el nombre de usuario de forma segura
        if isinstance(user, dict):
            username = user.get("usuario", "desconocido")
        else:
            username = getattr(user, "usuario", "desconocido")
            
        logger.warning(f"Acceso denegado: Usuario {username} no tiene el rol {role_name}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Se requiere el rol '{role_name}' para acceder a esta ruta",
            headers={"Location": "/unauthorized"}
        )
    return user

# Dependencia para requerir al menos uno de varios roles
async def require_any_role(role_names: List[str], user = Depends(get_current_user)):
    """Dependencia que requiere que el usuario tenga al menos uno de los roles especificados"""
    if not user_has_any_role(user, role_names):
        # Extraer el nombre de usuario de forma segura
        if isinstance(user, dict):
            username = user.get("usuario", "desconocido")
        else:
            username = getattr(user, "usuario", "desconocido")
            
        logger.warning(f"Acceso denegado: Usuario {username} no tiene ninguno de los roles {role_names}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Se requiere uno de estos roles para acceder: {', '.join(role_names)}",
            headers={"Location": "/unauthorized"}
        )
    return user

# Dependencia para requerir rol de admin con logging adicional
async def require_admin(
    db: Session = Depends(get_db),
    user: UserDB = Depends(get_authenticated_user)
):
    """Dependencia que requiere que el usuario tenga rol de administrador"""
    try:
        # Verificar roles directamente con SQL para evitar problemas
        from sqlalchemy import text
        
        # Consulta SQL directa con el nombre correcto de la tabla
        result = db.execute(text("""
            SELECT r.nombre
            FROM Roles r
            JOIN UsuariosRol ur ON r.id = ur.rol_id
            WHERE ur.usuario_id = :usuario_id
        """), {"usuario_id": user.codigo})
        
        # Convertir resultados a lista
        roles_nombres = [row[0] for row in result]
        
        # Verificar si el usuario tiene rol de admin
        is_admin = "admin" in roles_nombres
        
        logger.info(f"Verificando rol admin para usuario: {user.usuario} - Roles: {roles_nombres} - Es admin: {is_admin}")
        
        if not is_admin:
            # Intentar verificar si el usuario es admin por su nombre
            if user.usuario.lower() in ["admin", "administrator", "administrador"]:
                logger.info(f"Usuario {user.usuario} considerado admin por nombre de usuario")
                return user
                
            logger.warning(f"Acceso denegado: Usuario {user.usuario} no tiene rol de administrador")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Se requiere rol de administrador para acceder a esta ruta",
                headers={"Location": "/unauthorized"}
            )
        
        return user
    except Exception as e:
        # Si hay errores con la tabla de roles, verificar directamente por nombre de usuario
        logger.error(f"Error verificando rol admin por SQL: {str(e)}")
        
        # Verificación alternativa: considerar admin si el usuario se llama "admin"
        if user.usuario.lower() in ["admin", "administrator", "administrador"]:
            logger.info(f"Usuario {user.usuario} considerado admin por nombre de usuario (fallback)")
            return user
            
        # Dar acceso temporal a todos los usuarios mientras se resuelve el problema
        # Descomentar la siguiente línea para dar acceso temporal a todos
        # return user
        
        # O denegar acceso por defecto si hay error
        logger.warning(f"Acceso denegado: Error al verificar roles y usuario {user.usuario} no parece ser admin")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requiere rol de administrador para acceder a esta ruta",
            headers={"Location": "/unauthorized"}
        )


# Mantener aliases para compatibilidad con código existente
current_user = get_authenticated_user
get_current_user = get_authenticated_user
auth_user = get_authenticated_user

