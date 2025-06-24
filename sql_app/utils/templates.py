from fastapi.templating import Jinja2Templates

# Utilidad centralizada para templates Jinja2
# Usar siempre: from sql_app.utils.templates import templates

templates = Jinja2Templates(directory="sql_app/static")
