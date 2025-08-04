from fastapi import Request, status
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi import HTTPException
import os

def register_exception_handlers(app, templates=None):
    @app.exception_handler(StarletteHTTPException)
    async def custom_http_exception_handler(request: Request, exc: StarletteHTTPException):
        static_dir = os.path.join(os.path.dirname(__file__), "static")
        if exc.status_code == 404:
            return FileResponse(os.path.join(static_dir, '404.html'), status_code=404)
        elif exc.status_code == 401:
            return FileResponse(os.path.join(static_dir, '401.html'), status_code=401)
        elif exc.status_code == 403:
            return FileResponse(os.path.join(static_dir, '403.html'), status_code=403)
        elif exc.status_code == 405:
            return FileResponse(os.path.join(static_dir, '405.html'), status_code=405)
        elif exc.status_code == 500:
            return FileResponse(os.path.join(static_dir, '500.html'), status_code=500)
        elif exc.status_code == 503:
            return FileResponse(os.path.join(static_dir, '503.html'), status_code=503)
        elif exc.status_code == 505:
            return FileResponse(os.path.join(static_dir, '505.html'), status_code=505)
        return JSONResponse(status_code=exc.status_code, content=jsonable_encoder({"detail": exc.detail}))

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=jsonable_encoder({
                "detail": "Se produjo un error de validación.",
                "errors": exc.errors()
            })
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        if exc.status_code == status.HTTP_401_UNAUTHORIZED:
            accept_header = request.headers.get("accept", "")
            content_type = request.headers.get("content-type", "")
            is_api_request = (
                "application/json" in accept_header or
                "application/x-www-form-urlencoded" in content_type or
                request.url.path.startswith("/api/") or
                request.url.path.startswith("/admin") or
                (request.url.path.startswith("/usuarios_admin/") and request.url.path != "/usuarios_admin/" and not request.url.path.endswith(".html")) or
                request.url.path in ["/login", "/logout", "/usuarios/login"]
            )
            if is_api_request:
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={"detail": exc.detail},
                    headers={"WWW-Authenticate": "Bearer"}
                )
            else:
                return RedirectResponse(url="/loginpage")
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail}
        )
