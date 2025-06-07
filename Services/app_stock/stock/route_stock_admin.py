from fastapi import APIRouter, Depends, HTTPException, status, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from ....db.database import get_db
from ...security.security import get_current_user
import logging
import os

# Importar los modelos ORM que necesitamos
from ..articulos.model_articulos import Articulos
from ..depositos.model_depositos import Depositos
from ..stock.model_stock import Stock
from sqlalchemy import func, desc, text

# Configurar logger
logger = logging.getLogger(__name__)

# Configurar templates - Revisamos la ruta correcta
templates = Jinja2Templates(directory="sql_app/static")

# Crear router
router = APIRouter(
    prefix="/stock_admin",
    tags=["Stock Admin"],
    responses={status.HTTP_404_NOT_FOUND: {"message": "No encontrado"}}
)

@router.get("/", response_class=HTMLResponse)
async def get_stock_admin(request: Request, db: Session = Depends(get_db), 
                         current_user: dict = Depends(get_current_user)):
    """
    Página de administración del módulo de stock
    """
    try:
        # Obtener estadísticas usando ORM pero sin usar columnas que pueden no existir
        productos_count = db.query(Articulos).count()
        total_depositos = db.query(Depositos).count()
        
        # Contar movimientos (usando el campo nro_movimiento como indicador)
        try:
            total_movimientos = db.query(Stock.nro_movimiento).distinct().count()
        except Exception as e:
            logger.warning(f"Error al contar movimientos: {e}")
            total_movimientos = 0
        
        # Variables por defecto
        top_articulos = []
        movimientos = []
        
        # Verificar si la tabla tiene registros antes de intentar consultas complejas
        has_stock_records = db.query(Stock).first() is not None
        
        if has_stock_records:
            # Intenta obtener el top 5 de artículos por número de registros
            try:
                top_articulos_query = db.query(
                    Stock.codigo_art,
                    Articulos.descripcion,
                    func.count(Stock.id).label("total_registros")
                ).join(
                    Articulos, 
                    Stock.codigo_art == Articulos.id,
                    isouter=True
                ).group_by(
                    Stock.codigo_art, 
                    Articulos.descripcion
                ).order_by(
                    func.count(Stock.id).desc()
                ).limit(5)
                
                top_articulos_result = top_articulos_query.all()
                
                # Convertir a formato de diccionario
                top_articulos = [
                    {
                        "codigo_art": item.codigo_art,
                        "descripcion": item.descripcion or "Sin descripción",
                        "total_disponible": item.total_registros  # Usamos el conteo como indicador
                    }
                    for item in top_articulos_result
                ]
            except Exception as e:
                logger.warning(f"Error al obtener top 5 artículos: {e}")
            
            # Obtener movimientos recientes (sin usar campos problemáticos)
            try:
                movimientos_recientes = db.query(
                    Stock.id,
                    Stock.codigo_art,
                    Stock.fecha,
                    Stock.tipo
                ).order_by(
                    Stock.id.desc()
                ).limit(10).all()
                
                # Formatear movimientos
                movimientos = [
                    {
                        "id": mov.id,
                        "codigo_art": mov.codigo_art,
                        "cantidad": 1,  # Valor por defecto
                        "fecha": mov.fecha or "Sin fecha",
                        "tipo": "entrada" if mov.tipo else "salida"
                    }
                    for mov in movimientos_recientes
                ]
            except Exception as e:
                logger.warning(f"Error al obtener movimientos recientes: {e}")
            
        # Total de órdenes de trabajo (dato ficticio)
        total_ot = 12
        
        # Intentamos con una ruta alternativa siguiendo el formato de las otras páginas
        template_path = "stock_admin.html"
        
        # Vamos a intentar renderizar directamente el template usando la estructura de archivos que vemos en route_stock.py
        return templates.TemplateResponse(
            "stock_admin.html", 
            {
                "request": request,
                "user": current_user,
                "productos_count": productos_count,
                "total_depositos": total_depositos,
                "total_movimientos": total_movimientos,
                "total_ot": total_ot,
                "movimientos": movimientos,
                "top_articulos": top_articulos
            }
        )
    
    except Exception as e:
        logger.error(f"Error al cargar panel de administración de stock: {e}")
        return HTMLResponse(
            content=f"<html><body><h1>Error interno del servidor</h1><p>{str(e)}</p></body></html>",
            status_code=500
        )

@router.get("/api/recent-movements")
async def get_recent_movements(db: Session = Depends(get_db),
                             current_user: dict = Depends(get_current_user)):
    """
    API para obtener movimientos recientes para actualizar el dashboard
    """
    try:
        # Verificamos primero si hay registros
        has_records = db.query(Stock).first() is not None
        
        if not has_records:
            # Si no hay registros, devolvemos una lista vacía
            return {"movements": []}
            
        # Consulta ORM para obtener movimientos recientes
        movimientos_recientes = db.query(
            Stock.id,
            Stock.codigo_art,
            Stock.fecha,
            Stock.tipo
        ).order_by(
            Stock.id.desc()
        ).limit(10).all()
        
        # Formatear movimientos para la respuesta JSON
        movimientos = [
            {
                "id": mov.id,
                "codigo_art": mov.codigo_art,
                "cantidad": 1,  # Valor fijo genérico
                "fecha": mov.fecha or "Sin fecha",
                "tipo": "entrada" if mov.tipo else "salida"
            }
            for mov in movimientos_recientes
        ]
            
        return {"movements": movimientos}
    
    except Exception as e:
        logger.error(f"Error al obtener movimientos recientes: {e}")
        # En lugar de lanzar una excepción, devolvemos una lista vacía con un mensaje de error
        return {"movements": [], "error": str(e)}

@router.get("/dashboard", response_class=HTMLResponse)
async def get_stock_dashboard(request: Request, db: Session = Depends(get_db),
                             current_user: dict = Depends(get_current_user)):
    """
    Dashboard con estadísticas detalladas de stock
    """
    try:
        # Corregir la ruta para que apunte al archivo correcto
        with open("sql_app/static/app_stock/stock_dashboard.html", "r", encoding="utf-8") as file:
            html_content = file.read()
        return HTMLResponse(content=html_content)
    except Exception as e:
        logger.error(f"Error al cargar dashboard de stock: {e}")
        return HTMLResponse(
            content=f"<html><body><h1>Error interno del servidor</h1><p>{str(e)}</p></body></html>",
            status_code=500
        )
