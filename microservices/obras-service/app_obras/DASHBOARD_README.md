# Dashboard del Sistema de Obras de Arte

## Descripción

El dashboard del sistema de obras de arte proporciona una interfaz centralizada para gestionar y visualizar todas las funcionalidades relacionadas con el inventario de arte, incluyendo obras, artistas, exhibiciones, ventas y más.

## Acceso al Dashboard

### Rutas principales:
- **Dashboard principal**: `/app_obras/dashboard`
- **Redirección desde obras**: `/app_obras/obras` (redirige al dashboard)
- **API de estadísticas**: `/app_obras/dashboard/api/stats`
- **API de actividad reciente**: `/app_obras/dashboard/api/recent-activity`

## Funcionalidades del Dashboard

### 1. Estadísticas Principales
El dashboard muestra tarjetas con estadísticas clave:
- **Obras de Arte**: Total de obras en el inventario y disponibles
- **Artistas**: Número total de artistas registrados
- **Exhibiciones**: Total de exhibiciones y exhibiciones activas
- **Ventas**: Transacciones realizadas y pagos pendientes
- **Instituciones**: Museos, galerías y centros registrados
- **Documentos**: Certificados y archivos del sistema

### 2. Accesos Rápidos
Panel de enlaces directos a las principales funcionalidades:

#### Gestión Principal
- **Catálogo de Obras** (`/app_obras/artworks/html/`)
  - Gestión completa del inventario de obras
  - Agregar, editar y eliminar obras
  - Control de disponibilidad

- **Directorio de Artistas** (`/app_obras/artists/html/`)
  - Administración de información de artistas
  - Biografías, contactos y obras asociadas

- **Exhibiciones** (`/app_obras/exhibitions/html/`)
  - Programación y gestión de muestras
  - Fechas, ubicaciones y obras exhibidas

- **Gestión de Ventas** (`/app_obras/sales/html/`)
  - Control de transacciones
  - Estados de pago y documentación

#### Configuración y Soporte
- **Instituciones** (`/app_obras/institutions/html/`)
  - Gestión de museos, galerías y centros culturales
  - Información de contacto y colaboraciones

- **Ubicaciones** (`/app_obras/locations/html/`)
  - Control de espacios físicos y almacenamiento
  - Seguimiento de obras por ubicación

- **Estados de Obras** (`/app_obras/artwork_states/html/`)
  - Configuración de estados (disponible, vendido, en restauración, etc.)

- **Documentación** (`/app_obras/documents/html/`)
  - Gestión de certificados de autenticidad
  - Archivos digitales y documentación legal

### 3. Información Visual
- Gradiente artístico con patrón de fondo
- Iconografía específica para cada módulo
- Información de fecha y estadísticas en tiempo real
- Navegación rápida en la barra superior

### 4. APIs Disponibles

#### GET `/app_obras/dashboard/api/stats`
Retorna estadísticas completas del sistema en formato JSON:
```json
{
  "success": true,
  "data": {
    "artists_count": 15,
    "artworks_count": 127,
    "available_artworks": 98,
    "sold_artworks": 29,
    "sales_count": 45,
    "exhibitions_count": 8,
    "current_exhibitions": 3,
    "total_sales_value": 125000.00,
    "availability_rate": 77.2,
    "sales_rate": 22.8,
    "current_year": 2025
  }
}
```

#### GET `/app_obras/dashboard/api/recent-activity`
Retorna actividad reciente del sistema:
```json
{
  "success": true,
  "data": {
    "recent_artworks": [...],
    "current_exhibitions": [...],
    "pending_payments_count": 5
  }
}
```

## Integración en el Sistema Principal

El dashboard está integrado en el sistema principal a través de:

1. **Configuración de rutas**: `route_config_obras.py`
2. **Inclusión en main.py**: Se incluye automáticamente al llamar `configure_obras_routes(app)`
3. **Templates**: El archivo `obras_dashboard.html` en la carpeta `static/`

## Navegación

### Desde el dashboard:
- Hacer clic en cualquier tarjeta de estadísticas lleva a la sección correspondiente
- Los accesos rápidos proporcionan navegación directa a las funcionalidades
- La barra de navegación superior permite acceso rápido a obras, artistas y exhibiciones

### Hacia el dashboard:
- Desde `/app_obras/obras` se redirige automáticamente
- Enlaces directos desde otros módulos del sistema
- Navegación desde el logo/título del sistema

## Arquitectura Técnica

### Backend (route_dashboard.py)
- Router principal con prefijo `/dashboard`
- Router de redirección para acceso desde `/obras`
- Servicios integrados de todas las entidades
- Manejo de errores y logging

### Frontend (obras_dashboard.html)
- Diseño responsivo con Tailwind CSS
- Iconografía Font Awesome
- Integración potencial con Chart.js para gráficos
- Patrón visual específico para arte

### Servicios Utilizados
- `service_artists`: Gestión de artistas
- `service_artworks`: Gestión de obras
- `service_exhibitions`: Gestión de exhibiciones
- `service_sales`: Gestión de ventas
- `service_institutions`: Gestión de instituciones
- `service_locations`: Gestión de ubicaciones
- `service_artwork_states`: Gestión de estados
- `service_documents`: Gestión de documentos

## Mantenimiento y Expansión

Para agregar nuevas funcionalidades al dashboard:

1. **Nuevas estadísticas**: Agregar cálculos en la función `obras_dashboard()`
2. **Nuevos accesos rápidos**: Editar la sección correspondiente en `obras_dashboard.html`
3. **Nuevas APIs**: Agregar endpoints en `route_dashboard.py`
4. **Gráficos**: Implementar con Chart.js en el template HTML

El dashboard está diseñado para ser escalable y fácil de mantener, siguiendo las mismas convenciones arquitectónicas del resto del sistema.
