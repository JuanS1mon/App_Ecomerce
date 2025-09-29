/**
 * Scripts para la página de gestión de tickets
 */

// Estado global
let tickets = [];
let currentTicketId = null;
let currentTicket = null;  // Para almacenar la información completa del ticket actual
let usuarios = []; // Para el selector de asignación

// Elementos DOM frecuentemente usados
let ticketsList;
let loadingTickets;
let noTicketSelected;
let ticketDetail;
let formRespuesta;
let asignarASelect;
let filterEstado;
let filterPrioridad;
let searchTickets;

/**
 * Inicialización cuando el DOM está listo
 */
document.addEventListener('DOMContentLoaded', async function() {
    console.log('Inicializando página de gestión de tickets...');
    
    // Inicializar referencias a elementos DOM
    ticketsList = document.getElementById('tickets-list');
    loadingTickets = document.getElementById('loading-tickets');
    noTicketSelected = document.getElementById('no-ticket-selected');
    ticketDetail = document.getElementById('ticket-detail');
    formRespuesta = document.getElementById('form-respuesta');
    asignarASelect = document.getElementById('asignar-a');
    filterEstado = document.getElementById('filter-estado');
    filterPrioridad = document.getElementById('filter-prioridad');
    searchTickets = document.getElementById('search-tickets');
    
    // Cargar componentes dinámicos si existe la función
    if (window.cargarComponentes) {
        window.cargarComponentes();
    }
    
    // Cargar usuarios para el selector de asignación
    await cargarUsuarios();
    
    // Cargar tickets iniciales
    await cargarTickets();
    
    // Configurar event listeners
    setupEventListeners();
});

/**
 * Configura los event listeners para la interfaz
 */
function setupEventListeners() {
    // Event listener para filtros
    if (filterEstado) filterEstado.addEventListener('change', cargarTickets);
    if (filterPrioridad) filterPrioridad.addEventListener('change', cargarTickets);
    
    // Event listener para búsqueda
    if (searchTickets) {
        let searchTimeout;
        searchTickets.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(cargarTickets, 500);
        });
    }
    
    // Event listener para el formulario de respuesta
    if (formRespuesta) {
        formRespuesta.addEventListener('submit', function(e) {
            e.preventDefault();
            enviarRespuesta();
        });
    }
}

/**
 * Carga los usuarios disponibles para asignación
 */
async function cargarUsuarios() {
    if (!asignarASelect) return;
    
    try {
        // Usar valores por defecto iniciales
        const defaultUsers = [
            { id: 1, nombre: 'Soporte Nivel 1' },
            { id: 2, nombre: 'Soporte Nivel 2' },
            { id: 3, nombre: 'Administrador' }
        ];
        
        // Limpiar opciones existentes excepto la primera (si existe)
        while (asignarASelect.options.length > 1) {
            asignarASelect.remove(1);
        }
        
        try {
            // Usar la nueva ruta con parámetro de consulta para rol=tecnico
            const response = await fetch('/usuarios_admin/usuarios-por-rol/?rol=tecnico');
            
            if (response.ok) {
                usuarios = await response.json();
                
                // Si se cargaron usuarios del servidor, usarlos en lugar de los predeterminados
                if (Array.isArray(usuarios) && usuarios.length > 0) {
                    // Llenar el selector de asignación
                    usuarios.forEach(user => {
                        const option = document.createElement('option');
                        option.value = user.nombre || user.usuario;
                        option.textContent = user.nombre || user.usuario;
                        asignarASelect.appendChild(option);
                    });
                    return; // Salir de la función si ya cargamos usuarios del servidor
                }
            } else {
                console.warn('No se pudo cargar la lista de usuarios. Código de respuesta:', response.status);
                
                // Intentar con la ruta antigua como fallback
                const oldResponse = await fetch('/usuarios_admin/rol/tecnico');
                if (oldResponse.ok) {
                    usuarios = await oldResponse.json();
                    if (Array.isArray(usuarios) && usuarios.length > 0) {
                        usuarios.forEach(user => {
                            const option = document.createElement('option');
                            option.value = user.nombre || user.usuario;
                            option.textContent = user.nombre || user.usuario;
                            asignarASelect.appendChild(option);
                        });
                        return;
                    }
                }
            }
        } catch (fetchError) {
            console.warn('Error al intentar obtener usuarios del servidor:', fetchError);
        }
        
        // Si llegamos aquí, usamos los valores por defecto
        console.warn('Usando valores de usuario por defecto');
        defaultUsers.forEach(user => {
            const option = document.createElement('option');
            option.value = user.nombre;
            option.textContent = user.nombre;
            asignarASelect.appendChild(option);
        });
        
    } catch (error) {
        console.error('Error general al cargar usuarios:', error);
    }
}

/**
 * Carga tickets con los filtros actuales
 */
async function cargarTickets() {
    // Mostrar indicador de carga
    if (ticketsList) ticketsList.innerHTML = '';
    if (loadingTickets) loadingTickets.classList.remove('hidden');
    
    try {
        // Preparar parámetros de filtrado
        const estado = filterEstado ? filterEstado.value : '';
        const prioridad = filterPrioridad ? filterPrioridad.value : '';
        const busqueda = searchTickets ? searchTickets.value : '';
        
        // Construir URL con parámetros
        let url = '/tickets/gets_tickets?limit=50';
        if (estado) url += `&estado=${estado}`;
        if (prioridad) url += `&prioridad=${prioridad}`;
        if (busqueda) url += `&busqueda=${encodeURIComponent(busqueda)}`;
        
        // Realizar la petición
        const response = await fetch(url);
        if (!response.ok) throw new Error(`Error ${response.status}: ${response.statusText}`);
        
        tickets = await response.json();
        
        // Actualizar la lista de tickets
        actualizarListaTickets();
        
    } catch (error) {
        console.error('Error al cargar tickets:', error);
        mostrarError('No se pudieron cargar los tickets. Por favor, intenta de nuevo.');
    } finally {
        // Ocultar indicador de carga
        if (loadingTickets) loadingTickets.classList.add('hidden');
    }
}

/**
 * Actualiza la lista visual de tickets
 */
function actualizarListaTickets() {
    if (!ticketsList) return;
    
    // Limpiar lista
    ticketsList.innerHTML = '';
    
    // Si no hay tickets, mostrar mensaje
    if (!tickets || tickets.length === 0) {
        const emptyMessage = document.createElement('li');
        emptyMessage.className = 'py-10 px-6 text-center text-gray-500';
        emptyMessage.textContent = 'No se encontraron tickets con los filtros actuales';
        ticketsList.appendChild(emptyMessage);
        return;
    }
    
    // Agregar cada ticket a la lista
    tickets.forEach(ticket => {
        const ticketItem = document.createElement('li');
        ticketItem.className = `ticket-row p-4 border-l-4 hover:bg-gray-50 cursor-pointer ${getEstadoBorderClass(ticket.estado)}`;
        ticketItem.setAttribute('data-id', ticket.id);
        ticketItem.onclick = () => seleccionarTicket(ticket.id);
        
        // Determinar clases para prioridad
        const prioridadClass = getPrioridadClass(ticket.prioridad);
        
        // Formatear fecha
        const fecha = new Date(ticket.fecha_creacion);
        const fechaFormateada = `${fecha.getDate()}/${fecha.getMonth() + 1}/${fecha.getFullYear()}`;
        
        // Contenido del ticket
        ticketItem.innerHTML = `
            <div class="flex justify-between">
                <div class="flex-1">
                    <p class="font-medium text-gray-800 truncate">${ticket.titulo || 'Sin título'}</p>
                    <p class="text-sm text-gray-500 mt-1">
                        <span class="font-medium">#${ticket.id}</span> - 
                        <span>${ticket.solicitante || 'Anónimo'}</span>
                    </p>
                </div>
                <div class="flex items-start">
                    <span class="px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${prioridadClass}">
                        ${capitalizarPrimera(ticket.prioridad || 'baja')}
                    </span>
                </div>
            </div>
            <div class="mt-2 flex justify-between items-center">
                <span class="text-xs text-gray-500">${fechaFormateada}</span>
                <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getEstadoClass(ticket.estado)}">
                    ${formatearEstado(ticket.estado)}
                </span>
            </div>
        `;
        
        ticketsList.appendChild(ticketItem);
    });
}

/**
 * Carga los detalles de un ticket desde el servidor
 */
async function cargarDetallesTicket(ticketId) {
    try {
        console.log(`Cargando detalles del ticket ${ticketId}`);
        mostrarCargando(true);
        
        // Hacer la petición a la API para obtener detalles completos
        const response = await fetch(`/tickets/detalles/${ticketId}`);
        
        if (!response.ok) {
            if (response.status === 404) {
                mostrarError('Ticket no encontrado');
            } else {
                mostrarError(`Error al cargar ticket: ${response.statusText}`);
            }
            return false;
        }
        
        const ticket = await response.json();
        console.log('Ticket cargado:', ticket);
        console.log('Historial del ticket:', ticket.historial);
        
        // Guardar ticket actual globalmente
        currentTicket = ticket;
        
        // Mostrar información básica del ticket
        mostrarInformacionTicket(ticket);
        
        // Mostrar historial del ticket
        mostrarHistorialTicket(ticket);
        
        // Actualizar UI según el estado del ticket
        actualizarUISegunEstado(ticket.estado);
        
        return true;
    } catch (error) {
        console.error('Error al cargar detalles del ticket:', error);
        mostrarError('Error al cargar detalles del ticket');
        return false;
    } finally {
        mostrarCargando(false);
    }
}

/**
 * Muestra el historial de un ticket en formato de chat
 */
function mostrarHistorialTicket(ticket) {
    const historialContainer = document.getElementById('ticket-conversacion');
    
    if (!historialContainer) {
        console.error('No se encontró el contenedor del historial (ticket-conversacion)');
        return;
    }
    
    historialContainer.innerHTML = '';
    
    console.log('Procesando historial del ticket:', ticket.historial);
    
    // Verificar si el ticket tiene historial
    if (!ticket.historial || !Array.isArray(ticket.historial) || ticket.historial.length === 0) {
        // Si no hay historial, mostrar el mensaje inicial con la descripción
        const mensajeInicial = document.createElement('div');
        mensajeInicial.className = 'chat-message message-user';
        
        // Formatear fecha
        const fecha = new Date(ticket.fecha_creacion);
        const fechaFormateada = `${fecha.getDate()}/${fecha.getMonth() + 1}/${fecha.getFullYear()} ${fecha.getHours()}:${fecha.getMinutes().toString().padStart(2, '0')}`;
        
        mensajeInicial.innerHTML = `
            <div class="text-sm">
                <strong>${ticket.solicitante || 'Usuario'}</strong>
                <span class="text-xs text-gray-500 ml-2">${fechaFormateada}</span>
            </div>
            <div class="mt-1">${ticket.descripcion || 'Sin descripción'}</div>
        `;
        historialContainer.appendChild(mensajeInicial);
        return;
    }
    
    // Ordenar el historial por fecha (más reciente primero)
    const historialOrdenado = [...ticket.historial].sort((a, b) => {
        const fechaA = new Date(a.fecha);
        const fechaB = new Date(b.fecha);
        return fechaA - fechaB; // Orden ascendente para chat
    });
    
    // Crear elementos para cada entrada del historial usando estilos de chat
    historialOrdenado.forEach(entrada => {
        console.log('Procesando entrada:', entrada);
        
        // Formatear fecha
        let fechaFormateada;
        try {
            const fecha = new Date(entrada.fecha);
            fechaFormateada = fecha.toLocaleString();
        } catch (e) {
            console.warn('Error al formatear fecha:', entrada.fecha, e);
            fechaFormateada = entrada.fecha || 'Fecha desconocida';
        }
        
        // Verificar si es una respuesta
        const esRespuesta = entrada.comentario && entrada.comentario.startsWith('Respuesta:');
        
        // Crear elemento para la entrada
        const entradaEl = document.createElement('div');
        
        // Determinar si es del solicitante o del soporte basado en quién escribió
        const esUsuario = entrada.usuario === ticket.solicitante;
        
        // Estilo como mensaje de chat según el remitente
        entradaEl.className = `chat-message ${esUsuario ? 'message-user' : 'message-support'}`;
        
        // Extraer el contenido real de la respuesta (quitar el prefijo "Respuesta:")
        let comentarioTexto = entrada.comentario || '';
        if (esRespuesta) {
            comentarioTexto = comentarioTexto.substring('Respuesta:'.length).trim();
        }
        
        // Contenido HTML para la entrada con estilo de chat
        entradaEl.innerHTML = `
            <div class="flex justify-between items-center mb-1">
                <span class="font-medium">${entrada.usuario || 'Sistema'}</span>
                <span class="text-xs text-gray-500">${fechaFormateada}</span>
            </div>
            <div>
                ${formatearComentario(esRespuesta ? comentarioTexto : entrada.comentario)}
            </div>
        `;
        
        historialContainer.appendChild(entradaEl);
    });
    
    // Hacer scroll hasta el final de la conversación
    historialContainer.scrollTop = historialContainer.scrollHeight;
}

/**
 * Muestra u oculta el indicador de carga
 */
function mostrarCargando(mostrar) {
    const loadingIndicator = document.createElement('div');
    loadingIndicator.id = 'loading-indicator';
    loadingIndicator.className = 'fixed top-0 left-0 right-0 bg-blue-600 h-1 transition-all';
    loadingIndicator.style.width = mostrar ? '90%' : '100%';
    loadingIndicator.style.opacity = mostrar ? '1' : '0';
    loadingIndicator.style.zIndex = '9999';
    
    // Si ya existe, actualizarlo
    const existingIndicator = document.getElementById('loading-indicator');
    if (existingIndicator) {
        existingIndicator.style.width = mostrar ? '90%' : '100%';
        existingIndicator.style.opacity = mostrar ? '1' : '0';
        
        // Si se está ocultando, removerlo después de la transición
        if (!mostrar) {
            setTimeout(() => existingIndicator.remove(), 300);
        }
    } else if (mostrar) {
        // Si no existe y hay que mostrarlo
        document.body.appendChild(loadingIndicator);
    }
}

/**
 * Actualiza la UI según el estado del ticket
 */
function actualizarUISegunEstado(estado) {
    // Obtener elementos que podrían cambiar según el estado
    const formRespuesta = document.getElementById('form-respuesta');
    const submitBtn = document.getElementById('submit-respuesta');
    const nuevoEstadoSelect = document.getElementById('nuevo-estado');
    
    // Establecer valores predeterminados
    if (submitBtn) submitBtn.disabled = false;
    if (formRespuesta) formRespuesta.style.opacity = '1';
    
    // Si el ticket está cerrado, deshabilitar respuesta
    if (estado && estado.toLowerCase() === 'cerrado') {
        if (submitBtn) submitBtn.disabled = true;
        if (formRespuesta) formRespuesta.style.opacity = '0.5';
        
        // Añadir indicación visual
        const indicadorCerrado = document.createElement('div');
        indicadorCerrado.className = 'bg-red-100 text-red-800 p-2 text-center text-sm rounded mb-2';
        indicadorCerrado.innerHTML = '<i class="fas fa-lock mr-2"></i> Este ticket está cerrado y no se pueden añadir más respuestas';
        
        // Insertar antes del formulario
        if (formRespuesta && !document.getElementById('indicador-cerrado')) {
            indicadorCerrado.id = 'indicador-cerrado';
            formRespuesta.parentNode.insertBefore(indicadorCerrado, formRespuesta);
        }
    } else {
        // Remover indicador si existe
        const indicadorCerrado = document.getElementById('indicador-cerrado');
        if (indicadorCerrado) indicadorCerrado.remove();
    }
    
    // Actualizar opciones del selector de estado
    if (nuevoEstadoSelect) {
        // Si el ticket ya está cerrado, no permitir cambiarlo a abierto
        if (estado && estado.toLowerCase() === 'cerrado') {
            // Desactivar opción "abierto"
            for (let i = 0; i < nuevoEstadoSelect.options.length; i++) {
                const option = nuevoEstadoSelect.options[i];
                if (option.value === 'abierto') {
                    option.disabled = true;
                }
            }
        } else {
            // Habilitar todas las opciones
            for (let i = 0; i < nuevoEstadoSelect.options.length; i++) {
                nuevoEstadoSelect.options[i].disabled = false;
            }
        }
    }
}

/**
 * Muestra la información básica del ticket en el DOM
 */
function mostrarInformacionTicket(ticket) {
    // Actualizar elementos del DOM con la información del ticket
    const ticketTitulo = document.getElementById('ticket-titulo');
    if (ticketTitulo) ticketTitulo.textContent = ticket.titulo || 'Sin título';

    const ticketId = document.getElementById('ticket-id');
    if (ticketId) ticketId.textContent = `ID: #${ticket.id}`;

    const ticketSolicitante = document.getElementById('ticket-solicitante');
    if (ticketSolicitante) ticketSolicitante.textContent = `Solicitante: ${ticket.solicitante || 'Anónimo'}`;

    const ticketFecha = document.getElementById('ticket-fecha');
    if (ticketFecha && ticket.fecha_creacion) {
        const fecha = new Date(ticket.fecha_creacion);
        const fechaFormateada = `${fecha.getDate()}/${fecha.getMonth() + 1}/${fecha.getFullYear()}`;
        ticketFecha.textContent = `Creado: ${fechaFormateada}`;
    }

    const ticketPrioridad = document.getElementById('ticket-prioridad');
    if (ticketPrioridad) {
        ticketPrioridad.textContent = capitalizarPrimera(ticket.prioridad || 'normal');
        ticketPrioridad.className = `px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${getPrioridadClass(ticket.prioridad)}`;
    }

    const ticketEstado = document.getElementById('ticket-estado');
    if (ticketEstado) {
        ticketEstado.textContent = formatearEstado(ticket.estado || 'abierto');
        ticketEstado.className = `px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${getEstadoClass(ticket.estado)}`;
    }

    const ticketDescripcion = document.getElementById('ticket-descripcion');
    if (ticketDescripcion) {
        ticketDescripcion.textContent = ticket.descripcion || 'Sin descripción';
    }
}

/**
 * Formatea un comentario para mostrar enlaces y saltos de línea
 */
function formatearComentario(texto) {
    if (!texto) return 'Sin detalles';
    
    // Convertir URLs en enlaces clickeables
    const textoConEnlaces = texto.replace(
        /(https?:\/\/[^\s]+)/g, 
        '<a href="$1" target="_blank" rel="noopener noreferrer" class="text-blue-600 hover:underline">$1</a>'
    );
    
    // Convertir saltos de línea en <br>
    return textoConEnlaces.replace(/\n/g, '<br>');
}

/**
 * Selecciona un ticket para mostrar su detalle
 */
async function seleccionarTicket(ticketId) {
    // Actualizar estado visual de la selección
    const ticketItems = document.querySelectorAll('.ticket-row');
    ticketItems.forEach(item => {
        if (parseInt(item.getAttribute('data-id')) === ticketId) {
            item.classList.add('bg-gray-100');
            item.classList.add('selected');
        } else {
            item.classList.remove('bg-gray-100');
            item.classList.remove('selected');
        }
    });
    
    // Obtener detalles del ticket
    const ticket = tickets.find(t => t.id === ticketId);
    if (!ticket) return;
    
    currentTicketId = ticketId;
    
    // Actualizar interfaz
    if (noTicketSelected) noTicketSelected.classList.add('hidden');
    if (ticketDetail) ticketDetail.classList.remove('hidden');
    
    // Actualizar información básica del ticket con los datos que ya tenemos
    mostrarInformacionTicket(ticket);
    
    // Cargar detalles completos del ticket (historial, etc)
    await cargarDetallesTicket(ticketId);
}

/**
 * Envía una respuesta al ticket actual
 */
async function enviarRespuesta() {
    // Verificar que hay un ticket seleccionado
    if (!currentTicketId) {
        mostrarError('No hay ningún ticket seleccionado');
        return;
    }
    
    // Obtener datos del formulario
    const respuesta = document.getElementById('respuesta').value.trim();
    const nuevoEstado = document.getElementById('nuevo-estado').value;
    const asignarA = document.getElementById('asignar-a').value;
    
    // Validar respuesta
    if (!respuesta) {
        mostrarError('Debes escribir una respuesta');
        return;
    }
    
    try {
        // Mostrar indicador de carga y deshabilitar formulario
        const submitBtn = document.getElementById('submit-respuesta');
        const textoOriginal = submitBtn.innerHTML;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Enviando...';
        submitBtn.disabled = true;
        formRespuesta.querySelectorAll('input, textarea, select').forEach(el => el.disabled = true);
        
        // Preparar datos para enviar - USANDO FormData
        const formData = new FormData();
        formData.append('respuesta', respuesta);
        if (nuevoEstado) formData.append('nuevo_estado', nuevoEstado);
        if (asignarA) formData.append('asignar_a', asignarA);
        
        console.log('Enviando respuesta:', {
            ticketId: currentTicketId,
            respuesta: respuesta,
            nuevoEstado: nuevoEstado,
            asignarA: asignarA
        });
        
        // Enviar respuesta
        const response = await fetch(`/tickets/responder/${currentTicketId}`, {
            method: 'POST',
            body: formData // No establecer Content-Type para que se envíe como multipart/form-data
        });
        
        if (!response.ok) {
            const errorText = await response.text();
            let errorMessage = 'Error al enviar la respuesta';
            
            try {
                const errorData = JSON.parse(errorText);
                errorMessage = errorData.detail || errorMessage;
            } catch (e) {
                console.error('No se pudo parsear el error:', errorText);
            }
            
            throw new Error(errorMessage);
        }
        
        const responseData = await response.json();
        
        // Mostrar mensaje de éxito
        mostrarExito(responseData.message || 'Respuesta enviada correctamente');
        
        // Limpiar formulario
        document.getElementById('respuesta').value = '';
        
        // Recargar tickets para reflejar cambios
        await cargarTickets();
        
        // Si se cambió el estado, puede que el ticket ya no esté en la lista filtrada
        // Seleccionamos el mismo ticket si sigue presente
        const ticketActualizado = tickets.find(t => t.id === currentTicketId);
        if (ticketActualizado) {
            seleccionarTicket(currentTicketId);
        } else {
            // Si ya no está en la lista, volvemos a la vista sin selección
            currentTicketId = null;
            if (noTicketSelected) noTicketSelected.classList.remove('hidden');
            if (ticketDetail) ticketDetail.classList.add('hidden');
        }
        
    } catch (error) {
        console.error('Error al enviar respuesta:', error);
        mostrarError(`Error: ${error.message}`);
    } finally {
        // Restaurar formulario
        const submitBtn = document.getElementById('submit-respuesta');
        submitBtn.innerHTML = '<span>Enviar respuesta</span><i class="fas fa-paper-plane ml-2"></i>';
        submitBtn.disabled = false;
        formRespuesta.querySelectorAll('input, textarea, select').forEach(el => el.disabled = false);
    }
}

/**
 * Muestra un mensaje de éxito
 */
function mostrarExito(mensaje) {
    const toast = document.createElement('div');
    toast.className = 'fixed bottom-4 right-4 bg-green-500 text-white px-6 py-3 rounded-lg shadow-lg z-50 flex items-center';
    toast.innerHTML = `
        <i class="fas fa-check-circle mr-2"></i>
        <span>${mensaje}</span>
        <button class="ml-4 text-white hover:text-green-200" onclick="this.parentNode.remove()">
            <i class="fas fa-times"></i>
        </button>
    `;
    document.body.appendChild(toast);
    
    // Auto ocultar después de 3 segundos
    setTimeout(() => {
        toast.remove();
    }, 3000);
}

/**
 * Muestra un mensaje de error
 */
function mostrarError(mensaje) {
    const toast = document.createElement('div');
    toast.className = 'fixed bottom-4 right-4 bg-red-500 text-white px-6 py-3 rounded-lg shadow-lg z-50 flex items-center';
    toast.innerHTML = `
        <i class="fas fa-exclamation-circle mr-2"></i>
        <span>${mensaje}</span>
        <button class="ml-4 text-white hover:text-red-200" onclick="this.parentNode.remove()">
            <i class="fas fa-times"></i>
        </button>
    `;
    document.body.appendChild(toast);
    
    // Auto ocultar después de 5 segundos
    setTimeout(() => {
        toast.remove();
    }, 5000);
}

/**
 * Funciones de utilidad para formateo
 */

function formatearEstado(estado) {
    if (!estado) return 'Desconocido';
    
    switch (estado.toLowerCase()) {
        case 'abierto': return 'Abierto';
        case 'en_proceso': return 'En proceso';
        case 'cerrado': return 'Cerrado';
        default: return capitalizarPrimera(estado);
    }
}

function capitalizarPrimera(str) {
    if (!str) return '';
    return str.charAt(0).toUpperCase() + str.slice(1);
}

function getEstadoClass(estado) {
    if (!estado) return 'bg-gray-100 text-gray-800';
    
    switch (estado.toLowerCase()) {
        case 'abierto': return 'bg-blue-100 text-blue-800';
        case 'en_proceso': return 'bg-yellow-100 text-yellow-800';
        case 'cerrado': return 'bg-green-100 text-green-800';
        default: return 'bg-gray-100 text-gray-800';
    }
}

function getEstadoBorderClass(estado) {
    if (!estado) return 'border-gray-300';
    
    switch (estado.toLowerCase()) {
        case 'abierto': return 'border-blue-500';
        case 'en_proceso': return 'border-yellow-500';
        case 'cerrado': return 'border-green-500';
        default: return 'border-gray-300';
    }
}

function getPrioridadClass(prioridad) {
    if (!prioridad) return 'bg-gray-100 text-gray-800';
    
    switch (prioridad.toLowerCase()) {
        case 'baja': return 'bg-green-100 text-green-800';
        case 'media': return 'bg-blue-100 text-blue-800';
        case 'alta': return 'bg-yellow-100 text-yellow-800';
        case 'critica': return 'bg-red-100 text-red-800';
        default: return 'bg-gray-100 text-gray-800';
    }
}