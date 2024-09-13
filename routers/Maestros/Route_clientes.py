from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from db.database import get_db, SessionLocal
from db.schemas.Maestro.Schema_clientes import clientesRead, ClientesSeleccionados,clientesResultado,Fecha
from db.crud.Maestro.Crud_clientes import   gets_clientes,get_consulta_ventas
from typing import List
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.responses import FileResponse
import pandas as pd
import os
import subprocess




templates = Jinja2Templates(directory="static/html")  # Asegúrate de que tus plantillas estén en este directorio

router = APIRouter(
    prefix="/clientes",
    tags=["clientes"],
    responses={status.HTTP_404_NOT_FOUND: {"message": "ruta no encontrada"}}
)

@router.get("/pagina", response_class=HTMLResponse)
async def read_items():
    with open('static/html/clientes.html', 'r') as f:
        html_content = f.read()
    response = HTMLResponse(content=html_content, status_code=200)
    response.headers["Cache-Control"] = "no-store"
    return response

# Ruta para la página de index
@router.get("/consultadeventas")
async def index():
    response = FileResponse('static/html/consultadeventas.html')
    response.headers["Cache-Control"] = "no-store"
    return response


@router.post("/", response_model=list[clientesRead]) 
async def routes_gets_clientes_all (
    fecha: Fecha, 
    db: Session = Depends(get_db)):  
    db_clientes = gets_clientes(db, fecha.fecha_desde, fecha.fecha_hasta)
    if not db_clientes:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Route: clientess no encontrados")
    else:
        return db_clientes
    
import zipfile

@router.post("/resultado_consulta_ventas", response_class=HTMLResponse) 
async def routes_get_clientes_resultado_consulta_ventas(clientes_seleccionados: ClientesSeleccionados, db: Session = Depends(get_db)):
    # Extrae los valores del objeto JSON
    fecha_desde = clientes_seleccionados.mesAnoDesde
    fecha_hasta = clientes_seleccionados.mesAnoHasta
    seleccionados = clientes_seleccionados.seleccionados
    _, mes, ano = fecha_hasta.split('/')  # Se elimina 'dia' ya que no se utiliza
    # Crea una carpeta por mes
    carpeta = f'Ventas/{mes}{ano}'
    if not os.path.exists(carpeta):
        os.makedirs(carpeta)

    archivo_rar = f'{carpeta}/ventas.rar'
    if os.path.exists(archivo_rar):
        os.remove(archivo_rar)

    if not fecha_desde or not fecha_hasta:
        raise HTTPException(status_code=400, detail="No se seleccionó una fecha")

    archivos = []
    for seleccionado in seleccionados:
        try:
            resultado = get_consulta_ventas(db, fecha_desde, fecha_hasta, seleccionado.clienteWeb, seleccionado.sucursal)
        except Exception as e:
            print(e)
            raise HTTPException(status_code=500, detail="Error al obtener datos de ventas")

        if resultado:
            df = pd.DataFrame(resultado)
            nombres_meses = ["", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
            numero_mes = int(fecha_hasta[3:5])
            nombre_mes = nombres_meses[numero_mes]
            nombre_archivo = f"{carpeta}/{str(seleccionado.clienteWeb).zfill(5)}_{str(seleccionado.sucursal).zfill(3)}_{nombre_mes}{fecha_hasta[8:]}.xlsx"
            df.to_excel(nombre_archivo, index=False)
            archivos.append(nombre_archivo)

    if not archivos:
        raise HTTPException(status_code=404, detail="Route: clientes no encontrado")
    else:
        ruta_comando = r"C:\Program Files\WinRAR\WinRAR.exe"
        comando_rar = [ruta_comando, 'a', '-m5', '-r', archivo_rar] + archivos
        try:
            subprocess.run(comando_rar, check=True)
            return FileResponse(archivo_rar, media_type="application/x-rar-compressed", filename='ventas.rar')
        except subprocess.CalledProcessError as e:
            print(e)
            raise HTTPException(status_code=500, detail="Error al crear el archivo .rar")