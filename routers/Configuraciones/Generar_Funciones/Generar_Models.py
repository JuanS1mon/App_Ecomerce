def generate_model(module_name, field_names, field_types):
    """
    Genera el modelo SQLAlchemy para un módulo dado siguiendo el modelo proporcionado.
    """
    # Convertir el nombre del módulo a Capitalizado
    module_name_cap = module_name.capitalize()

    model_code = "from sqlalchemy import Column, Integer, String, Boolean, Float\n"
    model_code += "from ..database import Base\n\n"
    model_code += f"class {module_name_cap}(Base):\n"
    model_code += f"    __tablename__ = '{module_name.lower()}'\n\n"

    for field_name, field_type in zip(field_names, field_types):
        # Determinar el tipo de columna de SQLAlchemy
        if field_type == 'int':
            column_type = 'Integer'
            default_value = 'default=0'
        elif field_type == 'str':
            column_type = 'String(50)'
            default_value = "default=' '"
        elif field_type == 'bool':
            column_type = 'Boolean'
            default_value = 'default=False'
        elif field_type == 'float':
            column_type = 'Float'
            default_value = 'default=0.0'
        else:
            column_type = 'String'  # Tipo por defecto
            default_value = ''

        # Verificar si es la clave primaria (asumimos que es el primer campo)
        if field_name == field_names[0]:
            # Es clave primaria
            model_code += f"    {field_name} = Column({column_type}, primary_key=True, index=True, {default_value})\n"
        else:
            # Campos normales
            model_code += f"    {field_name} = Column({column_type}, {default_value})\n"

    return model_code