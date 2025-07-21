e# Sistema de Navegación Dinámico - Tipo Explorador de Windows

## 🚀 Características Principales

El sistema de navegación implementado en `navbar.html` ahora funciona como el explorador de archivos de Windows, mostrando la ruta completa de navegación dinámicamente.

## 📍 Cómo Funciona

### 1. **Rutas Configuradas**
El sistema incluye rutas predefinidas para:

- **Administración**: `/admin` → `/admin/usuarios` → `/admin/usuarios/perfil`
- **Inventario**: `/app_stock` → `/articulos` → `/articulos/dashboard`
- **Facturación**: `/facturacion` → `/facturas` → `/facturas/nueva`

### 2. **Rutas Dinámicas**
Para rutas no configuradas, el sistema genera automáticamente:
- Detecta IDs numéricos: `/usuarios/123` → "ID: 123"
- Reconoce acciones: `/usuarios/nuevo` → icono "+" y título "Nuevo"
- Capitaliza nombres: `/mi_perfil` → "Mi Perfil"

## 🎨 Ejemplos Visuales

```
🏠 Inicio > ⚙️ Administración > 👥 Usuarios > 👤 Perfil
```

```
🏠 Inicio > 📦 Inventario > 📊 Dashboard
```

```
🏠 Inicio > 📄 Facturación > 💰 Facturas > ➕ Nueva Factura
```

## 🔧 Uso desde JavaScript

### Actualizar navegación manualmente:
```javascript
window.refreshNavigation();
```

### Agregar nuevas rutas dinámicamente:
```javascript
window.addRoute('/nueva/ruta', {
    title: 'Mi Nueva Página',
    parent: '/nueva',
    icon: 'fa-star'
});
```

## 📱 Características Responsivas

- **Escritorio**: Muestra iconos + texto completo
- **Tablet**: Iconos + texto abreviado
- **Móvil**: Solo iconos esenciales

## 🎯 Casos de Uso Automáticos

| Ruta | Breadcrumb Generado |
|------|-------------------|
| `/admin` | Inicio > Administración |
| `/admin/usuarios` | Inicio > Administración > Usuarios |
| `/admin/usuarios/123` | Inicio > Administración > Usuarios > ID: 123 |
| `/admin/usuarios/nuevo` | Inicio > Administración > Usuarios > Nuevo Usuario |
| `/articulos/dashboard` | Inicio > Inventario > Artículos > Dashboard |
| `/facturas/editar/456` | Inicio > Facturación > Facturas > Editar Factura > ID: 456 |

## 🔄 Eventos y Funcionalidades

- **Auto-actualización**: Se actualiza automáticamente al cambiar de página
- **Historia del navegador**: Compatible con botones atrás/adelante
- **SPA Ready**: Funciona con aplicaciones de una sola página
- **Títulos dinámicos**: Actualiza el título de la pestaña automáticamente

## 🐛 Debug y Logging

El sistema incluye logs detallados en consola:
```
🔄 Generando breadcrumb para: /admin/usuarios/perfil
🗺️ Configuración de rutas cargada: 25 rutas disponibles
📱 DOM cargado, inicializando navegación
```

## ⚡ Rendimiento

- **Caché inteligente**: Evita regeneraciones innecesarias
- **Lazy loading**: Solo genera lo necesario
- **Optimización de DOM**: Mínimas manipulaciones del DOM
