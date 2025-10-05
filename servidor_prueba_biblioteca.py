#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 SERVIDOR DE PRUEBA SIMPLE
Para probar el sistema biblioteca sin todo el sistema complejo
"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

# Crear aplicación simple
app = FastAPI(
    title="Sistema de Prueba - Biblioteca",
    description="Servidor simple para probar el sistema multi-tabla",
    version="1.0.0"
)

# Montar archivos estáticos
app.mount("/static", StaticFiles(directory="sql_app/static"), name="static")

# Ruta principal
@app.get("/", response_class=HTMLResponse)
async def read_root():
    return """
    <html>
        <head>
            <title>Sistema Biblioteca - Prueba</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        </head>
        <body class="bg-light">
            <div class="container mt-5">
                <div class="row justify-content-center">
                    <div class="col-md-8">
                        <div class="card shadow">
                            <div class="card-header bg-primary text-white">
                                <h1 class="h3 mb-0">🎉 Sistema Multi-Tabla Funcionando</h1>
                            </div>
                            <div class="card-body">
                                <p class="lead">¡El sistema biblioteca se generó exitosamente!</p>
                                
                                <h5>📱 Formularios HTML Generados:</h5>
                                <div class="list-group">
                                    <a href="/static/html/forms/biblioteca_sistema/index.html" class="list-group-item list-group-item-action">
                                        🏠 Página Principal del Sistema
                                    </a>
                                    <a href="/static/html/forms/biblioteca_sistema/autores_form.html" class="list-group-item list-group-item-action">
                                        👥 Gestión de Autores
                                    </a>
                                    <a href="/static/html/forms/biblioteca_sistema/libros_form.html" class="list-group-item list-group-item-action">
                                        📚 Gestión de Libros
                                    </a>
                                </div>
                                
                                <hr>
                                
                                <h5>🔗 APIs REST (requiere sistema completo):</h5>
                                <div class="text-muted">
                                    <p>• GET /biblioteca_sistema/autores/ - Listar autores</p>
                                    <p>• POST /biblioteca_sistema/autores/ - Crear autor</p>
                                    <p>• GET /biblioteca_sistema/libros/ - Listar libros</p>
                                    <p>• POST /biblioteca_sistema/libros/ - Crear libro</p>
                                </div>
                                
                                <div class="alert alert-info">
                                    <strong>💡 Nota:</strong> Los formularios HTML funcionan independientemente. 
                                    Para APIs REST completas, usa el sistema principal con:
                                    <code>uvicorn sql_app.main:app --reload</code>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </body>
    </html>
    """

# Configurar las rutas del sistema biblioteca - DESHABILITADO POR AHORA
# Solo mostraremos los formularios HTML
print("📱 Formularios HTML disponibles en puerto 8002")
print("🔗 Sistema completo se puede acceder con el main.py principal")

if __name__ == "__main__":
    import uvicorn
    print("🚀 Iniciando servidor de prueba simple...")
    print("🔗 Servidor en: http://localhost:8002")
    print("📱 Formularios en: http://localhost:8002/static/html/forms/biblioteca_sistema/")
    uvicorn.run(app, host="127.0.0.1", port=8002, reload=True)