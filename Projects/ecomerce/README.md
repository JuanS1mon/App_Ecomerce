# Proyecto ecomerce

Proyecto generado automáticamente desde el Editor Visual.

## 📋 Descripción

Este proyecto contiene 7 tablas relacionadas generadas desde el Editor Visual.

## 🗂️ Estructura del Proyecto

```
ecomerce/
├── models/          # Modelos SQLAlchemy
├── schemas/         # Esquemas Pydantic
├── Controllers/     # Operaciones CRUD
├── routes/         # Rutas FastAPI
├── templates/      # Templates HTML/JS
├── __init__.py     # Inicialización del proyecto
├── routes_config.py # Configuración de rutas
├── requirements.txt # Dependencias
└── README.md       # Este archivo
```

## 📊 Tablas Incluidas

- **usuarios**: 13 campos
- **categorias**: 6 campos
- **productos**: 8 campos
- **stock**: 6 campos
- **carritos**: 4 campos
- **carrito_items**: 5 campos
- **pedidos**: 5 campos

## 🔗 Relaciones

6 relaciones definidas entre las tablas.

## 🚀 Instalación y Uso

1. Instalar dependencias:
```bash
pip install -r requirements.txt
```

2. Incluir en tu aplicación FastAPI:
```python
from ecomerce import configure_routes

app = FastAPI()
configure_routes(app)
```

## 📁 Archivos Generados

- Modelos SQLAlchemy con relaciones
- Esquemas Pydantic para validación
- Operaciones CRUD completas
- Rutas REST API
- Interfaces HTML/JS

---
*Generado automáticamente por el Editor Visual*
