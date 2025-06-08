"""
Configuración centralizada de importaciones para evitar duplicaciones y errores
Este módulo define las importaciones estándar que deben usarse en todo el proyecto
"""

"""

Configuración centralizada de importaciones para evitar duplicaciones y errores
Este módulo define las importaciones estándar que deben usarse en todo el proyecto
"""

"""

Configuración centralizada de importaciones para evitar duplicaciones y errores
Este módulo define las importaciones estándar que deben usarse en todo el proyecto
"""

"""

Configuración centralizada de importaciones para evitar duplicaciones y errores
Este módulo define las importaciones estándar que deben usarse en todo el proyecto
"""

# ================================
# IMPORTACIONES ESTÁNDAR DEL PROYECTO
# ================================

# FastAPI core
from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from sqlalchemy.orm import Session

# Base de datos
from sql_app.db.database import get_db

# Seguridad
from sql_app.Services.security.security import (
    get_current_user, 
    require_admin, 
    encriptar_clave,
    get_password_hash
)

# Modelos y esquemas comunes
from sql_app.db.schemas.config.Usuarios import UserDB
from sql_app.db.models.config.usuarios import usuarios as UsuariosModel
from sql_app.db.models.config.activityLog import ActivityLog
from sql_app.db.schemas.config.roles import Role, RoleCreate, RoleAssignment

# Utilidades
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any

# ================================
# CONFIGURACIÓN DE TEMPLATES
# ================================
templates = Jinja2Templates(directory="sql_app/static")

# ================================
# LOGGER ESTÁNDAR
# ================================
def get_logger(name: str) -> logging.Logger:
    """Obtiene un logger configurado para el módulo especificado"""
    return logging.getLogger(name)

# ================================
# DEFINICIONES DE IMPORTACIONES POR TIPO DE ARCHIVO
# ================================

ROUTER_IMPORTS = {
    'fastapi': [
        'APIRouter', 'Depends', 'Form', 'HTTPException', 'Request', 'status'
    ],
    'fastapi_responses': [
        'HTMLResponse', 'RedirectResponse', 'JSONResponse'
    ],
    'sqlalchemy': [
        'Session'
    ],
    'templates': 'Jinja2Templates',
    'database': 'get_db',
    'security': [
        'get_current_user', 'require_admin', 'encriptar_clave', 'get_password_hash'
    ],
    'schemas': ['UserDB'],
    'models': ['UsuariosModel', 'ActivityLog'],
    'utils': ['logging', 'datetime', 'List', 'Optional', 'Dict', 'Any']
}

SERVICE_IMPORTS = {
    'sqlalchemy': ['Session'],
    'sqlalchemy_exc': ['SQLAlchemyError'],
    'fastapi': ['HTTPException', 'status'],
    'typing': ['List', 'Optional', 'Dict', 'Any'],
    'logging': 'logging',
    'datetime': 'datetime'
}

# ================================
# RUTAS ESTÁNDAR PARA IMPORTACIONES
# ================================

IMPORT_PATHS = {
    # Base de datos
    'database': 'sql_app.db.database',
    'get_db': 'sql_app.db.database.get_db',
    
    # Seguridad
    'security': 'sql_app.Services.security.security',
    'get_current_user': 'sql_app.Services.security.security.get_current_user',
    'require_admin': 'sql_app.Services.security.security.require_admin',
    'encriptar_clave': 'sql_app.Services.security.security.encriptar_clave',
    'get_password_hash': 'sql_app.Services.security.security.get_password_hash',
    
    # Esquemas
    'UserDB': 'sql_app.db.schemas.config.Usuarios.UserDB',
    'Role': 'sql_app.db.schemas.config.roles.Role',
    'RoleCreate': 'sql_app.db.schemas.config.roles.RoleCreate',
    'RoleAssignment': 'sql_app.db.schemas.config.roles.RoleAssignment',
    
    # Modelos
    'UsuariosModel': 'sql_app.db.models.config.usuarios.usuarios',
    'ActivityLog': 'sql_app.db.models.config.activityLog.ActivityLog',
    
    # CRUD
    'get_tables': 'sql_app.db.crud.tablas.get_tables',
    
    # Templates
    'templates_dir': 'sql_app/static'
}

# ================================
# FUNCIONES DE UTILIDAD
# ================================

def get_standard_router_header() -> str:
    """Retorna el header estándar para archivos de router"""
    return '''"""
Módulo de router - Importaciones estandarizadas
"""

from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import logging
from datetime import datetime

from sql_app.db.database import get_db
from sql_app.Services.security.security import get_current_user, require_admin, encriptar_clave
from sql_app.db.schemas.config.Usuarios import UserDB
from sql_app.db.models.config.usuarios import usuarios as UsuariosModel

# Configuración
templates = Jinja2Templates(directory="sql_app/static")
logger = logging.getLogger(__name__)
'''

def get_standard_service_header() -> str:
    """Retorna el header estándar para archivos de servicio"""
    return '''"""
Módulo de servicio - Importaciones estandarizadas
"""

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status
from typing import List, Optional, Dict, Any
import logging
from datetime import datetime

logger = logging.getLogger(__name__)
'''
