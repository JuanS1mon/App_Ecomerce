from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import uvicorn

app = FastAPI()

# Configurar archivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/password-reset")
async def password_reset_page():
    """Página de recuperación de contraseña"""
    try:
        with open("static/reset_password.html", "r", encoding="utf-8") as f:
            return HTMLResponse(f.read())
    except FileNotFoundError:
        return HTMLResponse("<h1>Error: reset_password.html not found</h1>")

@app.get("/confirm-password-reset")
async def confirm_password_reset_page():
    """Página para confirmar el reset de contraseña"""
    try:
        with open("static/confirm_password_reset.html", "r", encoding="utf-8") as f:
            return HTMLResponse(f.read())
    except FileNotFoundError:
        return HTMLResponse("<h1>Error: confirm_password_reset.html not found</h1>")

@app.get("/")
async def root():
    return HTMLResponse("<h1>Servidor de prueba funcionando</h1><p><a href='/password-reset'>Ir a reset password</a></p><p><a href='/confirm-password-reset'>Ir a confirm password reset</a></p>")

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8001)