from fastapi import FastAPI
from routers.ecommerce_auth import router as ecommerce_auth_router
from db.database import get_db
import logging
import uvicorn

logging.basicConfig(level=logging.DEBUG)

app = FastAPI()

# Solo inicializar la conexión a DB sin crear tablas
try:
    # Probar conexión
    db = next(get_db())
    db.close()
    print("Base de datos inicializada correctamente")
except Exception as e:
    print(f"Error DB: {e}")

app.include_router(ecommerce_auth_router)
print("Router registrado")

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8003, log_level="debug")