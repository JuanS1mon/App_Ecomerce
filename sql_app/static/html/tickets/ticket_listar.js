// Declaración de variables globales - Esto va al inicio del archivo
let ticketsData = [];
let currentPage = 0;
let pageSize = 10; 
let totalTickets = 0;

/**
 * Función para mostrar error
 */
function mostrarError(mensaje) {
    console.error(mensaje);
    
    // Crear elemento para mostrar el error
    const errorDiv = document.createElement('div');
    errorDiv.className = 'bg-red-100 border-l-4 border-red-500 text-red-700 p-4 mb-4 error-message';
    errorDiv.innerHTML = `
        <div class="flex">
            <div class="flex-shrink-0">
                <i class="fas fa-exclamation-circle"></i>
            </div>
            <div class="ml-3">
                <p class="text-sm">${mensaje}</p>
            </div>
        </div>
    `;
    
    // Eliminar errores anteriores
    const existingErrors = document.querySelectorAll('.error-message');
    existingErrors.forEach(el => el.remove());
    
    // Buscar donde insertar el error
    const container = document.querySelector('main');
    if (container) {
        if (container.firstChild) {
            container.insertBefore(errorDiv, container.firstChild);
        } else {
            container.appendChild(errorDiv);
        }
    } else {
        document.body.insertBefore(errorDiv, document.body.firstChild);
    }
    
    // Auto-eliminar después de 10 segundos
    setTimeout(() => {
        if (errorDiv.parentNode) {
            errorDiv.parentNode.removeChild(errorDiv);
        }
    }, 10000);
}

/**
 * Función para mostrar cargando
 */
function mostrarCargando(mostrar) {
    const tbody = document.getElementById('ticketsTableBody');
    
    if (!tbody) {
        console.error('No se encontró el elemento tbody para indicador de carga');
        return;
    }
    
    if (mostrar) {
        tbody.innerHTML = `
            <tr>
                <td colspan="8" class="px-6 py-8 text-center">
                    <div class="flex justify-center">
                        <svg class="animate-spin h-8 w-8 text-indigo-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                        </svg>
                    </div>
                    <div class="mt-2 text-gray-500">Cargando tickets...</div>
                </td>
            </tr>
        `;
    }
}

/**
 * Actualiza la paginación
 */
function actualizarPaginacion() {
    const prevPageBtn = document.getElementById('prevPage');
    const nextPageBtn = document.getElementById('nextPage');
    const paginaActualEl = document.getElementById('paginaActual');
    const totalPaginasEl = document.getElementById('totalPaginas');
    
    if (!prevPageBtn || !nextPageBtn || !paginaActualEl || !totalPaginasEl) {
        console.warn('Elementos de paginación no encontrados');
        return;
    }
    
    // Calcular total de páginas
    const totalPages = Math.ceil(totalTickets / pageSize) || 1;
    
    // Actualizar textos
    paginaActualEl.textContent = currentPage + 1;
    totalPaginasEl.textContent = totalPages;
    
    // Habilitar/deshabilitar botones de navegación
    prevPageBtn.disabled = currentPage === 0;
    nextPageBtn.disabled = currentPage >= totalPages - 1 || totalTickets === 0;
    
    if (prevPageBtn.disabled) {
        prevPageBtn.classList.add('opacity-50', 'cursor-not-allowed');
    } else {
        prevPageBtn.classList.remove('opacity-50', 'cursor-not-allowed');
    }
    
    if (nextPageBtn.disabled) {
        nextPageBtn.classList.add('opacity-50', 'cursor-not-allowed');
    } else {
        nextPageBtn.classList.remove('opacity-50', 'cursor-not-allowed');
    }
}

/**
 * Inicializa filtros
 */
function initFiltros() {
    // Obtener elementos de filtros
    const filtroEstado = document.getElementById('filtroEstado');
    const filtroPrioridad = document.getElementById('filtroPrioridad');
    const filtroCategoria = document.getElementById('filtroCategoria');
    const filtroBusqueda = document.getElementById('filtroBusqueda');
    const btnBuscar = document.getElementById('btnBuscar');
    const filtroMisTickets = document.getElementById('filtroMisTickets');
    if (filtroMisTickets) {
        filtroMisTickets.addEventListener('change', function() {
            currentPage = 0; // Reiniciar paginación
            cargarTickets();
        });
        console.log('Evento registrado para filtroMisTickets');
    } else {
        console.warn('Elemento filtroMisTickets no encontrado en el DOM');
    }
    // Configurar eventos de filtros
    if (filtroEstado) {
        filtroEstado.addEventListener('change', function() {
            currentPage = 0;
            cargarTickets();
        });
    }
    
    if (filtroPrioridad) {
        filtroPrioridad.addEventListener('change', function() {
            currentPage = 0;
            cargarTickets();
        });
    }
    
    if (filtroCategoria) {
        filtroCategoria.addEventListener('change', function() {
            currentPage = 0;
            cargarTickets();
        });
    }
    
    // Configurar búsqueda con botón o tecla Enter
    if (btnBuscar) {
        btnBuscar.addEventListener('click', function() {
            currentPage = 0;
            cargarTickets();
        });
    }
    
    if (filtroBusqueda) {
        filtroBusqueda.addEventListener('keyup', function(event) {
            if (event.key === 'Enter') {
                currentPage = 0;
                cargarTickets();
            }
        });
    }
}
/**
 * Carga los tickets desde la API
 */
async function cargarTickets() {
    try {
        console.log('Cargando tickets desde API...');
        mostrarCargando(true);
        
        // Obtener valores de filtros
        const estado = document.getElementById('filtroEstado')?.value || '';
        const prioridad = document.getElementById('filtroPrioridad')?.value || '';
        const categoria = document.getElementById('filtroCategoria')?.value || '';
        const busqueda = document.getElementById('filtroBusqueda')?.value || '';
        
        // Obtener el valor del checkbox "Mis tickets"
        const soloMisTickets = document.getElementById('filtroMisTickets')?.checked || false;
        console.log('¿Mostrar solo mis tickets?:', soloMisTickets); // Para debugging
        
        // Construir URL con parámetros de consulta
        let url = `/tickets/gets_tickets?skip=${currentPage * pageSize}&limit=${pageSize}`;
        
        // Añadir filtros si tienen valor
        if (estado) url += `&estado=${encodeURIComponent(estado)}`;
        if (prioridad) url += `&prioridad=${encodeURIComponent(prioridad)}`;
        if (categoria) url += `&categoria=${encodeURIComponent(categoria)}`;
        if (busqueda) url += `&busqueda=${encodeURIComponent(busqueda)}`;
        if (soloMisTickets) url += `&solo_mis_tickets=true`;
        
        console.log('URL de la petición:', url);        
        // Realizar la petición con cabeceras de no-cache para evitar problemas de caché
        const response = await fetch(url, {
            method: 'GET',
            headers: {
                'Cache-Control': 'no-cache',
                'Pragma': 'no-cache'
            }
        });
        
        console.log('Estado de la respuesta:', response.status);
        
        if (!response.ok) {
            throw new Error(`Error en la petición: ${response.status} ${response.statusText}`);
        }
        
        // Obtener el texto de la respuesta primero para debugging
        const responseText = await response.text();
        console.log('Respuesta en texto:', responseText);
        
        // Intentar parsear como JSON
        let data;
        try {
            data = JSON.parse(responseText);
            console.log('Datos parseados:', data);
        } catch (parseError) {
            console.error('Error al parsear JSON:', parseError);
            throw new Error('La respuesta del servidor no es un JSON válido');
        }
        
        // Verificar que sea un array
        if (!Array.isArray(data)) {
            console.error('La respuesta no es un array:', data);
            throw new Error('Formato de respuesta incorrecto, se esperaba un array');
        }
        
        // Actualizar datos y contador
        ticketsData = data;
        totalTickets = ticketsData.length;
        
        console.log(`Se encontraron ${totalTickets} tickets`);
        
        // Renderizar tabla y actualizar paginación
        renderizarTablaTickets();
        actualizarPaginacion();
        
    } catch (error) {
        console.error('Error al cargar tickets:', error);
        mostrarError(`Error al cargar tickets: ${error.message}`);
        
        // En caso de error, limpiar la tabla
        ticketsData = [];
        renderizarTablaTickets();
        actualizarPaginacion();
    } finally {
        mostrarCargando(false);
    }
}

/**
 * Renderiza la tabla con los tickets
 */
function renderizarTablaTickets() {
    const tbody = document.getElementById('ticketsTableBody');
    
    if (!tbody) {
        console.error('No se encontró el elemento tbody para mostrar los tickets');
        return;
    }
    
    // Limpiar tabla
    tbody.innerHTML = '';
    
    if (ticketsData.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="8" class="px-6 py-8 text-center text-gray-500">
                    No se encontraron tickets con los criterios seleccionados
                </td>
            </tr>
        `;
        return;
    }
    
    // Renderizar filas
    ticketsData.forEach(ticket => {
        // Formatear fechas
        const fechaCreacion = ticket.fecha_creacion ? 
            new Date(ticket.fecha_creacion).toLocaleDateString() : '-';
        const fechaActualizacion = ticket.ultima_actualizacion ? 
            new Date(ticket.ultima_actualizacion).toLocaleDateString() : '-';
        
        // Determinar color de prioridad
        let prioridadClass = '';
        switch(ticket.prioridad ? ticket.prioridad.toLowerCase() : '') {
            case 'alta':
            case 'critica':
                prioridadClass = 'bg-red-100 text-red-800';
                break;
            case 'media':
                prioridadClass = 'bg-yellow-100 text-yellow-800';
                break;
            case 'baja':
                prioridadClass = 'bg-green-100 text-green-800';
                break;
            default:
                prioridadClass = 'bg-gray-100 text-gray-800';
        }
        
        // Determinar color de estado
        let estadoClass = '';
        switch(ticket.estado) {
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
        
        // Crear fila
        const row = document.createElement('tr');
        row.className = 'hover:bg-gray-50';
        row.innerHTML = `
            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                ${ticket.id || '-'}
            </td>
            <td class="px-6 py-4">
                <div class="flex items-center">
                    <div>
                        <div class="text-sm font-medium text-gray-900">${ticket.titulo || '-'}</div>
                        <div class="text-sm text-gray-500">${ticket.solicitante || '-'}</div>
                    </div>
                </div>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                ${formatearCategoria(ticket.categoria) || '-'}
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
                <span class="px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${prioridadClass}">
                    ${ticket.prioridad || '-'}
                </span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
                <span class="px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${estadoClass}">
                    ${formatearEstado(ticket.estado)}
                </span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                ${fechaCreacion}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                ${fechaActualizacion}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                <button 
                    onclick="verDetalleTicket(${ticket.id})" 
                    class="text-indigo-600 hover:text-indigo-900 mr-3"
                    title="Ver detalles">
                    <i class="fas fa-eye"></i>
                </button>
                <button 
                    onclick="editarTicket(${ticket.id})" 
                    class="text-blue-600 hover:text-blue-900"
                    title="Editar ticket">
                    <i class="fas fa-edit"></i>
                </button>
            </td>
        `;
        
        tbody.appendChild(row);
    });
}

/**
 * Formatea el estado para mostrar en la UI
 */
function formatearEstado(estado) {
    if (!estado) return '-';
    
    switch(estado) {
        case 'abierto': return 'Abierto';
        case 'en_proceso': return 'En Proceso';
        case 'cerrado': return 'Cerrado';
        default: return estado;
    }
}

/**
 * Formatea la categoría para mostrar en la UI
 */
function formatearCategoria(categoria) {
    if (!categoria) return '-';
    
    switch(categoria) {
        case 'hardware': return 'Hardware';
        case 'software': return 'Software';
        case 'red': return 'Red/Conectividad';
        case 'cuenta': return 'Cuentas/Accesos';
        case 'otro': return 'Otro';
        default: return categoria;
    }
}

/**
 * Editar un ticket
 */
function editarTicket(ticketId) {
    window.location.href = `/tickets/${ticketId}/editar`;
}

/**
 * Ver detalle de un ticket en el modal
 */
function verDetalleTicket(ticketId) {
    console.log(`Mostrando detalle del ticket ${ticketId}`);
    // Implementar código para mostrar el modal con los detalles del ticket
    // Puedes usar el modal que ya tienes definido en tu HTML
    const modal = document.getElementById('ticketModal');
    if (modal) {
        modal.classList.remove('hidden');
        
        // Aquí cargar los datos del ticket desde el backend
        fetch(`/tickets/${ticketId}`)
            .then(response => {
                if (!response.ok) throw new Error('Error al cargar el ticket');
                return response.json();
            })
            .then(ticket => {
                // Actualizar los datos en el modal
                document.getElementById('modalTicketTitle').textContent = ticket.titulo || '-';
                // Continuar con el resto de campos...
            })
            .catch(error => {
                console.error('Error:', error);
                mostrarError('Error al cargar detalles del ticket');
            });
    }
}

/**
 * Realiza un diagnóstico de la API
 */
async function diagnosticoAPI() {
    console.log("==== DIAGNÓSTICO DE API ====");
    try {
        // Probar la ruta directamente sin caché
        console.log("1. Probando ruta /tickets/gets_tickets directamente...");
        const response = await fetch('/tickets/gets_tickets', {
            method: 'GET',
            headers: {
                'Cache-Control': 'no-cache',
                'Pragma': 'no-cache'
            }
        });
        
        console.log("Estado de respuesta:", response.status);
        console.log("Headers:", Object.fromEntries([...response.headers]));
        
        if (!response.ok) {
            throw new Error(`Error en la API: ${response.status} ${response.statusText}`);
        }
        
        // Obtener texto de respuesta
        const text = await response.text();
        console.log("2. Respuesta en texto:", text);
        
        // Intentar parsear como JSON
        let data;
        try {
            data = JSON.parse(text);
            console.log("3. Datos JSON:", data);
            
            if (!Array.isArray(data)) {
                console.warn("⚠️ La respuesta no es un array:", data);
            } else {
                console.log(`✅ Se encontraron ${data.length} tickets`);
            }
        } catch (parseError) {
            console.error("❌ Error al parsear JSON:", parseError);
            throw new Error("La respuesta no es un JSON válido");
        }
        
        return data;
    } catch (error) {
        console.error("❌ Error en diagnóstico:", error);
        throw error;
    }
}
/**
 * Configura eventos de paginación
 */
function configurarPaginacion() {
    const prevPageBtn = document.getElementById('prevPage');
    const nextPageBtn = document.getElementById('nextPage');
    
    if (prevPageBtn) {
        prevPageBtn.addEventListener('click', function() {
            if (currentPage > 0) {
                currentPage--;
                cargarTickets();
            }
        });
    }
    
    if (nextPageBtn) {
        nextPageBtn.addEventListener('click', function() {
            if ((currentPage + 1) * pageSize < totalTickets) {
                currentPage++;
                cargarTickets();
            }
        });
    }
}

// Código de inicialización - Este va al final del archivo
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Inicializando página de tickets...');
    
    // Configurar eventos
    initFiltros();
    configurarPaginacion();
    
    // Botón de recargar - si existe
    const btnRecargar = document.getElementById('btnRecargar');
    if (btnRecargar) {
        btnRecargar.addEventListener('click', function() {
            console.log('Recargando tickets manualmente...');
            cargarTickets();
        });
    }
    
    // Cargar tickets automáticamente al iniciar
    cargarTickets();
    console.log('Inicialización completa');
});

// Función de carga inmediata para debugging
(function() {
    console.log('🔍 Comprobando si el DOM ya está cargado...');
    
    // Si el DOM ya está cargado, ejecutar carga inmediata
    if (document.readyState === 'complete' || document.readyState === 'interactive') {
        console.log('DOM ya cargado, ejecutando carga inmediata...');
        
        // Agregar botón de diagnóstico/reload si no existe
        if (!document.getElementById('btnDiagnostico')) {
            console.log('Agregando botón de diagnóstico al DOM...');
            const container = document.querySelector('main') || document.body;
            const btnContainer = document.createElement('div');
            btnContainer.className = 'fixed bottom-4 right-4 z-50';
            btnContainer.innerHTML = `
                <button id="btnDiagnostico" class="bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded shadow-lg flex items-center space-x-2">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                        <path fill-rule="evenodd" d="M4 2a1 1 0 011 1v2.101a7.002 7.002 0 0111.601 2.566 1 1 0 11-1.885.666A5.002 5.002 0 005.999 7H9a1 1 0 010 2H4a1 1 0 01-1-1V3a1 1 0 011-1zm.008 9.057a1 1 0 011.276.61A5.002 5.002 0 0014.001 13H11a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0v-2.101a7.002 7.002 0 01-11.601-2.566 1 1 0 01.61-1.276z" clip-rule="evenodd" />
                    </svg>
                    <span>Cargar tickets</span>
                </button>
            `;
            container.appendChild(btnContainer);
            
            // Configurar evento para el botón de diagnóstico
            document.getElementById('btnDiagnostico').addEventListener('click', function() {
                console.log('Diagnóstico iniciado manualmente...');
                diagnosticoAPI().then(data => {
                    if (Array.isArray(data) && data.length > 0) {
                        ticketsData = data;
                        totalTickets = data.length;
                        renderizarTablaTickets();
                        actualizarPaginacion();
                    } else {
                        console.log('No se obtuvieron datos del diagnóstico. Intentando carga normal...');
                        cargarTickets();
                    }
                }).catch(error => {
                    console.error('Error en diagnóstico:', error);
                    cargarTickets();
                });
            });
        }
    }
})();