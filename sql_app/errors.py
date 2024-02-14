# errores.py
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy.exc import SQLAlchemyError

async def http_400_exception_handler(request, exc: HTTPException):
    return JSONResponse(
        status_code=400,
        content={"detail": exc.detail},
    )
async def http_403_exception_handler(request, exc: HTTPException):
    return JSONResponse(
        status_code=403,
        content={"detail": exc.detail},
    )


async def http_404_exception_handler(request, exc: HTTPException):
    return JSONResponse(
        status_code=404,
        content={"detail": "Ouch registro no encontrado."},
    )

async def http_405_exception_handler(request, exc: HTTPException):
    return JSONResponse(
        status_code=405,
        content={"detail": "Ouch  :(  : Registro no encontrado."},
    )

async def http_410_exception_handler(request, exc: HTTPException):
    return JSONResponse(
        status_code=410,
        content={"detail": exc.detail},
    )

async def validation_exception_handler(request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"detail": "Hay un error en los datos. Por favor, verifica que el formato y los datos son correctos."},
    )

async def sqlalchemy_error_handler(request, exc: SQLAlchemyError):
    return JSONResponse(
        status_code=403,
        content={"detail": "No se pudo crear el registro, reintente nuevamente."},
    )

async def http_exception_handler(request, exc: StarletteHTTPException):
    return JSONResponse({"detail": str(exc.detail)}, status_code=exc.status_code)

async def internal_server_error_handler(request, exc: Exception):
    return JSONResponse({"detail": "Ha ocurrido un error interno del servidor. Por favor, inténtalo de nuevo más tarde."}, status_code=500)

def register_exception_handlers(app: FastAPI):
    app.add_exception_handler(HTTPException, http_400_exception_handler)
    app.add_exception_handler(HTTPException, http_404_exception_handler)
    app.add_exception_handler(HTTPException, http_405_exception_handler)
    app.add_exception_handler(HTTPException, http_410_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(SQLAlchemyError, sqlalchemy_error_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(Exception, internal_server_error_handler)