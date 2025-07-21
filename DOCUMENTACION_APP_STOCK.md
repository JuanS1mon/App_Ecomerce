# 📦 Documentación del Sistema de Gestión de Stock

## 🎯 Propósito General

El módulo `app_stock` es un **sistema integral de gestión de inventario** diseñado para empresas que necesitan controlar de manera precisa sus artículos, stock, depósitos y órdenes de trabajo. Este sistema permite un control completo del inventario con trazabilidad en tiempo real.

---

## 🏗️ Arquitectura del Sistema

El sistema está organizado en **6 módulos principales**:

### 1. 📋 **ARTÍCULOS** (`articulos/`)
**Propósito**: Gestión completa del catálogo de productos

**Funcionalidades principales**:
- ✅ **Registro de artículos** con código único, descripción, marca y modelo
- 💰 **Gestión de precios** (costo y venta) con historial completo
- 🏷️ **Generación automática de códigos de barras** (EAN, UPC, CODE128)
- 📱 **Generación de códigos QR** para identificación móvil
- 📊 **Historial de cambios de precios** con trazabilidad de usuario y motivo
- 🔍 **Búsqueda avanzada** por código, descripción o características

**Casos de uso**:
- Alta de nuevos productos en el catálogo
- Actualización masiva de precios
- Generación de etiquetas con códigos de barras/QR
- Consulta de historial de precios para análisis

### 2. 🏷️ **TIPOS DE ARTÍCULOS** (`articulos_tipos/`)
**Propósito**: Categorización y clasificación de artículos

**Funcionalidades principales**:
- 📁 **Creación de categorías** (ej: Electrónicos, Herramientas, Materiales)
- 🏗️ **Jerarquía de tipos** para organización estructurada
- 🔗 **Asociación automática** con artículos

**Casos de uso**:
- Organizar productos por familia
- Facilitar búsquedas y reportes por categoría
- Aplicar reglas específicas por tipo de artículo

### 3. 🏢 **DEPÓSITOS** (`depositos/`)
**Propósito**: Gestión de ubicaciones físicas de almacenamiento

**Funcionalidades principales**:
- 🏭 **Registro de depósitos** con ubicación y características
- 📍 **Ubicaciones específicas** dentro de cada depósito
- 🔒 **Control de acceso** por depósito
- 📊 **Capacidad y límites** por ubicación

**Casos de uso**:
- Definir almacenes principales y sucursales
- Controlar acceso a depósitos sensibles
- Optimizar ubicación de productos

### 4. 📦 **STOCK** (`stock/`)
**Propósito**: Control en tiempo real del inventario

**Funcionalidades principales**:
- 📊 **Stock calculado automáticamente** por artículo y depósito
- 📝 **Movimientos de entrada y salida** con trazabilidad completa
- 🔒 **Cantidades reservadas** para pedidos pendientes
- 📦 **Cantidades preparadas** para despacho
- ❌ **Anulación de movimientos** con auditoría
- 📈 **Reportes ISO** para auditorías
- 🚨 **Control de calidad** con bloqueos temporales

**Estados del stock**:
- **Disponible**: Cantidad lista para usar
- **Reservado**: Cantidad apartada para pedidos
- **Preparado**: Cantidad lista para despacho
- **Bloqueado**: Cantidad con problemas de calidad

**Casos de uso**:
- Consulta de stock disponible en tiempo real
- Registro de entradas de mercadería
- Control de salidas por ventas/consumo
- Reserva de stock para pedidos
- Auditorías de inventario

### 5. 🔢 **SERIES DE ARTÍCULOS** (`articulos_series/`)
**Propósito**: Trazabilidad individual de productos

**Funcionalidades principales**:
- 🔢 **Números de serie únicos** para cada unidad
- 📅 **Trazabilidad completa** desde ingreso hasta salida
- 🔍 **Seguimiento individual** de productos críticos
- 📋 **Historial de movimientos** por serie

**Casos de uso**:
- Control de equipos con garantía
- Trazabilidad de lotes de producción
- Cumplimiento normativo (farmacia, alimentos)

### 6. 🛠️ **ÓRDENES DE TRABAJO** (`ot/`)
**Propósito**: Gestión de trabajos que consumen materiales

**Funcionalidades principales**:
- 📝 **Creación de órdenes de trabajo** con materiales asociados
- 👥 **Asignación de personal** y área responsable
- ⏱️ **Control de tiempos** estimado vs real
- 📦 **Consumo automático de materiales** desde depósitos
- 📊 **Estados de seguimiento** (Pendiente → En Proceso → Finalizada)
- 📋 **Reportes de consumos** por OT

**Estados de OT**:
- **Pendiente**: Creada, esperando inicio
- **En Proceso**: En ejecución
- **Finalizada**: Completada con éxito
- **Cancelada**: Cancelada con devolución de materiales

**Casos de uso**:
- Mantenimiento de equipos
- Proyectos de construcción
- Procesos de manufactura
- Control de costos por trabajo

---

## 🔄 Flujo de Trabajo Típico

### 1. **Configuración Inicial**
1. Crear tipos de artículos (categorías)
2. Configurar depósitos y ubicaciones
3. Dar de alta artículos en el catálogo

### 2. **Operación Diaria**
1. **Recepción de mercadería**:
   - Registrar entrada en depósito
   - Actualizar stock disponible
   - Generar códigos de barras/QR si es necesario

2. **Procesamiento de pedidos**:
   - Consultar stock disponible
   - Reservar cantidades para pedidos
   - Preparar mercadería para despacho
   - Registrar salida definitiva

3. **Órdenes de trabajo**:
   - Crear OT con materiales necesarios
   - Reservar materiales automáticamente
   - Ejecutar trabajo consumiendo stock
   - Finalizar OT con reporte de consumos

### 3. **Control y Auditoría**
1. Consultar reportes de stock calculado
2. Revisar historial de movimientos
3. Generar reportes ISO para auditorías
4. Analizar historial de precios

---

## 🎯 Beneficios para el Usuario

### ✅ **Control Total**
- Visibilidad completa del inventario en tiempo real
- Trazabilidad desde el ingreso hasta la salida
- Auditoría completa de todos los movimientos

### 📊 **Reportes y Análisis**
- Stock valorizado por depósito
- Historial de precios para análisis de costos
- Reportes de consumos por OT
- Estadísticas de rotación de inventario

### 🚀 **Eficiencia Operativa**
- Automatización de cálculos de stock
- Códigos de barras/QR para agilizar operaciones
- Reservas automáticas en pedidos
- Control de calidad integrado

### 🔒 **Seguridad y Compliance**
- Control de acceso por depósito
- Auditoría completa de cambios
- Reportes ISO para certificaciones
- Trazabilidad individual por serie

---

## 🛠️ Tecnologías Utilizadas

- **Backend**: FastAPI con Python
- **Base de datos**: SQL Server con SQLAlchemy ORM
- **Códigos**: Generación automática de barras y QR
- **API REST**: Endpoints documentados con Swagger
- **Logs**: Sistema completo de auditoría

---

## 📞 Soporte

Este sistema está diseñado para ser **escalable** y **mantenible**, permitiendo agregar nuevas funcionalidades según las necesidades específicas de cada empresa.

Para más detalles técnicos, consulte la documentación de API en `/docs` cuando el sistema esté ejecutándose.
