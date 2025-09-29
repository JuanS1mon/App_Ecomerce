/**
 * Script avanzado de gestión de usuarios - Panel de administración
 * Versión mejorada con todas las funcionalidades del backend
 */

// ==================== INICIALIZACIÓN DE TOKEN ====================
function initializeToken() {
    // Extraer token de la URL si está presente
    const urlParams = new URLSearchParams(window.location.search);
    const tokenFromUrl = urlParams.get('token');
    
    if (tokenFromUrl) {
        console.log('🔑 Token encontrado en URL, guardando en localStorage');
        localStorage.setItem('access_token', tokenFromUrl);
        
        // Limpiar la URL para que no se vea el token
        const cleanUrl = window.location.origin + window.location.pathname;
        window.history.replaceState({}, document.title, cleanUrl);
    } else {
        console.log('🔍 No hay token en URL, verificando localStorage');
        const tokenFromStorage = localStorage.getItem('access_token');
        if (!tokenFromStorage) {
            console.log('❌ No hay token disponible, redirigiendo a login');
            window.location.href = '/loginpage';
            return false;
        }
    }
    return true;
}

// Inicializar token antes de cargar el DOM
if (!initializeToken()) {
    // Si no hay token, detener la ejecución
    throw new Error('Token requerido');
}

document.addEventListener('DOMContentLoaded', function() {
    // ==================== VARIABLES GLOBALES ====================
    let usuarios = [];
    let roles = [];
    let paginaActual = 1;
    let usuariosPorPagina = 10;
    let usuarioIdActual = null;
    let totalPaginas = 0;
    let tabActual = 'usuarios';

    // ==================== ELEMENTOS DEL DOM ====================
    // Tabla y paginación
    const usuariosTableBody = document.getElementById('users-table-body');
    const startRange = document.getElementById('startRange');
    const endRange = document.getElementById('endRange');
    const totalUsuarios = document.getElementById('totalUsuarios');
    const paginationNumbers = document.getElementById('paginationNumbers');
    const btnAnterior = document.getElementById('btnAnterior');
    const btnSiguiente = document.getElementById('btnSiguiente');
    const btnAnteriorMobile = document.getElementById('btnAnteriorMobile');
    const btnSiguienteMobile = document.getElementById('btnSiguienteMobile');

    // Filtros y búsqueda
    const searchUsuarios = document.getElementById('searchUsuarios');
    const filterRol = document.getElementById('filterRol');
    const filterEstado = document.getElementById('filterEstado');
    const btnAplicarFiltros = document.getElementById('btnAplicarFiltros');

    // Botones principales
    const btnNuevoUsuario = document.getElementById('btnNuevoUsuario');
    const btnExportarUsuarios = document.getElementById('btnExportarUsuarios');
    const btnImportarUsuarios = document.getElementById('btnImportarUsuarios');

    // Pestañas
    const tabUsuarios = document.getElementById('tab-usuarios');
    const tabRoles = document.getElementById('tab-roles');
    const tabPermisos = document.getElementById('tab-permisos');
    const tabAuditoria = document.getElementById('tab-auditoria');

    // Contenido de pestañas
    const contentUsuarios = document.getElementById('content-usuarios');
    const contentRoles = document.getElementById('content-roles');
    const contentPermisos = document.getElementById('content-permisos');
    const contentAuditoria = document.getElementById('content-auditoria');

    // Estadísticas
    const totalUsersElement = document.getElementById('total-users');
    const activeUsersElement = document.getElementById('active-users');
    const adminUsersElement = document.getElementById('admin-users');
    const totalRolesElement = document.getElementById('total-roles');

    // ==================== INICIALIZACIÓN ====================
    init();

    async function init() {
        console.log('🚀 Iniciando aplicación de gestión de usuarios...');
        
        // Cargar componentes
        if (window.loadComponents) {
            await loadComponents();
        }
        
        // Configurar eventos
        setupEventListeners();
        
        // Cargar datos iniciales
        await cargarDatosIniciales();
        
        console.log('✅ Aplicación de gestión de usuarios iniciada correctamente');
    }

    // ==================== CONFIGURACIÓN DE EVENTOS ====================
    function setupEventListeners() {
        // Búsqueda en tiempo real
        searchUsuarios?.addEventListener('input', debounce(cargarUsuarios, 500));
        
        // Aplicar filtros
        btnAplicarFiltros?.addEventListener('click', cargarUsuarios);
        filterEstado?.addEventListener('change', cargarUsuarios);
        filterRol?.addEventListener('change', cargarUsuarios);
        
        // Paginación
        btnAnterior?.addEventListener('click', () => cambiarPagina(paginaActual - 1));
        btnSiguiente?.addEventListener('click', () => cambiarPagina(paginaActual + 1));
        btnAnteriorMobile?.addEventListener('click', () => cambiarPagina(paginaActual - 1));
        btnSiguienteMobile?.addEventListener('click', () => cambiarPagina(paginaActual + 1));
        
        // Botones principales
        btnNuevoUsuario?.addEventListener('click', abrirModalNuevoUsuario);
        btnExportarUsuarios?.addEventListener('click', exportarUsuarios);
        btnImportarUsuarios?.addEventListener('click', abrirModalImportarUsuarios);
        
        // Pestañas
        tabUsuarios?.addEventListener('click', () => cambiarTab('usuarios'));
        tabRoles?.addEventListener('click', () => cambiarTab('roles'));
        tabPermisos?.addEventListener('click', () => cambiarTab('permisos'));
        tabAuditoria?.addEventListener('click', () => cambiarTab('auditoria'));
        
        // Teclas de atajo
        document.addEventListener('keydown', manejarTeclasAtajo);
    }

    // ==================== CARGA DE DATOS ====================
    async function cargarDatosIniciales() {
        try {
            await Promise.all([
                cargarEstadisticas(),
                cargarUsuarios(),
                cargarRoles()
            ]);
        } catch (error) {
            console.error('Error al cargar datos iniciales:', error);
            mostrarNotificacion('Error al cargar datos iniciales', 'error');
        }
    }    async function cargarUsuarios() {
        try {
            console.log('🔄 === INICIO CARGA USUARIOS ===');
            console.log('🔍 Token en localStorage:', localStorage.getItem('access_token') ? 'SÍ' : 'NO');
            
            mostrarCargando();
            
            // Construir parámetros de consulta
            const params = new URLSearchParams();
            const busqueda = searchUsuarios?.value?.trim();
            const estado = filterEstado?.value;
            const rol = filterRol?.value;
            
            if (busqueda) params.append('search', busqueda);
            if (estado) params.append('activo', estado);
            if (rol) params.append('rol', rol);
            
            console.log('🔄 Cargando usuarios con parámetros:', params.toString());
            console.log('🌐 URL completa:', `/usuarios_admin/usuarios-con-detalles/?${params.toString()}`);
            
            const response = await fetch(`/usuarios_admin/usuarios-con-detalles/?${params.toString()}`);
            
            console.log('📡 Status de respuesta:', response.status);
            console.log('📡 Headers de respuesta:', Object.fromEntries(response.headers));
            
            if (!response.ok) {
                const errorText = await response.text();
                console.log('❌ Error de respuesta:', errorText);
                throw new Error(`Error ${response.status}: ${response.statusText} - ${errorText}`);
            }
            
            usuarios = await response.json();
            console.log('✅ Usuarios cargados:', usuarios.length);
            console.log('📋 Primeros usuarios:', usuarios.slice(0, 2));
            
            renderizarUsuarios();
            actualizarPaginacion();
              } catch (error) {
            console.error('❌ Error al cargar usuarios:', error);
            mostrarNotificacion('Error al cargar usuarios: ' + error.message, 'error');
            mostrarErrorCarga();
        }
        console.log('🔚 === FIN CARGA USUARIOS ===');
    }
    }

    async function cargarEstadisticas() {
        try {
            const response = await fetch('/usuarios_admin/estadisticas-avanzadas/');
            
            if (!response.ok) {
                throw new Error(`Error ${response.status}: ${response.statusText}`);
            }
            
            const estadisticas = await response.json();
            console.log('📊 Estadísticas cargadas:', estadisticas);
            
            // Actualizar elementos de estadísticas
            if (totalUsersElement) totalUsersElement.textContent = estadisticas.resumen.total_usuarios;
            if (activeUsersElement) activeUsersElement.textContent = estadisticas.resumen.usuarios_activos;
            if (adminUsersElement) adminUsersElement.textContent = estadisticas.por_roles.admin || 0;
            if (totalRolesElement) totalRolesElement.textContent = Object.keys(estadisticas.por_roles).length;
            
        } catch (error) {
            console.error('❌ Error al cargar estadísticas:', error);
            // Valores por defecto en caso de error
            if (totalUsersElement) totalUsersElement.textContent = '0';
            if (activeUsersElement) activeUsersElement.textContent = '0';
            if (adminUsersElement) adminUsersElement.textContent = '0';
            if (totalRolesElement) totalRolesElement.textContent = '0';
        }
    }

    async function cargarRoles() {
        try {
            const response = await fetch('/usuarios_admin/roles/');
            
            if (!response.ok) {
                throw new Error(`Error ${response.status}: ${response.statusText}`);
            }
            
            roles = await response.json();
            console.log('🏷️ Roles cargados:', roles.length);
            
        } catch (error) {
            console.error('❌ Error al cargar roles:', error);
            roles = []; // Array vacío por defecto
        }
    }

    // ==================== RENDERIZADO DE USUARIOS ====================
    function renderizarUsuarios() {
        if (!usuariosTableBody) return;
        
        if (usuarios.length === 0) {
            mostrarMensajeVacio();
            return;
        }
        
        // Calcular paginación
        const inicio = (paginaActual - 1) * usuariosPorPagina;
        const fin = Math.min(inicio + usuariosPorPagina, usuarios.length);
        const usuariosPaginados = usuarios.slice(inicio, fin);
        
        // Actualizar información de paginación
        if (startRange) startRange.textContent = inicio + 1;
        if (endRange) endRange.textContent = fin;
        if (totalUsuarios) totalUsuarios.textContent = usuarios.length;
        
        // Generar HTML de usuarios
        const html = usuariosPaginados.map(usuario => generarFilaUsuario(usuario)).join('');
        usuariosTableBody.innerHTML = html;
        
        // Configurar eventos de la tabla
        configurarEventosTabla();
    }

    function generarFilaUsuario(usuario) {
        const estadoClass = usuario.activo ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800';
        const estadoTexto = usuario.activo ? 'Activo' : 'Inactivo';
        const avatarUrl = usuario.avatar || `https://ui-avatars.com/api/?name=${encodeURIComponent(usuario.nombre || usuario.usuario)}&background=random`;
        const roles = Array.isArray(usuario.roles) ? usuario.roles.join(', ') : 'Usuario';
        const ultimoAcceso = usuario.ultimo_acceso ? 
            new Date(usuario.ultimo_acceso).toLocaleDateString('es-ES') : 'Nunca';
        
        return `
            <tr class="hover:bg-gray-50 transition-colors duration-200">
                <td class="px-6 py-4 whitespace-nowrap">
                    <input type="checkbox" class="user-checkbox rounded border-gray-300" 
                           data-user-id="${usuario.id}">
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                    <div class="flex items-center">
                        <div class="flex-shrink-0 h-10 w-10">
                            <img class="h-10 w-10 rounded-full object-cover" 
                                 src="${avatarUrl}" 
                                 alt="${usuario.nombre || usuario.usuario}"
                                 onerror="this.src='https://ui-avatars.com/api/?name=${encodeURIComponent(usuario.usuario)}&background=6366f1&color=ffffff'">
                        </div>
                        <div class="ml-4">
                            <div class="text-sm font-medium text-gray-900">${usuario.usuario}</div>
                            <div class="text-sm text-gray-500">ID: ${usuario.id}</div>
                        </div>
                    </div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                    <div class="text-sm text-gray-900">${usuario.nombre || '-'}</div>
                    <div class="text-sm text-gray-500">${usuario.email || '-'}</div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                    <div class="text-sm text-gray-900">${roles}</div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                    <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${estadoClass}">
                        ${estadoTexto}
                    </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    ${ultimoAcceso}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <div class="flex space-x-2">
                        <button onclick="verDetallesUsuario(${usuario.id})" 
                                class="text-blue-600 hover:text-blue-900 p-1 rounded"
                                title="Ver detalles">
                            <i class="fas fa-eye"></i>
                        </button>
                        <button onclick="editarUsuario(${usuario.id})" 
                                class="text-green-600 hover:text-green-900 p-1 rounded"
                                title="Editar usuario">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button onclick="cambiarPasswordUsuario(${usuario.id})" 
                                class="text-orange-600 hover:text-orange-900 p-1 rounded"
                                title="Cambiar contraseña">
                            <i class="fas fa-key"></i>
                        </button>
                        <button onclick="toggleUsuarioEstado(${usuario.id}, ${!usuario.activo})" 
                                class="text-yellow-600 hover:text-yellow-900 p-1 rounded"
                                title="${usuario.activo ? 'Desactivar' : 'Activar'} usuario">
                            <i class="fas fa-toggle-${usuario.activo ? 'on' : 'off'}"></i>
                        </button>
                        <button onclick="eliminarUsuario(${usuario.id}, '${usuario.nombre || usuario.usuario}')" 
                                class="text-red-600 hover:text-red-900 p-1 rounded"
                                title="Eliminar usuario">
                            <i class="fas fa-trash-alt"></i>
                        </button>
                    </div>
                </td>
            </tr>
        `;
    }

    function configurarEventosTabla() {
        // Configurar checkbox de seleccionar todos
        const selectAll = document.getElementById('selectAll');
        if (selectAll) {
            selectAll.addEventListener('change', function() {
                const checkboxes = document.querySelectorAll('.user-checkbox');
                checkboxes.forEach(checkbox => {
                    checkbox.checked = this.checked;
                });
                actualizarBarraAcciones();
            });
        }
        
        // Configurar checkboxes individuales
        const userCheckboxes = document.querySelectorAll('.user-checkbox');
        userCheckboxes.forEach(checkbox => {
            checkbox.addEventListener('change', actualizarBarraAcciones);
        });
    }

    // ==================== FUNCIONES DE USUARIO ====================
    window.verDetallesUsuario = async function(userId) {
        try {
            const response = await fetch(`/usuarios_admin/usuarios/${userId}`);
            
            if (!response.ok) {
                throw new Error(`Error ${response.status}: ${response.statusText}`);
            }
            
            const usuario = await response.json();
            abrirModalDetallesUsuario(usuario);
            
        } catch (error) {
            console.error('Error al obtener detalles del usuario:', error);
            mostrarNotificacion('Error al cargar detalles del usuario', 'error');
        }
    };

    window.editarUsuario = async function(userId) {
        try {
            const response = await fetch(`/usuarios_admin/usuarios/${userId}`);
            
            if (!response.ok) {
                throw new Error(`Error ${response.status}: ${response.statusText}`);
            }
            
            const usuario = await response.json();
            abrirModalEditarUsuario(usuario);
            
        } catch (error) {
            console.error('Error al cargar usuario para editar:', error);
            mostrarNotificacion('Error al cargar usuario para editar', 'error');
        }
    };

    window.cambiarPasswordUsuario = function(userId) {
        abrirModalCambiarPassword(userId);
    };

    window.toggleUsuarioEstado = async function(userId, nuevoEstado) {
        try {
            const response = await fetch(`/usuarios_admin/usuarios/${userId}/toggle-status`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            if (!response.ok) {
                throw new Error(`Error ${response.status}: ${response.statusText}`);
            }
            
            const resultado = await response.json();
            mostrarNotificacion(resultado.message, 'success');
            await cargarUsuarios();
            
        } catch (error) {
            console.error('Error al cambiar estado del usuario:', error);
            mostrarNotificacion('Error al cambiar estado del usuario: ' + error.message, 'error');
        }
    };

    window.eliminarUsuario = function(userId, nombreUsuario) {
        abrirModalConfirmarEliminar(userId, nombreUsuario);
    };

    // ==================== MODALES ====================
    function abrirModalNuevoUsuario() {
        // Implementar modal de nuevo usuario
        console.log('Abriendo modal de nuevo usuario...');
        // TODO: Implementar
    }

    function abrirModalEditarUsuario(usuario) {
        // Implementar modal de edición
        console.log('Abriendo modal de edición para:', usuario);
        // TODO: Implementar
    }

    function abrirModalDetallesUsuario(usuario) {
        // Implementar modal de detalles
        console.log('Abriendo modal de detalles para:', usuario);
        // TODO: Implementar
    }

    function abrirModalCambiarPassword(userId) {
        // Implementar modal de cambio de contraseña
        console.log('Abriendo modal de cambio de contraseña para:', userId);
        // TODO: Implementar
    }

    function abrirModalConfirmarEliminar(userId, nombreUsuario) {
        // Implementar modal de confirmación de eliminación
        console.log('Abriendo modal de confirmación para eliminar:', nombreUsuario);
        // TODO: Implementar
    }

    function abrirModalImportarUsuarios() {
        // Implementar modal de importación
        console.log('Abriendo modal de importación de usuarios...');
        // TODO: Implementar
    }

    // ==================== FUNCIONES DE UTILIDAD ====================
    function mostrarCargando() {
        if (usuariosTableBody) {
            usuariosTableBody.innerHTML = `
                <tr class="animate-pulse">
                    <td colspan="7" class="px-6 py-4 text-center text-gray-500">
                        <i class="fas fa-spinner fa-spin mr-2"></i>
                        Cargando usuarios...
                    </td>
                </tr>
            `;
        }
    }

    function mostrarMensajeVacio() {
        if (usuariosTableBody) {
            usuariosTableBody.innerHTML = `
                <tr>
                    <td colspan="7" class="px-6 py-4 text-center text-gray-500">
                        <i class="fas fa-users text-4xl mb-2 opacity-50"></i>
                        <div>No se encontraron usuarios</div>
                        <div class="text-sm text-gray-400">Prueba ajustando los filtros de búsqueda</div>
                    </td>
                </tr>
            `;
        }
    }

    function mostrarErrorCarga() {
        if (usuariosTableBody) {
            usuariosTableBody.innerHTML = `
                <tr>
                    <td colspan="7" class="px-6 py-4 text-center text-red-500">
                        <i class="fas fa-exclamation-triangle text-4xl mb-2"></i>
                        <div>Error al cargar usuarios</div>
                        <button onclick="cargarUsuarios()" class="mt-2 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">
                            Reintentar
                        </button>
                    </td>
                </tr>
            `;
        }
    }

    function actualizarPaginacion() {
        totalPaginas = Math.ceil(usuarios.length / usuariosPorPagina);
        
        // Actualizar botones de navegación
        if (btnAnterior) {
            btnAnterior.disabled = paginaActual <= 1;
            btnAnterior.classList.toggle('opacity-50', paginaActual <= 1);
        }
        
        if (btnSiguiente) {
            btnSiguiente.disabled = paginaActual >= totalPaginas;
            btnSiguiente.classList.toggle('opacity-50', paginaActual >= totalPaginas);
        }
        
        if (btnAnteriorMobile) {
            btnAnteriorMobile.disabled = paginaActual <= 1;
            btnAnteriorMobile.classList.toggle('opacity-50', paginaActual <= 1);
        }
        
        if (btnSiguienteMobile) {
            btnSiguienteMobile.disabled = paginaActual >= totalPaginas;
            btnSiguienteMobile.classList.toggle('opacity-50', paginaActual >= totalPaginas);
        }
        
        // Generar números de página
        generarNumerosPagina();
    }

    function generarNumerosPagina() {
        if (!paginationNumbers) return;
        
        let html = '';
        const maxPagesToShow = 5;
        let startPage = Math.max(1, paginaActual - Math.floor(maxPagesToShow / 2));
        let endPage = Math.min(totalPaginas, startPage + maxPagesToShow - 1);
        
        if (endPage - startPage + 1 < maxPagesToShow && startPage > 1) {
            startPage = Math.max(1, endPage - maxPagesToShow + 1);
        }
        
        // Primera página
        if (startPage > 1) {
            html += generarBotonPagina(1);
            if (startPage > 2) {
                html += '<span class="px-3 py-2 text-gray-500">...</span>';
            }
        }
        
        // Páginas numeradas
        for (let i = startPage; i <= endPage; i++) {
            html += generarBotonPagina(i, i === paginaActual);
        }
        
        // Última página
        if (endPage < totalPaginas) {
            if (endPage < totalPaginas - 1) {
                html += '<span class="px-3 py-2 text-gray-500">...</span>';
            }
            html += generarBotonPagina(totalPaginas);
        }
        
        paginationNumbers.innerHTML = html;
        
        // Configurar eventos de los botones de página
        paginationNumbers.querySelectorAll('.page-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                const page = parseInt(this.dataset.page);
                cambiarPagina(page);
            });
        });
    }

    function generarBotonPagina(numero, activo = false) {
        const activeClass = activo 
            ? 'bg-blue-50 border-blue-500 text-blue-600 z-10' 
            : 'bg-white border-gray-300 text-gray-500 hover:bg-gray-50';
            
        return `
            <button data-page="${numero}" 
                    class="page-btn relative inline-flex items-center px-4 py-2 border ${activeClass} text-sm font-medium transition-colors duration-200">
                ${numero}
            </button>
        `;
    }

    function cambiarPagina(nuevaPagina) {
        if (nuevaPagina >= 1 && nuevaPagina <= totalPaginas && nuevaPagina !== paginaActual) {
            paginaActual = nuevaPagina;
            renderizarUsuarios();
            actualizarPaginacion();
        }
    }

    function cambiarTab(tab) {
        // Actualizar estado de pestañas
        document.querySelectorAll('.tab-button').forEach(btn => {
            btn.classList.remove('active', 'border-blue-500', 'text-blue-600');
            btn.classList.add('border-transparent', 'text-gray-500');
        });
        
        // Ocultar todo el contenido
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.add('hidden');
        });
        
        // Mostrar contenido de la pestaña activa
        const tabButton = document.getElementById(`tab-${tab}`);
        const tabContent = document.getElementById(`content-${tab}`);
        
        if (tabButton) {
            tabButton.classList.add('active', 'border-blue-500', 'text-blue-600');
            tabButton.classList.remove('border-transparent', 'text-gray-500');
        }
        
        if (tabContent) {
            tabContent.classList.remove('hidden');
        }
        
        tabActual = tab;
        
        // Cargar datos específicos de la pestaña si es necesario
        switch (tab) {
            case 'roles':
                cargarGestionRoles();
                break;
            case 'permisos':
                cargarGestionPermisos();
                break;
            case 'auditoria':
                cargarAuditoria();
                break;
        }
    }

    function cargarGestionRoles() {
        console.log('Cargando gestión de roles...');
        // TODO: Implementar
    }

    function cargarGestionPermisos() {
        console.log('Cargando gestión de permisos...');
        // TODO: Implementar
    }

    function cargarAuditoria() {
        console.log('Cargando auditoría...');
        // TODO: Implementar
    }

    function actualizarBarraAcciones() {
        const selectedCheckboxes = document.querySelectorAll('.user-checkbox:checked');
        console.log(`${selectedCheckboxes.length} usuarios seleccionados`);
        // TODO: Mostrar/ocultar barra de acciones masivas
    }

    function exportarUsuarios() {
        console.log('Exportando usuarios...');
        // TODO: Implementar exportación
    }

    function manejarTeclasAtajo(event) {
        // Atajo Ctrl+N para nuevo usuario
        if (event.ctrlKey && event.key === 'n') {
            event.preventDefault();
            abrirModalNuevoUsuario();
        }
        
        // Atajo F5 para recargar datos
        if (event.key === 'F5') {
            event.preventDefault();
            cargarDatosIniciales();
        }
    }

    function mostrarNotificacion(mensaje, tipo = 'info') {
        // Crear elemento de notificación
        const notification = document.createElement('div');
        notification.className = `fixed top-4 right-4 z-50 p-4 rounded-lg shadow-lg max-w-sm transition-all duration-300 transform translate-x-full`;
        
        // Configurar colores según el tipo
        const colores = {
            success: 'bg-green-500 text-white',
            error: 'bg-red-500 text-white',
            warning: 'bg-yellow-500 text-white',
            info: 'bg-blue-500 text-white'
        };
        
        const iconos = {
            success: 'fas fa-check-circle',
            error: 'fas fa-times-circle',
            warning: 'fas fa-exclamation-triangle',
            info: 'fas fa-info-circle'
        };
        
        notification.className += ` ${colores[tipo] || colores.info}`;
        
        notification.innerHTML = `
            <div class="flex items-center">
                <i class="${iconos[tipo] || iconos.info} mr-2"></i>
                <span>${mensaje}</span>
                <button onclick="this.parentElement.parentElement.remove()" class="ml-4 text-white hover:text-gray-200">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        // Animación de entrada
        setTimeout(() => {
            notification.classList.remove('translate-x-full');
        }, 100);
        
        // Auto-remover después de 5 segundos
        setTimeout(() => {
            if (notification.parentElement) {
                notification.classList.add('translate-x-full');
                setTimeout(() => {
                    if (notification.parentElement) {
                        notification.remove();
                    }
                }, 300);
            }
        }, 5000);
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

    // ==================== EXPORTAR FUNCIONES GLOBALES ====================
    window.usuariosAdmin = {
        cargarUsuarios,
        cargarEstadisticas,
        cambiarTab,
        mostrarNotificacion
    };
});
