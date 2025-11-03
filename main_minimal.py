#!/usr/bin/env python3
"""
Versión minimalista de main.py para debugging
"""
from fastapi import FastAPI

app = FastAPI(title="Test Server")

@app.get("/")
async def root():
    return {"message": "Server is running"}

@app.get("/test")
async def test():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    print("🚀 Iniciando servidor minimalista...")
    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="info")