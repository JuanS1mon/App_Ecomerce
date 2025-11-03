from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

# Importaciones esenciales
from routers.ecommerce_auth import router as ecommerce_auth_router
from Projects.ecomerce.routes_config import configure_routes as configure_ecomerce_routes

app = FastAPI(
    title="Sistema Ecommerce",
    description="API para ecommerce",
    version="1.0.0"
)

# Static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(ecommerce_auth_router)
configure_ecomerce_routes(app)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)