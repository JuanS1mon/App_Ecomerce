# Módulo de Mensajes

Este módulo contiene toda la funcionalidad relacionada con el sistema de mensajes de la aplicación.

## Estructura del Módulo

```
sql_app/Services/mensajes/
├── README.md                      # Este archivo
├── __init__.py                    # Router principal del módulo
├── crud_mensajes.py               # Operaciones CRUD
├── schema_mensajes.py             # Esquemas Pydantic
├── route_mensajes.py              # API endpoints públicos
├── route_mensajes_admin.py        # API endpoints de administración
├── route_static.py                # Servir archivos estáticos
├── frontend/                      # Archivos del frontend
│   └── admin/                     # Interfaz de administración
│       ├── mensajes.html          # Página principal de admin
│       ├── mensajes-demo.html     # Página demo
│       └── js/                    # Archivos JavaScript
│           ├── mensajes-admin.js  # JS para página principal
│           └── mensajes-demo.js   # JS para página demo
└── scripts/                       # Scripts de utilidad
    └── crear_mensajes_db.py       # Script para crear datos de prueba
```

## URLs Disponibles

### Frontend (Páginas)
- `/administracion/mensajes` - Página principal de administración
- `/administracion/mensajes-demo` - Página demo sin autenticación

### API Endpoints
- `/api/mensajes/` - API público de mensajes
- `/admin/api/mensajes/` - API de administración (requiere autenticación)

### Archivos Estáticos
- `/mensajes/static/js/{file}` - Archivos JavaScript
- `/mensajes/static/admin/{path}` - Archivos estáticos de admin

## Funcionalidades

### Administración de Mensajes
- ✅ Dashboard con estadísticas
- ✅ Lista de mensajes con filtros
- ✅ CRUD completo (Crear, Leer, Actualizar, Eliminar)
- ✅ Vista de tarjetas y tabla
- ✅ Sistema de paginación
- ✅ Búsqueda en tiempo real
- ✅ Filtros por tipo, prioridad y estado

### Tipos de Mensaje
- `sistema` - Mensajes del sistema
- `alerta` - Alertas importantes
- `notificacion` - Notificaciones generales
- `usuario` - Mensajes entre usuarios

### Prioridades
- `baja` - Prioridad baja
- `normal` - Prioridad normal
- `alta` - Prioridad alta
- `urgente` - Prioridad urgente

## Uso

### Para Desarrolladores

#### Agregar Nuevos Endpoints
Editar `route_mensajes.py` o `route_mensajes_admin.py` según corresponda.

#### Modificar el Frontend
Los archivos HTML y JS están en `frontend/admin/`. Usar el router de estáticos para servir archivos adicionales.

#### Ejecutar Scripts
```bash
# Desde la raíz del proyecto
python sql_app/Services/mensajes/scripts/crear_mensajes_db.py
```

### Para Usuarios
Acceder a `/administracion/mensajes-demo` para probar el sistema sin autenticación.

## Dependencias

- FastAPI
- SQLAlchemy
- Pydantic
- Tailwind CSS (CDN)
- Font Awesome (CDN)

## Notas de Desarrollo

- El módulo está completamente autocontenido en `/Services/mensajes/`
- Los archivos estáticos se sirven a través del router específico
- El sistema demo funciona con datos simulados para testing
- La autenticación es opcional en la versión demo
