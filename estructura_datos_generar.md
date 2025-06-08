# Estructura de Datos para el Endpoint /generate

## Análisis del archivo Generar.py

El endpoint `/generate` recibe datos a través de **form-data** (no JSON), pero aquí está la estructura equivalente para que una IA pueda generar los datos necesarios:

## Estructura de Datos Requerida

### Campos Obligatorios:
```json
{
  "module_name": "string",           // Nombre del módulo a generar (ej: "usuario", "producto")
  "field_names[]": ["string"],       // Array de nombres de campos (ej: ["nombre", "email", "edad"])
  "field_types[]": ["string"]        // Array de tipos de campos (ej: ["string", "string", "integer"])
}
```

### Campos Opcionales (booleanos):
```json
{
  "generate_crud": "true|false",      // Generar funciones CRUD
  "generate_route": "true|false",     // Generar archivo de rutas
  "generate_schema": "true|false",    // Generar schemas de Pydantic
  "generate_html_form": "true|false", // Generar formulario HTML
  "generate_tests": "true|false",     // Generar archivos de test
  "agregar_rutas": "true|false",      // Agregar rutas al main.py
  "generate_service": "true|false"    // Generar servicio completo
}
```

## Ejemplo Completo de Estructura:

### Para generar un módulo "producto":
```json
{
  "module_name": "producto",
  "field_names[]": ["nombre", "precio", "descripcion", "categoria_id", "stock"],
  "field_types[]": ["string", "float", "text", "integer", "integer"],
  "generate_crud": "true",
  "generate_route": "true", 
  "generate_schema": "true",
  "generate_html_form": "true",
  "generate_tests": "false",
  "agregar_rutas": "true",
  "generate_service": "false"
}
```

### Para generar un servicio completo "cliente":
```json
{
  "module_name": "cliente",
  "field_names[]": ["nombre", "email", "telefono", "direccion"],
  "field_types[]": ["string", "string", "string", "text"],
  "generate_crud": "false",
  "generate_route": "false", 
  "generate_schema": "false",
  "generate_html_form": "false",
  "generate_tests": "false",
  "agregar_rutas": "false",
  "generate_service": "true"
}
```

## Tipos de Datos Soportados para field_types[]:
- `string`: Texto corto
- `text`: Texto largo
- `integer`: Número entero
- `float`: Número decimal
- `boolean`: Verdadero/Falso
- `date`: Fecha
- `datetime`: Fecha y hora

## Comportamiento del Sistema:

1. **Si `generate_service` es "true"**: 
   - Se ignora `generate_crud` y se genera un servicio completo
   - Incluye: modelo, schema, crud, rutas, HTML y JS
   - Se registra automáticamente en el ServicesManager

2. **Si `generate_crud` es "true"**:
   - Se generan componentes individuales según las opciones marcadas
   - Cada componente se guarda en su directorio correspondiente

## Estructura para Prompt de IA:

```
Necesito que generes una estructura de datos para el endpoint /generate con los siguientes campos:

OBLIGATORIOS:
- module_name: Nombre del módulo (en minúsculas, sin espacios)
- field_names[]: Array con nombres de los campos de la tabla/modelo
- field_types[]: Array con tipos de datos correspondientes a cada campo

OPCIONALES (usar "true" o "false"):
- generate_crud: Para generar funciones CRUD
- generate_route: Para generar rutas FastAPI
- generate_schema: Para generar schemas Pydantic
- generate_html_form: Para generar formularios HTML
- generate_tests: Para generar tests
- agregar_rutas: Para agregar al main.py
- generate_service: Para generar servicio completo (anula las otras opciones)

Tipos de datos disponibles: string, text, integer, float, boolean, date, datetime

Por favor genera los datos para: [DESCRIPCIÓN DE LO QUE QUIERES GENERAR]
```

## Notas Importantes:

- Los arrays `field_names[]` y `field_types[]` deben tener la misma longitud
- Si `generate_service` es true, las demás opciones se ignoran
- El `module_name` se convierte automáticamente a minúsculas
- Los nombres de campos también se convierten a minúsculas automáticamente
