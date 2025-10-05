#!/usr/bin/env python3
"""Versión mínima del generador para debugging"""

from fastapi import APIRouter
from fastapi.responses import HTMLResponse
import logging

# Configurar router básico
router = APIRouter(
    include_in_schema=False,
    prefix="/generar",
    tags=["generar"]
)

# Logger básico
logger = logging.getLogger("generador_minimo")

@router.get("/")
async def migraciones_page():
    """Endpoint mínimo del generador sin templates"""
    try:
        logger.info("🚀 Acceso al generador mínimo")
        
        html_content = """
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>🛠️ Generador de Código</title>
            <style>
                body { 
                    font-family: Arial, sans-serif; 
                    max-width: 800px; 
                    margin: 50px auto; 
                    padding: 20px;
                    background: #f5f5f5;
                }
                .container {
                    background: white;
                    padding: 30px;
                    border-radius: 10px;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                }
                .form-group {
                    margin-bottom: 20px;
                }
                label {
                    display: block;
                    margin-bottom: 5px;
                    font-weight: bold;
                }
                input, select, button {
                    width: 100%;
                    padding: 10px;
                    border: 1px solid #ddd;
                    border-radius: 5px;
                    font-size: 16px;
                }
                button {
                    background: #007bff;
                    color: white;
                    border: none;
                    cursor: pointer;
                    margin-top: 10px;
                }
                button:hover {
                    background: #0056b3;
                }
                .result {
                    margin-top: 20px;
                    padding: 15px;
                    border-radius: 5px;
                    display: none;
                }
                .success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
                .error { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🛠️ Generador de Código FastAPI</h1>
                <p>Versión simplificada del generador. Funciona correctamente.</p>
                
                <form id="generatorForm">
                    <div class="form-group">
                        <label for="module_name">Nombre del Módulo:</label>
                        <input type="text" id="module_name" name="module_name" placeholder="ej: productos" required>
                    </div>
                    
                    <div class="form-group">
                        <label for="field_name">Nombre del Campo:</label>
                        <input type="text" id="field_name" name="field_name" placeholder="ej: nombre" required>
                    </div>
                    
                    <div class="form-group">
                        <label for="field_type">Tipo del Campo:</label>
                        <select id="field_type" name="field_type" required>
                            <option value="string">String</option>
                            <option value="integer">Integer</option>
                            <option value="boolean">Boolean</option>
                            <option value="datetime">DateTime</option>
                        </select>
                    </div>
                    
                    <button type="submit">Generar Código</button>
                </form>
                
                <div id="result" class="result"></div>
            </div>
            
            <script>
                document.getElementById('generatorForm').addEventListener('submit', async function(e) {
                    e.preventDefault();
                    
                    const formData = new FormData(this);
                    const data = {
                        module_name: formData.get('module_name'),
                        field_names: [formData.get('field_name')],
                        field_types: [formData.get('field_type')],
                        generate_schema: true,
                        generate_crud: true,
                        generate_route: true
                    };
                    
                    try {
                        const response = await fetch('/generar/generate', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify(data)
                        });
                        
                        const result = await response.json();
                        const resultDiv = document.getElementById('result');
                        
                        resultDiv.className = 'result ' + (result.success ? 'success' : 'error');
                        resultDiv.innerHTML = '<strong>' + (result.success ? 'Éxito:' : 'Error:') + '</strong> ' + result.message;
                        resultDiv.style.display = 'block';
                        
                    } catch (error) {
                        const resultDiv = document.getElementById('result');
                        resultDiv.className = 'result error';
                        resultDiv.innerHTML = '<strong>Error:</strong> ' + error.message;
                        resultDiv.style.display = 'block';
                    }
                });
            </script>
        </body>
        </html>
        """
        
        return HTMLResponse(content=html_content, status_code=200)
        
    except Exception as e:
        logger.error(f"❌ Error en generador mínimo: {str(e)}")
        return HTMLResponse(content=f"""
        <html>
            <body>
                <h1>Error en Generador</h1>
                <p>Error: {str(e)}</p>
            </body>
        </html>
        """, status_code=500)

@router.post("/generate")
async def generate_minimal():
    """Endpoint mínimo para generación"""
    try:
        logger.info("📝 Solicitud de generación mínima")
        
        return {
            "success": True,
            "message": "✅ Generador mínimo funcionando correctamente. El sistema está operativo."
        }
        
    except Exception as e:
        logger.error(f"❌ Error en generación mínima: {str(e)}")
        return {
            "success": False,
            "message": f"Error: {str(e)}"
        }

if __name__ == "__main__":
    print("✅ Generador mínimo cargado correctamente")