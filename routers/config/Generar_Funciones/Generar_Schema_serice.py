def generate_schema(module_name, field_names, field_types):
    """
    Genera el esquema Pydantic para un módulo dado siguiendo el modelo proporcionado.
    """
    # Convertir el nombre del módulo a Capitalizado
    module_name_cap = module_name.capitalize()

    # Mapeo de tipos SQL a tipos de Python/Pydantic
    type_mapping = {
        'int': 'int',
        'integer': 'int',
        'bigint': 'int',
        'smallint': 'int',
        'varchar': 'str',
        'char': 'str',
        'text': 'str',
        'float': 'float',
        'double': 'float',
        'decimal': 'float',
        'numeric': 'float',
        'bool': 'bool',
        'boolean': 'bool',
        'date': 'date',
        'datetime': 'datetime',
        # Agrega más mapeos según sea necesario
    }

    # Convertir tipos SQL a tipos Python
    python_field_types = []
    for field_type in field_types:
        field_type = field_type.lower()
        python_type = type_mapping.get(field_type, 'str')  # Usar 'str' como tipo por defecto
        python_field_types.append(python_type)

    # Suponemos que el primer campo es la clave primaria
    primary_key = field_names[0]
    primary_key_type = python_field_types[0]

    # Los campos restantes forman la clase base
    base_fields = field_names[1:]
    base_field_types = python_field_types[1:]

    # Importaciones necesarias
    schema_code = "from typing import Optional, List, Dict, Any\n"
    schema_code += "from pydantic import BaseModel, ConfigDict\n"
    schema_code += "from datetime import date, datetime\n\n"

    # Definir la clase Base
    base_class_name = f"{module_name_cap}Base"
    schema_code += f"class {base_class_name}(BaseModel):\n"
    for field_name, field_type in zip(base_fields, base_field_types):
        if field_type.startswith("Optional["):
            schema_code += f"    {field_name}: {field_type} = None\n"
        else:
            schema_code += f"    {field_name}: {field_type}\n"
    schema_code += "\n"

    # Definir la clase Create
    create_class_name = f"{module_name_cap}Create"
    schema_code += f"class {create_class_name}({base_class_name}):\n"
    schema_code += f"    {primary_key}: {primary_key_type}\n\n"

    # Definir la clase Update
    update_class_name = f"{module_name_cap}Update"
    schema_code += f"class {update_class_name}({base_class_name}):\n"
    schema_code += f"    pass\n\n"

    # Definir la clase Read
    read_class_name = f"{module_name_cap}Read"
    schema_code += f"class {read_class_name}({base_class_name}):\n"
    schema_code += f"    {primary_key}: {primary_key_type}\n"
    schema_code += f"    model_config = ConfigDict(from_attributes=True)\n"

    return schema_code