/**
 * Script avanzado de gestión de usuarios - Panel de administración
 * Versión mejorada con todas las funcionalidades del backend
 */

document.addEventListener('DOMContentLoaded', function() {
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

    // Inicializar token al inicio
    if (!initializeToken()) {
        return; // Detener la ejecución si no hay token
    }

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

    // ==================== FUNCIONES PRINCIPALES ====================
    
    async function cargarUsuarios() {
        try {
            console.log('🔄 === INICIO CARGA USUARIOS ===');
            console.log('🔍 Token en localStorage:', localStorage.getItem('access_token') ? 'SÍ' : 'NO');
            
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

    function renderizarUsuarios() {
        if (!usuariosTableBody) {
            console.error('❌ No se encontró el contenedor de la tabla de usuarios');
            return;
        }

        const inicio = (paginaActual - 1) * usuariosPorPagina;
        const fin = inicio + usuariosPorPagina;
        const usuariosPagina = usuarios.slice(inicio, fin);

        if (usuariosPagina.length === 0) {
            usuariosTableBody.innerHTML = `
                <tr>
                    <td colspan="6" class="px-6 py-8 text-center text-gray-500">
                        <i class="fas fa-users text-4xl mb-4 text-gray-300"></i>
                        <p class="text-lg">No se encontraron usuarios</p>
                        <p class="text-sm">Intenta ajustar los filtros de búsqueda</p>
                    </td>
                </tr>
            `;
            return;
        }

        usuariosTableBody.innerHTML = usuariosPagina.map(usuario => `
            <tr class="hover:bg-gray-50 transition-colors duration-200">
                <td class="px-6 py-4 whitespace-nowrap">
                    <div class="flex items-center">
                        <img class="h-10 w-10 rounded-full" src="${usuario.avatar || 'https://ui-avatars.com/api/?name=' + encodeURIComponent(usuario.nombre || usuario.usuario) + '&background=667eea&color=fff'}" alt="">
                        <div class="ml-4">
                            <div class="text-sm font-medium text-gray-900">${usuario.nombre || usuario.usuario}</div>
                            <div class="text-sm text-gray-500">@${usuario.usuario}</div>
                        </div>
                    </div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                    <div class="text-sm text-gray-900">${usuario.email || 'Sin email'}</div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                    <div class="flex flex-wrap gap-1">
                        ${(usuario.roles || ['usuario']).map(rol => `
                            <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                                ${rol}
                            </span>
                        `).join('')}
                    </div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                    <span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${usuario.activo ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}">
                        <span class="w-1.5 h-1.5 mr-1.5 rounded-full ${usuario.activo ? 'bg-green-400' : 'bg-red-400'}"></span>
                        ${usuario.activo ? 'Activo' : 'Inactivo'}
                    </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    ${usuario.fecha_creacion ? new Date(usuario.fecha_creacion).toLocaleDateString() : 'Sin fecha'}
                </td>                <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <div class="flex space-x-2 justify-end">
                        <button onclick="verDetallesUsuario(${usuario.id})" class="text-blue-600 hover:text-blue-900 transition-colors duration-200" title="Ver detalles">
                            <i class="fas fa-eye"></i>
                        </button>
                        <button onclick="editarUsuario(${usuario.id})" class="text-yellow-600 hover:text-yellow-900 transition-colors duration-200" title="Editar">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button onclick="resetearPassword(${usuario.id})" class="text-purple-600 hover:text-purple-900 transition-colors duration-200" title="Resetear contraseña">
                            <i class="fas fa-key"></i>
                        </button>
                        <button onclick="toggleUsuarioStatus(${usuario.id})" class="text-${usuario.activo ? 'red' : 'green'}-600 hover:text-${usuario.activo ? 'red' : 'green'}-900 transition-colors duration-200" title="${usuario.activo ? 'Desactivar' : 'Activar'}">
                            <i class="fas fa-${usuario.activo ? 'user-slash' : 'user-check'}"></i>
                        </button>
                        <button onclick="eliminarUsuario(${usuario.id})" class="text-red-600 hover:text-red-900 transition-colors duration-200" title="Eliminar">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </td>
            </tr>
        `).join('');
    }

    function actualizarPaginacion() {
        totalPaginas = Math.ceil(usuarios.length / usuariosPorPagina);
        
        // Actualizar información de rango
        if (startRange) {
            const inicio = usuarios.length > 0 ? (paginaActual - 1) * usuariosPorPagina + 1 : 0;
            startRange.textContent = inicio;
        }
        if (endRange) {
            const fin = Math.min(paginaActual * usuariosPorPagina, usuarios.length);
            endRange.textContent = fin;
        }
        if (totalUsuarios) {
            totalUsuarios.textContent = usuarios.length;
        }
    }

    function mostrarErrorCarga() {
        if (usuariosTableBody) {
            usuariosTableBody.innerHTML = `
                <tr>
                    <td colspan="6" class="px-6 py-8 text-center text-red-500">
                        <i class="fas fa-exclamation-triangle text-4xl mb-4"></i>
                        <p class="text-lg">Error al cargar usuarios</p>
                        <button onclick="cargarUsuarios()" class="mt-2 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">
                            Reintentar
                        </button>
                    </td>
                </tr>
            `;
        }
    }    function mostrarNotificacion(mensaje, tipo = 'info') {
        // Crear contenedor de notificaciones si no existe
        let contenedor = document.getElementById('notificaciones');
        if (!contenedor) {
            contenedor = document.createElement('div');
            contenedor.id = 'notificaciones';
            contenedor.className = 'fixed top-4 right-4 z-50 space-y-2';
            document.body.appendChild(contenedor);
        }
        
        const tipos = {
            success: 'bg-green-500',
            error: 'bg-red-500',
            warning: 'bg-yellow-500',
            info: 'bg-blue-500'
        };
        
        const iconos = {
            success: 'fas fa-check-circle',
            error: 'fas fa-exclamation-circle',
            warning: 'fas fa-exclamation-triangle',
            info: 'fas fa-info-circle'
        };
        
        const notificacion = document.createElement('div');
        notificacion.className = `transform transition-all duration-300 translate-x-full`;
        notificacion.innerHTML = `
            <div class="${tipos[tipo] || tipos.info} text-white px-6 py-4 rounded-lg shadow-lg max-w-sm">
                <div class="flex items-center">
                    <i class="${iconos[tipo] || iconos.info} mr-3"></i>
                    <span class="flex-1">${mensaje}</span>
                    <button onclick="this.parentElement.parentElement.parentElement.remove()" class="ml-3 text-white hover:text-gray-200">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
            </div>
        `;
        
        contenedor.appendChild(notificacion);
        
        // Animación de entrada
        setTimeout(() => {
            notificacion.classList.remove('translate-x-full');
        }, 100);
        
        // Auto-remover después de 5 segundos
        setTimeout(() => {
            if (notificacion.parentElement) {
                notificacion.classList.add('translate-x-full');
                setTimeout(() => {
                    if (notificacion.parentElement) {
                        notificacion.remove();
                    }
                }, 300);
            }
        }, 5000);
    }

    // ==================== EVENT LISTENERS ====================
    function setupEventListeners() {
        // Botón nuevo usuario
        const btnNuevoUsuario = document.getElementById('btnNuevoUsuario');
        if (btnNuevoUsuario) {
            btnNuevoUsuario.addEventListener('click', crearNuevoUsuario);
        }
        
        // Búsqueda en tiempo real
        const searchUsuarios = document.getElementById('searchUsuarios');
        if (searchUsuarios) {
            searchUsuarios.addEventListener('input', debounce(cargarUsuarios, 500));
        }
        
        // Filtros
        const filterEstado = document.getElementById('filterEstado');
        const filterRol = document.getElementById('filterRol');
        const btnAplicarFiltros = document.getElementById('btnAplicarFiltros');
        
        if (filterEstado) {
            filterEstado.addEventListener('change', cargarUsuarios);
        }
        if (filterRol) {
            filterRol.addEventListener('change', cargarUsuarios);
        }
        if (btnAplicarFiltros) {
            btnAplicarFiltros.addEventListener('click', cargarUsuarios);
        }
        
        // Exportar e importar (placeholder)
        const btnExportarUsuarios = document.getElementById('btnExportarUsuarios');
        const btnImportarUsuarios = document.getElementById('btnImportarUsuarios');
        
        if (btnExportarUsuarios) {
            btnExportarUsuarios.addEventListener('click', () => {
                mostrarNotificacion('Funcionalidad de exportar en desarrollo', 'info');
            });
        }
        if (btnImportarUsuarios) {
            btnImportarUsuarios.addEventListener('click', () => {
                mostrarNotificacion('Funcionalidad de importar en desarrollo', 'info');
            });
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
    }// ==================== FUNCIONES GLOBALES PARA HTML ====================
    window.cargarUsuarios = cargarUsuarios;
    
    window.verDetallesUsuario = async function(userId) {
        try {
            console.log('Ver detalles del usuario:', userId);
            const response = await fetch(`/usuarios_admin/usuarios/${userId}`);
            
            if (!response.ok) {
                throw new Error(`Error ${response.status}: ${response.statusText}`);
            }
            
            const usuario = await response.json();
            mostrarModalDetalles(usuario);
            
        } catch (error) {
            console.error('Error al obtener detalles del usuario:', error);
            mostrarNotificacion('Error al cargar detalles del usuario', 'error');
        }
    };
    
    window.editarUsuario = async function(userId) {
        try {
            console.log('Editar usuario:', userId);
            const response = await fetch(`/usuarios_admin/usuarios/${userId}`);
            
            if (!response.ok) {
                throw new Error(`Error ${response.status}: ${response.statusText}`);
            }
            
            const usuario = await response.json();
            mostrarModalEdicion(usuario);
            
        } catch (error) {
            console.error('Error al cargar usuario para edición:', error);
            mostrarNotificacion('Error al cargar datos del usuario', 'error');
        }
    };
    
    window.toggleUsuarioStatus = async function(userId) {
        try {
            console.log('Toggle status del usuario:', userId);
            
            if (!confirm('¿Estás seguro de que quieres cambiar el estado de este usuario?')) {
                return;
            }
            
            const response = await fetch(`/usuarios_admin/usuarios/${userId}/toggle-status`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            if (!response.ok) {
                throw new Error(`Error ${response.status}: ${response.statusText}`);
            }
            
            const result = await response.json();
            mostrarNotificacion(result.message || 'Estado cambiado exitosamente', 'success');
            
            // Recargar usuarios para reflejar el cambio
            await cargarUsuarios();
            
        } catch (error) {
            console.error('Error al cambiar estado del usuario:', error);
            mostrarNotificacion('Error al cambiar estado del usuario', 'error');
        }
    };
    
    window.eliminarUsuario = async function(userId) {
        try {
            console.log('Eliminar usuario:', userId);
            
            if (!confirm('¿Estás seguro de que quieres eliminar este usuario? Esta acción no se puede deshacer.')) {
                return;
            }
            
            const response = await fetch(`/usuarios_admin/usuarios/${userId}`, {
                method: 'DELETE'
            });
            
            if (!response.ok) {
                throw new Error(`Error ${response.status}: ${response.statusText}`);
            }
            
            mostrarNotificacion('Usuario eliminado exitosamente', 'success');
            
            // Recargar usuarios para reflejar el cambio
            await cargarUsuarios();
            
        } catch (error) {
            console.error('Error al eliminar usuario:', error);
            mostrarNotificacion('Error al eliminar usuario', 'error');
        }
    };
    
    window.crearNuevoUsuario = function() {
        mostrarModalNuevoUsuario();
    };
    
    window.resetearPassword = async function(userId) {
        try {
            if (!confirm('¿Estás seguro de que quieres resetear la contraseña de este usuario?')) {
                return;
            }
            
            const response = await fetch(`/usuarios_admin/usuarios/${userId}/resetear-password`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            if (!response.ok) {
                throw new Error(`Error ${response.status}: ${response.statusText}`);
            }
            
            const result = await response.json();
            mostrarNotificacion(`Contraseña reseteada. Nueva contraseña: ${result.nueva_password}`, 'success');
            
        } catch (error) {
            console.error('Error al resetear contraseña:', error);
            mostrarNotificacion('Error al resetear contraseña', 'error');
        }
    };

    // ==================== MODALES Y UI ====================
    
    function mostrarModalDetalles(usuario) {
        const modal = crearModal('Detalles del Usuario', `
            <div class="space-y-4">
                <div class="grid grid-cols-2 gap-4">
                    <div>
                        <label class="block text-sm font-medium text-gray-700">Usuario</label>
                        <p class="text-sm text-gray-900">${usuario.usuario}</p>
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700">Nombre</label>
                        <p class="text-sm text-gray-900">${usuario.nombre || 'Sin nombre'}</p>
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700">Email</label>
                        <p class="text-sm text-gray-900">${usuario.email || 'Sin email'}</p>
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700">Estado</label>
                        <span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${usuario.activo ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}">
                            ${usuario.activo ? 'Activo' : 'Inactivo'}
                        </span>
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700">Fecha de Creación</label>
                        <p class="text-sm text-gray-900">${usuario.fecha_creacion ? new Date(usuario.fecha_creacion).toLocaleString() : 'Sin fecha'}</p>
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700">Último Acceso</label>
                        <p class="text-sm text-gray-900">${usuario.ultimo_acceso ? new Date(usuario.ultimo_acceso).toLocaleString() : 'Nunca'}</p>
                    </div>
                </div>
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Roles</label>
                    <div class="flex flex-wrap gap-1">
                        ${(usuario.roles || ['usuario']).map(rol => `
                            <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                                ${rol}
                            </span>
                        `).join('')}
                    </div>
                </div>
            </div>
        `, [
            {
                text: 'Editar',
                class: 'bg-blue-600 hover:bg-blue-700 text-white',
                onClick: () => {
                    cerrarModal();
                    editarUsuario(usuario.id);
                }
            },
            {
                text: 'Cerrar',
                class: 'bg-gray-300 hover:bg-gray-400 text-gray-700',
                onClick: cerrarModal
            }
        ]);
    }
    
    function mostrarModalEdicion(usuario) {
        const modal = crearModal('Editar Usuario', `
            <form id="formEditarUsuario" class="space-y-4">
                <div class="grid grid-cols-2 gap-4">
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">Usuario</label>
                        <input type="text" id="edit_usuario" value="${usuario.usuario}" 
                            class="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500" readonly>
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">Nombre</label>
                        <input type="text" id="edit_nombre" value="${usuario.nombre || ''}" 
                            class="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500">
                    </div>
                    <div class="col-span-2">
                        <label class="block text-sm font-medium text-gray-700 mb-1">Email</label>
                        <input type="email" id="edit_email" value="${usuario.email || ''}" 
                            class="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500">
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">Estado</label>
                        <select id="edit_activo" class="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500">
                            <option value="true" ${usuario.activo ? 'selected' : ''}>Activo</option>
                            <option value="false" ${!usuario.activo ? 'selected' : ''}>Inactivo</option>
                        </select>
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">Nueva Contraseña (opcional)</label>
                        <input type="password" id="edit_password" placeholder="Dejar vacío para no cambiar" 
                            class="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500">
                    </div>
                </div>
            </form>
        `, [
            {
                text: 'Guardar Cambios',
                class: 'bg-blue-600 hover:bg-blue-700 text-white',
                onClick: () => guardarEdicionUsuario(usuario.id)
            },
            {
                text: 'Cancelar',
                class: 'bg-gray-300 hover:bg-gray-400 text-gray-700',
                onClick: cerrarModal
            }
        ]);
    }
    
    function mostrarModalNuevoUsuario() {
        const modal = crearModal('Crear Nuevo Usuario', `
            <form id="formNuevoUsuario" class="space-y-4">
                <div class="grid grid-cols-2 gap-4">
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">Usuario *</label>
                        <input type="text" id="new_usuario" required 
                            class="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500">
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">Nombre</label>
                        <input type="text" id="new_nombre" 
                            class="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500">
                    </div>
                    <div class="col-span-2">
                        <label class="block text-sm font-medium text-gray-700 mb-1">Email</label>
                        <input type="email" id="new_email" 
                            class="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500">
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">Contraseña *</label>
                        <input type="password" id="new_password" required 
                            class="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500">
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">Estado</label>
                        <select id="new_activo" class="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500">
                            <option value="true">Activo</option>
                            <option value="false">Inactivo</option>
                        </select>
                    </div>
                </div>
            </form>
        `, [
            {
                text: 'Crear Usuario',
                class: 'bg-green-600 hover:bg-green-700 text-white',
                onClick: guardarNuevoUsuario
            },
            {
                text: 'Cancelar',
                class: 'bg-gray-300 hover:bg-gray-400 text-gray-700',
                onClick: cerrarModal
            }
        ]);
    }
    
    async function guardarEdicionUsuario(userId) {
        try {
            const datos = {
                nombre: document.getElementById('edit_nombre').value,
                email: document.getElementById('edit_email').value,
                activo: document.getElementById('edit_activo').value === 'true'
            };
            
            const password = document.getElementById('edit_password').value;
            if (password) {
                datos.password = password;
            }
            
            const response = await fetch(`/usuarios_admin/usuarios/${userId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(datos)
            });
            
            if (!response.ok) {
                const error = await response.text();
                throw new Error(`Error ${response.status}: ${error}`);
            }
            
            const result = await response.json();
            mostrarNotificacion('Usuario actualizado exitosamente', 'success');
            cerrarModal();
            await cargarUsuarios();
            
        } catch (error) {
            console.error('Error al guardar cambios:', error);
            mostrarNotificacion('Error al guardar cambios: ' + error.message, 'error');
        }
    }
    
    async function guardarNuevoUsuario() {
        try {
            const datos = {
                usuario: document.getElementById('new_usuario').value,
                nombre: document.getElementById('new_nombre').value,
                email: document.getElementById('new_email').value,
                password: document.getElementById('new_password').value,
                activo: document.getElementById('new_activo').value === 'true'
            };
            
            if (!datos.usuario || !datos.password) {
                mostrarNotificacion('Usuario y contraseña son obligatorios', 'error');
                return;
            }
            
            const response = await fetch('/usuarios_admin/usuarios/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(datos)
            });
            
            if (!response.ok) {
                const error = await response.text();
                throw new Error(`Error ${response.status}: ${error}`);
            }
            
            const result = await response.json();
            mostrarNotificacion('Usuario creado exitosamente', 'success');
            cerrarModal();
            await cargarUsuarios();
            
        } catch (error) {
            console.error('Error al crear usuario:', error);
            mostrarNotificacion('Error al crear usuario: ' + error.message, 'error');
        }
    }
    
    function crearModal(titulo, contenido, botones = []) {
        // Remover modal existente si lo hay
        const modalExistente = document.getElementById('modal-overlay');
        if (modalExistente) {
            modalExistente.remove();
        }
        
        const modal = document.createElement('div');
        modal.id = 'modal-overlay';
        modal.className = 'fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50';
        modal.innerHTML = `
            <div class="relative top-20 mx-auto p-5 border w-11/12 md:w-3/4 lg:w-1/2 shadow-lg rounded-md bg-white">
                <div class="mt-3">
                    <div class="flex justify-between items-center mb-4">
                        <h3 class="text-lg font-medium text-gray-900">${titulo}</h3>
                        <button onclick="cerrarModal()" class="text-gray-400 hover:text-gray-600">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                    <div class="mt-2 px-7 py-3">
                        ${contenido}
                    </div>
                    <div class="items-center px-4 py-3">
                        <div class="flex space-x-3 justify-end">
                            ${botones.map(boton => `
                                <button class="px-4 py-2 rounded-md text-sm font-medium ${boton.class}" 
                                    onclick="(${boton.onClick.toString()})()">${boton.text}</button>
                            `).join('')}
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        return modal;
    }
    
    window.cerrarModal = function() {
        const modal = document.getElementById('modal-overlay');
        if (modal) {
            modal.remove();
        }
    };    // ==================== INICIALIZACIÓN ====================
    console.log('🚀 Iniciando aplicación de gestión de usuarios...');
    
    // Configurar event listeners
    setupEventListeners();
    
    // Cargar datos iniciales
    cargarUsuarios();
    
    console.log('✅ Aplicación de gestión de usuarios iniciada correctamente');
});
