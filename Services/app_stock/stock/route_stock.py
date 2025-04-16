from fastapi import APIRouter, HTTPException, status, Depends, Query
from sqlalchemy.orm import Session
from db.database import get_db
from .schema_stock import StockCreate, StockUpdate, StockRead
from .model_stock import Stock as StockModel
from .service_stock import create_stock, get_stock, gets_stock, delete_stock, update_stock
from fastapi.responses import HTMLResponse, FileResponse
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/stock",
    tags=["stock"],
    responses={status.HTTP_404_NOT_FOUND: {"message": "ruta no encontrada"}}
)

@router.post("/", response_model=StockRead, status_code=status.HTTP_201_CREATED)
async def routes_post_stock(stock: StockCreate, db: Session = Depends(get_db)):
    if stock.id is None or stock.nro_movimiento is None:
        raise HTTPException(status_code=status.HTTP_417_EXPECTATION_FAILED, detail="Todos los campos requeridos deben tener un valor")
    try:
        stock_model = StockModel(**stock.model_dump())
        db_stock = create_stock(db=db, stock=stock_model)
        return StockRead.model_validate(db_stock)
    except Exception as e:
        logger.error(f"Error al crear Stock: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al crear el registro.")


@router.get("/id/{id}", response_model=StockRead)
async def routes_get_stock_id(id: int, db: Session = Depends(get_db)):
    try:
        db_stock = get_stock(db, id)
        if not db_stock:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route: stock no encontrado")
        return StockRead.model_validate(db_stock)
    except Exception as e:
        logger.error(f"Error al obtener Stock: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener el registro.")


@router.get("/", response_model=List[StockRead])
async def routes_gets_stock_all(db: Session = Depends(get_db)):
    try:
        db_stock = gets_stock(db)
        if not db_stock:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Route: stocks no encontrados")
        return [StockRead.model_validate(stock) for stock in db_stock]
    except Exception as e:
        logger.error(f"Error al obtener registros de Stock: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener los registros.")


@router.delete("/id/{id}", response_model=StockRead)
async def routes_delete_stock_numero(id: int, db: Session = Depends(get_db)):
    try:
        resultado_stock = get_stock(db, id)
        if not resultado_stock:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route: stock no encontrado")
        db_stock = delete_stock(db, id)
        return StockRead.model_validate(db_stock)
    except Exception as e:
        logger.error(f"Error al eliminar Stock: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al eliminar el registro.")


@router.put("/id/{id}", response_model=StockRead)
async def routes_update_stock(id: int, stock: StockUpdate, db: Session = Depends(get_db)):
    logger.info(f"Actualizando Stock con id = {id}")
    try:
        stock_data = stock.model_dump()
        db_stock = update_stock(db=db, id=id, stock_data=stock_data)
        return StockRead.model_validate(db_stock)
    except Exception as e:
        logger.error(f"Error al actualizar Stock: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al actualizar el registro.")


@router.get("/pagina", response_class=HTMLResponse)
async def get_pagina():
    try:
        # Ruta actualizada: ahora buscamos en static/module_name/index.html
        with open(f"static/stock/index.html", "r", encoding="utf-8") as file:
            html_content = file.read()
        return HTMLResponse(content=html_content)
    except Exception as e:
        logger.error(f"Error al obtener la pagina HTML: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener la pagina HTML.")


@router.get("/dashboard", response_class=HTMLResponse)
async def get_dashboard():
    """
    Endpoint que sirve la página del dashboard de stock
    """
    try:
        # Modificado para usar la función de respuesta directa y no leer el archivo
        return HTMLResponse(content=html_dashboard_content())
    except Exception as e:
        logger.error(f"Error al obtener la página del dashboard: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                          detail="Error al cargar el dashboard de stock.")

def html_dashboard_content():
    """
    Función que devuelve el contenido HTML del dashboard como una cadena de texto
    en lugar de leerlo desde un archivo para evitar problemas de codificación.
    """
    return """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard de Stock</title>
    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
    <!-- Font Awesome para iconos -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.1.1/css/all.min.css">
    <!-- Chart.js para gráficos -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        :root {
            --primary-color: #3498db;
            --secondary-color: #2ecc71;
            --warning-color: #f39c12;
            --danger-color: #e74c3c;
            --light-bg: #f8f9fa;
            --dark-bg: #343a40;
        }
        
        body {
            background-color: #f5f5f5;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        
        .dashboard-container {
            padding: 20px;
        }
        
        .card {
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            margin-bottom: 20px;
            border: none;
            transition: transform 0.3s;
        }
        
        .card:hover {
            transform: translateY(-5px);
        }
        
        .card-header {
            border-radius: 10px 10px 0 0 !important;
            font-weight: 600;
        }
        
        .metric-card {
            text-align: center;
            padding: 20px;
        }
        
        .metric-value {
            font-size: 2.5rem;
            font-weight: 700;
            margin: 10px 0;
        }
        
        .metric-title {
            font-size: 1.1rem;
            color: #6c757d;
        }
        
        .metric-icon {
            font-size: 2rem;
            margin-bottom: 15px;
        }
        
        .table-container {
            overflow-x: auto;
        }
        
        .bg-primary-light {
            background-color: rgba(52, 152, 219, 0.1);
            color: var(--primary-color);
        }
        
        .bg-success-light {
            background-color: rgba(46, 204, 113, 0.1);
            color: var(--secondary-color);
        }
        
        .bg-warning-light {
            background-color: rgba(243, 156, 18, 0.1);
            color: var(--warning-color);
        }
        
        .bg-danger-light {
            background-color: rgba(231, 76, 60, 0.1);
            color: var(--danger-color);
        }
        
        .nav-pills .nav-link.active {
            background-color: var(--primary-color);
        }
        
        .btn-primary {
            background-color: var(--primary-color);
            border-color: var(--primary-color);
        }
        
        .badge-low-stock {
            background-color: var(--danger-color);
            color: white;
        }
        
        .badge-medium-stock {
            background-color: var(--warning-color);
            color: white;
        }
        
        .badge-good-stock {
            background-color: var(--secondary-color);
            color: white;
        }
        
        .dashboard-header {
            margin-bottom: 20px;
        }
        
        .dashboard-title {
            font-weight: 700;
            color: #343a40;
        }
        
        .dashboard-subtitle {
            color: #6c757d;
        }
    </style>
</head>
<body>
    <div class="container-fluid dashboard-container">
        <!-- Header -->
        <div class="row dashboard-header">
            <div class="col-md-8">
                <h1 class="dashboard-title">Dashboard de Stock</h1>
                <p class="dashboard-subtitle">Control y análisis de inventario en tiempo real</p>
            </div>
            <div class="col-md-4 text-end">
                <div class="btn-group" role="group">
                    <button type="button" class="btn btn-outline-primary" onclick="window.location.href='/stock/pagina'">
                        <i class="fas fa-list"></i> Gestión de Stock
                    </button>
                    <button type="button" class="btn btn-outline-secondary" onclick="exportToPDF()">
                        <i class="fas fa-file-pdf"></i> Exportar
                    </button>
                </div>
            </div>
        </div>

        <!-- Métricas principales -->
        <div class="row">
            <div class="col-xl-3 col-md-6">
                <div class="card metric-card bg-primary-light">
                    <div class="metric-icon">
                        <i class="fas fa-boxes"></i>
                    </div>
                    <div class="metric-value" id="total-items">-</div>
                    <div class="metric-title">Total de Artículos</div>
                </div>
            </div>
            <div class="col-xl-3 col-md-6">
                <div class="card metric-card bg-success-light">
                    <div class="metric-icon">
                        <i class="fas fa-dollar-sign"></i>
                    </div>
                    <div class="metric-value" id="total-value">-</div>
                    <div class="metric-title">Valor del Inventario</div>
                </div>
            </div>
            <div class="col-xl-3 col-md-6">
                <div class="card metric-card bg-warning-light">
                    <div class="metric-icon">
                        <i class="fas fa-exclamation-triangle"></i>
                    </div>
                    <div class="metric-value" id="low-stock">-</div>
                    <div class="metric-title">Artículos con Stock Bajo</div>
                </div>
            </div>
            <div class="col-xl-3 col-md-6">
                <div class="card metric-card bg-danger-light">
                    <div class="metric-icon">
                        <i class="fas fa-history"></i>
                    </div>
                    <div class="metric-value" id="recent-movements">-</div>
                    <div class="metric-title">Movimientos Recientes</div>
                </div>
            </div>
        </div>

        <!-- Gráficos y tablas -->
        <div class="row">
            <!-- Gráfico circular de distribución de stock -->
            <div class="col-lg-6">
                <div class="card">
                    <div class="card-header bg-white">
                        <div class="d-flex justify-content-between align-items-center">
                            <h5 class="mb-0">Distribución del Inventario</h5>
                            <div class="btn-group btn-group-sm">
                                <button type="button" class="btn btn-outline-secondary">Semanal</button>
                                <button type="button" class="btn btn-outline-secondary active">Mensual</button>
                                <button type="button" class="btn btn-outline-secondary">Anual</button>
                            </div>
                        </div>
                    </div>
                    <div class="card-body">
                        <canvas id="stockDistributionChart" height="300"></canvas>
                    </div>
                </div>
            </div>

            <!-- Gráfico de líneas de tendencias de stock -->
            <div class="col-lg-6">
                <div class="card">
                    <div class="card-header bg-white">
                        <div class="d-flex justify-content-between align-items-center">
                            <h5 class="mb-0">Tendencias de Inventario</h5>
                            <div class="btn-group btn-group-sm">
                                <button type="button" class="btn btn-outline-secondary active">7 días</button>
                                <button type="button" class="btn btn-outline-secondary">30 días</button>
                                <button type="button" class="btn btn-outline-secondary">90 días</button>
                            </div>
                        </div>
                    </div>
                    <div class="card-body">
                        <canvas id="stockTrendsChart" height="300"></canvas>
                    </div>
                </div>
            </div>
        </div>

        <div class="row">
            <!-- Tabla de artículos con stock bajo -->
            <div class="col-lg-6">
                <div class="card">
                    <div class="card-header bg-white">
                        <div class="d-flex justify-content-between align-items-center">
                            <h5 class="mb-0">Artículos con Stock Bajo</h5>
                            <a href="#" class="btn btn-sm btn-outline-primary">Ver todos</a>
                        </div>
                    </div>
                    <div class="card-body table-container">
                        <table class="table table-hover">
                            <thead>
                                <tr>
                                    <th>Código</th>
                                    <th>Artículo</th>
                                    <th>Cantidad</th>
                                    <th>Estado</th>
                                </tr>
                            </thead>
                            <tbody id="low-stock-table">
                                <!-- Los datos se cargarán dinámicamente -->
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>

            <!-- Movimientos recientes -->
            <div class="col-lg-6">
                <div class="card">
                    <div class="card-header bg-white">
                        <div class="d-flex justify-content-between align-items-center">
                            <h5 class="mb-0">Movimientos Recientes</h5>
                            <a href="#" class="btn btn-sm btn-outline-primary">Ver todos</a>
                        </div>
                    </div>
                    <div class="card-body table-container">
                        <table class="table table-hover">
                            <thead>
                                <tr>
                                    <th>Nro. Mov.</th>
                                    <th>Artículo</th>
                                    <th>Cantidad</th>
                                    <th>Tipo</th>
                                    <th>Fecha</th>
                                </tr>
                            </thead>
                            <tbody id="recent-movements-table">
                                <!-- Los datos se cargarán dinámicamente -->
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Bootstrap JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/js/bootstrap.bundle.min.js"></script>
    
    <!-- Script principal -->
    <script>
        // Formatear números como moneda
        function formatCurrency(value) {
            return new Intl.NumberFormat('es-AR', { 
                style: 'currency', 
                currency: 'ARS',
                minimumFractionDigits: 2
            }).format(value);
        }

        // Función para obtener los datos del dashboard
        async function fetchDashboardData() {
            try {
                const response = await fetch('/stock/api/dashboard-data');
                if (!response.ok) {
                    throw new Error('Error al obtener datos del dashboard');
                }
                const data = await response.json();
                updateDashboard(data);
            } catch (error) {
                console.error('Error:', error);
                document.getElementById('dashboard-container').innerHTML = `
                    <div class="alert alert-danger" role="alert">
                        Error al cargar los datos del dashboard. Por favor, intente nuevamente más tarde.
                    </div>
                `;
            }
        }

        // Función para actualizar el dashboard con los datos
        function updateDashboard(data) {
            // Actualizar métricas principales
            document.getElementById('total-items').textContent = data.total_items;
            document.getElementById('total-value').textContent = formatCurrency(data.total_value);
            document.getElementById('low-stock').textContent = data.low_stock_items.length;
            document.getElementById('recent-movements').textContent = data.recent_movements.length;

            // Actualizar tabla de artículos con stock bajo
            const lowStockTable = document.getElementById('low-stock-table');
            lowStockTable.innerHTML = '';
            
            if (data.low_stock_items.length === 0) {
                lowStockTable.innerHTML = '<tr><td colspan="4" class="text-center">No hay artículos con stock bajo</td></tr>';
            } else {
                data.low_stock_items.forEach(item => {
                    const row = document.createElement('tr');
                    
                    // Determinar la clase de badge según la cantidad
                    let badgeClass = '';
                    if (item.cantidad < 5) {
                        badgeClass = 'badge-low-stock';
                    } else if (item.cantidad < 10) {
                        badgeClass = 'badge-medium-stock';
                    } else {
                        badgeClass = 'badge-good-stock';
                    }
                    
                    row.innerHTML = `
                        <td>${item.codigo_art || '-'}</td>
                        <td>${item.descripcion || 'Sin descripción'}</td>
                        <td>${item.cant_disponible || 0}</td>
                        <td><span class="badge ${badgeClass}">${item.cant_disponible < 5 ? 'Crítico' : 'Bajo'}</span></td>
                    `;
                    lowStockTable.appendChild(row);
                });
            }

            // Actualizar tabla de movimientos recientes
            const recentMovementsTable = document.getElementById('recent-movements-table');
            recentMovementsTable.innerHTML = '';
            
            if (data.recent_movements.length === 0) {
                recentMovementsTable.innerHTML = '<tr><td colspan="5" class="text-center">No hay movimientos recientes</td></tr>';
            } else {
                data.recent_movements.forEach(movement => {
                    const row = document.createElement('tr');
                    const date = movement.fecha ? new Date(movement.fecha).toLocaleDateString('es-AR') : '-';
                    
                    row.innerHTML = `
                        <td>${movement.nro_movimiento || '-'}</td>
                        <td>${movement.codigo_art || '-'}</td>
                        <td>${movement.cant_disponible || 0}</td>
                        <td>${movement.tipo ? 'Entrada' : 'Salida'}</td>
                        <td>${date}</td>
                    `;
                    recentMovementsTable.appendChild(row);
                });
            }

            // Inicializar gráficos
            initCharts(data);
        }

        // Función para inicializar los gráficos
        function initCharts(data) {
            // Gráfico de distribución de stock
            const ctxDistribution = document.getElementById('stockDistributionChart').getContext('2d');
            new Chart(ctxDistribution, {
                type: 'doughnut',
                data: {
                    labels: ['Stock Alto', 'Stock Medio', 'Stock Bajo', 'Stock Crítico'],
                    datasets: [{
                        data: [
                            // Clasificar artículos por nivel de stock (ejemplo)
                            data.total_items - data.low_stock_items.length - 5, // Stock alto (ejemplo)
                            5, // Stock medio (ejemplo)
                            data.low_stock_items.filter(item => item.cant_disponible >= 5).length, // Stock bajo
                            data.low_stock_items.filter(item => item.cant_disponible < 5).length // Stock crítico
                        ],
                        backgroundColor: [
                            '#2ecc71', // Verde - Stock alto
                            '#3498db', // Azul - Stock medio
                            '#f39c12', // Amarillo - Stock bajo
                            '#e74c3c'  // Rojo - Stock crítico
                        ],
                        borderWidth: 0
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'bottom'
                        }
                    }
                }
            });

            // Gráfico de tendencias de stock
            const ctxTrends = document.getElementById('stockTrendsChart').getContext('2d');
            
            // Datos de ejemplo para el gráfico de tendencias
            const labels = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo'];
            const entradas = [12, 19, 15, 8, 22, 14, 10]; // Datos de ejemplo
            const salidas = [8, 15, 12, 6, 18, 10, 7];    // Datos de ejemplo
            
            new Chart(ctxTrends, {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: [
                        {
                            label: 'Entradas',
                            data: entradas,
                            borderColor: '#2ecc71',
                            backgroundColor: 'rgba(46, 204, 113, 0.1)',
                            borderWidth: 2,
                            fill: true,
                            tension: 0.3
                        },
                        {
                            label: 'Salidas',
                            data: salidas,
                            borderColor: '#e74c3c',
                            backgroundColor: 'rgba(231, 76, 60, 0.1)',
                            borderWidth: 2,
                            fill: true,
                            tension: 0.3
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'bottom'
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
        }

        // Función para exportar a PDF (simulada)
        function exportToPDF() {
            alert('Exportando a PDF...\n\nEsta funcionalidad requiere implementación adicional con una biblioteca como jsPDF o usando el backend para generar PDFs.');
        }

        // Cargar datos al iniciar la página
        document.addEventListener('DOMContentLoaded', fetchDashboardData);
    </script>
</body>
</html>"""


@router.get("/api/dashboard-data")
async def get_dashboard_data(db: Session = Depends(get_db)):
    """
    Endpoint API que devuelve los datos necesarios para el dashboard
    """
    try:
        # Obtener todos los registros de stock
        stock_items = gets_stock(db)
        
        # Crear algunos datos "mock" basados en los artículos disponibles
        # Ya que no tenemos todas las columnas en la tabla real
        
        # Ejemplo de datos para el dashboard adaptado a nuestras columnas disponibles
        dashboard_data = {
            "total_items": len(stock_items),
            "total_value": len(stock_items) * 1000,  # Valor ficticio ya que no tenemos precios
            "low_stock_items": [],
            "recent_movements": [StockRead.model_validate(item) for item in stock_items[-10:]] if stock_items else []
        }
        
        # Generar algunos datos de ejemplo para los artículos con stock bajo
        # hasta que la tabla real tenga estos campos
        low_stock_mock = []
        for i, item in enumerate(stock_items[:5]):  # Tomamos los primeros 5 como ejemplo
            low_stock_item = StockRead.model_validate(item)
            # Añadimos propiedades para la interfaz (estos valores no existen en la BD real)
            setattr(low_stock_item, "descripcion", f"Artículo de prueba {i+1}")
            setattr(low_stock_item, "cant_disponible", i + 3)  # Valores simulados entre 3 y 7
            low_stock_mock.append(low_stock_item)
            
        dashboard_data["low_stock_items"] = low_stock_mock
        
        return dashboard_data
    except Exception as e:
        logger.error(f"Error al obtener datos para el dashboard: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                           detail="Error al procesar los datos del dashboard.")
