from fastapi.templating import Jinja2Templates
from datetime import datetime

# Utilidad centralizada para templates Jinja2
# Usar siempre: from utils.templates import templates

templates = Jinja2Templates(directory="templates")

# Agregar filtros personalizados
def truncate_filter(text, length=100, suffix="..."):
    """Filtro para truncar texto"""
    if isinstance(text, str) and len(text) > length:
        return text[:length].rstrip() + suffix
    return text

def default_filter(value, default_value):
    """Filtro para valores por defecto"""
    return value if value is not None else default_value

def strftime_filter(date, format_str='%d/%m/%Y'):
    """Filtro para formatear fechas"""
    if isinstance(date, datetime):
        return date.strftime(format_str)
    return str(date) if date else ""

# Registrar filtros
templates.env.filters['truncate'] = truncate_filter
templates.env.filters['default'] = default_filter
templates.env.filters['strftime'] = strftime_filter

# Función helper para fechas que se puede usar directamente en templates
def format_date(date, format_str='%d/%m/%Y'):
    """Función helper para formatear fechas"""
    if isinstance(date, datetime):
        return date.strftime(format_str)
    return str(date) if date else ""

# Agregar funciones globales al template
templates.env.globals['format_date'] = format_date
