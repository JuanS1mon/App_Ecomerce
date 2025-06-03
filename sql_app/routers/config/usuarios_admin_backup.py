from fastapi import APIRouter, Depends, HTTPException, Request, Form, Body
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
import re
from datetime import datetime
from passlib.context import CryptContext

try:
    from ...db.database import get_db
except ImportError:
    from sql_app.db.database import get_db
# Importar el modelo SQLAlchemy para las consultas a la BD
try:
    from ...db.models.config.usuarios_rol import usuarios_rol as UsuariosRolModel
except ImportError:
    from sql_app.db.models.config.usuarios_rol import usuarios_rol as UsuariosRolModel
# Importar el esquema Pydantic para las respuestas
try:
    from ...db.schemas.config.Usuarios import Usuario as UserSchema
except ImportError:
    from sql_app.db.schemas.config.Usuarios import Usuario as UserSchema
# Para manejar contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter(
    prefix="/usuarios_admin",
    tags=["Usuarios"],
    include_in_schema=False,
)

# Configuración de templates
templates = Jinja2Templates(directory="static/html")

# ----- Rutas para vistas -----

@router.get("", response_class=HTMLResponse)
async def pagina_usuarios(request: Request, user: UserSchema = Depends(require_admin)):
    """Renderiza la página de administración de usuarios"""
    return templates.TemplateResponse("usuarios/usuarios_admin.html", {
        "request": request,
        "user": user,
        "titulo": "Gestión de Usuarios"
    })

@router.get("/roles", response_class=HTMLResponse)
async def pagina_usuarios(request: Request, user: UserSchema = Depends(require_admin)):
    """Renderiza la página de administración de usuarios"""
    return templates.TemplateResponse("usuarios/usuario_roles.html", {
        "request": request,
        "user": user,
        "titulo": "Gestión de roles"
    })

@router.get("/usuarios-roles", response_class=HTMLResponse)
async def pagina_usuarios(request: Request, user: UserSchema = Depends(require_admin)):
    """Renderiza la página de administración de usuarios"""
    return templates.TemplateResponse("usuarios/usuarios_roles.html", {
        "request": request,
        "user": user,
        "titulo": "Gestión de Usuarios y roles"
    })

@router.get("/permisos", response_class=HTMLResponse)
async def pagina_usuarios(request: Request, user: UserSchema = Depends(require_admin)):
    """Renderiza la página de administración de usuarios"""
    return templates.TemplateResponse("usuarios/usuarios_permisos.html", {
        "request": request,
        "user": user,
        "titulo": "Gestión de Permisos"
    })


@router.get("/usuarios", response_model=Dict[str, Any], )
async def listar_usuarios(request: Request,db: Session = Depends(get_db),page: int = 1,limit: int = 10,search: Optional[str] = None,rol: Optional[str] = None,
    estado: Optional[str] = None,user: UserSchema = Depends(require_admin)
):
    """Obtiene la lista paginada de usuarios con filtros opcionales"""
    # Importar modelos y SQL directo
try:
    from ...db.models.config.usuarios import usuarios as UsuariosModel
except ImportError:
    from sql_app.db.models.config.usuarios import usuarios as UsuariosModel
    print("Ejecutando endpoint listar_usuarios")
    
    try:
        # Iniciar la consulta usando el modelo SQLAlchemy
        query = db.query(UsuariosModel)
        
        # Aplicar filtros
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                (UsuariosModel.usuario.ilike(search_term)) |
                (UsuariosModel.nombre.ilike(search_term)) |
                (UsuariosModel.mail.ilike(search_term))
            )
        
        # Filtro por estado
        if estado:
            estado_valor = True if estado.lower() == "activo" else False
            query = query.filter(UsuariosModel.activo == estado_valor)
        
        # Filtro por rol es más complicado debido al problema con la tabla de roles
        # No lo aplicamos aquí, filtraremos después por rol si es necesario
        
        # Contar total de registros después de filtrar pero antes de paginar
        total_usuarios = query.count()
        print(f"Total de usuarios encontrados (sin paginación): {total_usuarios}")
        
        # Calcular total de páginas (mínimo 1)
        total_pages = max(1, (total_usuarios + limit - 1) // limit)
        
        # Asegurarnos de que la página solicitada está dentro del rango válido
        page = min(max(1, page), total_pages)
        
        # Aplicar orden y paginación
        query = query.order_by(UsuariosModel.codigo)
        usuarios = query.offset((page - 1) * limit).limit(limit).all()
        
        print(f"Usuarios recuperados para página {page}: {len(usuarios)}")
        
        # Preparar la respuesta JSON
        usuarios_list = []
        for usuario in usuarios:
            # En lugar de usar join, obtener roles con SQL directo para diagnóstico
            try:
                # Intentar con tabla 'UsuariosRol'
                roles_result = db.execute(
                    text("""
                        SELECT r.id, r.nombre, r.descripcion
                        FROM Roles r
                        JOIN UsuariosRol ur ON r.id = ur.rol_id
                        WHERE ur.usuario_id = :user_id
                    """),
                    {"user_id": usuario.codigo}
                )
                
                roles = [{"id": role[0], "nombre": role[1], "descripcion": role[2]} for role in roles_result]
                print(f"Roles obtenidos para usuario {usuario.codigo} usando tabla 'UsuariosRol': {roles}")
                
            except Exception as e1:
                print(f"Error con 'UsuariosRol' para usuario {usuario.codigo}: {str(e1)}")
                
                try:
                    # Intentar con tabla 'usuario_roles'
                    roles_result = db.execute(
                        text("""
                            SELECT r.id, r.nombre, r.descripcion
                            FROM Roles r
                            JOIN usuario_roles ur ON r.id = ur.role_id
                            WHERE ur.usuario_id = :user_id
                        """),
                        {"user_id": usuario.codigo}
                    )
                    
                    roles = [{"id": role[0], "nombre": role[1], "descripcion": role[2]} for role in roles_result]
                    print(f"Roles obtenidos para usuario {usuario.codigo} usando tabla 'usuario_roles': {roles}")
                    
                except Exception as e2:
                    print(f"Error con 'usuario_roles' para usuario {usuario.codigo}: {str(e2)}")
                    roles = []
            
            # Filtrar por rol si se especificó
            if rol and not roles:
                continue  # No incluir este usuario si no tiene el rol especificado
                
            if rol and all(r["nombre"] != rol for r in roles):
                continue  # No incluir este usuario si no tiene el rol especificado
            
            # Determinar rol principal
            rol_principal = roles[0]["nombre"] if roles else "usuario"
            
            # Crear diccionario del usuario con sus roles
            user_dict = {
                "id": usuario.codigo,
                "usuario": usuario.usuario,
                "nombre": usuario.nombre or "",
                "email": usuario.mail or "",
                "rol": rol_principal,
                "roles": roles,
                "estado": "activo" if usuario.activo else "inactivo"
            }
            usuarios_list.append(user_dict)
        
        # Ajustar total si filtramos por rol después de la consulta
        if rol:
            total_usuarios = len(usuarios_list)
            total_pages = max(1, (total_usuarios + limit - 1) // limit)
        
        # Devolver respuesta con paginación
        response = {
            "usuarios": usuarios_list,
            "total": total_usuarios,
            "pagina": page,
            "paginas": total_pages,
            "por_pagina": limit
        }
        
        print(f"Respuesta generada con {len(usuarios_list)} usuarios")
        return response
        
    except Exception as e:
        print(f"ERROR GENERAL en listar_usuarios: {str(e)}")
        print(f"Tipo de error: {type(e).__name__}")
        
        import traceback
        traceback.print_exc()
        
        # Devolver una respuesta vacía pero válida en caso de error
        return {
            "usuarios": [],
            "total": 0,
            "pagina": 1,
            "paginas": 1,
            "por_pagina": limit,
            "error": f"Error al obtener usuarios: {str(e)}"
        }

@router.post("/usuarios", response_model=Dict[str, Any])
async def crear_usuario(
    datos: Dict[str, Any] = Body(...),
    db: Session = Depends(get_db),
    user: UserSchema = Depends(current_user)
):
    """Crea un nuevo usuario con su rol asignado"""
    # Importar modelos con nombres consistentes
    from sqlalchemy import func
try:
    from ...db.models.config.usuarios import usuarios as UsuariosModel
except ImportError:
    from sql_app.db.models.config.usuarios import usuarios as UsuariosModel
    # Validaciones de datos
    if not datos.get("usuario"):
        raise HTTPException(status_code=422, detail="El nombre de usuario es obligatorio")
    
    if not datos.get("email"):
        raise HTTPException(status_code=422, detail="El correo electrónico es obligatorio")
    
    if not datos.get("password"):
        raise HTTPException(status_code=422, detail="La contraseña es obligatoria")
    
    # Verificar que el usuario no exista
    usuario_existente = db.query(UsuariosModel).filter(
        UsuariosModel.usuario == datos["usuario"]
    ).first()
    
    if usuario_existente:
        raise HTTPException(status_code=400, detail="El nombre de usuario ya está en uso")
    
    # Verificar que el email no exista
    email_existente = db.query(UsuariosModel).filter(
        UsuariosModel.mail == datos["email"]
    ).first()
    
    if email_existente:
        raise HTTPException(status_code=400, detail="El correo electrónico ya está registrado")
    
    try:
        # Generar nuevo ID para el usuario
        max_codigo = db.query(func.max(UsuariosModel.codigo)).scalar() or 0
        nuevo_codigo = max_codigo + 1
        
        print(f"Creando usuario con código: {nuevo_codigo}")
        
        # Crear el nuevo usuario
        nuevo_usuario = UsuariosModel(
            codigo=nuevo_codigo,
            usuario=datos["usuario"],
            nombre=datos.get("nombre", ""),
            mail=datos["email"],
            clave=pwd_context.hash(datos["password"]),
            activo=datos.get("estado", "activo") == "activo"
        )
        
        db.add(nuevo_usuario)
        db.flush()  # Para obtener el ID sin hacer commit
        
        print(f"Usuario creado con código: {nuevo_usuario.codigo}")
        
        # Asignar rol al usuario si se especificó
        if datos.get("rol"):
            print(f"Asignando rol: {datos['rol']}")
            
            # Buscar el rol por nombre
            rol = db.query(RolesModel).filter(
                RolesModel.nombre == datos["rol"]
            ).first()
            
            # Si el rol no existe, crearlo
            if not rol:
                print(f"Rol no encontrado, creando nuevo rol: {datos['rol']}")
                rol = RolesModel(
                    nombre=datos["rol"],
                    descripcion=f"Rol {datos['rol']}"
                )
                db.add(rol)
                db.flush()
                print(f"Rol creado con ID: {rol.id}")
            else:
                print(f"Rol encontrado con ID: {rol.id}")
            
            # Crear la relación usuario-rol
            usuario_rol = UsuariosRolModel(
                usuario_id=nuevo_usuario.codigo,
                rol_id=rol.id
            )
            
            print(f"Creando relación usuario-rol: usuario_id={usuario_rol.usuario_id}, rol_id={usuario_rol.rol_id}")
            
            db.add(usuario_rol)
            print("Relación usuario-rol creada")
        else:
            print("No se especificó rol, usando rol por defecto")
            # Opcionalmente, asignar rol por defecto si no se especificó
            rol_default = db.query(RolesModel).filter(
                RolesModel.nombre == "usuario"
            ).first()
            
            if rol_default:
                usuario_rol = UsuariosRolModel(
                    usuario_id=nuevo_usuario.codigo,
                    rol_id=rol_default.id
                )
                db.add(usuario_rol)
                print(f"Asignado rol por defecto: {rol_default.nombre}")
        
        # Confirmar los cambios
        db.commit()
        print("Cambios guardados en la base de datos")
        
        return {
            "id": nuevo_usuario.codigo,
            "usuario": nuevo_usuario.usuario,
            "mensaje": "Usuario creado correctamente"
        }
    except Exception as e:
        db.rollback()
        print(f"Error al crear usuario: {str(e)}")
        print(f"Tipo de error: {type(e).__name__}")
        print(f"Detalles del error: {str(e)}")
        
        if hasattr(e, '__traceback__'):
            import traceback
            print("Traceback:")
            traceback.print_tb(e.__traceback__)
            
        raise HTTPException(status_code=500, detail=f"Error al crear el usuario: {str(e)}")
    
@router.put("/usuarios/{id}", response_model=Dict[str, Any])
async def actualizar_usuario(
    id: int,
    datos: Dict[str, Any] = Body(...),
    db: Session = Depends(get_db),
    user: UserSchema = Depends(current_user)
):
    """Actualiza un usuario existente y su rol"""
    # Importar modelos
try:
    from ...db.models.config.usuarios import usuarios as UsuariosModel
except ImportError:
    from sql_app.db.models.config.usuarios import usuarios as UsuariosModel
    print(f"Intentando actualizar usuario con ID: {id}")
    print(f"Datos recibidos: {datos}")
    
    # Verificar que el usuario exista
    usuario = db.query(UsuariosModel).filter(UsuariosModel.codigo == id).first()
    if not usuario:
        print(f"Usuario con ID {id} no encontrado")
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    print(f"Usuario encontrado: {usuario.usuario} (código: {usuario.codigo})")
    
    # Validar datos requeridos
    if not datos.get("usuario"):
        raise HTTPException(status_code=422, detail="El nombre de usuario es obligatorio")
    
    if not datos.get("email"):
        raise HTTPException(status_code=422, detail="El correo electrónico es obligatorio")
    
    # Verificar que el usuario no esté duplicado (si fue cambiado)
    if datos["usuario"] != usuario.usuario:
        usuario_existente = db.query(UsuariosModel).filter(
            (UsuariosModel.usuario == datos["usuario"]) & 
            (UsuariosModel.codigo != id)
        ).first()
        
        if usuario_existente:
            print(f"El usuario '{datos['usuario']}' ya está en uso por otro usuario")
            raise HTTPException(status_code=400, detail="El nombre de usuario ya está en uso")
    
    # Verificar que el email no esté duplicado (si fue cambiado)
    if datos["email"] != usuario.mail:
        email_existente = db.query(UsuariosModel).filter(
            (UsuariosModel.mail == datos["email"]) & 
            (UsuariosModel.codigo != id)
        ).first()
        
        if email_existente:
            print(f"El email '{datos['email']}' ya está registrado para otro usuario")
            raise HTTPException(status_code=400, detail="El correo electrónico ya está registrado")
    
    try:
        # Actualizar campos básicos del usuario
        print(f"Actualizando datos básicos del usuario {id}")
        usuario.usuario = datos["usuario"]
        usuario.nombre = datos.get("nombre", usuario.nombre)
        usuario.mail = datos["email"]
        
        # Actualizar contraseña si se proporcionó
        if datos.get("password") and datos["password"].strip():
            print("Actualizando contraseña del usuario")
            usuario.clave = pwd_context.hash(datos["password"])
        
        # Actualizar estado si se proporcionó
        if "estado" in datos:
            estado_valor = datos["estado"] == "activo"
            print(f"Actualizando estado del usuario a: {datos['estado']} ({estado_valor})")
            usuario.activo = estado_valor
        
        # IMPORTANTE: Actualizar el rol si se proporcionó
        if datos.get("rol"):
            print(f"Intentando actualizar rol a: {datos['rol']}")
            
            # Buscar el rol por nombre
            rol = db.query(RolesModel).filter(RolesModel.nombre == datos["rol"]).first()
            
            # Crear el rol si no existe
            if not rol:
                print(f"Rol '{datos['rol']}' no encontrado, creando nuevo rol")
                rol = RolesModel(
                    nombre=datos["rol"],
                    descripcion=f"Rol {datos['rol']}"
                )
                db.add(rol)
                db.flush()
                print(f"Nuevo rol creado con ID: {rol.id}")
            else:
                print(f"Rol encontrado: {rol.nombre} (ID: {rol.id})")
            
            # Eliminar roles existentes del usuario
            num_deleted = db.query(UsuariosRolModel).filter(
                UsuariosRolModel.usuario_id == id
            ).delete(synchronize_session=False)
            print(f"Eliminados {num_deleted} roles previos del usuario")
            
            # Asignar el nuevo rol
            nuevo_rol = UsuariosRolModel(
                usuario_id=id,
                rol_id=rol.id
            )
            db.add(nuevo_rol)
            print(f"Asignado nuevo rol ({rol.nombre}) al usuario {id}")
        else:
            print("No se proporcionó rol para actualizar")
        
        # Guardar cambios
        db.commit()
        print(f"Usuario {id} actualizado correctamente")
        
        # Recuperar roles actualizados para el usuario
        roles_query = db.query(RolesModel).join(
            UsuariosRolModel,
            RolesModel.id == UsuariosRolModel.rol_id
        ).filter(UsuariosRolModel.usuario_id == id)
        
        roles = [{"id": rol.id, "nombre": rol.nombre} for rol in roles_query]
        rol_principal = roles[0]["nombre"] if roles else "usuario"
        
        # Respuesta con datos actualizados
        return {
            "id": usuario.codigo,
            "usuario": usuario.usuario,
            "email": usuario.mail,
            "nombre": usuario.nombre,
            "estado": "activo" if usuario.activo else "inactivo",
            "rol": rol_principal,
            "roles": roles,
            "mensaje": "Usuario actualizado correctamente"
        }
    except Exception as e:
        db.rollback()
        print(f"Error al actualizar usuario: {str(e)}")
        print(f"Tipo de error: {type(e).__name__}")
        
        if hasattr(e, '__traceback__'):
            import traceback
            print("Traceback:")
            traceback.print_tb(e.__traceback__)
        
        raise HTTPException(status_code=500, detail=f"Error al actualizar el usuario: {str(e)}")
    
@router.delete("/usuarios/{id}", response_model=Dict[str, Any])
async def eliminar_usuario(
    id: int,
    db: Session = Depends(get_db),
    user: UserSchema = Depends(current_user)
):
    """Elimina un usuario y todas sus relaciones"""
    # Importar modelos necesarios
try:
    from ...db.models.config.usuarios import usuarios as UsuariosModel
except ImportError:
    from sql_app.db.models.config.usuarios import usuarios as UsuariosModel
    print(f"Solicitando eliminar usuario con ID: {id}")
    
    # Verificar que el usuario exista
    usuario = db.query(UsuariosModel).filter(UsuariosModel.codigo == id).first()
    if not usuario:
        print(f"Usuario con ID {id} no encontrado")
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    print(f"Usuario encontrado: {usuario.usuario} (código: {usuario.codigo})")
    
    # No permitir eliminar al propio usuario administrador
    if usuario.codigo == user.codigo:
        print(f"Intento de eliminar la propia cuenta de administrador: {user.codigo}")
        raise HTTPException(status_code=400, detail="No puedes eliminar tu propia cuenta de administrador")
    
    try:
        # Primero eliminar las relaciones con roles (para evitar restricciones de clave foránea)
        num_roles_deleted = db.query(UsuariosRolModel).filter(
            UsuariosRolModel.usuario_id == id
        ).delete(synchronize_session=False)
        
        print(f"Eliminados {num_roles_deleted} registros de roles asociados al usuario {id}")
        
        # Luego eliminar el usuario
        db.delete(usuario)
        print(f"Usuario {id} marcado para eliminación")
        
        # Confirmar los cambios
        db.commit()
        print(f"Usuario {id} eliminado correctamente")
        
        return {
            "id": id,
            "mensaje": "Usuario eliminado correctamente"
        }
    except Exception as e:
        db.rollback()
        print(f"Error al eliminar usuario {id}: {str(e)}")
        print(f"Tipo de error: {type(e).__name__}")
        
        if hasattr(e, '__traceback__'):
            import traceback
            print("Traceback:")
            traceback.print_tb(e.__traceback__)
            
        raise HTTPException(status_code=500, detail=f"Error al eliminar el usuario: {str(e)}")
        
@router.get("/roles/", response_model=List[Dict[str, Any]])
async def listar_roles(
    db: Session = Depends(get_db), 
    user: UserSchema = Depends(current_user),
    search: Optional[str] = None
):
    """Obtiene la lista de roles disponibles con filtrado opcional"""
    # Importar modelo de roles
    try:
        from ...db.models.config.roles import roles as RolesModel
    except ImportError:
        from sql_app.db.models.config.roles import roles as RolesModel
        
    print("Solicitando lista de roles")
    
    # Iniciar la consulta
    query = db.query(RolesModel)
    
    # Aplicar filtro de búsqueda si se proporciona
    if search:
        search_term = f"%{search}%"
        print(f"Filtrando roles por término: {search}")
        query = query.filter(
            (RolesModel.nombre.ilike(search_term)) |
            (RolesModel.descripcion.ilike(search_term))
        )
    
    # Ordenar roles por nombre
    query = query.order_by(RolesModel.nombre)
    
    # Obtener roles desde la base de datos
    roles = query.all()
    
    # Si no hay roles, crear algunos por defecto
    if not roles:
        print("No se encontraron roles, creando roles predeterminados")
        roles_default = [
            RolesModel(nombre="admin", descripcion="Administrador del sistema con acceso completo"),
            RolesModel(nombre="editor", descripcion="Editor con permisos para crear y modificar contenido"),
            RolesModel(nombre="usuario", descripcion="Usuario estándar con acceso básico")
        ]
        
        try:
            # Añadir roles por defecto
            db.add_all(roles_default)
            db.commit()
            print("Roles predeterminados creados correctamente")
            roles = roles_default
        except Exception as e:
            db.rollback()
            print(f"Error al crear roles por defecto: {str(e)}")
            print(f"Tipo de error: {type(e).__name__}")
            
            # Intentar una consulta sin filtros para ver si hay algún rol
            roles = db.query(RolesModel).all()
    else:
        print(f"Se encontraron {len(roles)} roles")
    
    # Importar el modelo UsuariosRol con try/except
    try:
        from ...db.models.config.usuarios_rol import usuarios_rol as UsuariosRolModel
    except ImportError:
        from sql_app.db.models.config.usuarios_rol import usuarios_rol as UsuariosRolModel
    
    # Convertir a formato para la respuesta, incluyendo conteo de usuarios por rol
    roles_response = []
    
    for rol in roles:
        try:
            # Contar usuarios asignados a este rol
            usuarios_count = db.query(UsuariosRolModel).filter(
                UsuariosRolModel.rol_id == rol.id
            ).count()
            
            # Agregar rol con conteo de usuarios
            roles_response.append({
                "id": rol.id,
                "nombre": rol.nombre,
                "descripcion": rol.descripcion or "",
                "usuarios_count": usuarios_count
            })
        except Exception as e:
            print(f"Error al procesar información del rol {rol.id}: {str(e)}")
            
            # Agregar rol sin conteo de usuarios
            roles_response.append({
                "id": rol.id,
                "nombre": rol.nombre,
                "descripcion": rol.descripcion or "",
                "usuarios_count": 0
            })
    
    return roles_response

@router.get("/rol/tecnico", response_model=List[Dict[str, Any]])
async def obtener_lista_tecnicos(
    db: Session = Depends(get_db),
    user: UserSchema = Depends(current_user)
):
    """
    Retorna una lista básica de usuarios técnicos (compatibilidad con versión anterior)
    """
    # Redirigir a la nueva función más genérica
    return await obtener_usuarios_por_rol(db=db, user=user, rol="tecnico")

@router.get("/usuarios-por-rol/", response_model=List[Dict[str, Any]])
async def obtener_usuarios_por_rol(
    db: Session = Depends(get_db),
    user: UserSchema = Depends(current_user),
    rol: Optional[str] = None
):
    """
    Retorna una lista básica de usuarios para selectores (sin información sensible)
    Filtra por rol especificado como parámetro de consulta (opcional)
    """
    try:
        # Importar modelos necesarios
try:
    from ...db.models.config.usuarios import usuarios as UsuariosModel
except ImportError:
    from sql_app.db.models.config.usuarios import usuarios as UsuariosModel
        usuarios_filtrados = []
        
        # Si se especifica un rol, filtrar por ese rol
        if rol:
            print(f"Buscando usuarios con rol: {rol}")
            query = text("""
                SELECT u.codigo, u.usuario, u.nombre, u.mail
                FROM usuarios u
                JOIN UsuariosRol ur ON u.codigo = ur.usuario_id
                JOIN Roles r ON ur.rol_id = r.id
                WHERE r.nombre = :rol AND u.activo = 1
                ORDER BY u.nombre, u.usuario
            """)
            
            result = db.execute(query, {"rol": rol})
            
            for row in result:
                usuarios_filtrados.append({
                    "id": row[0],
                    "usuario": row[1],
                    "nombre": row[2] or row[1],
                    "email": row[3]
                })
                
            # Si no encontramos usuarios con ese rol pero el rol es 'tecnico',
            # podemos buscar roles similares como soporte, helpdesk, etc.
            if not usuarios_filtrados and rol.lower() == "tecnico":
                print("Buscando roles alternativos para soporte técnico...")
                query = text("""
                    SELECT u.codigo, u.usuario, u.nombre, u.mail
                    FROM usuarios u
                    JOIN UsuariosRol ur ON u.codigo = ur.usuario_id
                    JOIN Roles r ON ur.rol_id = r.id
                    WHERE r.nombre IN ('soporte', 'helpdesk', 'it', 'support') AND u.activo = 1
                    ORDER BY u.nombre, u.usuario
                """)
                
                result = db.execute(query)
                
                for row in result:
                    usuarios_filtrados.append({
                        "id": row[0],
                        "usuario": row[1],
                        "nombre": row[2] or row[1],
                        "email": row[3]
                    })
            
        # Si no se especificó rol o no se encontraron usuarios con ese rol,
        # devolver todos los usuarios activos
        if not usuarios_filtrados:
            if rol:
                print(f"No se encontraron usuarios con rol '{rol}'. Devolviendo todos los usuarios activos.")
            else:
                print("No se especificó rol. Devolviendo todos los usuarios activos.")
                
            query = text("""
                SELECT u.codigo, u.usuario, u.nombre, u.mail
                FROM usuarios u
                WHERE u.activo = 1
                ORDER BY u.nombre, u.usuario
            """)
            
            result = db.execute(query)
            
            for row in result:
                usuarios_filtrados.append({
                    "id": row[0],
                    "usuario": row[1],
                    "nombre": row[2] or row[1],
                    "email": row[3]
                })
        
        # Si aún no encontramos usuarios, devolver una lista predeterminada
        if not usuarios_filtrados:
            print("No se encontraron usuarios activos. Devolviendo lista predeterminada.")
            if rol and rol.lower() == "tecnico":
                usuarios_filtrados = [
                    {"id": 1, "usuario": "soporte", "nombre": "Soporte Nivel 1", "email": "soporte@example.com"},
                    {"id": 2, "usuario": "tecnico", "nombre": "Técnico Nivel 2", "email": "tecnico@example.com"}
                ]
            else:
                usuarios_filtrados = [
                    {"id": 1, "usuario": "soporte", "nombre": "Soporte Nivel 1", "email": "soporte@example.com"},
                    {"id": 2, "usuario": "tecnico", "nombre": "Técnico Nivel 2", "email": "tecnico@example.com"},
                    {"id": 3, "usuario": "admin", "nombre": "Administrador", "email": "admin@example.com"}
                ]
        
        return usuarios_filtrados
    
    except Exception as e:
        print(f"Error al obtener lista de usuarios: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # En caso de error, devolver una lista predeterminada
        if rol and rol.lower() == "tecnico":
            return [
                {"id": 1, "usuario": "soporte", "nombre": "Soporte Nivel 1", "email": "soporte@example.com"},
                {"id": 2, "usuario": "tecnico", "nombre": "Técnico Nivel 2", "email": "tecnico@example.com"}
            ]
        else:
            return [
                {"id": 1, "usuario": "soporte", "nombre": "Soporte Nivel 1", "email": "soporte@example.com"},
                {"id": 2, "usuario": "tecnico", "nombre": "Técnico Nivel 2", "email": "tecnico@example.com"},
                {"id": 3, "usuario": "admin", "nombre": "Administrador", "email": "admin@example.com"}
            ]
@router.get("/usuario-rol", response_model=Dict[str, Any])
async def get_current_user_roles(
    current_user: UserSchema = Depends(current_user)
):
    """Devuelve los roles del usuario actualmente autenticado"""
    try:
        # Acceso a la base de datos
        db = next(get_db())
        
        # Importar modelos necesarios
try:
    from ...db.models.config.roles import roles as RolesModel
except ImportError:
    from sql_app.db.models.config.roles import roles as RolesModel
        # Consultar los roles del usuario actual usando SQL directo para mayor compatibilidad
        from sqlalchemy import text
        
        query = text("""
            SELECT r.id, r.nombre, r.descripcion
            FROM Roles r
            JOIN UsuariosRol ur ON r.id = ur.rol_id
            WHERE ur.usuario_id = :user_id
        """)
        
        result = db.execute(query, {"user_id": current_user.codigo})
        
        roles = []
        for row in result:
            roles.append({
                "id": row[0],
                "nombre": row[1],
                "descripcion": row[2] if row[2] else ""
            })
        
        # Si no se encontraron roles, verificar si el usuario es administrador por otro medio
        if not roles and hasattr(current_user, "es_admin") and current_user.es_admin:
            roles.append({
                "id": 1,
                "nombre": "admin",
                "descripcion": "Administrador del sistema"
            })
        
        # Lista plana de nombres de roles para simplificar verificaciones en el frontend
        role_names = [role["nombre"] for role in roles]
        
        return {
            "roles": role_names,
            "roles_detalle": roles,
            "user_id": current_user.codigo,
            "username": current_user.usuario
        }
    except Exception as e:
        print(f"Error al obtener roles del usuario actual: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # En caso de error, determinar si el usuario tiene acceso de administrador
        # a través de la información disponible en el token
        admin_access = False
        if hasattr(current_user, "es_admin"):
            admin_access = current_user.es_admin
        
        # Proporcionar una respuesta por defecto basada en información disponible
        role_names = ["usuario"]
        if admin_access:
            role_names.append("admin")
            
        return {
            "roles": role_names,
            "roles_detalle": [{"id": 0, "nombre": role, "descripcion": ""} for role in role_names],
            "user_id": getattr(current_user, "codigo", 0),
            "username": getattr(current_user, "usuario", "usuario"),
            "error": f"Error al consultar roles: {str(e)}"
        }