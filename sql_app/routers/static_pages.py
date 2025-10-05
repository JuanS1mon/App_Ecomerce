from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from sqlalchemy.orm import Session
from sql_app.db.database import get_db
from sql_app.utils.templates import templates
import logging
logger = logging.getLogger("main")

router = APIRouter()

@router.get("/debug-template", include_in_schema=False)
async def debug_template(request: Request):
    try:
        import os
        current_dir = os.getcwd()
        template_dir = templates.env.loader.searchpath
        static_path = "sql_app/static/index.html"
        static_exists = os.path.exists(static_path)
        return JSONResponse({
            "current_directory": current_dir,
            "template_searchpath": template_dir,
            "static_file_path": static_path,
            "static_file_exists": static_exists,
            "available_files": os.listdir("sql_app/static") if os.path.exists("sql_app/static") else "Directory not found"
        })
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

@router.get("/index", response_class=HTMLResponse, include_in_schema=False)
@router.get("/", response_class=HTMLResponse, include_in_schema=False)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@router.get("/terminos", response_class=HTMLResponse, include_in_schema=False)
async def get_terminos():
    with open("sql_app/static/terminos.html", "r", encoding="utf-8") as file:
        return HTMLResponse(content=file.read(), status_code=200)

@router.get("/privacidad", response_class=HTMLResponse, include_in_schema=False)
async def get_privacidad():
    with open("sql_app/static/privacidad.html", "r", encoding="utf-8") as file:
        return HTMLResponse(content=file.read(), status_code=200)

@router.get("/registerpage", response_class=HTMLResponse, include_in_schema=False)
async def get_register_page():
    with open("sql_app/static/register.html", "r", encoding="utf-8") as file:
        return HTMLResponse(content=file.read(), status_code=200)

@router.get("/loginpage", response_class=HTMLResponse, include_in_schema=False)
async def get_login_page():
    with open("sql_app/static/login.html", "r", encoding="utf-8") as file:
        return HTMLResponse(content=file.read(), status_code=200)

@router.get("/test-perfil", response_class=HTMLResponse, include_in_schema=False)
async def get_test_perfil():
    """Página de prueba para el perfil de usuario"""
    with open("sql_app/static/test_perfil.html", "r", encoding="utf-8") as file:
        return HTMLResponse(content=file.read(), status_code=200)
        return HTMLResponse(content=file.read(), status_code=200)

@router.get("/login-simple", response_class=HTMLResponse, include_in_schema=False)
async def get_login_simple():
    with open("sql_app/static/login.html", "r", encoding="utf-8") as file:
        return HTMLResponse(content=file.read(), status_code=200)

@router.get("/test-interceptor", response_class=HTMLResponse, include_in_schema=False)
async def get_test_interceptor():
    with open("sql_app/static/test-interceptor.html", "r", encoding="utf-8") as file:
        return HTMLResponse(content=file.read(), status_code=200)
