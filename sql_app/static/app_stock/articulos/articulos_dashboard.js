/**
 * Dashboard de Artículos
 * Script para gestionar la funcionalidad interactiva del dashboard
 */

// Variables globales
let pricesChart = null;

// Inicializar cuando el DOM esté cargado
document.addEventListener('DOMContentLoaded', function() {
    // Inicializar componentes UI
    initUI();
    
    // Cargar datos del gráfico (desde elemento data-prices o API)
    loadChartData();
    
    // Activar botones y menús
    setupEventListeners();
});

/**
 * Inicializa elementos de la interfaz de usuario
 */
function initUI() {
    // Menú de usuario
    const userMenuButton = document.getElementById('user-menu-button');
    const userMenu = document.getElementById('user-menu');
    
    if (userMenuButton && userMenu) {
        userMenuButton.addEventListener('click', function() {
            userMenu.classList.toggle('hidden');
        });
        
        // Cerrar al hacer clic fuera
        document.addEventListener('click', function(event) {
            if (!userMenuButton.contains(event.target) && !userMenu.contains(event.target)) {
                userMenu.classList.add('hidden');
            }
        });
    }
    
    // Menú de opciones del gráfico
    const chartOptionsBtn = document.getElementById('chart-options');
    const chartMenu = document.getElementById('chart-menu');
    
    if (chartOptionsBtn && chartMenu) {
        chartOptionsBtn.addEventListener('click', function() {
            chartMenu.classList.toggle('hidden');
        });
        
        // Cerrar al hacer clic fuera
        document.addEventListener('click', function(event) {
            if (!chartOptionsBtn.contains(event.target) && !chartMenu.contains(event.target)) {
                chartMenu.classList.add('hidden');
            }
        });
    }
}

/**
 * Configura listeners para eventos de la página
 */
function setupEventListeners() {
    // Botón de recargar gráfico
    const refreshChartBtn = document.getElementById('refresh-chart');
    if (refreshChartBtn) {
        refreshChartBtn.addEventListener('click', function() {
            const url = refreshChartBtn.getAttribute('data-url') || '/articulos/estadisticas';
            fetch(url)
                .then(response => response.json())
                .then(data => {
                    if (data.price_data) {
                        updateChart(data.price_data);
                    }
                })
                .catch(error => {
                    console.error('Error al actualizar gráfico:', error);
                });
        });
    }
    
    // Enlaces de exportación en el menú del gráfico
    const chartMenu = document.getElementById('chart-menu');
    if (chartMenu) {
        const exportPngLink = chartMenu.querySelector('a:nth-child(1)');
        if (exportPngLink) {
            exportPngLink.addEventListener('click', function(e) {
                e.preventDefault();
                exportChartAs('png');
            });
        }
        
        const exportPdfLink = chartMenu.querySelector('a:nth-child(2)');
        if (exportPdfLink) {
            exportPdfLink.addEventListener('click', function(e) {
                e.preventDefault();
                exportChartAs('pdf');
            });
        }
    }
}

/**
 * Carga los datos del gráfico de cambios de precios
 */
function loadChartData() {
    const priceDataElement = document.getElementById('price-data');
    
    if (priceDataElement && priceDataElement.dataset.prices) {
        try {
            const priceData = JSON.parse(priceDataElement.dataset.prices);
            initPricesChart(priceData);
        } catch (error) {
            console.error('Error al parsear datos de precios:', error);
            
            // Intentar obtener datos desde la API como respaldo
            fetch('/articulos/estadisticas')
                .then(response => response.json())
                .then(data => {
                    if (data.price_data) {
                        initPricesChart(data.price_data);
                    }
                })
                .catch(error => {
                    console.error('Error al cargar datos del gráfico desde API:', error);
                    showEmptyChart();
                });
        }
    } else {
        // No hay elemento con datos, cargar desde API
        fetch('/articulos/estadisticas')
            .then(response => response.json())
            .then(data => {
                if (data.price_data) {
                    initPricesChart(data.price_data);
                }
            })
            .catch(error => {
                console.error('Error al cargar datos del gráfico desde API:', error);
                showEmptyChart();
            });
    }
}

/**
 * Inicializa el gráfico de cambios de precios
 */
function initPricesChart(priceData) {
    const ctx = document.getElementById('pricesChart');
    if (!ctx) return;
    
    // Preparar datos para el gráfico
    const labels = priceData.labels || [];
    const costoPriceData = priceData.costo || [];
    const ventaPriceData = priceData.venta || [];
    
    // Destruir gráfico existente si hay uno
    if (pricesChart) {
        pricesChart.destroy();
    }
    
    // Crear el nuevo gráfico
    pricesChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Cambios en precio de costo',
                    data: costoPriceData,
                    backgroundColor: 'rgba(59, 130, 246, 0.6)',
                    borderColor: 'rgb(59, 130, 246)',
                    borderWidth: 1
                },
                {
                    label: 'Cambios en precio de venta',
                    data: ventaPriceData,
                    backgroundColor: 'rgba(16, 185, 129, 0.6)',
                    borderColor: 'rgb(16, 185, 129)',
                    borderWidth: 1
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                },
                tooltip: {
                    mode: 'index',
                    intersect: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Cantidad de cambios de precio'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Mes'
                    }
                }
            }
        }
    });
}

/**
 * Actualiza los datos del gráfico
 */
function updateChart(priceData) {
    if (!pricesChart) {
        initPricesChart(priceData);
        return;
    }
    
    pricesChart.data.labels = priceData.labels || [];
    pricesChart.data.datasets[0].data = priceData.costo || [];
    pricesChart.data.datasets[1].data = priceData.venta || [];
    
    // Asegurarse de que la leyenda esté visible y el título del eje Y sea correcto
    pricesChart.options.plugins.legend.display = true;
    pricesChart.options.scales.y.title.text = 'Cantidad de cambios de precio';
    
    pricesChart.update();
}

/**
 * Muestra un gráfico vacío cuando no hay datos disponibles
 */
function showEmptyChart() {
    const ctx = document.getElementById('pricesChart');
    if (!ctx) return;
    
    if (pricesChart) {
        pricesChart.destroy();
    }
    
    pricesChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['No hay datos disponibles'],
            datasets: [{
                data: [0],
                backgroundColor: 'rgba(200, 200, 200, 0.3)',
                borderColor: 'rgb(200, 200, 200)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    enabled: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        display: false
                    },
                    title: {
                        display: true,
                        text: 'Cantidad de cambios de precio'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Mes'
                    }
                }
            }
        }
    });
}

/**
 * Exporta el gráfico como imagen (png) o documento (pdf)
 */
function exportChartAs(format) {
    if (!pricesChart) return;
    
    if (format === 'png') {
        const url = pricesChart.toBase64Image();
        const link = document.createElement('a');
        link.href = url;
        link.download = 'cambios-precios.png';
        link.click();
    } else if (format === 'pdf') {
        // Esto requeriría una biblioteca adicional como jsPDF
        alert('Exportación a PDF no implementada aún');
    }
}

/**
 * Actualiza los datos de actividades recientes con respuesta de la API
 */
function updateRecentActivities(activities) {
    const container = document.getElementById('recent-activities-container');
    if (!container || !activities || activities.length === 0) return;
    
    container.innerHTML = '';
    
    activities.forEach(activity => {
        let borderColorClass = 'border-blue-500';
        let bgColorClass = 'bg-blue-50';
        let icon = '';
        
        // Determinar colores según tipo de actividad
        if (activity.tipo_precio === 'costo') {
            borderColorClass = 'border-blue-500';
            bgColorClass = 'bg-blue-50';
        } else if (activity.tipo_precio === 'venta') {
            borderColorClass = 'border-green-500';
            bgColorClass = 'bg-green-50';
        }
        
        // Crear elemento de actividad
        const activityEl = document.createElement('div');
        activityEl.className = `p-4 border-l-4 ${borderColorClass} ${bgColorClass} rounded-r mt-3`;
        
        // Construir contenido
        let content = `
            <div class="flex justify-between items-start">
                <div>
                    <h3 class="font-medium">Cambio de precio en artículo</h3>
                    <p class="text-sm text-gray-600">Artículo: ${activity.articulo_descripcion}</p>
                </div>
                <span class="text-xs text-gray-500">${activity.tiempo_transcurrido}</span>
            </div>
            <div class="mt-2 flex items-center">
                <span class="text-xs bg-${activity.variacion_porcentual >= 0 ? 'green' : 'red'}-100
                            text-${activity.variacion_porcentual >= 0 ? 'green' : 'red'}-800 px-2 py-1 rounded">
                    ${activity.variacion_porcentual >= 0 ? '+' : ''}${activity.variacion_porcentual}%
                </span>
                <span class="ml-2 text-xs text-gray-600">
                    $${activity.precio_anterior} → $${activity.precio_nuevo}
                </span>
            </div>
        `;
        
        activityEl.innerHTML = content;
        container.appendChild(activityEl);
    });
}

/**
 * Carga actividades recientes desde la API
 */
function loadRecentActivities() {
    const container = document.getElementById('recent-activities-container');
    if (!container) return;
    
    const url = container.getAttribute('data-url') || '/articulos/actividades-recientes';
    
    fetch(url)
        .then(response => response.json())
        .then(data => {
            updateRecentActivities(data);
        })
        .catch(error => {
            console.error('Error al cargar actividades recientes:', error);
        });
}

// Intentar cargar actividades recientes después de que todo esté listo
window.addEventListener('load', function() {
    setTimeout(loadRecentActivities, 500);
});