from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse, HTMLResponse, Response
import logging
import os
import httpx
from sql_app.config import ENVIRONMENT, STATIC_DIR

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.logger = logging.getLogger("uvicorn.error")
        self.is_production = ENVIRONMENT == "production"
        
    async def dispatch(self, request, call_next):
        import time
        start_time = time.time()
        client_ip = request.client.host if request.client else "unknown"
        method = request.method
        url = str(request.url)
        
        # Log básico siempre
        self.logger.info(f"{method} {url}")
        
        # Información detallada solo en desarrollo
        if not self.is_production:
            headers = dict(request.headers)
            user_agent = headers.get("user-agent", "unknown")
            self.logger.info(f"   📍 IP: {client_ip}")
            self.logger.info(f"   🔍 User-Agent: {user_agent[:100]}...")
            self.logger.debug(f"📍 Encabezados: {headers}")
            self.logger.debug(f"📍 Cookies: {request.cookies}")
            
            auth_header = request.headers.get("Authorization")
            if auth_header:
                self.logger.debug(f"🔑 Encabezado Authorization detectado")
            
            access_token_cookie = request.cookies.get("access_token")
            if access_token_cookie:
                self.logger.debug(f"🔑 Cookie access_token detectada")
        
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            
            if self.is_production:
                # Log mínimo en producción
                self.logger.info(f"{method} {url} -> {response.status_code} ({process_time:.3f}s)")
            else:
                # Log detallado en desarrollo
                self.logger.info(f"✅ {method} {url} -> {response.status_code}")
                self.logger.info(f"   ⏱️  Tiempo: {process_time:.3f}s")
                self.logger.info(f"   📤 Content-Type: {response.headers.get('content-type', 'unknown')}")
            
            response.headers["X-Process-Time"] = str(process_time)
        except Exception as e:
            process_time = time.time() - start_time
            self.logger.error(f"❌ {method} {url} -> ERROR ({process_time:.3f}s): {str(e)}")
            raise
        return response

class FrontendRedirectMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        from sql_app.config import FRONTEND_URL
        frontend_prefix = "/frontend"
        if request.url.path.startswith(frontend_prefix):
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(f"{FRONTEND_URL}{request.url.path[len(frontend_prefix):]}")
                    if response.status_code == 200:
                        return RedirectResponse(url=f"{FRONTEND_URL}{request.url.path[len(frontend_prefix):]}")
            except httpx.RequestError:
                return JSONResponse(status_code=503, content={"detail": "El frontend está caído. Por favor, intenta más tarde."})
        return await call_next(request)

class CustomErrorMiddleware(BaseHTTPMiddleware):
    """Sirve páginas de error HTML desde el STATIC_DIR configurado.

    Se adapta al movimiento de carpetas evitando rutas rotas (antes dependía de ..\static relativo al archivo).
    Si la página no existe devuelve un fallback Response simple para no disparar un 500 adicional.
    Excluye rutas de documentación y API para no interferir con respuestas JSON.
    """

    ERROR_PAGES = {
        401: '401.html',
        403: '403.html',
        404: '404.html',
        405: '405.html',
        500: '500.html',
        503: '503.html',
        505: '505.html'
    }

    def _resolve_static_dir(self):
        # STATIC_DIR puede venir relativo (p.e. 'sql_app/static'); normalizamos a absoluto.
        if os.path.isabs(STATIC_DIR):
            base = STATIC_DIR
        else:
            base = os.path.abspath(os.path.join(os.getcwd(), STATIC_DIR))
        return base

    def _error_file_response(self, status_code: int):
        static_dir = self._resolve_static_dir()
        filename = self.ERROR_PAGES.get(status_code)
        if not filename:
            return Response(status_code=status_code)
        path = os.path.join(static_dir, filename)
        if os.path.exists(path):
            try:
                return FileResponse(path, status_code=status_code)
            except Exception:  # fallback final si hubiese un problema de lectura
                pass
        # Fallback mínimo HTML para no romper cadena de errores
        return HTMLResponse(f"<html><body><h1>{status_code}</h1><p>Error</p></body></html>", status_code=status_code)

    async def dispatch(self, request, call_next):
        response = await call_next(request)
        # Rutas excluidas (doc, api) y favicon (evitar transformar un 404 de favicon en HTML ruidoso)
        excluded_prefixes = ("/docs", "/redoc", "/openapi.json", "/api")
        if request.url.path.startswith(excluded_prefixes) or request.url.path == "/favicon.ico":
            return response
        if response.status_code in self.ERROR_PAGES:
            return self._error_file_response(response.status_code)
        return response

class UserTemplateMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        if isinstance(response, HTMLResponse) or getattr(response, "media_type", None) == "text/html":
            try:
                if hasattr(response, "context") and isinstance(response.context, dict):
                    if "user" not in response.context:
                        pass
            except Exception as e:
                logging.getLogger("main").error(f"Error al procesar middleware de templates: {e}")
        return response

class DebugMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        logger = logging.getLogger("main")
        logger.debug("🔍 Middleware procesando: %s %s", request.method, request.url)
        logger.debug("📍 Encabezados: %s", request.headers)
        logger.debug("📍 Cookies: %s", request.cookies)
        auth_header = request.headers.get("Authorization")
        if auth_header:
            logger.debug("🔑 Encabezado Authorization detectado: %s", auth_header)
        else:
            logger.debug("❌ Encabezado Authorization no presente")
        access_token_cookie = request.cookies.get("access_token")
        if access_token_cookie:
            logger.debug("🔑 Cookie access_token detectada: %s", access_token_cookie)
        else:
            logger.debug("❌ Cookie access_token no presente")
        response = await call_next(request)
        logger.debug("📤 Respuesta: %s %s", response.status_code, response.headers.get("Content-Type"))
        return response
