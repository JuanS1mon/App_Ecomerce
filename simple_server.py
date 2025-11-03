from fastapi import FastAPI
from Projects.ecomerce.routes_config import configure_routes
from db.database import get_db
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure ecommerce routes
configure_routes(app)

@app.get("/")
async def root():
    return {"message": "Ecommerce API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)