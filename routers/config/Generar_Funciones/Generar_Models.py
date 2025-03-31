def generate_model(module_name, field_names, field_types):
    """
    Genera el modelo SQLAlchemy para un módulo dado siguiendo el modelo proporcionado.
    """
    # Convertir el nombre del módulo a Capitalizado
    module_name_cap = module_name.capitalize()

    # Importaciones necesarias
    model_code = "from sqlalchemy import Column, Integer, String, Boolean, Float\n"
    model_code += "from ..database import Base\n\n"

    # Definir la clase del modelo
    model_code += f"class {module_name_cap}(Base):\n"
    model_code += f"    __tablename__ = '{module_name.lower()}'\n\n"

    # Definir los campos del modelo
    for field_name, field_type in zip(field_names, field_types):
        if field_type == "int":
            model_code += f"    {field_name} = Column(Integer, primary_key=True, index=True, default=0)\n"
        elif field_type == "str":
            model_code += f"    {field_name} = Column(String(50), default=' ')\n"
        elif field_type == "float":
            model_code += f"    {field_name} = Column(Float, default=0.0)\n"
        elif field_type == "bool":
            model_code += f"    {field_name} = Column(Boolean, default=False)\n"
        elif field_type.startswith("Optional["):
            inner_type = field_type[len("Optional["):-1]
            if inner_type == "int":
                model_code += f"    {field_name} = Column(Integer, index=True, nullable=True)\n"
            elif inner_type == "str":
                model_code += f"    {field_name} = Column(String(50), nullable=True)\n"
            elif inner_type == "float":
                model_code += f"    {field_name} = Column(Float, nullable=True)\n"
            elif inner_type == "bool":
                model_code += f"    {field_name} = Column(Boolean, nullable=True)\n"

    return model_code