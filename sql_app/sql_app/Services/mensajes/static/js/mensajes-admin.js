/**
 * Administración de Mensajes - JavaScript
 * Maneja la funcionalidad de la página de administración de mensajes
 */

// Variables globales
let mensajes = [];
let usuarios = [];
let estadisticas = {};
let filtros = {
    tipo: 'todos',
    prioridad: 'todas',
    estado: 'todos',
    busqueda: ''
};

// URLs de la API
const API_BASE = '/api/mensajes';
const ADMIN_API_BASE = '/admin/api/mensajes';
const PUBLIC_API_BASE = '/api/public/mensajes';

/**
 * Inicialización de la página
 */
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Inicializando administración de mensajes...');
    
    // Verificar autenticación primero
    verificarAutenticacion().then(autenticado => {
        if (autenticado) {
            console.log('✅ Usuario autenticado, cargando datos...');
            inicializarPagina();
        } else {
            console.log('⚠️ Usuario no autenticado, usando modo público...');
            inicializarModoPublico();
        }
    });
    
    // Configurar event listeners
    configurarEventListeners();
});

/**
 * Verificar si el usuario está autenticado
 */
async function verificarAutenticacion() {
    try {
        const response = await fetch('/auth/me', {
            credentials: 'include',
            headers: {
                'Accept': 'application/json'
            }
        });
        
        if (response.ok) {
            const userData = await response.json();
            console.log('Usuario autenticado:', userData);
            return true;
        } else {
            console.log('Usuario no autenticado:', response.status);
            return false;
        }
    } catch (error) {
        console.error('Error verificando autenticación:', error);
        return false;
    }
}

/**
 * Inicializar página en modo autenticado
 */
async function inicializarPagina() {
    try {
        await Promise.all([
            cargarEstadisticas(),
            cargarUsuarios(),
            cargarMensajes()
        ]);
        console.log('✅ Página inicializada correctamente');
    } catch (error) {
        console.error('❌ Error inicializando página:', error);
        // Fallback a modo público si hay errores
        inicializarModoPublico();
    }
}

/**
 * Inicializar página en modo público (sin autenticación)
 */
async function inicializarModoPublico() {
    try {
        console.log('🔓 Iniciando modo público...');
        await cargarMensajesPublico();
        mostrarEstadisticasPublicas();
        console.log('✅ Modo público inicializado');
    } catch (error) {
        console.error('❌ Error en modo público:', error);
    }
}

/**
 * Cargar estadísticas de mensajes
 */
async function cargarEstadisticas() {
    try {
        console.log('📊 Cargando estadísticas...');
        
        // Intentar API autenticada primero
        let response = await fetch(`${ADMIN_API_BASE}/estadisticas`, {
            credentials: 'include',
            headers: { 'Accept': 'application/json' }
        });
        
        // Si falla, usar API pública
        if (!response.ok) {
            console.log('⚠️ API autenticada falló, usando API pública...');
            response = await fetch(`${PUBLIC_API_BASE}/estadisticas`, {
                headers: { 'Accept': 'application/json' }
            });
        }
        
        if (response.ok) {
            estadisticas = await response.json();
            mostrarEstadisticas();
        } else {
            throw new Error(`Error ${response.status}: ${response.statusText}`);
        }
    } catch (error) {
        console.error('Error cargando estadísticas:', error);
        mostrarEstadisticasPublicas();
    }
}

/**
 * Cargar lista de usuarios
 */
async function cargarUsuarios() {
    try {
        console.log('👥 Cargando usuarios...');
        
        const response = await fetch(`${ADMIN_API_BASE}/usuarios`, {
            credentials: 'include',
            headers: { 'Accept': 'application/json' }
        });
        
        if (response.ok) {
            usuarios = await response.json();
            poblarSelectUsuarios();
        } else {
            console.log('⚠️ No se pudieron cargar usuarios (requiere autenticación)');
            usuarios = [{ codigo: 'juan', nombre: 'Usuario Público' }];
        }
    } catch (error) {
        console.error('Error cargando usuarios:', error);
        usuarios = [{ codigo: 'juan', nombre: 'Usuario Público' }];
    }
}

/**
 * Cargar mensajes
 */
async function cargarMensajes() {
    try {
        console.log('📧 Cargando mensajes...');
        
        // Intentar API autenticada primero
        let response = await fetch(`${ADMIN_API_BASE}/todos`, {
            credentials: 'include',
            headers: { 'Accept': 'application/json' }
        });
        
        // Si falla, usar API pública
        if (!response.ok) {
            console.log('⚠️ API autenticada falló, usando API pública...');
            response = await fetch(`${PUBLIC_API_BASE}/navbar`, {
                headers: { 'Accept': 'application/json' }
            });
        }
        
        if (response.ok) {
            const data = await response.json();
            console.log('📨 Datos recibidos de la API:', data);
            
            // Manejar diferentes formatos de respuesta
            if (Array.isArray(data)) {
                // Respuesta de API autenticada (array directo)
                mensajes = data;
                console.log('✅ Mensajes de API autenticada:', mensajes.length);
            } else if (data.mensajes && Array.isArray(data.mensajes)) {
                // Respuesta de API pública (objeto con array mensajes)
                mensajes = data.mensajes;
                console.log('✅ Mensajes de API pública:', mensajes.length);
            } else {
                console.warn('⚠️ Formato de respuesta inesperado:', data);
                mensajes = [];
            }
            mostrarMensajes();
        } else {
            throw new Error(`Error ${response.status}: ${response.statusText}`);
        }
    } catch (error) {
        console.error('Error cargando mensajes:', error);
        cargarMensajesPublico();
    }
}

/**
 * Cargar mensajes en modo público
 */
async function cargarMensajesPublico() {
    try {
        console.log('📧 Cargando mensajes público...');
        
        const response = await fetch(`${PUBLIC_API_BASE}/navbar`, {
            headers: { 'Accept': 'application/json' }
        });
        
        if (response.ok) {
            const data = await response.json();
            console.log('📨 Datos recibidos de la API:', data);
            
            // Extraer el array de mensajes del objeto respuesta
            if (data.mensajes && Array.isArray(data.mensajes)) {
                mensajes = data.mensajes;
                console.log('✅ Mensajes extraídos correctamente:', mensajes.length);
            } else {
                console.warn('⚠️ Formato de respuesta inesperado:', data);
                mensajes = [];
            }
            mostrarMensajes();
        } else {
            console.warn('⚠️ API falló, usando datos de demostración');
            // Datos de demostración si la API falla
            mensajes = [
                {
                    id: 1,
                    titulo: 'Mensaje de bienvenida',
                    contenido: 'Bienvenido al sistema de mensajes',
                    tipo: 'sistema',
                    prioridad: 'normal',
                    leido: false,
                    fecha_creacion: new Date().toISOString(),
                    nombre_emisor: 'Sistema'
                }
            ];
            mostrarMensajes();
        }
    } catch (error) {
        console.error('Error cargando mensajes público:', error);
        mensajes = [];
        mostrarMensajes();
    }
}

/**
 * Mostrar estadísticas en la UI
 */
function mostrarEstadisticas() {
    const stats = estadisticas;
    
    // Actualizar contadores - usando los IDs correctos de la página HTML
    updateElementText('stat-total', stats.total_mensajes || 0);
    updateElementText('stat-no-leidos', stats.mensajes_no_leidos || 0);
    updateElementText('stat-urgentes', stats.mensajes_urgentes || 0);
    updateElementText('stat-hoy', stats.usuarios_activos || 0);
}

/**
 * Mostrar estadísticas públicas (datos estáticos)
 */
function mostrarEstadisticasPublicas() {
    updateElementText('stat-total', mensajes.length);
    updateElementText('stat-no-leidos', mensajes.filter(m => !m.leido).length);
    updateElementText('stat-urgentes', mensajes.filter(m => m.prioridad === 'alta').length);
    updateElementText('stat-hoy', 1);
}

/**
 * Mostrar mensajes en la tabla
 */
function mostrarMensajes() {
    // Intentar la vista de tabla primero
    const tbody = document.getElementById('tabla-mensajes');
    const vistaTabla = document.getElementById('vista-tabla');
    const vistaTarjetas = document.getElementById('vista-tarjetas');
    const listaMensajes = document.getElementById('lista-mensajes');
    
    if (tbody && vistaTabla && !vistaTabla.classList.contains('hidden')) {
        // Mostrar en vista de tabla
        mostrarMensajesTabla(tbody);
    } else if (listaMensajes) {
        // Mostrar en vista de tarjetas
        mostrarMensajesTarjetas(listaMensajes);
    } else {
        console.error('No se encontró contenedor para mostrar mensajes');
        return;
    }
    
    // Actualizar contador total
    const totalElement = document.getElementById('total-mensajes');
    if (totalElement) {
        const total = aplicarFiltrosAMensajes(mensajes).length;
        totalElement.textContent = `${total} mensaje${total !== 1 ? 's' : ''}`;
    }
}

/**
 * Mostrar mensajes en vista de tabla
 */
function mostrarMensajesTabla(tbody) {
    // Limpiar tabla
    tbody.innerHTML = '';
    
    // Aplicar filtros
    let mensajesFiltrados = aplicarFiltrosAMensajes(mensajes);
    
    if (mensajesFiltrados.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="6" class="text-center py-8 text-gray-500">
                    <i class="fas fa-inbox text-4xl mb-4 block"></i>
                    No hay mensajes que mostrar
                </td>
            </tr>
        `;
        return;
    }
    
    // Generar filas
    mensajesFiltrados.forEach(mensaje => {
        const fila = crearFilaMensaje(mensaje);
        tbody.appendChild(fila);
    });
    
    console.log(`✅ Mostrados ${mensajesFiltrados.length} mensajes en tabla`);
}

/**
 * Mostrar mensajes en vista de tarjetas
 */
function mostrarMensajesTarjetas(contenedor) {
    // Limpiar contenedor
    contenedor.innerHTML = '';
    
    // Aplicar filtros
    let mensajesFiltrados = aplicarFiltrosAMensajes(mensajes);
    
    if (mensajesFiltrados.length === 0) {
        contenedor.innerHTML = `
            <div class="flex items-center justify-center py-12 col-span-full">
                <div class="text-center">
                    <i class="fas fa-inbox text-4xl text-gray-400 mb-4"></i>
                    <p class="text-gray-500">No hay mensajes que mostrar</p>
                </div>
            </div>
        `;
        return;
    }
    
    // Generar tarjetas
    mensajesFiltrados.forEach(mensaje => {
        const tarjeta = crearTarjetaMensaje(mensaje);
        contenedor.appendChild(tarjeta);
    });
    
    console.log(`✅ Mostrados ${mensajesFiltrados.length} mensajes en tarjetas`);
}

/**
 * Crear tarjeta de mensaje para la vista de tarjetas
 */
function crearTarjetaMensaje(mensaje) {
    const div = document.createElement('div');
    div.className = 'mensaje-card bg-white rounded-lg shadow-sm border border-gray-200 p-4 hover:shadow-md transition-shadow';
    
    const prioridadColor = {
        'alta': 'bg-red-100 text-red-800',
        'media': 'bg-yellow-100 text-yellow-800',
        'normal': 'bg-green-100 text-green-800',
        'baja': 'bg-blue-100 text-blue-800'
    };
    
    const tipoIcon = {
        'sistema': 'fas fa-cog text-blue-600',
        'alerta': 'fas fa-exclamation-triangle text-red-600',
        'notificacion': 'fas fa-bell text-yellow-600',
        'mensaje': 'fas fa-envelope text-green-600'
    };
    
    div.innerHTML = `
        <div class="flex items-start justify-between mb-3">
            <div class="flex items-center space-x-2">
                <i class="${tipoIcon[mensaje.tipo] || 'fas fa-envelope text-gray-600'}"></i>
                <span class="px-2 py-1 text-xs font-medium rounded-full ${prioridadColor[mensaje.prioridad] || prioridadColor['normal']}">
                    ${mensaje.prioridad || 'normal'}
                </span>
            </div>
            <span class="px-2 py-1 text-xs font-medium rounded-full ${mensaje.leido ? 'bg-gray-100 text-gray-600' : 'bg-blue-100 text-blue-600'}">
                ${mensaje.leido ? 'Leído' : 'No leído'}
            </span>
        </div>
        
        <h3 class="font-medium text-gray-900 mb-2 line-clamp-2">${mensaje.titulo || 'Sin título'}</h3>
        
        <p class="text-sm text-gray-600 mb-3 line-clamp-3">${mensaje.contenido || 'Sin contenido'}</p>
        
        <div class="flex items-center justify-between text-xs text-gray-500 mb-3">
            <span>De: ${mensaje.nombre_emisor || 'Sistema'}</span>
            <span>${formatearFecha(mensaje.fecha_creacion)}</span>
        </div>
        
        <div class="flex space-x-2">
            <button onclick="verMensaje(${mensaje.id})" class="flex-1 bg-blue-50 text-blue-600 hover:bg-blue-100 px-3 py-2 rounded text-sm font-medium">
                Ver
            </button>
            <button onclick="editarMensaje(${mensaje.id})" class="flex-1 bg-green-50 text-green-600 hover:bg-green-100 px-3 py-2 rounded text-sm font-medium">
                Editar
            </button>
            <button onclick="eliminarMensaje(${mensaje.id})" class="bg-red-50 text-red-600 hover:bg-red-100 px-3 py-2 rounded text-sm font-medium">
                <i class="fas fa-trash"></i>
            </button>
        </div>
    `;
    
    return div;
}

/**
 * Crear fila de mensaje para la tabla
 */
function crearFilaMensaje(mensaje) {
    const tr = document.createElement('tr');
    tr.className = 'mensaje-card hover:bg-gray-50 border-b border-gray-100';
    
    const prioridadColor = {
        'alta': 'text-red-600 bg-red-100',
        'media': 'text-yellow-600 bg-yellow-100',
        'normal': 'text-green-600 bg-green-100',
        'baja': 'text-blue-600 bg-blue-100'
    };
    
    const tipoIcon = {
        'sistema': 'fas fa-cog',
        'alerta': 'fas fa-exclamation-triangle',
        'notificacion': 'fas fa-bell',
        'mensaje': 'fas fa-envelope'
    };
    
    tr.innerHTML = `
        <td class="px-4 py-3">
            <div class="flex items-center space-x-3">
                <i class="${tipoIcon[mensaje.tipo] || 'fas fa-envelope'} text-blue-600"></i>
                <div>
                    <div class="font-medium text-gray-900">${mensaje.titulo || 'Sin título'}</div>
                    <div class="text-sm text-gray-500">${mensaje.nombre_emisor || 'Sistema'}</div>
                </div>
            </div>
        </td>
        <td class="px-4 py-3">
            <span class="px-2 py-1 text-xs font-medium rounded-full ${prioridadColor[mensaje.prioridad] || prioridadColor['normal']}">
                ${mensaje.prioridad || 'normal'}
            </span>
        </td>
        <td class="px-4 py-3">
            <span class="px-2 py-1 text-xs font-medium rounded-full ${mensaje.leido ? 'bg-gray-100 text-gray-600' : 'bg-blue-100 text-blue-600'}">
                ${mensaje.leido ? 'Leído' : 'No leído'}
            </span>
        </td>
        <td class="px-4 py-3 text-sm text-gray-600">
            ${formatearFecha(mensaje.fecha_creacion)}
        </td>
        <td class="px-4 py-3">
            <div class="flex space-x-2">
                <button onclick="verMensaje(${mensaje.id})" class="text-blue-600 hover:text-blue-800" title="Ver mensaje">
                    <i class="fas fa-eye"></i>
                </button>
                <button onclick="editarMensaje(${mensaje.id})" class="text-green-600 hover:text-green-800" title="Editar">
                    <i class="fas fa-edit"></i>
                </button>
                <button onclick="eliminarMensaje(${mensaje.id})" class="text-red-600 hover:text-red-800" title="Eliminar">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        </td>
    `;
    
    return tr;
}

/**
 * Aplicar filtros a los mensajes
 */
function aplicarFiltrosAMensajes(mensajes) {
    return mensajes.filter(mensaje => {
        // Filtro por tipo
        if (filtros.tipo !== 'todos' && mensaje.tipo !== filtros.tipo) {
            return false;
        }
        
        // Filtro por prioridad
        if (filtros.prioridad !== 'todas' && mensaje.prioridad !== filtros.prioridad) {
            return false;
        }
        
        // Filtro por estado (leído/no leído)
        if (filtros.estado === 'leidos' && !mensaje.leido) {
            return false;
        }
        if (filtros.estado === 'no-leidos' && mensaje.leido) {
            return false;
        }
        
        // Filtro por búsqueda
        if (filtros.busqueda) {
            const termino = filtros.busqueda.toLowerCase();
            const titulo = (mensaje.titulo || '').toLowerCase();
            const contenido = (mensaje.contenido || '').toLowerCase();
            const emisor = (mensaje.nombre_emisor || '').toLowerCase();
            
            if (!titulo.includes(termino) && !contenido.includes(termino) && !emisor.includes(termino)) {
                return false;
            }
        }
        
        return true;
    });
}

/**
 * Configurar event listeners
 */
function configurarEventListeners() {
    // Filtros - usar los IDs correctos de la página HTML
    const filtroTipo = document.getElementById('filtro-tipo');
    const filtroPrioridad = document.getElementById('filtro-prioridad');
    const filtroEstado = document.getElementById('filtro-estado');
    const campoBusqueda = document.getElementById('filtro-busqueda');
    
    if (filtroTipo) {
        filtroTipo.addEventListener('change', (e) => {
            filtros.tipo = e.target.value;
            mostrarMensajes();
        });
    }
    
    if (filtroPrioridad) {
        filtroPrioridad.addEventListener('change', (e) => {
            filtros.prioridad = e.target.value;
            mostrarMensajes();
        });
    }
    
    if (filtroEstado) {
        filtroEstado.addEventListener('change', (e) => {
            filtros.estado = e.target.value;
            mostrarMensajes();
        });
    }
    
    if (campoBusqueda) {
        const busquedaDebounced = debounce((termino) => {
            filtros.busqueda = termino;
            mostrarMensajes();
        }, 300);
        
        campoBusqueda.addEventListener('input', (e) => {
            busquedaDebounced(e.target.value);
        });
    }
}

/**
 * Funciones auxiliares
 */
function updateElementText(id, text) {
    const element = document.getElementById(id);
    if (element) {
        element.textContent = text;
    }
}

function formatearFecha(fechaString) {
    if (!fechaString) return 'Sin fecha';
    
    try {
        const fecha = new Date(fechaString);
        return fecha.toLocaleDateString('es-ES', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    } catch (error) {
        return 'Fecha inválida';
    }
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function poblarSelectUsuarios() {
    const select = document.getElementById('destinatario');
    if (!select) return;
    
    select.innerHTML = '<option value="">Seleccionar usuario...</option>';
    usuarios.forEach(usuario => {
        const option = document.createElement('option');
        option.value = usuario.codigo;
        option.textContent = usuario.nombre;
        select.appendChild(option);
    });
}

/**
 * Funciones de acciones (placeholder - se implementarán según necesidad)
 */
function verMensaje(id) {
    console.log('Ver mensaje:', id);
    // TODO: Implementar modal de visualización
}

function editarMensaje(id) {
    console.log('Editar mensaje:', id);
    // TODO: Implementar edición
}

function eliminarMensaje(id) {
    console.log('🗑️ Solicitud de eliminar mensaje:', id);
    
    // Confirmar eliminación
    if (!confirm('¿Estás seguro de que deseas eliminar este mensaje?')) {
        console.log('❌ Eliminación cancelada por el usuario');
        return;
    }
    
    eliminarMensajeConfirmado(id);
}

/**
 * Eliminar mensaje con confirmación
 */
async function eliminarMensajeConfirmado(id) {
    try {
        console.log('🗑️ Eliminando mensaje ID:', id);
        
        let response;
        
        // Intentar con API de administración primero (si está autenticado)
        try {
            response = await fetch(`${ADMIN_API_BASE}/${id}`, {
                method: 'DELETE',
                credentials: 'include',
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                }
            });
            
            if (response.ok) {
                console.log('✅ Mensaje eliminado via API de admin');
            } else if (response.status === 401 || response.status === 403) {
                console.log('⚠️ No autorizado para API admin, intentando endpoint público...');
                throw new Error('No autorizado');
            } else {
                throw new Error(`Error ${response.status}: ${response.statusText}`);
            }
        } catch (error) {
            console.log('⚠️ API admin falló, intentando con API público...');
            
            // Fallback: usar endpoint público de mensajes (no admin)
            response = await fetch(`/api/mensajes/${id}`, {
                method: 'DELETE',
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                }
            });
            
            if (!response.ok) {
                throw new Error(`Error ${response.status}: ${response.statusText}`);
            }
            console.log('✅ Mensaje eliminado via API público');
        }
        
        // Mostrar mensaje de éxito
        mostrarNotificacion('✅ Mensaje eliminado correctamente', 'success');
        
        // Recargar mensajes
        console.log('🔄 Recargando lista de mensajes...');
        await cargarMensajes();
        
    } catch (error) {
        console.error('❌ Error eliminando mensaje:', error);
        mostrarNotificacion(`❌ Error al eliminar mensaje: ${error.message}`, 'error');
    }
}

/**
 * Mostrar notificación temporal
 */
function mostrarNotificacion(mensaje, tipo = 'info') {
    // Crear elemento de notificación
    const notificacion = document.createElement('div');
    notificacion.className = `fixed top-4 right-4 p-4 rounded-lg shadow-lg z-50 max-w-sm transition-all duration-300 ${
        tipo === 'success' ? 'bg-green-100 border border-green-400 text-green-700' :
        tipo === 'error' ? 'bg-red-100 border border-red-400 text-red-700' :
        'bg-blue-100 border border-blue-400 text-blue-700'
    }`;
    
    notificacion.innerHTML = `
        <div class="flex items-center justify-between">
            <span class="text-sm font-medium">${mensaje}</span>
            <button onclick="this.parentElement.parentElement.remove()" class="ml-3 text-gray-400 hover:text-gray-600">
                <i class="fas fa-times"></i>
            </button>
        </div>
    `;
    
    // Agregar al DOM
    document.body.appendChild(notificacion);
    
    // Auto-eliminar después de 5 segundos
    setTimeout(() => {
        if (notificacion.parentElement) {
            notificacion.remove();
        }
    }, 5000);
}

function abrirModalNuevoMensaje() {
    const modal = document.getElementById('modal-mensaje');
    if (modal) {
        modal.classList.remove('hidden');
    }
}

function cerrarModalMensaje() {
    const modal = document.getElementById('modal-mensaje');
    if (modal) {
        modal.classList.add('hidden');
    }
}

function aplicarFiltros() {
    mostrarMensajes();
}

/**
 * Cambiar entre vista de tarjetas y tabla
 */
function cambiarVista(vista) {
    const vistaTabla = document.getElementById('vista-tabla');
    const vistaTarjetas = document.getElementById('vista-tarjetas');
    const btnTabla = document.getElementById('btn-vista-tabla');
    const btnTarjetas = document.getElementById('btn-vista-tarjetas');
    
    if (vista === 'tabla') {
        vistaTabla.classList.remove('hidden');
        vistaTarjetas.classList.add('hidden');
        btnTabla.classList.add('bg-blue-100', 'text-blue-600');
        btnTabla.classList.remove('text-gray-600', 'hover:bg-gray-100');
        btnTarjetas.classList.remove('bg-blue-100', 'text-blue-600');
        btnTarjetas.classList.add('text-gray-600', 'hover:bg-gray-100');
    } else {
        vistaTarjetas.classList.remove('hidden');
        vistaTabla.classList.add('hidden');
        btnTarjetas.classList.add('bg-blue-100', 'text-blue-600');
        btnTarjetas.classList.remove('text-gray-600', 'hover:bg-gray-100');
        btnTabla.classList.remove('bg-blue-100', 'text-blue-600');
        btnTabla.classList.add('text-gray-600', 'hover:bg-gray-100');
    }
    
    // Re-mostrar mensajes en la nueva vista
    mostrarMensajes();
}

/**
 * Limpiar todos los filtros
 */
function limpiarFiltros() {
    // Resetear filtros
    filtros = {
        tipo: 'todos',
        prioridad: 'todas',
        estado: 'todos',
        busqueda: ''
    };
    
    // Limpiar controles de la UI
    const filtroTipo = document.getElementById('filtro-tipo');
    const filtroPrioridad = document.getElementById('filtro-prioridad');
    const filtroEstado = document.getElementById('filtro-estado');
    const campoBusqueda = document.getElementById('filtro-busqueda');
    
    if (filtroTipo) filtroTipo.value = '';
    if (filtroPrioridad) filtroPrioridad.value = '';
    if (filtroEstado) filtroEstado.value = '';
    if (campoBusqueda) campoBusqueda.value = '';
    
    // Re-mostrar mensajes
    mostrarMensajes();
}

// Exportar funciones globales
window.cargarEstadisticas = cargarEstadisticas;
window.cargarUsuarios = cargarUsuarios;
window.cargarMensajes = cargarMensajes;
window.aplicarFiltros = aplicarFiltros;
window.abrirModalNuevoMensaje = abrirModalNuevoMensaje;
window.cerrarModalMensaje = cerrarModalMensaje;
window.verMensaje = verMensaje;
window.editarMensaje = editarMensaje;
window.eliminarMensaje = eliminarMensaje;
window.cambiarVista = cambiarVista;
window.limpiarFiltros = limpiarFiltros;
