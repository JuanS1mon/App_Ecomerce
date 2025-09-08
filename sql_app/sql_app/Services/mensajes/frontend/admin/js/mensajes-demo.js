/**
 * Sistema de Administración de Mensajes - Versión Demo
 * Funciona con datos simulados para demostración
 */

// Variables globales
let paginaActual = 1;
let totalPaginas = 1;
let vistaActual = 'tarjetas';
let filtrosActuales = {};
let usuarios = [];
let mensajes = [];
let wsClient = null; // Cliente WebSocket

// Datos simulados basados en la base de datos real
const mensajesSimulados = [
    {
        id: 1,
        titulo: "¡Bienvenido al Sistema!",
        contenido: "Este es tu primer mensaje en el sistema de administración. Aquí podrás gestionar todas las notificaciones y comunicaciones importantes.",
        tipo: "sistema",
        prioridad: "normal",
        leido: false,
        usuario_receptor_id: 1,
        fecha_creacion: "2025-01-21T15:30:00",
        metadatos: { origen: "sistema", categoria: "bienvenida" }
    },
    {
        id: 2,
        titulo: "Mantenimiento Programado",
        contenido: "El sistema estará en mantenimiento el próximo domingo de 2:00 AM a 6:00 AM. Durante este tiempo, algunas funcionalidades podrían no estar disponibles.",
        tipo: "alerta",
        prioridad: "alta",
        leido: false,
        usuario_receptor_id: 1,
        fecha_creacion: "2025-01-21T16:00:00",
        metadatos: { origen: "admin", fecha_mantenimiento: "2025-01-28" }
    },
    {
        id: 3,
        titulo: "Nueva Función: Reportes Avanzados",
        contenido: "Ya está disponible la nueva función de reportes avanzados en el menú de análisis. Podrás generar reportes personalizados y exportarlos en múltiples formatos.",
        tipo: "notificacion",
        prioridad: "normal",
        leido: true,
        usuario_receptor_id: 1,
        fecha_creacion: "2025-01-21T14:15:00",
        metadatos: { origen: "producto", version: "2.1.0" }
    },
    {
        id: 4,
        titulo: "🚨 URGENTE: Actualización de Seguridad",
        contenido: "Se ha detectado una vulnerabilidad de seguridad. Por favor, cambia tu contraseña inmediatamente y revisa tu actividad reciente.",
        tipo: "alerta",
        prioridad: "urgente",
        leido: false,
        usuario_receptor_id: 1,
        fecha_creacion: "2025-01-21T17:45:00",
        metadatos: { origen: "seguridad", nivel_alerta: "critico" }
    },
    {
        id: 5,
        titulo: "Recordatorio: Actualizar Perfil",
        contenido: "Recuerda actualizar tu información de perfil para mantener tus datos actualizados en el sistema.",
        tipo: "usuario",
        prioridad: "baja",
        leido: false,
        usuario_receptor_id: 1,
        fecha_creacion: "2025-01-21T12:00:00",
        metadatos: { origen: "sistema", tipo_recordatorio: "perfil" }
    },
    {
        id: 6,
        titulo: "¡Felicidades! Nuevo Logro Desbloqueado",
        contenido: "Has desbloqueado el logro 'Explorador' por navegar por todas las secciones del sistema. ¡Sigue explorando para desbloquear más logros!",
        tipo: "notificacion",
        prioridad: "baja",
        leido: true,
        usuario_receptor_id: 1,
        fecha_creacion: "2025-01-21T10:30:00",
        metadatos: { origen: "gamificacion", logro: "explorador" }
    },
    {
        id: 7,
        titulo: "Invitación a Colaborar",
        contenido: "Te han invitado a colaborar en el proyecto 'Sistema de Gestión'. Revisa los detalles en tu panel de proyectos.",
        tipo: "usuario",
        prioridad: "normal",
        leido: false,
        usuario_receptor_id: 2,
        fecha_creacion: "2025-01-21T09:15:00",
        metadatos: { origen: "colaboracion", proyecto_id: "12345" }
    },
    {
        id: 8,
        titulo: "Backup Completado",
        contenido: "El backup automático del sistema se ha completado exitosamente. Todos tus datos están seguros.",
        tipo: "sistema",
        prioridad: "normal",
        leido: true,
        usuario_receptor_id: 2,
        fecha_creacion: "2025-01-21T08:00:00",
        metadatos: { origen: "backup", backup_id: "backup_20250121" }
    }
];

const usuariosSimulados = [
    { id: 1, nombre: 'Admin', email: 'admin@sistema.com', es_admin: true },
    { id: 2, nombre: 'Usuario Test', email: 'test@ejemplo.com', es_admin: false },
    { id: 3, nombre: 'Juan Test', email: 'juan@ejemplo.com', es_admin: false }
];

// Inicialización
document.addEventListener('DOMContentLoaded', function() {
    inicializarSistemaDemo();
});

async function inicializarSistemaDemo() {
    try {
        console.log('🚀 Inicializando sistema DEMO de administración de mensajes...');
        
        // Inicializar WebSocket para notificaciones en tiempo real
        await inicializarWebSocket();
        
        // Usar datos simulados
        usuarios = usuariosSimulados;
        mensajes = mensajesSimulados;
        
        await Promise.all([
            cargarEstadisticasDemo(),
            cargarUsuariosDemo(),
            cargarMensajesDemo()
        ]);
        
        configurarEventListeners();
        console.log('✅ Sistema DEMO inicializado correctamente');
        
        // Mostrar notificación de demo
        mostrarNotificacion('Modo DEMO: Todas las funcionalidades están simuladas. Notificaciones en tiempo real activas!', 'info');
        
    } catch (error) {
        console.error('❌ Error al inicializar sistema:', error);
        mostrarNotificacion('Error al inicializar el sistema', 'error');
    }
}

async function inicializarWebSocket() {
    try {
        console.log('🔌 Inicializando conexión WebSocket...');
        
        // Solicitar permisos de notificación
        await requestNotificationPermission();
        
        // Crear cliente WebSocket
        wsClient = new NotificationWebSocket({
            url: 'ws://localhost:8000/ws/notifications',
            userId: 999, // Usuario demo
            token: 'demo-token',
            onConnect: () => {
                console.log('✅ Conectado a notificaciones en tiempo real');
                mostrarNotificacion('🔔 Notificaciones en tiempo real conectadas', 'success');
                
                // Actualizar indicador de conexión
                actualizarIndicadorConexion(true);
            },
            onDisconnect: () => {
                console.log('🔌 Desconectado de notificaciones');
                mostrarNotificacion('🔌 Conexión de notificaciones perdida', 'warning');
                
                // Actualizar indicador de conexión
                actualizarIndicadorConexion(false);
            },
            onMessage: (data) => {
                console.log('📨 Notificación recibida:', data);
                manejarNotificacionWebSocket(data);
            },
            onError: (error) => {
                console.error('❌ Error en WebSocket:', error);
            }
        });
        
        // Conectar
        wsClient.connect();
        
        // Configurar listeners específicos
        wsClient.on('new_message', (data) => {
            console.log('📩 Nuevo mensaje via WebSocket:', data);
            simularNuevoMensajeDemo(data.data);
        });
        
        wsClient.on('urgent_message', (data) => {
            console.log('🚨 Mensaje urgente via WebSocket:', data);
            simularMensajeUrgenteDemo(data.data);
        });
        
    } catch (error) {
        console.error('❌ Error inicializando WebSocket:', error);
        mostrarNotificacion('Error conectando notificaciones en tiempo real', 'warning');
    }
}

function actualizarIndicadorConexion(conectado) {
    // Crear indicador si no existe
    let indicador = document.getElementById('websocket-status');
    if (!indicador) {
        indicador = document.createElement('div');
        indicador.id = 'websocket-status';
        indicador.className = 'fixed bottom-4 left-4 px-3 py-2 rounded-lg text-sm font-medium z-40';
        document.body.appendChild(indicador);
    }
    
    if (conectado) {
        indicador.className = 'fixed bottom-4 left-4 px-3 py-2 rounded-lg text-sm font-medium z-40 bg-green-500 text-white';
        indicador.innerHTML = '<i class="fas fa-wifi mr-2"></i>Notificaciones Conectadas';
    } else {
        indicador.className = 'fixed bottom-4 left-4 px-3 py-2 rounded-lg text-sm font-medium z-40 bg-red-500 text-white';
        indicador.innerHTML = '<i class="fas fa-wifi-slash mr-2"></i>Notificaciones Desconectadas';
    }
}

function manejarNotificacionWebSocket(data) {
    switch (data.type) {
        case 'new_message':
            // El mensaje ya se maneja en el listener específico
            break;
            
        case 'system_notification':
            mostrarNotificacion(`🔔 ${data.data.title}: ${data.data.content}`, 'info');
            break;
            
        case 'connection_stats':
            console.log('📊 Estadísticas de conexión:', data.data);
            break;
            
        default:
            console.log('📨 Mensaje WebSocket no manejado:', data);
    }
}

function simularNuevoMensajeDemo(messageData) {
    // Crear nuevo mensaje en el sistema demo
    const nuevoMensaje = {
        id: Math.max(...mensajesSimulados.map(m => m.id)) + 1,
        titulo: messageData.title || 'Nuevo Mensaje en Tiempo Real',
        contenido: messageData.content || 'Este mensaje llegó via WebSocket en tiempo real',
        tipo: messageData.tipo || 'notificacion',
        prioridad: messageData.prioridad || 'normal',
        leido: false,
        usuario_receptor_id: messageData.usuario_receptor_id || 999,
        fecha_creacion: new Date().toISOString(),
        metadatos: { origen: "websocket", tiempo_real: true }
    };
    
    // Agregar al array
    mensajesSimulados.unshift(nuevoMensaje);
    
    // Recargar vista
    cargarMensajesDemo(paginaActual);
    cargarEstadisticasDemo();
    
    // Mostrar notificación
    mostrarNotificacion(`📩 Nuevo mensaje: ${nuevoMensaje.titulo}`, 'success');
}

function simularMensajeUrgenteDemo(messageData) {
    // Crear mensaje urgente
    const mensajeUrgente = {
        id: Math.max(...mensajesSimulados.map(m => m.id)) + 1,
        titulo: messageData.title || '🚨 MENSAJE URGENTE EN TIEMPO REAL',
        contenido: messageData.content || 'Este es un mensaje urgente recibido via WebSocket',
        tipo: messageData.tipo || 'alerta',
        prioridad: 'urgente',
        leido: false,
        usuario_receptor_id: messageData.usuario_receptor_id || 999,
        fecha_creacion: new Date().toISOString(),
        metadatos: { origen: "websocket", urgente: true, tiempo_real: true }
    };
    
    // Agregar al array
    mensajesSimulados.unshift(mensajeUrgente);
    
    // Recargar vista
    cargarMensajesDemo(paginaActual);
    cargarEstadisticasDemo();
    
    // Mostrar notificación especial para urgentes
    mostrarNotificacion(`🚨 URGENTE: ${mensajeUrgente.titulo}`, 'error', 8000);
}

function configurarEventListeners() {
    // Filtros
    document.getElementById('filtro-busqueda').addEventListener('input', debounce(aplicarFiltros, 500));
    document.getElementById('filtro-tipo').addEventListener('change', aplicarFiltros);
    document.getElementById('filtro-prioridad').addEventListener('change', aplicarFiltros);
    document.getElementById('filtro-estado').addEventListener('change', aplicarFiltros);
    
    // Formulario
    document.getElementById('form-mensaje').addEventListener('submit', guardarMensajeDemo);
}

// === CARGA DE DATOS DEMO ===

async function cargarEstadisticasDemo() {
    try {
        console.log('📊 Cargando estadísticas...');
        
        const stats = {
            total: mensajes.length,
            no_leidos: mensajes.filter(m => !m.leido).length,
            urgentes: mensajes.filter(m => m.prioridad === 'urgente').length,
            hoy: mensajes.filter(m => {
                const hoy = new Date().toDateString();
                const fechaMensaje = new Date(m.fecha_creacion).toDateString();
                return hoy === fechaMensaje;
            }).length
        };
        
        document.getElementById('stat-total').textContent = stats.total;
        document.getElementById('stat-no-leidos').textContent = stats.no_leidos;
        document.getElementById('stat-urgentes').textContent = stats.urgentes;
        document.getElementById('stat-hoy').textContent = stats.hoy;
        
        console.log('✅ Estadísticas cargadas:', stats);
        
    } catch (error) {
        console.error('❌ Error al cargar estadísticas:', error);
        document.getElementById('stat-total').textContent = '-';
        document.getElementById('stat-no-leidos').textContent = '-';
        document.getElementById('stat-urgentes').textContent = '-';
        document.getElementById('stat-hoy').textContent = '-';
    }
}

async function cargarUsuariosDemo() {
    try {
        console.log('👥 Cargando usuarios...');
        
        const select = document.getElementById('usuario-receptor');
        select.innerHTML = '<option value="">Seleccionar usuario...</option>';
        
        usuarios.forEach(usuario => {
            const option = document.createElement('option');
            option.value = usuario.id;
            option.textContent = `${usuario.nombre} (${usuario.email})`;
            select.appendChild(option);
        });
        
        console.log('✅ Usuarios cargados:', usuarios.length);
        
    } catch (error) {
        console.error('❌ Error al cargar usuarios:', error);
    }
}

async function cargarMensajesDemo(pagina = 1) {
    try {
        console.log(`📨 Cargando mensajes (página ${pagina})...`);
        
        // Aplicar filtros
        let mensajesFiltrados = [...mensajes];
        
        if (filtrosActuales.busqueda) {
            const busqueda = filtrosActuales.busqueda.toLowerCase();
            mensajesFiltrados = mensajesFiltrados.filter(m => 
                m.titulo.toLowerCase().includes(busqueda) ||
                m.contenido.toLowerCase().includes(busqueda)
            );
        }
        
        if (filtrosActuales.tipo) {
            mensajesFiltrados = mensajesFiltrados.filter(m => m.tipo === filtrosActuales.tipo);
        }
        
        if (filtrosActuales.prioridad) {
            mensajesFiltrados = mensajesFiltrados.filter(m => m.prioridad === filtrosActuales.prioridad);
        }
        
        if (filtrosActuales.estado) {
            const esLeido = filtrosActuales.estado === 'leido';
            mensajesFiltrados = mensajesFiltrados.filter(m => m.leido === esLeido);
        }
        
        // Paginación
        const itemsPorPagina = 10;
        const inicio = (pagina - 1) * itemsPorPagina;
        const fin = inicio + itemsPorPagina;
        const mensajesPagina = mensajesFiltrados.slice(inicio, fin);
        
        // Actualizar variables globales
        mensajes = mensajesFiltrados; // Para mantener coherencia
        paginaActual = pagina;
        totalPaginas = Math.ceil(mensajesFiltrados.length / itemsPorPagina);
        
        // Mostrar mensajes según la vista
        if (vistaActual === 'tarjetas') {
            mostrarMensajesTarjetas(mensajesPagina);
        } else {
            mostrarMensajesTabla(mensajesPagina);
        }
        
        actualizarPaginacion();
        document.getElementById('total-mensajes').textContent = `${mensajesFiltrados.length} mensajes`;
        
        console.log('✅ Mensajes cargados:', mensajesPagina.length);
        
    } catch (error) {
        console.error('❌ Error al cargar mensajes:', error);
        mostrarError('Error al cargar mensajes: ' + error.message);
    }
}

// === VISUALIZACIÓN ===

function mostrarMensajesTarjetas(mensajesMostrar = mensajes) {
    const container = document.getElementById('lista-mensajes');
    
    if (mensajesMostrar.length === 0) {
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
    
    container.innerHTML = mensajesMostrar.map(mensaje => `
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
                            <button onclick="verMensajeDemo(${mensaje.id})" class="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100">
                                <i class="fas fa-eye mr-2"></i>Ver detalles
                            </button>
                            <button onclick="editarMensajeDemo(${mensaje.id})" class="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100">
                                <i class="fas fa-edit mr-2"></i>Editar
                            </button>
                            <button onclick="toggleLeidoMensajeDemo(${mensaje.id})" class="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100">
                                <i class="fas fa-${mensaje.leido ? 'envelope' : 'envelope-open'} mr-2"></i>
                                Marcar como ${mensaje.leido ? 'no leído' : 'leído'}
                            </button>
                            <hr class="my-1">
                            <button onclick="eliminarMensajeDemo(${mensaje.id})" class="block w-full text-left px-4 py-2 text-sm text-red-700 hover:bg-red-50">
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
                    ${obtenerNombreUsuario(mensaje.usuario_receptor_id)}
                </span>
                <span>
                    <i class="fas fa-clock mr-1"></i>
                    ${formatearFecha(mensaje.fecha_creacion)}
                </span>
            </div>
        </div>
    `).join('');
}

function mostrarMensajesTabla(mensajesMostrar = mensajes) {
    const tbody = document.getElementById('tabla-mensajes');
    
    if (mensajesMostrar.length === 0) {
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
    
    tbody.innerHTML = mensajesMostrar.map(mensaje => `
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
                    <button onclick="verMensajeDemo(${mensaje.id})" class="text-blue-600 hover:text-blue-900" title="Ver">
                        <i class="fas fa-eye"></i>
                    </button>
                    <button onclick="editarMensajeDemo(${mensaje.id})" class="text-green-600 hover:text-green-900" title="Editar">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button onclick="toggleLeidoMensajeDemo(${mensaje.id})" class="text-yellow-600 hover:text-yellow-900" title="Toggle leído">
                        <i class="fas fa-${mensaje.leido ? 'envelope' : 'envelope-open'}"></i>
                    </button>
                    <button onclick="eliminarMensajeDemo(${mensaje.id})" class="text-red-600 hover:text-red-900" title="Eliminar">
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
    cargarMensajesDemo(paginaActual);
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
    cargarMensajesDemo(1);
}

function limpiarFiltros() {
    document.getElementById('filtro-busqueda').value = '';
    document.getElementById('filtro-tipo').value = '';
    document.getElementById('filtro-prioridad').value = '';
    document.getElementById('filtro-estado').value = '';
    
    filtrosActuales = {};
    cargarMensajesDemo(1);
}

// === FUNCIONES DEMO ===

function verMensajeDemo(id) {
    const mensaje = mensajesSimulados.find(m => m.id === id);
    if (!mensaje) return;
    
    const contenido = document.getElementById('contenido-ver-mensaje');
    contenido.innerHTML = `
        <div class="space-y-6">
            <div class="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
                <div class="flex items-center">
                    <i class="fas fa-info-circle text-blue-600 mr-2"></i>
                    <span class="text-blue-800 font-medium">Modo Demo</span>
                </div>
                <p class="text-blue-700 text-sm mt-1">Esta es una vista de solo lectura. En el sistema real podrías editar y gestionar este mensaje.</p>
            </div>
            
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
                    <p class="text-sm text-gray-900">${obtenerNombreUsuario(mensaje.usuario_receptor_id)}</p>
                </div>
                <div>
                    <label class="block text-sm font-medium text-gray-500">Fecha de creación</label>
                    <p class="text-sm text-gray-900">${formatearFecha(mensaje.fecha_creacion)}</p>
                </div>
                <div>
                    <label class="block text-sm font-medium text-gray-500">Estado</label>
                    <p class="text-sm text-gray-900">${mensaje.leido ? 'Leído' : 'No leído'}</p>
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
                <button onclick="editarMensajeDemo(${mensaje.id}); cerrarModalVerMensaje()" 
                        class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors">
                    <i class="fas fa-edit mr-2"></i>Editar (Demo)
                </button>
                <button onclick="toggleLeidoMensajeDemo(${mensaje.id})" 
                        class="px-4 py-2 bg-gray-600 hover:bg-gray-700 text-white rounded-lg transition-colors">
                    <i class="fas fa-${mensaje.leido ? 'envelope' : 'envelope-open'} mr-2"></i>
                    ${mensaje.leido ? 'Marcar no leído' : 'Marcar leído'}
                </button>
            </div>
        </div>
    `;
    
    document.getElementById('modal-ver-mensaje').classList.remove('hidden');
    ocultarMenusMensajes();
}

function editarMensajeDemo(id) {
    const mensaje = mensajesSimulados.find(m => m.id === id);
    if (!mensaje) return;
    
    // Llenar formulario
    document.getElementById('mensaje-id').value = mensaje.id;
    document.getElementById('mensaje-titulo').value = mensaje.titulo;
    document.getElementById('mensaje-contenido').value = mensaje.contenido;
    document.getElementById('mensaje-tipo').value = mensaje.tipo;
    document.getElementById('mensaje-prioridad').value = mensaje.prioridad;
    document.getElementById('usuario-receptor').value = mensaje.usuario_receptor_id;
    document.getElementById('mensaje-metadatos').value = JSON.stringify(mensaje.metadatos || {}, null, 2);
    
    // Cambiar título del modal
    document.getElementById('modal-titulo').textContent = 'Editar Mensaje (Demo)';
    document.getElementById('btn-guardar-texto').textContent = 'Actualizar Mensaje';
    
    // Mostrar modal
    document.getElementById('modal-mensaje').classList.remove('hidden');
    ocultarMenusMensajes();
}

function toggleLeidoMensajeDemo(id) {
    const mensaje = mensajesSimulados.find(m => m.id === id);
    if (mensaje) {
        mensaje.leido = !mensaje.leido;
        
        // Recargar vista
        cargarMensajesDemo(paginaActual);
        cargarEstadisticasDemo();
        
        mostrarNotificacion(`Mensaje marcado como ${mensaje.leido ? 'leído' : 'no leído'} (Demo)`, 'success');
    }
    
    ocultarMenusMensajes();
}

function eliminarMensajeDemo(id) {
    if (!confirm('¿Estás seguro de que quieres eliminar este mensaje? (Esta es una demostración)')) {
        return;
    }
    
    const index = mensajesSimulados.findIndex(m => m.id === id);
    if (index !== -1) {
        mensajesSimulados.splice(index, 1);
        cargarMensajesDemo(paginaActual);
        cargarEstadisticasDemo();
        mostrarNotificacion('Mensaje eliminado (Demo)', 'success');
    }
    
    ocultarMenusMensajes();
}

function guardarMensajeDemo(event) {
    event.preventDefault();
    
    const data = {
        titulo: document.getElementById('mensaje-titulo').value,
        contenido: document.getElementById('mensaje-contenido').value,
        tipo: document.getElementById('mensaje-tipo').value,
        prioridad: document.getElementById('mensaje-prioridad').value,
        usuario_receptor_id: parseInt(document.getElementById('usuario-receptor').value),
        metadatos: document.getElementById('mensaje-metadatos').value || '{}'
    };
    
    const mensajeId = document.getElementById('mensaje-id').value;
    
    if (mensajeId) {
        // Actualizar mensaje existente
        const mensaje = mensajesSimulados.find(m => m.id === parseInt(mensajeId));
        if (mensaje) {
            Object.assign(mensaje, data);
            mostrarNotificacion('Mensaje actualizado (Demo)', 'success');
        }
    } else {
        // Crear nuevo mensaje
        const nuevoMensaje = {
            id: Math.max(...mensajesSimulados.map(m => m.id)) + 1,
            ...data,
            leido: false,
            fecha_creacion: new Date().toISOString(),
            metadatos: JSON.parse(data.metadatos || '{}')
        };
        
        mensajesSimulados.unshift(nuevoMensaje);
        mostrarNotificacion('Mensaje creado (Demo)', 'success');
    }
    
    cerrarModalMensaje();
    cargarMensajesDemo();
    cargarEstadisticasDemo();
}

// === FUNCIONES AUXILIARES ===

function obtenerNombreUsuario(userId) {
    const usuario = usuarios.find(u => u.id === userId);
    return usuario ? usuario.nombre : `Usuario ${userId}`;
}

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
    ocultarMenusMensajes();
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
    
    setTimeout(() => {
        notificacion.remove();
    }, 3000);
}

// === FUNCIONES DE PRUEBA WEBSOCKET ===

function probarNotificacionDemo() {
    if (wsClient && wsClient.isConnected) {
        // Simular recepción de notificación
        const notificacionDemo = {
            type: 'new_message',
            data: {
                id: Math.random() * 1000,
                title: 'Mensaje de Prueba en Tiempo Real',
                content: 'Este es un mensaje de prueba enviado via WebSocket para demostrar las notificaciones en tiempo real.',
                tipo: 'notificacion',
                prioridad: 'normal',
                usuario_receptor_id: 999
            }
        };
        
        manejarNotificacionWebSocket(notificacionDemo);
        simularNuevoMensajeDemo(notificacionDemo.data);
        
        mostrarNotificacion('🧪 Notificación de prueba enviada', 'success');
    } else {
        mostrarNotificacion('❌ WebSocket no conectado', 'error');
    }
}

function probarMensajeUrgente() {
    if (wsClient && wsClient.isConnected) {
        // Simular mensaje urgente
        const mensajeUrgente = {
            type: 'urgent_message',
            data: {
                id: Math.random() * 1000,
                title: '🚨 PRUEBA: Mensaje Urgente en Tiempo Real',
                content: 'Este es un mensaje urgente de prueba. En un sistema real, este tipo de mensajes requeriría atención inmediata.',
                tipo: 'alerta',
                prioridad: 'urgente',
                usuario_receptor_id: 999
            }
        };
        
        manejarNotificacionWebSocket(mensajeUrgente);
        simularMensajeUrgenteDemo(mensajeUrgente.data);
        
        mostrarNotificacion('🚨 Mensaje urgente de prueba enviado', 'warning');
    } else {
        mostrarNotificacion('❌ WebSocket no conectado', 'error');
    }
}

function mostrarEstadisticasWS() {
    if (wsClient) {
        const status = wsClient.getStatus();
        const stats = `
            Estado WebSocket:
            • Conectado: ${status.isConnected ? '✅ Sí' : '❌ No'}
            • Conectando: ${status.isConnecting ? '🔄 Sí' : '⏸️ No'}
            • Intentos de reconexión: ${status.reconnectAttempts}
            • URL: ${status.url}
            • Usuario ID: ${status.userId}
        `;
        
        alert(stats);
        
        // Solicitar estadísticas del servidor
        if (wsClient.isConnected) {
            wsClient.requestStats();
        }
    } else {
        mostrarNotificacion('❌ Cliente WebSocket no inicializado', 'error');
    }
}

function probarNotificacionSistema() {
    if (wsClient && wsClient.isConnected) {
        const notificacionSistema = {
            type: 'system_notification',
            data: {
                title: 'Mantenimiento Programado',
                content: 'El sistema entrará en mantenimiento en 30 minutos. Guarde su trabajo.',
                notification_type: 'maintenance',
                timestamp: new Date().toISOString()
            }
        };
        
        manejarNotificacionWebSocket(notificacionSistema);
        mostrarNotificacion('🔧 Notificación de sistema enviada', 'info');
    } else {
        mostrarNotificacion('❌ WebSocket no conectado', 'error');
    }
}

// Función para reconectar manualmente
function reconectarWebSocket() {
    if (wsClient) {
        wsClient.disconnect();
        setTimeout(() => {
            wsClient.connect();
            mostrarNotificacion('🔄 Intentando reconectar WebSocket...', 'info');
        }, 1000);
    }
}

function mostrarError(mensaje) {
    const container = document.getElementById('lista-mensajes');
    container.innerHTML = `
        <div class="flex items-center justify-center py-12 col-span-full">
            <div class="text-center">
                <i class="fas fa-exclamation-triangle text-4xl text-red-400 mb-4"></i>
                <p class="text-red-600">${mensaje}</p>
                <button onclick="cargarMensajesDemo()" class="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
                    Reintentar
                </button>
            </div>
        </div>
    `;
}

// === PAGINACIÓN ===

function actualizarPaginacion() {
    const totalMensajes = mensajes.length;
    const inicio = Math.min((paginaActual - 1) * 10 + 1, totalMensajes);
    const fin = Math.min(paginaActual * 10, totalMensajes);
    
    document.getElementById('pag-inicio').textContent = totalMensajes > 0 ? inicio : 0;
    document.getElementById('pag-fin').textContent = fin;
    document.getElementById('pag-total').textContent = totalMensajes;
    
    document.getElementById('btn-anterior').disabled = paginaActual <= 1;
    document.getElementById('btn-siguiente').disabled = paginaActual >= totalPaginas;
}

function paginaAnterior() {
    if (paginaActual > 1) {
        cargarMensajesDemo(paginaActual - 1);
    }
}

function paginaSiguiente() {
    if (paginaActual < totalPaginas) {
        cargarMensajesDemo(paginaActual + 1);
    }
}

// === MODALES ===

function abrirModalNuevoMensaje() {
    limpiarFormularioMensaje();
    document.getElementById('modal-titulo').textContent = 'Nuevo Mensaje (Demo)';
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
