/**
 * Dashboard de Administración de Tickets
 */

// Variables globales para los gráficos
let chartEstados = null;
let chartCategorias = null;
let chartTendencia = null;
let chartPrioridades = null;
let dashboardData = null;
let loadingIndicator = null;

/**
 * Inicializa la página cuando el DOM está listo
 */
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM cargado - Inicializando dashboard de tickets');
    
    // Inicializar referencia al indicador de carga
    loadingIndicator = document.getElementById('loading-indicator');
    
    // Inicializar gráficos
    inicializarGraficos();
    
    // Cargar datos iniciales
    cargarDashboardData();
    
    // Configurar event listeners
    setupEventListeners();

    // Iniciar actualización automática
    iniciarActualizacionAutomatica();
    
    // Cargar componentes dinámicos si es necesario
    if (window.cargarComponentes) {
        window.cargarComponentes();
    }
});

/**
 * Configura los event listeners de los elementos interactivos
 */
function setupEventListeners() {
    // Listener para cambio de período
    const periodSelect = document.getElementById('period-select');
    if (periodSelect) {
        periodSelect.addEventListener('change', cambiarPeriodo);
    }
}

/**
 * Maneja el cambio de período seleccionado
 */
function cambiarPeriodo() {
    const periodo = document.getElementById('period-select').value;
    const customDates = document.getElementById('custom-dates');
    
    // Mostrar/ocultar selector de fechas personalizadas
    if (periodo === 'personalizado') {
        customDates.classList.remove('hidden');
    } else {
        customDates.classList.add('hidden');
        // Cargar datos automáticamente al cambiar período (excepto si es personalizado)
        cargarDashboardData();
    }
}
// Configuración de actualizaciones automáticas
let autoRefreshEnabled = true;
const intervaloActualizacion = 5 * 60 * 1000; // 5 minutos en milisegundos
let timerInterval = null;
let actualizacionTimer = null;

/**
 * Inicializa la actualización automática
 */
function iniciarActualizacionAutomatica() {
    // Crear temporizador para actualizar datos
    actualizacionTimer = setInterval(() => {
        if (autoRefreshEnabled) {
            console.log('Actualizando datos automáticamente...');
            cargarDashboardData();
        }
    }, intervaloActualizacion);
    
    // Iniciar el contador visual
    actualizarContador();
    
    // Configurar botón de pausa/reanudar
    const toggleButton = document.getElementById('toggle-auto-refresh');
    if (toggleButton) {
        toggleButton.addEventListener('click', toggleAutoRefresh);
    }
}

/**
 * Actualiza el contador visual
 */
function actualizarContador() {
    const contador = document.getElementById('contador-actualizacion');
    if (!contador) return;
    
    // Limpiar intervalo previo si existe
    if (timerInterval) clearInterval(timerInterval);
    
    // Iniciar valores
    let segundos = intervaloActualizacion / 1000;
    
    // Actualizar contador cada segundo
    timerInterval = setInterval(() => {
        if (!autoRefreshEnabled) return;
        
        segundos--;
        const minutos = Math.floor(segundos / 60);
        const segs = Math.floor(segundos % 60);
        contador.textContent = `${minutos}:${segs.toString().padStart(2, '0')}`;
        
        // Si llegamos a cero, reiniciar
        if (segundos <= 0) {
            clearInterval(timerInterval);
            // El contador se reiniciará cuando cargarDashboardData termine
        }
    }, 1000);
}

/**
 * Activa/desactiva la actualización automática
 */
function toggleAutoRefresh() {
    autoRefreshEnabled = !autoRefreshEnabled;
    
    const toggleButton = document.getElementById('toggle-auto-refresh');
    if (toggleButton) {
        if (autoRefreshEnabled) {
            toggleButton.innerHTML = '<i class="fas fa-pause"></i>';
            toggleButton.title = 'Pausar actualización automática';
            actualizarContador(); // Reiniciar contador
        } else {
            toggleButton.innerHTML = '<i class="fas fa-play"></i>';
            toggleButton.title = 'Reanudar actualización automática';
        }
    }
    
    console.log(`Actualización automática: ${autoRefreshEnabled ? 'activada' : 'pausada'}`);
}
/**
 * Aplica el período personalizado seleccionado
 */
function aplicarPeriodoPersonalizado() {
    const fechaInicio = document.getElementById('start_date').value;
    const fechaFin = document.getElementById('end_date').value;
    
    if (!fechaInicio || !fechaFin) {
        mostrarError('Debes seleccionar ambas fechas para el período personalizado');
        return;
    }
    
    cargarDashboardData();
}

/**
 * Función de conveniencia para recargar los datos
 */
function cargarDatos() {
    cargarDashboardData();
}

/**
 * Inicializa los gráficos vacíos
 */
function inicializarGraficos() {
    console.log('Inicializando gráficos...');
    
    // Gráfico de estados (Pie chart)
    const ctxEstados = document.getElementById('chart-estados');
    if (ctxEstados) {
        chartEstados = new Chart(ctxEstados, {
            type: 'doughnut',
            data: {
                labels: ['Abiertos', 'En Proceso', 'Cerrados'],
                datasets: [{
                    data: [0, 0, 0],
                    backgroundColor: ['#3b82f6', '#f59e0b', '#10b981'],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'right'
                    }
                },
                cutout: '60%',
                animation: {
                    animateScale: true,
                    animateRotate: true
                }
            }
        });
    }
    
    // Gráfico de categorías (Bar chart)
    const ctxCategorias = document.getElementById('chart-categorias');
    if (ctxCategorias) {
        chartCategorias = new Chart(ctxCategorias, {
            type: 'bar',
            data: {
                labels: ['Hardware', 'Software', 'Red', 'Cuenta', 'Otro'],
                datasets: [{
                    label: 'Tickets por categoría',
                    data: [0, 0, 0, 0, 0],
                    backgroundColor: [
                        'rgba(54, 162, 235, 0.6)',
                        'rgba(75, 192, 192, 0.6)',
                        'rgba(255, 159, 64, 0.6)',
                        'rgba(153, 102, 255, 0.6)',
                        'rgba(201, 203, 207, 0.6)'
                    ],
                    borderColor: [
                        'rgba(54, 162, 235, 1)',
                        'rgba(75, 192, 192, 1)',
                        'rgba(255, 159, 64, 1)',
                        'rgba(153, 102, 255, 1)',
                        'rgba(201, 203, 207, 1)'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            precision: 0
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        });
    }
    
    // Gráfico de tendencia (Line chart)
    const ctxTendencia = document.getElementById('chart-tendencia');
    if (ctxTendencia) {
        chartTendencia = new Chart(ctxTendencia, {
            type: 'line',
            data: {
                labels: ['', '', '', '', '', '', ''],
                datasets: [
                    {
                        label: 'Nuevos',
                        data: [0, 0, 0, 0, 0, 0, 0],
                        backgroundColor: 'rgba(59, 130, 246, 0.2)',
                        borderColor: 'rgba(59, 130, 246, 1)',
                        borderWidth: 2,
                        tension: 0.4,
                        fill: true
                    },
                    {
                        label: 'Resueltos',
                        data: [0, 0, 0, 0, 0, 0, 0],
                        backgroundColor: 'rgba(16, 185, 129, 0.2)',
                        borderColor: 'rgba(16, 185, 129, 1)',
                        borderWidth: 2,
                        tension: 0.4,
                        fill: true
                    }
                ]
            },
            options: {
                responsive: true,
                interaction: {
                    mode: 'index',
                    intersect: false,
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            precision: 0
                        }
                    }
                }
            }
        });
    }
    
    // Gráfico de prioridades (Doughnut chart)
    const ctxPrioridades = document.getElementById('chart-prioridades');
    if (ctxPrioridades) {
        chartPrioridades = new Chart(ctxPrioridades, {
            type: 'doughnut',
            data: {
                labels: ['Baja', 'Media', 'Alta', 'Crítica'],
                datasets: [{
                    data: [0, 0, 0, 0],
                    backgroundColor: [
                        '#10b981', // Verde para baja
                        '#3b82f6', // Azul para media
                        '#f59e0b', // Naranja para alta
                        '#ef4444'  // Rojo para crítica
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'right'
                    }
                },
                cutout: '60%',
                animation: {
                    animateScale: true,
                    animateRotate: true
                }
            }
        });
    }
    
    console.log('Gráficos inicializados correctamente');
}

/**
 * Carga los datos del dashboard desde la API
 */
async function cargarDashboardData() {
    console.log('Cargando datos del dashboard...');
    
    // Mostrar spinners de carga
    mostrarLoadingIndicators(true);
    
    try {
        // Obtener período seleccionado
        const periodo = document.getElementById('period-select').value;
        let url = `/tickets/statistics?period=${periodo}`;
        
        // Si es período personalizado, agregar fechas
        if (periodo === 'personalizado') {
            const fechaInicio = document.getElementById('start_date').value;
            const fechaFin = document.getElementById('end_date').value;
            
            if (!fechaInicio || !fechaFin) {
                throw new Error('Para el período personalizado debes seleccionar ambas fechas');
            }
            
            url += `&start_date=${fechaInicio}&end_date=${fechaFin}`;
        }
        
        console.log('Consultando API:', url);
        
        // Realizar petición a la API
        const response = await fetch(url, {
            method: 'GET',
            headers: {
                'Cache-Control': 'no-cache',
                'Pragma': 'no-cache'
            }
        });
        
        if (!response.ok) {
            throw new Error(`Error en la petición: ${response.status} ${response.statusText}`);
        }
        
        // Obtener datos
        dashboardData = await response.json();
        console.log('Datos recibidos:', dashboardData);
        
        // Actualizar componentes de la interfaz
        actualizarKPIs();
        actualizarGraficos();
        actualizarTicketsRecientes();
        actualizarTicketsCriticos();
        actualizarMetricas();
        
        // Ocultar spinners de carga
        mostrarLoadingIndicators(false);
        
    } catch (error) {
        console.error('Error al cargar datos del dashboard:', error);
        mostrarError(`Error al cargar datos: ${error.message}`);
        
        // Ocultar spinners de carga
        mostrarLoadingIndicators(false);
    }
}

/**
 * Muestra u oculta los indicadores de carga
 */
function mostrarLoadingIndicators(mostrar) {
    const loadingElements = document.querySelectorAll('.loading-overlay');
    loadingElements.forEach(element => {
        if (mostrar) {
            element.classList.remove('hidden');
        } else {
            element.classList.add('hidden');
        }
    });
    
    // También controlar el indicador principal de carga
    if (loadingIndicator) {
        if (mostrar) {
            loadingIndicator.classList.remove('hidden');
        } else {
            loadingIndicator.classList.add('hidden');
        }
    }
}

/**
 * Actualiza las tarjetas de KPIs con los datos recibidos
 */
function actualizarKPIs() {
    if (!dashboardData) return;
    
    // Actualizar números en tarjetas - CORREGIDO para usar los IDs correctos
    const totalTickets = document.getElementById('kpi-total');
    const ticketsAbiertos = document.getElementById('kpi-abiertos');
    const ticketsProceso = document.getElementById('kpi-proceso');
    const ticketsCerrados = document.getElementById('kpi-cerrados');
    
    if (totalTickets) totalTickets.textContent = dashboardData.total || 0;
    if (ticketsAbiertos) ticketsAbiertos.textContent = dashboardData.abiertos || 0;
    if (ticketsProceso) ticketsProceso.textContent = dashboardData.proceso || 0;
    if (ticketsCerrados) ticketsCerrados.textContent = dashboardData.cerrados || 0;
    
    // Actualizar comparaciones si existen los elementos
    if (dashboardData.comparacion) {
        actualizarComparacion('kpi-total-change', dashboardData.comparacion.total);
        actualizarComparacion('kpi-abiertos-change', dashboardData.comparacion.abiertos);
        actualizarComparacion('kpi-proceso-change', dashboardData.comparacion.proceso);
        actualizarComparacion('kpi-cerrados-change', dashboardData.comparacion.cerrados);
    }
}

/**
 * Actualiza el indicador de comparación en una tarjeta
 */
function actualizarComparacion(elementId, valor) {
    if (valor === undefined) return;
    
    const elemento = document.getElementById(elementId);
    if (!elemento) return;
    
    let iconoClass, textClass;
    let texto = valor > 0 ? `+${valor}%` : `${valor}%`;
    
    if (valor === 0) {
        iconoClass = 'fa-minus text-gray-600';
        textClass = 'text-gray-600';
    } else if (valor > 0) {
        iconoClass = 'fa-arrow-up text-green-600';  // Crecimiento (verde para cerrados, rojo para otros)
        textClass = elementId.includes('cerrados') ? 'text-green-600' : 'text-red-600';
    } else {
        iconoClass = 'fa-arrow-down text-red-600';  // Decrecimiento (rojo para cerrados, verde para otros)
        textClass = elementId.includes('cerrados') ? 'text-red-600' : 'text-green-600';
    }
    
    // Actualizar contenido con clases correctas
    elemento.innerHTML = `<i class="fas ${iconoClass} mr-1"></i> <span class="${textClass}">${texto}</span>`;
}

/**
 * Actualiza los gráficos con los datos recibidos
 */
function actualizarGraficos() {
    if (!dashboardData) return;
    
    // Actualizar gráfico de estados
    if (chartEstados) {
        chartEstados.data.datasets[0].data = dashboardData.porEstado || [0, 0, 0];
        chartEstados.update();
    }
    
    // Actualizar gráfico de categorías
    if (chartCategorias) {
        chartCategorias.data.datasets[0].data = dashboardData.porCategoria || [0, 0, 0, 0, 0];
        chartCategorias.update();
        
        // Actualizar leyendas si es necesario
        const leyendaContainer = document.getElementById('categorias-leyenda');
        if (leyendaContainer) {
            // Puedes añadir código aquí para actualizar las leyendas
        }
    }
    
    // Actualizar gráfico de tendencia
    if (chartTendencia && dashboardData.tendencia) {
        // Obtener etiquetas adecuadas según el período
        const etiquetas = obtenerEtiquetasPeriodo(dashboardData.period);
        
        chartTendencia.data.labels = etiquetas;
        chartTendencia.data.datasets[0].data = dashboardData.tendencia.nuevos || [0, 0, 0, 0, 0, 0, 0];
        chartTendencia.data.datasets[1].data = dashboardData.tendencia.resueltos || [0, 0, 0, 0, 0, 0, 0];
        chartTendencia.update();
    }
    
    // Actualizar gráfico de prioridades
    if (chartPrioridades) {
        chartPrioridades.data.datasets[0].data = dashboardData.porPrioridad || [0, 0, 0, 0];
        chartPrioridades.update();
    }
}

/**
 * Obtiene las etiquetas para el gráfico de tendencia según el período
 */
function obtenerEtiquetasPeriodo(periodo) {
    // Código existente para etiquetas de períodos...
    const hoy = new Date();
    
    switch (periodo) {
        case 'hoy':
            return ['00:00', '03:00', '06:00', '09:00', '12:00', '15:00', '18:00', '21:00'];
        case 'semana':
            const diasSemana = ['Dom', 'Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb'];
            const etiquetasDias = [];
            for (let i = 6; i >= 0; i--) {
                const fecha = new Date(hoy);
                fecha.setDate(hoy.getDate() - i);
                etiquetasDias.push(diasSemana[fecha.getDay()]);
            }
            return etiquetasDias;
        case 'mes':
            return ['Semana 1', 'Semana 2', 'Semana 3', 'Semana 4', 'Semana 5'];
        case 'trimestre':
            const mesesCorto = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'];
            const etiquetasMeses = [];
            for (let i = 2; i >= 0; i--) {
                const fecha = new Date(hoy);
                fecha.setMonth(hoy.getMonth() - i);
                etiquetasMeses.push(mesesCorto[fecha.getMonth()]);
            }
            return etiquetasMeses;
        case 'anio':
            const meses = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'];
            const ultimosMeses = [];
            for (let i = 11; i >= 0; i--) {
                const fecha = new Date(hoy);
                fecha.setMonth(hoy.getMonth() - i);
                ultimosMeses.push(meses[fecha.getMonth()]);
            }
            return ultimosMeses;
        default:
            return ['', '', '', '', '', '', ''];
    }
}

/**
 * Actualiza la tabla de tickets recientes
 */
function actualizarTicketsRecientes() {
    if (!dashboardData || !dashboardData.ticketsRecientes) return;
    
    const tbody = document.getElementById('tickets-recientes');
    if (!tbody) return;
    
    // Limpiar tabla
    tbody.innerHTML = '';
    
    // Si no hay tickets, mostrar mensaje
    if (dashboardData.ticketsRecientes.length === 0) {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td colspan="5" class="px-4 py-4 text-center text-gray-500">
                No hay tickets recientes
            </td>
        `;
        tbody.appendChild(tr);
        return;
    }
    
    // Agregar tickets
    dashboardData.ticketsRecientes.forEach(ticket => {
        const tr = document.createElement('tr');
        
        // Formatear fecha
        const fecha = new Date(ticket.fecha_creacion);
        const fechaFormateada = `${fecha.getDate()}/${fecha.getMonth() + 1}/${fecha.getFullYear()}`;
        
        // Determinar clase para el estado
        let estadoClass = '';
        switch (ticket.estado) {
            case 'abierto':
                estadoClass = 'bg-blue-100 text-blue-800';
                break;
            case 'en_proceso':
                estadoClass = 'bg-yellow-100 text-yellow-800';
                break;
            case 'cerrado':
                estadoClass = 'bg-green-100 text-green-800';
                break;
            default:
                estadoClass = 'bg-gray-100 text-gray-800';
        }
        
        tr.innerHTML = `
            <td class="px-4 py-2 whitespace-nowrap">
                <a href="/tickets/detalle/${ticket.id}" class="text-indigo-600 hover:text-indigo-900">
                    #${ticket.id}
                </a>
            </td>
            <td class="px-4 py-2">
                ${ticket.titulo}
            </td>
            <td class="px-4 py-2 whitespace-nowrap">
                ${ticket.solicitante || 'Anónimo'}
            </td>
            <td class="px-4 py-2 whitespace-nowrap">
                <span class="px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${estadoClass}">
                    ${formatearEstado(ticket.estado)}
                </span>
            </td>
            <td class="px-4 py-2 whitespace-nowrap text-right text-sm text-gray-500">
                ${fechaFormateada}
            </td>
        `;
        
        tbody.appendChild(tr);
    });
}

/**
 * Actualiza la tabla de tickets críticos
 */
function actualizarTicketsCriticos() {
    if (!dashboardData || !dashboardData.ticketsCriticos) return;
    
    const tbody = document.getElementById('tickets-criticos');
    if (!tbody) return;
    
    // Limpiar tabla
    tbody.innerHTML = '';
    
    // Si no hay tickets, mostrar mensaje
    if (dashboardData.ticketsCriticos.length === 0) {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td colspan="5" class="px-4 py-4 text-center text-gray-500">
                No hay tickets críticos pendientes
            </td>
        `;
        tbody.appendChild(tr);
        return;
    }
    
    // Agregar tickets
    dashboardData.ticketsCriticos.forEach(ticket => {
        const tr = document.createElement('tr');
        
        // Formatear fecha
        const fecha = new Date(ticket.fecha_creacion);
        const fechaFormateada = `${fecha.getDate()}/${fecha.getMonth() + 1}/${fecha.getFullYear()}`;
        
        // Determinar clase para el estado
        let estadoClass = '';
        switch (ticket.estado) {
            case 'abierto':
                estadoClass = 'bg-blue-100 text-blue-800';
                break;
            case 'en_proceso':
                estadoClass = 'bg-yellow-100 text-yellow-800';
                break;
            case 'cerrado':
                estadoClass = 'bg-green-100 text-green-800';
                break;
            default:
                estadoClass = 'bg-gray-100 text-gray-800';
        }
        
        tr.innerHTML = `
            <td class="px-4 py-2 whitespace-nowrap">
                <a href="/tickets/detalle/${ticket.id}" class="text-indigo-600 hover:text-indigo-900">
                    #${ticket.id}
                </a>
            </td>
            <td class="px-4 py-2">
                ${ticket.titulo}
            </td>
            <td class="px-4 py-2 whitespace-nowrap">
                ${ticket.departamento || 'No asignado'}
            </td>
            <td class="px-4 py-2 whitespace-nowrap">
                <span class="px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${estadoClass}">
                    ${formatearEstado(ticket.estado)}
                </span>
            </td>
            <td class="px-4 py-2 whitespace-nowrap text-right text-sm text-gray-500">
                ${fechaFormateada}
            </td>
        `;
        
        tbody.appendChild(tr);
    });
}

/**
 * Actualiza las métricas de rendimiento
 */
function actualizarMetricas() {
    if (!dashboardData || !dashboardData.metricas) return;
    
    const metricas = dashboardData.metricas;
    
    // Actualizar valores si existen los elementos - CORREGIDO con los IDs correctos
    const tiempoRespuesta = document.getElementById('metrica-respuesta');
    const tiempoResolucion = document.getElementById('metrica-resolucion');
    const tasaResolucion = document.getElementById('metrica-plazo');
    const satisfaccion = document.getElementById('metrica-satisfaccion');
    
    if (tiempoRespuesta) tiempoRespuesta.textContent = `${metricas.tiempo_primera_respuesta || 0}h`;
    if (tiempoResolucion) tiempoResolucion.textContent = `${metricas.tiempo_resolucion || 0}h`;
    if (tasaResolucion) tasaResolucion.textContent = `${metricas.tasa_resolucion_plazo || 0}%`;
    if (satisfaccion) satisfaccion.textContent = metricas.satisfaccion_cliente || 0;
}

/**
 * Formatea un estado de ticket para mostrar
 */
function formatearEstado(estado) {
    if (!estado) return 'Desconocido';
    
    switch (estado.toLowerCase()) {
        case 'abierto':
            return 'Abierto';
        case 'en_proceso':
            return 'En proceso';
        case 'cerrado':
            return 'Cerrado';
        default:
            return estado.charAt(0).toUpperCase() + estado.slice(1);
    }
}

/**
 * Muestra un mensaje de error
 */
function mostrarError(mensaje) {
    console.error(mensaje);
    
    // Crear un elemento para mostrar el error
    const alerta = document.createElement('div');
    alerta.className = 'fixed bottom-4 right-4 bg-red-500 text-white px-6 py-3 rounded-lg shadow-lg z-50 flex items-center';
    alerta.innerHTML = `
        <i class="fas fa-exclamation-circle mr-2"></i>
        <span>${mensaje}</span>
        <button class="ml-4 text-white hover:text-red-200" onclick="this.parentNode.remove()">
            <i class="fas fa-times"></i>
        </button>
    `;
    
    document.body.appendChild(alerta);
    
    // Auto ocultar después de 5 segundos
    setTimeout(() => {
        alerta.remove();
    }, 5000);
}

// Para compatibilidad con otros scripts
function testAPI() {
    cargarDashboardData();
}