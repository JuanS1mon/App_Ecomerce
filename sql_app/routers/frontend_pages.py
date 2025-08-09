from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(
    prefix="",
    tags=["Frontend"],
    include_in_schema=False
)

@router.get("/login", response_class=HTMLResponse)
@router.get("/loginpage", response_class=HTMLResponse)
async def login_page():
    """Página de login simplificada sin interferencias JS"""
    try:
        with open("sql_app/static/login_simple.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        # Fallback al login original si no existe el simplificado
        try:
            with open("sql_app/static/login.html", "r", encoding="utf-8") as f:
                return HTMLResponse(content=f.read())
        except FileNotFoundError:
            return HTMLResponse("""
            <html><body>
            <h1>Login no encontrado</h1>
            <p>Los archivos de login no están disponibles</p>
            </body></html>
            """, status_code=404)

@router.get("/admin-dashboard.html", response_class=HTMLResponse)
async def admin_dashboard_page():
    """Carga segura del panel de administración con autenticación AJAX"""
    try:
        with open("admin-loader.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse("""
        <html><body>
        <h1>Error</h1>
        <p>El cargador del panel de administración no está disponible</p>
        <a href="/loginpage">Ir al login</a>
        </body></html>
        """, status_code=404)

@router.get("/test-auth-direct.html", response_class=HTMLResponse)
async def test_auth_direct():
    """Página de prueba directa de autenticación"""
    try:
        with open("test-auth-direct.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse("""
        <html><body>
        <h1>Error</h1>
        <p>La página de prueba no está disponible</p>
        </body></html>
        """, status_code=404)

@router.get("/test-auth-complete.html", response_class=HTMLResponse)
async def test_auth_complete():
    """Página de test completo del flujo de autenticación"""
    try:
        with open("test-auth-complete-ui.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse("""
        <html><body>
        <h1>Error</h1>
        <p>La página de test completo no está disponible</p>
        </body></html>
        """, status_code=404)

@router.get("/editor-visual", response_class=HTMLResponse)
@router.get("/editor-visual.html", response_class=HTMLResponse)
async def editor_visual():
    """Editor Visual Avanzado - Fase 3"""
    try:
        import os
        # Usar ruta absoluta completa
        base_dir = r"C:\Users\PCJuan\Desktop\sql_app"
        file_path = os.path.join(base_dir, "static", "html", "editor_visual.html")
        
        if not os.path.exists(file_path):
            return HTMLResponse(f"""
            <html><body>
            <h1>Error: Archivo no encontrado</h1>
            <p>Ruta buscada: {file_path}</p>
            <p>Directorio actual: {os.getcwd()}</p>
            <p>Archivo existe: {os.path.exists(file_path)}</p>
            </body></html>
            """, status_code=404)
            
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            return HTMLResponse(content=content)
            
    except Exception as e:
        return HTMLResponse(f"""
        <html><body>
        <h1>Error al cargar Editor Visual</h1>
        <p>Error: {str(e)}</p>
        <p>Directorio actual: {os.getcwd()}</p>
        </body></html>
        """, status_code=500)
