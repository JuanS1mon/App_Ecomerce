# Sistema de Gestión de Obras de Arte

## Descripción
Sistema completo para la gestión de obras de arte, artistas, exhibiciones y ventas. Basado en FastAPI y SQLAlchemy.

## Estructura del Proyecto

```
sql_app/Services/app_obras/
├── artists/                    # Gestión de artistas
│   ├── __init__.py
│   ├── model_artists.py       # Modelo SQLAlchemy
│   ├── schema_artists.py      # Esquemas Pydantic
│   ├── service_artists.py     # Lógica de negocio
│   └── route_artists.py       # Endpoints FastAPI
├── artworks/                   # Gestión de obras de arte
│   ├── __init__.py
│   ├── model_artworks.py      # Modelo principal
│   ├── schema_artworks.py     # Esquemas Pydantic
│   ├── service_artworks.py    # Lógica de negocio
│   └── route_artworks.py      # Endpoints FastAPI
├── artwork_states/             # Estados de las obras
├── locations/                  # Ubicaciones geográficas
├── institutions/               # Instituciones y galerías
├── exhibitions/                # Exhibiciones y muestras
├── sales/                      # Gestión de ventas
├── documents/                  # Documentos vinculados
└── route_config_stock.py      # Configuración de rutas
```

## Modelos de Datos

### 🖼️ Artworks (Obras de Arte) - Modelo Principal
- **ID**: Identificador único
- **Código de Inventario**: Código único (ej: CP.2020.001)
- **Título**: Título oficial de la obra
- **Artista**: Relación con tabla Artists
- **Año de Creación**: Año en que se creó
- **Técnica y Materiales**: Descripción técnica
- **Dimensiones**: Medidas de la obra
- **Estado**: Relación con ArtworkStates
- **Disponibilidad**: Flags para disponible/vendida/mercado secundario

### 👤 Artists (Artistas)
- **ID**: Identificador único  
- **Nombre Completo**: Nombre del artista

### 🧭 ArtworkStates (Estados)
- **ID**: Identificador único
- **Descripción**: Estado actual ("En producción", "En restauración", etc.)

### 📍 Locations (Ubicaciones)
- **ID**: Identificador único
- **Nombre**: Lugar (depósito, museo, etc.)
- **Ciudad, País**: Ubicación geográfica
- **Dirección**: Dirección opcional

### 🏛️ Institutions (Instituciones)
- **ID**: Identificador único
- **Nombre**: Institución o feria
- **Ubicación**: Relación con Locations

### 🎭 Exhibitions (Exhibiciones)
- **ID**: Identificador único
- **Obra**: Relación con Artworks
- **Nombre de la Muestra**: Título de la exhibición
- **Institución**: Donde se exhibe
- **Curador**: Responsable de la muestra
- **Fechas**: Inicio y fin
- **Documentación**: Enlaces relacionados

### 💵 Sales (Ventas)
- **ID**: Identificador único
- **Obra**: Relación con Artworks
- **Año de Venta**: Cuándo se vendió
- **Galería**: Quién vendió
- **Comprador**: A quién se vendió
- **Ubicación**: Donde ocurrió la venta
- **Valores**: Lista y real
- **Porcentaje del Artista**: % de comisión
- **Estado de Pago**: Pagado/Parcial/Pendiente

### 📂 Documents (Documentos)
- **ID**: Identificador único
- **Obra**: Relación con Artworks
- **Tipo**: Factura, Certificado, etc.
- **URL**: Enlace al documento

## Endpoints API

### Artists
- `GET /app_obras/artists/` - Listar artistas
- `POST /app_obras/artists/` - Crear artista
- `GET /app_obras/artists/id/{id}` - Obtener artista por ID
- `PUT /app_obras/artists/id/{id}` - Actualizar artista
- `DELETE /app_obras/artists/id/{id}` - Eliminar artista

### Artworks
- `GET /app_obras/artworks/` - Listar obras (con filtros)
- `POST /app_obras/artworks/` - Crear obra
- `GET /app_obras/artworks/id/{id}` - Obtener obra por ID
- `GET /app_obras/artworks/inventory/{code}` - Obtener por código
- `PUT /app_obras/artworks/id/{id}` - Actualizar obra
- `DELETE /app_obras/artworks/id/{id}` - Eliminar obra

## Rutas HTML

### Artists
- `GET /app_obras/artists/html/` - Listado de artistas
- `GET /app_obras/artists/html/create` - Formulario de creación
- `GET /app_obras/artists/html/edit/{id}` - Formulario de edición

### Artworks
- `GET /app_obras/artworks/html/` - Catálogo de obras
- `GET /app_obras/artworks/html/create` - Formulario de creación
- `GET /app_obras/artworks/html/edit/{id}` - Formulario de edición

## Funcionalidades Implementadas

✅ **Completas:**
- Modelo de datos completo para todas las entidades
- CRUD para Artists (API + HTML)
- CRUD para Artworks (API + HTML)
- Esquemas Pydantic para validación
- Servicios de lógica de negocio
- Templates HTML responsivos con Bootstrap

🚧 **Pendientes:**
- CRUD para las demás entidades (States, Locations, etc.)
- Relaciones entre modelos en las consultas
- Filtros avanzados
- Reportes y estadísticas
- Subida de imágenes
- Autenticación y autorización

## Instalación y Uso

1. Asegurarse de que todas las dependencias estén instaladas
2. Importar el configurador de rutas en tu aplicación principal:

```python
from sql_app.Services.app_obras.route_config_stock import configure_obras_routes

app = FastAPI()
configure_obras_routes(app)
```

3. Ejecutar las migraciones de base de datos para crear las tablas
4. Acceder a las rutas HTML o usar la API directamente

## Próximos Pasos

1. **Completar servicios faltantes** para todas las entidades
2. **Implementar relaciones** en las consultas (joins)
3. **Crear formularios completos** con selects para artistas y estados
4. **Agregar validaciones** de negocio
5. **Implementar búsqueda avanzada** y filtros
6. **Crear dashboards** con estadísticas
7. **Integrar autenticación** de usuarios

## Tecnologías Utilizadas

- **FastAPI**: Framework web
- **SQLAlchemy**: ORM para base de datos
- **Pydantic**: Validación y serialización
- **Bootstrap 5**: Framework CSS
- **Font Awesome**: Iconografía
- **Jinja2**: Motor de templates
