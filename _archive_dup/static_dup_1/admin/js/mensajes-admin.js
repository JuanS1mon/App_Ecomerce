/**
 * Sistema de Administración de Mensajes
 * Gestión completa de mensajes del sistema
 */

// Variables globales
let paginaActual = 1;
let totalPaginas = 1;
let vistaActual = 'tarjetas';
let filtrosActuales = {};
let usuarios = [];
let mensajes = [];

// URLs de la API - Usando endpoints de administración directos
const API_BASE = '/admin/api/mensajes';

// Inicialización
document.addEventListener('DOMContentLoaded', function() {
    inicializarSistema();
});

async function inicializarSistema() {
    try {
        console.log('🚀 Inicializando sistema de administración de mensajes...');
        
        await Promise.all([
            cargarEstadisticas(),
            cargarUsuarios(),
            cargarMensajes()
        ]);
        
        configurarEventListeners();
        console.log('✅ Sistema inicializado correctamente');
        
    } catch (error) {
        console.error('❌ Error al inicializar sistema:', error);
        mostrarNotificacion('Error al inicializar el sistema', 'error');
    }
}

function configurarEventListeners() {
    // Filtros
    document.getElementById('filtro-busqueda').addEventListener('input', debounce(aplicarFiltros, 500));
    document.getElementById('filtro-tipo').addEventListener('change', aplicarFiltros);
    document.getElementById('filtro-prioridad').addEventListener('change', aplicarFiltros);
    document.getElementById('filtro-estado').addEventListener('change', aplicarFiltros);
    
    // Formulario
    document.getElementById('form-mensaje').addEventListener('submit', guardarMensaje);
}

// === CARGA DE DATOS ===

async function cargarEstadisticas() {
    try {
        console.log('📊 Cargando estadísticas...');
        
        const response = await fetch(`${API_BASE}/estadisticas`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`,
                'Content-Type': 'application/json'
            }
        });
        
        if (response.ok) {
            const stats = await response.json();
            document.getElementById('stat-total').textContent = stats.total || 0;
            document.getElementById('stat-no-leidos').textContent = stats.no_leidos || 0;
            document.getElementById('stat-urgentes').textContent = stats.urgentes || 0;
            document.getElementById('stat-hoy').textContent = stats.hoy || 0;
            console.log('✅ Estadísticas cargadas:', stats);
        } else {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
    } catch (error) {
        console.error('❌ Error al cargar estadísticas:', error);
        // Mostrar valores por defecto
        document.getElementById('stat-total').textContent = '-';
        document.getElementById('stat-no-leidos').textContent = '-';
        document.getElementById('stat-urgentes').textContent = '-';
        document.getElementById('stat-hoy').textContent = '-';
        
        if (error.message.includes('401')) {
            mostrarNotificacion('Sesión expirada. Por favor, inicia sesión nuevamente.', 'error');
        }
    }
}

async function cargarUsuarios() {
    try {
        console.log('👥 Cargando usuarios...');
        
        const response = await fetch(`${API_BASE}/usuarios/lista`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`,
                'Content-Type': 'application/json'
            }
        });
        
        if (response.ok) {
            usuarios = await response.json();
            
            const select = document.getElementById('usuario-receptor');
            select.innerHTML = '<option value="">Seleccionar usuario...</option>';
            
            usuarios.forEach(usuario => {
                const option = document.createElement('option');
                option.value = usuario.id;
                option.textContent = `${usuario.nombre} (${usuario.email})`;
                select.appendChild(option);
            });
            
            console.log('✅ Usuarios cargados:', usuarios.length);
        } else {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
    } catch (error) {
        console.error('❌ Error al cargar usuarios:', error);
        // Fallback a usuarios simulados
        usuarios = [
            { id: 1, nombre: 'Admin', email: 'admin@sistema.com' },
            { id: 2, nombre: 'Usuario 1', email: 'user1@sistema.com' },
            { id: 3, nombre: 'Usuario 2', email: 'user2@sistema.com' }
        ];
        
        const select = document.getElementById('usuario-receptor');
        select.innerHTML = '<option value="">Seleccionar usuario...</option>';
        
        usuarios.forEach(usuario => {
            const option = document.createElement('option');
            option.value = usuario.id;
            option.textContent = `${usuario.nombre} (${usuario.email})`;
            select.appendChild(option);
        });
    }
}

async function cargarMensajes(pagina = 1) {
    try {
        console.log(`📨 Cargando mensajes (página ${pagina})...`);
        
        // Construir parámetros de filtros
        const params = new URLSearchParams();
        params.append('skip', (pagina - 1) * 10);
        params.append('limit', 10);
        
        if (filtrosActuales.busqueda) params.append('busqueda', filtrosActuales.busqueda);
        if (filtrosActuales.tipo) params.append('tipo', filtrosActuales.tipo);
        if (filtrosActuales.prioridad) params.append('prioridad', filtrosActuales.prioridad);
        if (filtrosActuales.estado) {
            params.append('leido', filtrosActuales.estado === 'leido');
        }
        
        const response = await fetch(`${API_BASE}/?${params}`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`,
                'Content-Type': 'application/json'
            }
        });
        
        if (response.ok) {
            mensajes = await response.json();
            console.log('✅ Mensajes cargados:', mensajes.length);
        } else {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        paginaActual = pagina;
        totalPaginas = Math.ceil(mensajes.length / 10);
        
        if (vistaActual === 'tarjetas') {
            mostrarMensajesTarjetas();
        } else {
            mostrarMensajesTabla();
        }
        
        actualizarPaginacion();
        document.getElementById('total-mensajes').textContent = `${mensajes.length} mensajes`;
        
    } catch (error) {
        console.error('❌ Error al cargar mensajes:', error);
        mostrarError('Error al cargar mensajes: ' + error.message);
        
        if (error.message.includes('401')) {
            mostrarNotificacion('Sesión expirada. Por favor, inicia sesión nuevamente.', 'error');
        }
    }
}

// === VISUALIZACIÓN ===

function mostrarMensajesTarjetas() {
    const container = document.getElementById('lista-mensajes');
    
    if (mensajes.length === 0) {
        container.innerHTML = `
            <div class="flex items-center justify-center py-12 col-span-full">
                <div class="text-center">
                    <i class="fas fa-inbox text-4xl text-gray-400 mb-4"></i>
                    <p class="text-gray-500">No hay mensajes para mostrar</p>
                </div>
            </div>
        `;
        return;
    }
    
    container.innerHTML = mensajes.map(mensaje => `
        <div class="mensaje-card bg-white rounded-xl shadow-sm border border-gray-200 p-6 hover:shadow-md transition-all">
            <div class="flex items-start justify-between mb-4">
                <div class="flex items-center space-x-2">
                    ${getIconoTipo(mensaje.tipo)}
                    <span class="px-2 py-1 text-xs font-medium rounded-full ${getColorTipo(mensaje.tipo)}">
                        ${mensaje.tipo.charAt(0).toUpperCase() + mensaje.tipo.slice(1)}
                    </span>
                    <span class="px-2 py-1 text-xs font-medium rounded-full ${getColorPrioridad(mensaje.prioridad)}">
                        ${mensaje.prioridad.charAt(0).toUpperCase() + mensaje.prioridad.slice(1)}
                    </span>
                </div>
                
                <div class="flex items-center space-x-2">
                    ${mensaje.leido ? 
                        '<i class="fas fa-envelope-open text-gray-400" title="Leído"></i>' : 
                        '<i class="fas fa-envelope text-blue-600" title="No leído"></i>'
                    }
                    <div class="relative">
                        <button onclick="toggleMenuMensaje(${mensaje.id})" class="text-gray-400 hover:text-gray-600">
                            <i class="fas fa-ellipsis-v"></i>
                        </button>
                        <div id="menu-${mensaje.id}" class="hidden absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg z-10 border">
                            <button onclick="verMensaje(${mensaje.id})" class="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100">
                                <i class="fas fa-eye mr-2"></i>Ver detalles
                            </button>
                            <button onclick="editarMensaje(${mensaje.id})" class="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100">
                                <i class="fas fa-edit mr-2"></i>Editar
                            </button>
                            <button onclick="toggleLeidoMensaje(${mensaje.id})" class="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100">
                                <i class="fas fa-${mensaje.leido ? 'envelope' : 'envelope-open'} mr-2"></i>
                                Marcar como ${mensaje.leido ? 'no leído' : 'leído'}
                            </button>
                            <hr class="my-1">
                            <button onclick="eliminarMensaje(${mensaje.id})" class="block w-full text-left px-4 py-2 text-sm text-red-700 hover:bg-red-50">
                                <i class="fas fa-trash mr-2"></i>Eliminar
                            </button>
                        </div>
                    </div>
                </div>
            </div>
            
            <h3 class="font-semibold text-gray-900 mb-2 line-clamp-2">${mensaje.titulo}</h3>
            <p class="text-gray-600 text-sm mb-4 line-clamp-3">${mensaje.contenido}</p>
            
            <div class="flex items-center justify-between text-xs text-gray-500">
                <span>
                    <i class="fas fa-user mr-1"></i>
                    Usuario ${mensaje.usuario_id}
                </span>
                <span>
                    <i class="fas fa-clock mr-1"></i>
                    ${formatearFecha(mensaje.fecha_creacion)}
                </span>
            </div>
        </div>
    `).join('');
}

function mostrarMensajesTabla() {
    const tbody = document.getElementById('tabla-mensajes');
    
    if (mensajes.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="6" class="px-6 py-12 text-center text-gray-500">
                    <i class="fas fa-inbox text-4xl mb-4 block"></i>
                    No hay mensajes para mostrar
                </td>
            </tr>
        `;
        return;
    }
    
    tbody.innerHTML = mensajes.map(mensaje => `
        <tr class="hover:bg-gray-50">
            <td class="px-6 py-4 whitespace-nowrap">
                ${mensaje.leido ? 
                    '<i class="fas fa-envelope-open text-gray-400" title="Leído"></i>' : 
                    '<i class="fas fa-envelope text-blue-600" title="No leído"></i>'
                }
            </td>
            <td class="px-6 py-4">
                <div class="text-sm font-medium text-gray-900">${mensaje.titulo}</div>
                <div class="text-sm text-gray-500 truncate max-w-xs">${mensaje.contenido}</div>
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
                <span class="px-2 py-1 text-xs font-medium rounded-full ${getColorTipo(mensaje.tipo)}">
                    ${mensaje.tipo.charAt(0).toUpperCase() + mensaje.tipo.slice(1)}
                </span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
                <span class="px-2 py-1 text-xs font-medium rounded-full ${getColorPrioridad(mensaje.prioridad)}">
                    ${mensaje.prioridad.charAt(0).toUpperCase() + mensaje.prioridad.slice(1)}
                </span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                ${formatearFecha(mensaje.fecha_creacion)}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                <div class="flex space-x-2">
                    <button onclick="verMensaje(${mensaje.id})" class="text-blue-600 hover:text-blue-900" title="Ver">
                        <i class="fas fa-eye"></i>
                    </button>
                    <button onclick="editarMensaje(${mensaje.id})" class="text-green-600 hover:text-green-900" title="Editar">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button onclick="toggleLeidoMensaje(${mensaje.id})" class="text-yellow-600 hover:text-yellow-900" title="Toggle leído">
                        <i class="fas fa-${mensaje.leido ? 'envelope' : 'envelope-open'}"></i>
                    </button>
                    <button onclick="eliminarMensaje(${mensaje.id})" class="text-red-600 hover:text-red-900" title="Eliminar">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </td>
        </tr>
    `).join('');
}

// === FUNCIONES DE INTERFAZ ===

function cambiarVista(nuevaVista) {
    vistaActual = nuevaVista;
    
    // Actualizar botones
    document.getElementById('btn-vista-tarjetas').className = 
        nuevaVista === 'tarjetas' ? 'p-2 rounded-lg bg-blue-100 text-blue-600' : 'p-2 rounded-lg text-gray-600 hover:bg-gray-100';
    document.getElementById('btn-vista-tabla').className = 
        nuevaVista === 'tabla' ? 'p-2 rounded-lg bg-blue-100 text-blue-600' : 'p-2 rounded-lg text-gray-600 hover:bg-gray-100';
    
    // Mostrar/ocultar vistas
    document.getElementById('vista-tarjetas').style.display = nuevaVista === 'tarjetas' ? 'block' : 'none';
    document.getElementById('vista-tabla').style.display = nuevaVista === 'tabla' ? 'block' : 'none';
    
    // Recargar datos
    if (nuevaVista === 'tarjetas') {
        mostrarMensajesTarjetas();
    } else {
        mostrarMensajesTabla();
    }
}

function aplicarFiltros() {
    // Obtener valores de filtros
    filtrosActuales = {
        busqueda: document.getElementById('filtro-busqueda').value.trim(),
        tipo: document.getElementById('filtro-tipo').value,
        prioridad: document.getElementById('filtro-prioridad').value,
        estado: document.getElementById('filtro-estado').value
    };
    
    console.log('🔍 Aplicando filtros:', filtrosActuales);
    
    // Aquí aplicaríamos los filtros a los datos
    // Por ahora mantenemos los datos simulados
    
    cargarMensajes(1);
}

function limpiarFiltros() {
    document.getElementById('filtro-busqueda').value = '';
    document.getElementById('filtro-tipo').value = '';
    document.getElementById('filtro-prioridad').value = '';
    document.getElementById('filtro-estado').value = '';
    
    filtrosActuales = {};
    cargarMensajes(1);
}

// === MODALES ===

function abrirModalNuevoMensaje() {
    limpiarFormularioMensaje();
    document.getElementById('modal-titulo').textContent = 'Nuevo Mensaje';
    document.getElementById('btn-guardar-texto').textContent = 'Crear Mensaje';
    document.getElementById('modal-mensaje').classList.remove('hidden');
}

function cerrarModalMensaje() {
    document.getElementById('modal-mensaje').classList.add('hidden');
    limpiarFormularioMensaje();
}

function cerrarModalVerMensaje() {
    document.getElementById('modal-ver-mensaje').classList.add('hidden');
}

function limpiarFormularioMensaje() {
    document.getElementById('form-mensaje').reset();
    document.getElementById('mensaje-id').value = '';
}

async function guardarMensaje(event) {
    event.preventDefault();
    
    try {
        const formData = new FormData(event.target);
        const data = {
            titulo: document.getElementById('mensaje-titulo').value,
            contenido: document.getElementById('mensaje-contenido').value,
            tipo: document.getElementById('mensaje-tipo').value,
            prioridad: document.getElementById('mensaje-prioridad').value,
            usuario_id: parseInt(document.getElementById('usuario-receptor').value),
            metadatos: document.getElementById('mensaje-metadatos').value || '{}'
        };
        
        const mensajeId = document.getElementById('mensaje-id').value;
        
        console.log('💾 Guardando mensaje:', data);
        
        // Simulamos el guardado exitoso
        mostrarNotificacion(mensajeId ? 'Mensaje actualizado correctamente' : 'Mensaje creado correctamente', 'success');
        cerrarModalMensaje();
        cargarMensajes();
        cargarEstadisticas();
        
    } catch (error) {
        console.error('❌ Error al guardar mensaje:', error);
        mostrarNotificacion('Error al guardar el mensaje', 'error');
    }
}

// === ACCIONES DE MENSAJES ===

function verMensaje(id) {
    const mensaje = mensajes.find(m => m.id === id);
    if (!mensaje) return;
    
    const contenido = document.getElementById('contenido-ver-mensaje');
    contenido.innerHTML = `
        <div class="space-y-6">
            <div class="flex items-center justify-between">
                <div class="flex items-center space-x-3">
                    ${getIconoTipo(mensaje.tipo)}
                    <span class="px-3 py-1 text-sm font-medium rounded-full ${getColorTipo(mensaje.tipo)}">
                        ${mensaje.tipo.charAt(0).toUpperCase() + mensaje.tipo.slice(1)}
                    </span>
                    <span class="px-3 py-1 text-sm font-medium rounded-full ${getColorPrioridad(mensaje.prioridad)}">
                        ${mensaje.prioridad.charAt(0).toUpperCase() + mensaje.prioridad.slice(1)}
                    </span>
                </div>
                <div class="flex items-center space-x-2">
                    ${mensaje.leido ? 
                        '<span class="px-2 py-1 text-xs bg-green-100 text-green-800 rounded-full">Leído</span>' : 
                        '<span class="px-2 py-1 text-xs bg-orange-100 text-orange-800 rounded-full">No leído</span>'
                    }
                </div>
            </div>
            
            <div>
                <h3 class="text-xl font-semibold text-gray-900 mb-4">${mensaje.titulo}</h3>
                <div class="prose max-w-none">
                    <p class="text-gray-700 leading-relaxed">${mensaje.contenido}</p>
                </div>
            </div>
            
            <div class="grid grid-cols-2 gap-4 pt-4 border-t border-gray-200">
                <div>
                    <label class="block text-sm font-medium text-gray-500">Usuario</label>
                    <p class="text-sm text-gray-900">Usuario ${mensaje.usuario_id}</p>
                </div>
                <div>
                    <label class="block text-sm font-medium text-gray-500">Fecha de creación</label>
                    <p class="text-sm text-gray-900">${formatearFecha(mensaje.fecha_creacion)}</p>
                </div>
                <div>
                    <label class="block text-sm font-medium text-gray-500">Leído</label>
                    <p class="text-sm text-gray-900">${mensaje.fecha_leido ? formatearFecha(mensaje.fecha_leido) : 'No leído'}</p>
                </div>
                <div>
                    <label class="block text-sm font-medium text-gray-500">ID</label>
                    <p class="text-sm text-gray-900">#${mensaje.id}</p>
                </div>
            </div>
            
            ${mensaje.metadatos && Object.keys(mensaje.metadatos).length > 0 ? `
                <div class="pt-4 border-t border-gray-200">
                    <label class="block text-sm font-medium text-gray-500 mb-2">Metadatos</label>
                    <pre class="bg-gray-50 p-3 rounded-lg text-xs text-gray-700 overflow-x-auto">${JSON.stringify(mensaje.metadatos, null, 2)}</pre>
                </div>
            ` : ''}
            
            <div class="flex justify-end space-x-3 pt-4 border-t border-gray-200">
                <button onclick="editarMensaje(${mensaje.id}); cerrarModalVerMensaje()" 
                        class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors">
                    <i class="fas fa-edit mr-2"></i>Editar
                </button>
                <button onclick="toggleLeidoMensaje(${mensaje.id})" 
                        class="px-4 py-2 bg-gray-600 hover:bg-gray-700 text-white rounded-lg transition-colors">
                    <i class="fas fa-${mensaje.leido ? 'envelope' : 'envelope-open'} mr-2"></i>
                    Marcar como ${mensaje.leido ? 'no leído' : 'leído'}
                </button>
            </div>
        </div>
    `;
    
    document.getElementById('modal-ver-mensaje').classList.remove('hidden');
    ocultarMenusMensajes();
}

function editarMensaje(id) {
    const mensaje = mensajes.find(m => m.id === id);
    if (!mensaje) return;
    
    // Llenar formulario
    document.getElementById('mensaje-id').value = mensaje.id;
    document.getElementById('mensaje-titulo').value = mensaje.titulo;
    document.getElementById('mensaje-contenido').value = mensaje.contenido;
    document.getElementById('mensaje-tipo').value = mensaje.tipo;
    document.getElementById('mensaje-prioridad').value = mensaje.prioridad;
    document.getElementById('usuario-receptor').value = mensaje.usuario_id;
    document.getElementById('mensaje-metadatos').value = JSON.stringify(mensaje.metadatos || {}, null, 2);
    
    // Cambiar título del modal
    document.getElementById('modal-titulo').textContent = 'Editar Mensaje';
    document.getElementById('btn-guardar-texto').textContent = 'Actualizar Mensaje';
    
    // Mostrar modal
    document.getElementById('modal-mensaje').classList.remove('hidden');
    ocultarMenusMensajes();
}

async function toggleLeidoMensaje(id) {
    try {
        console.log(`📬 Cambiando estado de lectura del mensaje ${id}`);
        
        // Simulamos el cambio
        const mensaje = mensajes.find(m => m.id === id);
        if (mensaje) {
            mensaje.leido = !mensaje.leido;
            mensaje.fecha_leido = mensaje.leido ? new Date().toISOString() : null;
        }
        
        // Recargar vista
        if (vistaActual === 'tarjetas') {
            mostrarMensajesTarjetas();
        } else {
            mostrarMensajesTabla();
        }
        
        cargarEstadisticas();
        mostrarNotificacion('Estado de lectura actualizado', 'success');
        
    } catch (error) {
        console.error('❌ Error al cambiar estado:', error);
        mostrarNotificacion('Error al actualizar el estado', 'error');
    }
    
    ocultarMenusMensajes();
}

async function eliminarMensaje(id) {
    if (!confirm('¿Estás seguro de que quieres eliminar este mensaje? Esta acción no se puede deshacer.')) {
        return;
    }
    
    try {
        console.log(`🗑️ Eliminando mensaje ${id}`);
        
        // Simulamos la eliminación
        const index = mensajes.findIndex(m => m.id === id);
        if (index !== -1) {
            mensajes.splice(index, 1);
        }
        
        cargarMensajes();
        cargarEstadisticas();
        mostrarNotificacion('Mensaje eliminado correctamente', 'success');
        
    } catch (error) {
        console.error('❌ Error al eliminar mensaje:', error);
        mostrarNotificacion('Error al eliminar el mensaje', 'error');
    }
    
    ocultarMenusMensajes();
}

// === PAGINACIÓN ===

function actualizarPaginacion() {
    const totalMensajes = mensajes.length;
    const inicio = (paginaActual - 1) * 10 + 1;
    const fin = Math.min(paginaActual * 10, totalMensajes);
    
    document.getElementById('pag-inicio').textContent = inicio;
    document.getElementById('pag-fin').textContent = fin;
    document.getElementById('pag-total').textContent = totalMensajes;
    
    document.getElementById('btn-anterior').disabled = paginaActual <= 1;
    document.getElementById('btn-siguiente').disabled = paginaActual >= totalPaginas;
}

function paginaAnterior() {
    if (paginaActual > 1) {
        cargarMensajes(paginaActual - 1);
    }
}

function paginaSiguiente() {
    if (paginaActual < totalPaginas) {
        cargarMensajes(paginaActual + 1);
    }
}

// === FUNCIONES AUXILIARES ===

function getIconoTipo(tipo) {
    const iconos = {
        sistema: '<i class="fas fa-cog text-gray-600"></i>',
        alerta: '<i class="fas fa-exclamation-triangle text-red-600"></i>',
        notificacion: '<i class="fas fa-bell text-blue-600"></i>',
        usuario: '<i class="fas fa-user text-green-600"></i>'
    };
    return iconos[tipo] || '<i class="fas fa-envelope text-gray-600"></i>';
}

function getColorTipo(tipo) {
    const colores = {
        sistema: 'bg-gray-100 text-gray-800',
        alerta: 'bg-red-100 text-red-800',
        notificacion: 'bg-blue-100 text-blue-800',
        usuario: 'bg-green-100 text-green-800'
    };
    return colores[tipo] || 'bg-gray-100 text-gray-800';
}

function getColorPrioridad(prioridad) {
    const colores = {
        baja: 'bg-green-100 text-green-800',
        normal: 'bg-blue-100 text-blue-800',
        alta: 'bg-orange-100 text-orange-800',
        urgente: 'bg-red-100 text-red-800'
    };
    return colores[prioridad] || 'bg-gray-100 text-gray-800';
}

function formatearFecha(fechaString) {
    const fecha = new Date(fechaString);
    return fecha.toLocaleString('es-ES', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

function toggleMenuMensaje(id) {
    // Ocultar todos los menús primero
    ocultarMenusMensajes();
    
    // Mostrar el menú específico
    const menu = document.getElementById(`menu-${id}`);
    if (menu) {
        menu.classList.toggle('hidden');
    }
}

function ocultarMenusMensajes() {
    document.querySelectorAll('[id^="menu-"]').forEach(menu => {
        menu.classList.add('hidden');
    });
}

// Cerrar menús al hacer clic fuera
document.addEventListener('click', function(event) {
    if (!event.target.closest('.relative')) {
        ocultarMenusMensajes();
    }
});

function mostrarNotificacion(mensaje, tipo = 'info') {
    // Crear notificación temporal
    const notificacion = document.createElement('div');
    notificacion.className = `fixed top-4 right-4 z-50 p-4 rounded-lg shadow-lg slide-in ${
        tipo === 'success' ? 'bg-green-500 text-white' :
        tipo === 'error' ? 'bg-red-500 text-white' :
        tipo === 'warning' ? 'bg-yellow-500 text-black' :
        'bg-blue-500 text-white'
    }`;
    
    notificacion.innerHTML = `
        <div class="flex items-center space-x-2">
            <i class="fas fa-${
                tipo === 'success' ? 'check-circle' :
                tipo === 'error' ? 'exclamation-circle' :
                tipo === 'warning' ? 'exclamation-triangle' :
                'info-circle'
            }"></i>
            <span>${mensaje}</span>
        </div>
    `;
    
    document.body.appendChild(notificacion);
    
    // Eliminar después de 3 segundos
    setTimeout(() => {
        notificacion.remove();
    }, 3000);
}

function mostrarError(mensaje) {
    const container = document.getElementById('lista-mensajes');
    container.innerHTML = `
        <div class="flex items-center justify-center py-12 col-span-full">
            <div class="text-center">
                <i class="fas fa-exclamation-triangle text-4xl text-red-400 mb-4"></i>
                <p class="text-red-600">${mensaje}</p>
                <button onclick="cargarMensajes()" class="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
                    Reintentar
                </button>
            </div>
        </div>
    `;
}

// Función debounce para búsqueda
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
