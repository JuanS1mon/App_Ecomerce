#!/usr/bin/env python3
"""
Script para interceptar y mostrar los datos que llegan al endpoint de registro
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import uvicorn
import json

app = FastAPI()

@app.post("/ecommerce/auth/register")
async def intercept_register(request: Request):
    """Intercepta la solicitud de registro y muestra los datos"""
    try:
        # Obtener el body de la solicitud
        body = await request.body()
        data = json.loads(body.decode('utf-8'))

        print("=== DATOS RECIBIDOS EN REGISTRO ===")
        print(f"Headers: {dict(request.headers)}")
        print(f"Body: {json.dumps(data, indent=2, ensure_ascii=False)}")

        # Validar campos requeridos
        required_fields = ['nombre', 'apellido', 'email', 'contraseña']
        missing_fields = []
        for field in required_fields:
            if field not in data or not data[field] or str(data[field]).strip() == '':
                missing_fields.append(field)

        if missing_fields:
            print(f"❌ CAMPOS FALTANTES O VACÍOS: {missing_fields}")
            return JSONResponse(
                content={"detail": f"Campos requeridos faltantes: {missing_fields}"},
                status_code=400
            )

        # Validar contraseña
        if len(str(data.get('contraseña', ''))) < 6:
            print("❌ CONTRASEÑA DEMASIADO CORTA")
            return JSONResponse(
                content={"detail": "La contraseña debe tener al menos 6 caracteres"},
                status_code=400
            )

        print("✅ DATOS VÁLIDOS - Continuando con registro real...")

        # Aquí redirigiríamos al registro real, pero por ahora solo mostramos
        return JSONResponse(
            content={"message": "Datos interceptados correctamente", "data": data},
            status_code=200
        )

    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return JSONResponse(
            content={"detail": f"Error procesando solicitud: {str(e)}"},
            status_code=500
        )

if __name__ == "__main__":
    print("🚀 Iniciando servidor de interceptación en puerto 8002...")
    print("📝 Ve a http://localhost:8001/ecommerce/register y registra un usuario")
    print("📊 Los datos se mostrarán aquí...")
    uvicorn.run(app, host="0.0.0.0", port=8002)