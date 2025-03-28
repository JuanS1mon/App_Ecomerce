def generate_model(module_name, field_names, field_types):
    """
    Genera el modelo SQLAlchemy para un módulo dado siguiendo el modelo proporcionado.
    """
    # Convertir el nombre del módulo a Capitalizado
    module_name_cap = module_name.capitalize()

    # Importaciones necesarias con soporte para más tipos de datos
    model_code = "from sqlalchemy import Column, Integer, String, Boolean, Float, Date, DateTime, Text, ForeignKey\n"
    model_code += "from sqlalchemy.sql import func\n"
    model_code += "from db.database import Base\n\n"

    # Definir la clase del modelo
    model_code += f"class {module_name_cap}(Base):\n"
    model_code += f"    __tablename__ = '{module_name.lower()}'\n\n"

    # Mapeo de tipos SQL a tipos SQLAlchemy
    type_mapping = {
        'int': 'Integer',
        'integer': 'Integer',
        'bigint': 'Integer',
        'smallint': 'Integer',
        'varchar': 'String(255)',
        'char': 'String(50)',
        'text': 'Text',
        'float': 'Float',
        'double': 'Float',
        'decimal': 'Float',
        'numeric': 'Float',
        'bool': 'Boolean',
        'boolean': 'Boolean',
        'date': 'Date',
        'datetime': 'DateTime',
    }

    # Definir los campos del modelo
    for i, (field_name, field_type) in enumerate(zip(field_names, field_types)):
        field_type = field_type.lower()
        sqlalchemy_type = type_mapping.get(field_type, 'String(255)')
        
        # El primer campo es la clave primaria
        if i == 0:
            model_code += f"    {field_name} = Column({sqlalchemy_type}, primary_key=True, index=True"
            if field_type in ['int', 'integer', 'bigint', 'smallint']:
                model_code += ", autoincrement=True"
            model_code += ")\n"
        # Para campos de fecha/hora, añadir valores por defecto automáticos
        elif field_type == 'datetime':
            model_code += f"    {field_name} = Column({sqlalchemy_type}, default=func.now())\n"
        # Para otros tipos de datos
        elif field_type in ['varchar', 'char', 'text']:
            model_code += f"    {field_name} = Column({sqlalchemy_type}, default='')\n"
        elif field_type in ['int', 'integer', 'bigint', 'smallint']:
            model_code += f"    {field_name} = Column({sqlalchemy_type}, default=0)\n"
        elif field_type in ['float', 'double', 'decimal', 'numeric']:
            model_code += f"    {field_name} = Column({sqlalchemy_type}, default=0.0)\n"
        elif field_type in ['bool', 'boolean']:
            model_code += f"    {field_name} = Column({sqlalchemy_type}, default=False)\n"
        else:
            model_code += f"    {field_name} = Column({sqlalchemy_type})\n"

    return model_code