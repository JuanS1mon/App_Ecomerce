# 🧪 Carpeta de Tests

Esta carpeta contiene todos los archivos de testing y desarrollo que fueron organizados para mantener el directorio principal limpio.

## 📁 Estructura

```
tests/
├── api/           # Tests de endpoints y APIs
├── database/      # Tests de base de datos, migraciones, tablas
├── integration/   # Tests de integración y flujos completos
├── performance/   # Tests de rendimiento y optimización
├── ui/            # Tests de interfaz de usuario y temas
├── unit/          # Tests unitarios y funciones específicas
└── files/         # Archivos de prueba (JSON, CSV, HTML, etc.)
```

## 📊 Resumen de archivos organizados

- **API**: 12 archivos - Tests de endpoints, rutas y APIs
- **Database**: 10 archivos - Tests de base de datos y migraciones
- **Integration**: 8 archivos - Tests de sistemas completos
- **Unit**: 12 archivos - Tests unitarios de funciones específicas
- **Performance**: 3 archivos - Tests de rendimiento
- **UI**: 4 archivos - Tests de interfaz de usuario
- **Files**: 8 archivos - Archivos de datos de prueba

## 🚫 Ignorado en Git

Esta carpeta está incluida en `.gitignore` para evitar subir archivos de desarrollo al repositorio.

## 🔄 Reorganización

Los archivos fueron organizados automáticamente desde el directorio raíz el 11/10/2025 usando el script `organize_tests.py`.

### Criterios de categorización:

- **api**: *api*, *endpoint*, *route*, *request*
- **database**: *db*, *table*, *migration*, *crud*, *sql*  
- **performance**: *performance*, *async*, *optimization*
- **ui**: *theme*, *admin*, *visual*, *frontend*, *template*
- **integration**: *complete*, *flow*, *sistema*, *multi*, *generator*
- **unit**: Todo lo demás que no coincida con los patrones anteriores

## 📝 Notas

- Los archivos originales estaban en el directorio raíz creando desorden
- Esta organización facilita el mantenimiento y desarrollo
- Los tests pueden ejecutarse desde sus respectivas carpetas
- Para restaurar un archivo específico, simplemente muévelo de vuelta al directorio raíz si es necesario