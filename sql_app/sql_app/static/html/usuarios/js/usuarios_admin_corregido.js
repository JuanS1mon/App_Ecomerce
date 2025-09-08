/**
 * Script avanzado de gestión de usuarios - Panel de administración
 * Versión mejorada con todas las funcionalidades del backend
 */

// ==================== VARIABLES GLOBALES ====================
let usuarios = [];
let roles = [];
let paginaActual = 1;
let usuariosPorPagina = 10;
let usuarioIdActual = null;
let totalPaginas = 0;
let tabActual = 'usuarios';
let authToken = null; // Token de autenticación para las API calls

// ==================== FUNCIONES GLOBALES ====================

function initializeToken() {
    // Extraer token de la URL para usarlo en las API calls
    const urlParams = new URLSearchParams(window.location.search);
    const tokenFromUrl = urlParams.get('token');
    
    if (tokenFromUrl) {
        authToken = tokenFromUrl;
        console.log('🔐 Token extraído de URL para API calls');
        
        // Opcional: limpiar la URL para que no se vea el token (comentado para debugging)
        // const cleanUrl = window.location.origin + window.location.pathname;
        // window.history.replaceState({}, document.title, cleanUrl);
    } else {
        console.log('⚠️ No se encontró token en URL');
    }
    
    console.log('✅ Frontend inicializado - token guardado para API calls');
    return true;
}

// Función helper para construir URLs con token de autenticación
function buildAuthUrl(baseUrl) {
    if (!authToken) {
        console.warn('⚠️ No hay token disponible para la llamada a:', baseUrl);
        return baseUrl;
    }
    
    const separator = baseUrl.includes('?') ? '&' : '?';
    const urlWithToken = `${baseUrl}${separator}token=${authToken}`;
    console.log('🔐 URL con token construida:', baseUrl, '-> [URL con token]');
    return urlWithToken;
}

async function cargarUsuarios() {
    try {
        console.log('🔄 === INICIO CARGA USUARIOS ===');
        console.log('🔍 Cargando usuarios sin token (backend maneja autenticación)');
        
        // Construir parámetros de consulta
        const params = new URLSearchParams();
        const searchUsuarios = document.getElementById('searchUsuarios');
        const filterEstado = document.getElementById('filterEstado');
        const filterRol = document.getElementById('filterRol');
        
        const busqueda = searchUsuarios?.value?.trim();
        const estado = filterEstado?.value;
        const rol = filterRol?.value;
        
        if (busqueda) params.append('search', busqueda);
        if (estado) params.append('activo', estado);
        if (rol) params.append('rol', rol);
          console.log('🔄 Cargando usuarios con parámetros:', params.toString());
        
        const baseUrl = `/usuarios_admin/usuarios-con-detalles/?${params.toString()}`;
        const urlWithAuth = buildAuthUrl(baseUrl);
        console.log('🌐 URL completa con auth:', '[URL protegida]');
        
        const response = await fetch(urlWithAuth);
        
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
    const usuariosTableBody = document.getElementById('users-table-body');
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
                <td colspan="7" class="px-6 py-8 text-center text-gray-500">
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
                <input type="checkbox" value="${usuario.id}" class="rounded border-gray-300 user-checkbox">
            </td>
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
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                <div class="flex space-x-2 justify-end">
                    <button class="text-blue-600 hover:text-blue-900 transition-colors duration-200 btn-ver-detalles" data-user-id="${usuario.id}" title="Ver detalles">
                        <i class="fas fa-eye"></i>
                    </button>
                    <button class="text-yellow-600 hover:text-yellow-900 transition-colors duration-200 btn-editar" data-user-id="${usuario.id}" title="Editar">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="text-purple-600 hover:text-purple-900 transition-colors duration-200 btn-resetear-password" data-user-id="${usuario.id}" title="Resetear contraseña">
                        <i class="fas fa-key"></i>
                    </button>
                    <button class="text-${usuario.activo ? 'red' : 'green'}-600 hover:text-${usuario.activo ? 'red' : 'green'}-900 transition-colors duration-200 btn-toggle-status" data-user-id="${usuario.id}" title="${usuario.activo ? 'Desactivar' : 'Activar'}">
                        <i class="fas fa-${usuario.activo ? 'user-slash' : 'user-check'}"></i>
                    </button>
                    <button class="text-red-600 hover:text-red-900 transition-colors duration-200 btn-eliminar" data-user-id="${usuario.id}" title="Eliminar">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </td>
        </tr>
    `).join('');
    
    // Configurar event listeners para los botones de acción
    configurarEventosTabla();
}

function configurarEventosTabla() {
    // Botones de ver detalles
    document.querySelectorAll('.btn-ver-detalles').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const userId = e.currentTarget.getAttribute('data-user-id');
            verDetallesUsuario(parseInt(userId));
        });
    });

    // Botones de editar
    document.querySelectorAll('.btn-editar').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const userId = e.currentTarget.getAttribute('data-user-id');
            editarUsuario(parseInt(userId));
        });
    });

    // Botones de resetear contraseña
    document.querySelectorAll('.btn-resetear-password').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const userId = e.currentTarget.getAttribute('data-user-id');
            resetearPassword(parseInt(userId));
        });
    });

    // Botones de toggle status
    document.querySelectorAll('.btn-toggle-status').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const userId = e.currentTarget.getAttribute('data-user-id');
            toggleUsuarioStatus(parseInt(userId));
        });
    });

    // Botones de eliminar
    document.querySelectorAll('.btn-eliminar').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const userId = e.currentTarget.getAttribute('data-user-id');
            eliminarUsuario(parseInt(userId));
        });
    });
}

async function verDetallesUsuario(userId) {
    try {
        console.log('Ver detalles del usuario:', userId);
        const url = buildAuthUrl(`/usuarios_admin/usuarios/${userId}`);
        const response = await fetch(url);
        
        if (!response.ok) {
            throw new Error(`Error ${response.status}: ${response.statusText}`);
        }
        
        const usuario = await response.json();
        mostrarModalDetalles(usuario);
        
    } catch (error) {
        console.error('Error al obtener detalles del usuario:', error);
        mostrarNotificacion('Error al cargar detalles del usuario', 'error');
    }
}

async function editarUsuario(userId) {
    try {
        console.log('Editar usuario:', userId);
        const url = buildAuthUrl(`/usuarios_admin/usuarios/${userId}`);
        const response = await fetch(url);
        
        if (!response.ok) {
            throw new Error(`Error ${response.status}: ${response.statusText}`);
        }
        
        const usuario = await response.json();
        mostrarModalEdicion(usuario);
        
    } catch (error) {
        console.error('Error al cargar usuario para edición:', error);
        mostrarNotificacion('Error al cargar datos del usuario', 'error');
    }
}

async function eliminarUsuario(userId) {
    try {
        console.log('Eliminar usuario:', userId);
        
        if (!confirm('¿Estás seguro de que quieres eliminar este usuario? Esta acción no se puede deshacer.')) {
            return;
        }
          const url = buildAuthUrl(`/usuarios_admin/usuarios/${userId}`);
        const response = await fetch(url, {
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
}

async function toggleUsuarioStatus(userId) {
    try {
        console.log('Toggle status del usuario:', userId);
        
        if (!confirm('¿Estás seguro de que quieres cambiar el estado de este usuario?')) {
            return;
        }
          const url = buildAuthUrl(`/usuarios_admin/usuarios/${userId}/toggle-status`);
        const response = await fetch(url, {
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
}

async function resetearPassword(userId) {
    try {
        if (!confirm('¿Estás seguro de que quieres resetear la contraseña de este usuario?')) {
            return;
        }
        
        const url = buildAuthUrl(`/usuarios_admin/usuarios/${userId}/resetear-password`);
        const response = await fetch(url, {
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
}

function crearNuevoUsuario() {
    mostrarModalNuevoUsuario();
}

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
        { text: 'Editar', class: 'bg-blue-600 hover:bg-blue-700 text-white', action: 'edit', userId: usuario.id },
        { text: 'Cerrar', class: 'bg-gray-300 hover:bg-gray-400 text-gray-700', action: 'close' }
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
        { text: 'Guardar Cambios', class: 'bg-blue-600 hover:bg-blue-700 text-white', action: 'save', userId: usuario.id },
        { text: 'Cancelar', class: 'bg-gray-300 hover:bg-gray-400 text-gray-700', action: 'close' }
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
        { text: 'Crear Usuario', class: 'bg-green-600 hover:bg-green-700 text-white', action: 'create' },
        { text: 'Cancelar', class: 'bg-gray-300 hover:bg-gray-400 text-gray-700', action: 'close' }
    ]);
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
                    <button class="text-gray-400 hover:text-gray-600 btn-cerrar-modal">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                <div class="mt-2 px-7 py-3">
                    ${contenido}
                </div>
                <div class="items-center px-4 py-3">
                    <div class="flex space-x-3 justify-end">
                        ${botones.map((boton, index) => `
                            <button class="px-4 py-2 rounded-md text-sm font-medium ${boton.class} btn-modal-action" 
                                data-action="${boton.action}" data-user-id="${boton.userId || ''}">${boton.text}</button>
                        `).join('')}
                    </div>
                </div>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    // Configurar event listeners del modal
    modal.querySelector('.btn-cerrar-modal').addEventListener('click', cerrarModal);
    
    modal.querySelectorAll('.btn-modal-action').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const action = e.target.getAttribute('data-action');
            const userId = e.target.getAttribute('data-user-id');
            
            switch(action) {
                case 'close':
                    cerrarModal();
                    break;
                case 'edit':
                    cerrarModal();
                    editarUsuario(parseInt(userId));
                    break;
                case 'save':
                    guardarEdicionUsuario(parseInt(userId));
                    break;
                case 'create':
                    guardarNuevoUsuario();
                    break;
                case 'create-rol':
                    guardarNuevoRol();
                    break;
                case 'save-rol':
                    guardarEdicionRol(parseInt(userId));
                    break;
            }
        });
    });
    
    return modal;
}

function cerrarModal() {
    const modal = document.getElementById('modal-overlay');
    if (modal) {
        modal.remove();
    }
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
          const url = buildAuthUrl(`/usuarios_admin/usuarios/${userId}`);
        const response = await fetch(url, {
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
          const url = buildAuthUrl('/usuarios_admin/usuarios/');
        const response = await fetch(url, {
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

// ==================== FUNCIONES PARA GESTIÓN DE ROLES ====================

function mostrarModalNuevoRol() {
    const modal = crearModal('Crear Nuevo Rol', `
        <form id="formNuevoRol" class="space-y-4">
            <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Nombre del Rol *</label>
                <input type="text" id="new_rol_nombre" required 
                    class="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500">
            </div>
            <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Descripción</label>
                <textarea id="new_rol_descripcion" rows="3"
                    class="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"></textarea>
            </div>
            <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Permisos</label>
                <div class="space-y-2">
                    <label class="flex items-center">
                        <input type="checkbox" class="rounded border-gray-300 permiso-checkbox" value="usuarios.ver">
                        <span class="ml-2 text-sm text-gray-700">Ver usuarios</span>
                    </label>
                    <label class="flex items-center">
                        <input type="checkbox" class="rounded border-gray-300 permiso-checkbox" value="usuarios.crear">
                        <span class="ml-2 text-sm text-gray-700">Crear usuarios</span>
                    </label>
                    <label class="flex items-center">
                        <input type="checkbox" class="rounded border-gray-300 permiso-checkbox" value="usuarios.editar">
                        <span class="ml-2 text-sm text-gray-700">Editar usuarios</span>
                    </label>
                    <label class="flex items-center">
                        <input type="checkbox" class="rounded border-gray-300 permiso-checkbox" value="usuarios.eliminar">
                        <span class="ml-2 text-sm text-gray-700">Eliminar usuarios</span>
                    </label>
                </div>
            </div>
        </form>
    `, [
        { text: 'Crear Rol', class: 'bg-green-600 hover:bg-green-700 text-white', action: 'create-rol' },
        { text: 'Cancelar', class: 'bg-gray-300 hover:bg-gray-400 text-gray-700', action: 'close' }
    ]);
}

function editarRol(rolId) {
    const rol = roles.find(r => r.id === rolId);
    if (!rol) {
        mostrarNotificacion('Rol no encontrado', 'error');
        return;
    }
    
    const modal = crearModal('Editar Rol', `
        <form id="formEditarRol" class="space-y-4">
            <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Nombre del Rol *</label>
                <input type="text" id="edit_rol_nombre" value="${rol.nombre}" required 
                    class="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500">
            </div>
            <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Descripción</label>
                <textarea id="edit_rol_descripcion" rows="3"
                    class="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500">${rol.descripcion}</textarea>
            </div>
        </form>
    `, [
        { text: 'Guardar Cambios', class: 'bg-blue-600 hover:bg-blue-700 text-white', action: 'save-rol', userId: rolId },
        { text: 'Cancelar', class: 'bg-gray-300 hover:bg-gray-400 text-gray-700', action: 'close' }
    ]);
}

function eliminarRol(rolId) {
    const rol = roles.find(r => r.id === rolId);
    if (!rol) {
        mostrarNotificacion('Rol no encontrado', 'error');
        return;
    }
    
    if (!confirm(`¿Estás seguro de que quieres eliminar el rol "${rol.nombre}"? Esta acción no se puede deshacer.`)) {
        return;
    }
    
    mostrarNotificacion('Rol eliminado exitosamente', 'success');
    cargarRoles(); // Recargar roles
}

async function guardarNuevoRol() {
    try {
        const nombre = document.getElementById('new_rol_nombre').value;
        const descripcion = document.getElementById('new_rol_descripcion').value;
        
        if (!nombre) {
            mostrarNotificacion('El nombre del rol es obligatorio', 'error');
            return;
        }
        
        // Simular creación de rol
        mostrarNotificacion('Rol creado exitosamente', 'success');
        cerrarModal();
        cargarRoles();
        
    } catch (error) {
        console.error('Error al crear rol:', error);
        mostrarNotificacion('Error al crear rol', 'error');
    }
}

async function guardarEdicionRol(rolId) {
    try {
        const nombre = document.getElementById('edit_rol_nombre').value;
        const descripcion = document.getElementById('edit_rol_descripcion').value;
        
        if (!nombre) {
            mostrarNotificacion('El nombre del rol es obligatorio', 'error');
            return;
        }
        
        // Simular edición de rol
        mostrarNotificacion('Rol actualizado exitosamente', 'success');
        cerrarModal();
        cargarRoles();
        
    } catch (error) {
        console.error('Error al actualizar rol:', error);
        mostrarNotificacion('Error al actualizar rol', 'error');
    }
}

// ==================== FUNCIONES PARA PERMISOS Y AUDITORÍA ====================

async function cargarPermisos() {
    try {
        console.log('🔐 Cargando permisos...');
        const url = buildAuthUrl('/usuarios_admin/permisos/');
        const response = await fetch(url);
        
        if (!response.ok) {
            throw new Error(`Error ${response.status}: ${response.statusText}`);
        }
        
        const permisos = await response.json();
        console.log('✅ Permisos cargados:', permisos.length);
        
        renderizarPermisos(permisos);
        
    } catch (error) {
        console.error('❌ Error al cargar permisos:', error);
        mostrarNotificacion('Error al cargar permisos: ' + error.message, 'error');
        // Renderizar permisos estáticos en caso de error
        renderizarPermisos([]);
    }
}

async function cargarAuditoria() {
    try {
        console.log('📋 Cargando auditoría...');
        const url = buildAuthUrl('/usuarios_admin/auditoria/');
        const response = await fetch(url);
        
        if (!response.ok) {
            throw new Error(`Error ${response.status}: ${response.statusText}`);
        }
        
        const auditoria = await response.json();
        console.log('✅ Auditoría cargada:', auditoria.logs.length, 'logs');
        
        renderizarAuditoria(auditoria);
        
    } catch (error) {
        console.error('❌ Error al cargar auditoría:', error);
        mostrarNotificacion('Error al cargar auditoría: ' + error.message, 'error');
        // Renderizar auditoría vacía en caso de error
        renderizarAuditoria({ logs: [], total: 0 });
    }
}

function renderizarPermisos(permisos) {
    const contentPermisos = document.getElementById('content-permisos');
    if (!contentPermisos) return;
    
    if (!permisos || permisos.length === 0) {
        // Renderizar contenido estático si no hay datos
        contentPermisos.innerHTML = `
            <div class="bg-white rounded-lg shadow-md p-6">
                <div class="flex justify-between items-center mb-6">
                    <h3 class="text-lg font-semibold text-gray-800">
                        <i class="fas fa-shield-alt mr-2"></i>
                        Gestión de Permisos
                    </h3>
                    <button id="btnNuevoPermiso" class="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg text-sm transition-colors duration-200">
                        <i class="fas fa-plus mr-2"></i>
                        Nuevo Permiso
                    </button>
                </div>
                
                <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    <div class="space-y-4">
                        <h4 class="text-md font-medium text-gray-800">Permisos por Módulo</h4>
                        
                        <div class="border border-gray-200 rounded-lg">
                            <div class="bg-gray-50 px-4 py-3 border-b border-gray-200">
                                <h5 class="font-medium text-gray-800">👥 Gestión de Usuarios</h5>
                            </div>
                            <div class="p-4 space-y-2">
                                <div class="flex justify-between items-center">
                                    <span class="text-sm text-gray-700">Ver usuarios</span>
                                    <span class="text-xs bg-green-100 text-green-800 px-2 py-1 rounded">Activo</span>
                                </div>
                                <div class="flex justify-between items-center">
                                    <span class="text-sm text-gray-700">Crear usuarios</span>
                                    <span class="text-xs bg-green-100 text-green-800 px-2 py-1 rounded">Activo</span>
                                </div>
                                <div class="flex justify-between items-center">
                                    <span class="text-sm text-gray-700">Editar usuarios</span>
                                    <span class="text-xs bg-green-100 text-green-800 px-2 py-1 rounded">Activo</span>
                                </div>
                                <div class="flex justify-between items-center">
                                    <span class="text-sm text-gray-700">Eliminar usuarios</span>
                                    <span class="text-xs bg-red-100 text-red-800 px-2 py-1 rounded">Restringido</span>
                                </div>
                            </div>
                        </div>
                        
                        <div class="border border-gray-200 rounded-lg">
                            <div class="bg-gray-50 px-4 py-3 border-b border-gray-200">
                                <h5 class="font-medium text-gray-800">🎫 Gestión de Tickets</h5>
                            </div>
                            <div class="p-4 space-y-2">
                                <div class="flex justify-between items-center">
                                    <span class="text-sm text-gray-700">Ver tickets</span>
                                    <span class="text-xs bg-green-100 text-green-800 px-2 py-1 rounded">Activo</span>
                                </div>
                                <div class="flex justify-between items-center">
                                    <span class="text-sm text-gray-700">Crear tickets</span>
                                    <span class="text-xs bg-green-100 text-green-800 px-2 py-1 rounded">Activo</span>
                                </div>
                                <div class="flex justify-between items-center">
                                    <span class="text-sm text-gray-700">Asignar tickets</span>
                                    <span class="text-xs bg-yellow-100 text-yellow-800 px-2 py-1 rounded">Solo Admin</span>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="space-y-4">
                        <h4 class="text-md font-medium text-gray-800">Matriz de Permisos por Rol</h4>
                        
                        <div class="overflow-x-auto">
                            <table class="min-w-full border border-gray-200 rounded-lg">
                                <thead class="bg-gray-50">
                                    <tr>
                                        <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Acción</th>
                                        <th class="px-4 py-2 text-center text-xs font-medium text-gray-500 uppercase">Admin</th>
                                        <th class="px-4 py-2 text-center text-xs font-medium text-gray-500 uppercase">Manager</th>
                                        <th class="px-4 py-2 text-center text-xs font-medium text-gray-500 uppercase">Usuario</th>
                                    </tr>
                                </thead>
                                <tbody class="divide-y divide-gray-200">
                                    <tr>
                                        <td class="px-4 py-2 text-sm text-gray-700">Gestionar usuarios</td>
                                        <td class="px-4 py-2 text-center"><i class="fas fa-check text-green-600"></i></td>
                                        <td class="px-4 py-2 text-center"><i class="fas fa-times text-red-600"></i></td>
                                        <td class="px-4 py-2 text-center"><i class="fas fa-times text-red-600"></i></td>
                                    </tr>
                                    <tr class="bg-gray-50">
                                        <td class="px-4 py-2 text-sm text-gray-700">Ver reportes</td>
                                        <td class="px-4 py-2 text-center"><i class="fas fa-check text-green-600"></i></td>
                                        <td class="px-4 py-2 text-center"><i class="fas fa-check text-green-600"></i></td>
                                        <td class="px-4 py-2 text-center"><i class="fas fa-times text-red-600"></i></td>
                                    </tr>
                                    <tr>
                                        <td class="px-4 py-2 text-sm text-gray-700">Crear tickets</td>
                                        <td class="px-4 py-2 text-center"><i class="fas fa-check text-green-600"></i></td>
                                        <td class="px-4 py-2 text-center"><i class="fas fa-check text-green-600"></i></td>
                                        <td class="px-4 py-2 text-center"><i class="fas fa-check text-green-600"></i></td>
                                    </tr>
                                    <tr class="bg-gray-50">
                                        <td class="px-4 py-2 text-sm text-gray-700">Configurar sistema</td>
                                        <td class="px-4 py-2 text-center"><i class="fas fa-check text-green-600"></i></td>
                                        <td class="px-4 py-2 text-center"><i class="fas fa-times text-red-600"></i></td>
                                        <td class="px-4 py-2 text-center"><i class="fas fa-times text-red-600"></i></td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        `;
        return;
    }
    
    // Si hay datos de permisos del backend, renderizar dinámicamente
    // Agrupar permisos por categoría
    const permisosPorCategoria = {};
    permisos.forEach(permiso => {
        if (!permisosPorCategoria[permiso.categoria]) {
            permisosPorCategoria[permiso.categoria] = [];
        }
        permisosPorCategoria[permiso.categoria].push(permiso);
    });
    
    let html = `
        <div class="bg-white rounded-lg shadow-md p-6">
            <div class="flex justify-between items-center mb-6">
                <h3 class="text-lg font-semibold text-gray-800">
                    <i class="fas fa-shield-alt mr-2"></i>
                    Gestión de Permisos
                </h3>
                <button id="btnNuevoPermiso" class="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg text-sm transition-colors duration-200">
                    <i class="fas fa-plus mr-2"></i>
                    Nuevo Permiso
                </button>
            </div>
    `;
    
    Object.keys(permisosPorCategoria).forEach(categoria => {
        html += `
            <div class="bg-white rounded-lg shadow-md mb-6">
                <div class="bg-gray-50 px-6 py-3 border-b">
                    <h3 class="text-lg font-semibold text-gray-800">${categoria}</h3>
                </div>
                <div class="p-6">
                    <div class="space-y-4">
        `;
        
        permisosPorCategoria[categoria].forEach(permiso => {
            const rolesHtml = permiso.roles_asignados.map(rol => 
                `<span class="inline-block bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded-full mr-1">${rol}</span>`
            ).join('');
            
            html += `
                <div class="flex items-center justify-between border-b pb-3">
                    <div class="flex-1">
                        <div class="flex items-center">
                            <i class="fas fa-key text-gray-400 mr-3"></i>
                            <div>
                                <h4 class="font-medium text-gray-900">${permiso.nombre}</h4>
                                <p class="text-sm text-gray-600">${permiso.descripcion}</p>
                            </div>
                        </div>
                    </div>
                    <div class="ml-4">
                        <div class="text-sm text-gray-500 mb-1">Asignado a:</div>
                        <div>${rolesHtml}</div>
                    </div>
                </div>
            `;
        });
        
        html += `
                    </div>
                </div>
            </div>
        `;
    });
    
    html += `</div>`;
    contentPermisos.innerHTML = html;
}

function renderizarAuditoria(auditoria) {
    const contentAuditoria = document.getElementById('content-auditoria');
    if (!contentAuditoria) return;
    
    if (!auditoria || !auditoria.logs || auditoria.logs.length === 0) {
        contentAuditoria.innerHTML = `
            <div class="text-center py-8">
                <i class="fas fa-clipboard-list text-4xl text-gray-300 mb-4"></i>
                <p class="text-gray-500 text-lg">No hay logs de auditoría disponibles</p>
                <p class="text-gray-400 text-sm">Los logs aparecerán aquí cuando se realicen acciones en el sistema</p>
            </div>
        `;
        return;
    }
    
    // Calcular estadísticas
    const exitos = auditoria.logs.filter(log => log.resultado === 'ÉXITO').length;
    const fallos = auditoria.logs.filter(log => log.resultado === 'FALLO').length;
    const usuariosUnicos = new Set(auditoria.logs.map(log => log.usuario)).size;
    
    let html = `
        <!-- Estadísticas de auditoría -->
        <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
            <div class="bg-blue-50 p-4 rounded-lg">
                <div class="flex items-center">
                    <i class="fas fa-list-alt text-blue-600 text-2xl mr-3"></i>
                    <div>
                        <p class="text-sm text-blue-600">Total Eventos</p>
                        <p class="text-2xl font-bold text-blue-800">${auditoria.total || auditoria.logs.length}</p>
                    </div>
                </div>
            </div>
            <div class="bg-green-50 p-4 rounded-lg">
                <div class="flex items-center">
                    <i class="fas fa-check-circle text-green-600 text-2xl mr-3"></i>
                    <div>
                        <p class="text-sm text-green-600">Éxitos</p>
                        <p class="text-2xl font-bold text-green-800">${exitos}</p>
                    </div>
                </div>
            </div>
            <div class="bg-red-50 p-4 rounded-lg">
                <div class="flex items-center">
                    <i class="fas fa-exclamation-circle text-red-600 text-2xl mr-3"></i>
                    <div>
                        <p class="text-sm text-red-600">Fallos</p>
                        <p class="text-2xl font-bold text-red-800">${fallos}</p>
                    </div>
                </div>
            </div>
            <div class="bg-purple-50 p-4 rounded-lg">
                <div class="flex items-center">
                    <i class="fas fa-users text-purple-600 text-2xl mr-3"></i>
                    <div>
                        <p class="text-sm text-purple-600">Usuarios Únicos</p>
                        <p class="text-2xl font-bold text-purple-800">${usuariosUnicos}</p>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Tabla de logs -->
        <div class="bg-white rounded-lg shadow-md">
            <div class="px-6 py-4 border-b border-gray-200">
                <h3 class="text-lg font-semibold text-gray-800">Registro de Actividad</h3>
            </div>
            <div class="overflow-x-auto">
                <table class="min-w-full divide-y divide-gray-200">
                    <thead class="bg-gray-50">
                        <tr>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Fecha</th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Usuario</th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Acción</th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Módulo</th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Resultado</th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">IP</th>
                        </tr>
                    </thead>
                    <tbody class="bg-white divide-y divide-gray-200">
    `;
    
    auditoria.logs.forEach(log => {
        const fecha = new Date(log.fecha).toLocaleString('es-ES');
        const resultadoClass = log.resultado === 'ÉXITO' ? 'text-green-800 bg-green-100' : 'text-red-800 bg-red-100';
        
        // Iconos por tipo de acción
        const iconos = {
            'LOGIN_SUCCESS': 'fas fa-sign-in-alt',
            'LOGIN_FAILED': 'fas fa-sign-in-alt',
            'USER_CREATED': 'fas fa-user-plus',
            'USER_UPDATED': 'fas fa-user-edit',
            'USER_DELETED': 'fas fa-user-minus',
            'PASSWORD_CHANGED': 'fas fa-key',
            'ROLE_ASSIGNED': 'fas fa-user-tag',
            'LOGOUT': 'fas fa-sign-out-alt',
            'DATA_MIGRATION': 'fas fa-database',
            'REPORT_GENERATED': 'fas fa-chart-bar',
            'SYSTEM_CONFIG_CHANGED': 'fas fa-cogs'
        };
        const iconoAccion = iconos[log.accion] || 'fas fa-info-circle';
        
        html += `
            <tr class="hover:bg-gray-50">
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${fecha}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">${log.usuario}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    <div class="flex items-center">
                        <i class="${iconoAccion} text-gray-400 mr-2"></i>
                        <div>
                            <div class="font-medium">${log.accion.replace(/_/g, ' ')}</div>
                            <div class="text-xs text-gray-500">${log.descripcion}</div>
                        </div>
                    </div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    <span class="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-gray-100 text-gray-800">
                        ${log.modulo}
                    </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm">
                    <span class="inline-flex px-2 py-1 text-xs font-semibold rounded-full ${resultadoClass}">
                        ${log.resultado}
                    </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${log.ip}</td>
            </tr>
        `;
    });
    
    html += `
                    </tbody>
                </table>
            </div>
        </div>
    `;
    
    contentAuditoria.innerHTML = html;
}

// ==================== FIN DE FUNCIONES ====================

// ==================== UTILIDADES ====================

function actualizarPaginacion() {
    totalPaginas = Math.ceil(usuarios.length / usuariosPorPagina);
    
    // Actualizar información de rango
    const startRange = document.getElementById('startRange');
    const endRange = document.getElementById('endRange');
    const totalUsuarios = document.getElementById('totalUsuarios');
    
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
    const usuariosTableBody = document.getElementById('users-table-body');
    if (usuariosTableBody) {
        usuariosTableBody.innerHTML = `
            <tr>
                <td colspan="7" class="px-6 py-8 text-center text-red-500">
                    <i class="fas fa-exclamation-triangle text-4xl mb-4"></i>
                    <p class="text-lg">Error al cargar usuarios</p>
                    <button class="mt-2 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 btn-reintentar">
                        Reintentar
                    </button>
                </td>
            </tr>
        `;
        
        // Event listener para el botón de reintentar
        const btnReintentar = usuariosTableBody.querySelector('.btn-reintentar');
        if (btnReintentar) {
            btnReintentar.addEventListener('click', cargarUsuarios);
        }
    }
}

function mostrarNotificacion(mensaje, tipo = 'info') {
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
                <button class="ml-3 text-white hover:text-gray-200 btn-cerrar-notificacion">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        </div>
    `;
    
    contenedor.appendChild(notificacion);
    
    // Event listener para cerrar notificación
    notificacion.querySelector('.btn-cerrar-notificacion').addEventListener('click', () => {
        notificacion.remove();
    });
    
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

// ==================== EVENT LISTENERS PRINCIPALES ====================
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
    
    // Pestañas de navegación
    const tabUsuarios = document.getElementById('tab-usuarios');
    const tabRoles = document.getElementById('tab-roles');
    const tabPermisos = document.getElementById('tab-permisos');
    const tabAuditoria = document.getElementById('tab-auditoria');
    
    if (tabUsuarios) {
        tabUsuarios.addEventListener('click', () => cambiarTab('usuarios'));
    }
    if (tabRoles) {
        tabRoles.addEventListener('click', () => cambiarTab('roles'));
    }
    if (tabPermisos) {
        tabPermisos.addEventListener('click', () => cambiarTab('permisos'));
    }
    if (tabAuditoria) {
        tabAuditoria.addEventListener('click', () => cambiarTab('auditoria'));
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

// ==================== CARGA DE DATOS ESTADÍSTICOS, ROLES, PERMISOS Y AUDITORÍA ====================

async function cargarEstadisticas() {
    try {
        console.log('📊 Cargando estadísticas...');
        const url = buildAuthUrl('/usuarios_admin/estadisticas-avanzadas/');
        const response = await fetch(url);
        
        if (!response.ok) {
            throw new Error(`Error ${response.status}: ${response.statusText}`);
        }
        
        const estadisticas = await response.json();
        console.log('📊 Estadísticas cargadas:', estadisticas);
        
        // Actualizar elementos de estadísticas usando los datos del resumen
        const totalUsersElement = document.getElementById('total-users');
        const activeUsersElement = document.getElementById('active-users');
        const adminUsersElement = document.getElementById('admin-users');
        const totalRolesElement = document.getElementById('total-roles');
        
        if (totalUsersElement) {
            totalUsersElement.textContent = estadisticas.resumen.total_usuarios || 0;
            console.log('📊 Total usuarios actualizado:', estadisticas.resumen.total_usuarios);
        }
        if (activeUsersElement) {
            activeUsersElement.textContent = estadisticas.resumen.usuarios_activos || 0;
            console.log('📊 Usuarios activos actualizado:', estadisticas.resumen.usuarios_activos);
        }
        if (adminUsersElement) {
            // Usar total_administradores del resumen, no del por_roles
            const adminCount = estadisticas.resumen.total_administradores || 
                              estadisticas.por_roles.admin || 
                              estadisticas.por_roles.administrador || 1;
            adminUsersElement.textContent = adminCount;
            console.log('📊 Administradores actualizado:', adminCount);
        }
        if (totalRolesElement) {
            const totalRoles = estadisticas.resumen.total_roles || 
                              Object.keys(estadisticas.por_roles || {}).length || 0;
            totalRolesElement.textContent = totalRoles;
            console.log('📊 Total roles actualizado:', totalRoles);
        }
        
        return estadisticas;
        
    } catch (error) {
        console.error('❌ Error al cargar estadísticas:', error);
        // Valores por defecto en caso de error
        const totalUsersElement = document.getElementById('total-users');
        const activeUsersElement = document.getElementById('active-users');
        const adminUsersElement = document.getElementById('admin-users');
        const totalRolesElement = document.getElementById('total-roles');
        
        if (totalUsersElement) totalUsersElement.textContent = '0';
        if (activeUsersElement) activeUsersElement.textContent = '0';
        if (adminUsersElement) adminUsersElement.textContent = '0';
        if (totalRolesElement) totalRolesElement.textContent = '0';
        
        mostrarNotificacion('Error al cargar estadísticas: ' + error.message, 'error');
    }
}

async function cargarRoles() {
    try {
        console.log('🏷️ Cargando roles...');
        const url = buildAuthUrl('/usuarios_admin/roles/');
        const response = await fetch(url);
        
        if (!response.ok) {
            throw new Error(`Error ${response.status}: ${response.statusText}`);
        }
        
        roles = await response.json();
        console.log('✅ Roles cargados:', roles.length);
        
        renderizarRoles();
        
    } catch (error) {
        console.error('❌ Error al cargar roles:', error);
        mostrarNotificacion('Error al cargar roles: ' + error.message, 'error');
    }
}

function renderizarRoles() {
    const contentRoles = document.getElementById('content-roles');
    if (!contentRoles) return;
    
    contentRoles.innerHTML = `
        <div class="bg-white rounded-lg shadow-md p-6">
            <div class="flex justify-between items-center mb-6">
                <h3 class="text-lg font-semibold text-gray-800">
                    <i class="fas fa-tags mr-2"></i>
                    Gestión de Roles
                </h3>
                <button id="btnNuevoRol" class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm transition-colors duration-200">
                    <i class="fas fa-plus mr-2"></i>
                    Nuevo Rol
                </button>
            </div>
            
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                ${roles.map(rol => `
                    <div class="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow duration-200">
                        <div class="flex justify-between items-start mb-3">
                            <h4 class="text-lg font-medium text-gray-900">${rol.nombre}</h4>
                            <div class="flex space-x-2">
                                <button class="text-blue-600 hover:text-blue-800 btn-editar-rol" data-rol-id="${rol.id}" title="Editar rol">
                                    <i class="fas fa-edit"></i>
                                </button>
                                <button class="text-red-600 hover:text-red-800 btn-eliminar-rol" data-rol-id="${rol.id}" title="Eliminar rol">
                                    <i class="fas fa-trash"></i>
                                </button>
                            </div>
                        </div>
                        <p class="text-gray-600 text-sm mb-3">${rol.descripcion}</p>
                        <div class="flex justify-between items-center text-sm">
                            <span class="text-gray-500">${rol.usuarios_count} usuarios</span>
                            <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                                ${rol.nombre}
                            </span>
                        </div>
                    </div>
                `).join('')}
            </div>
        </div>
    `;
    
    // Configurar event listeners
    configurarEventosRoles();
}

function configurarEventosRoles() {
    // Botón nuevo rol
    const btnNuevoRol = document.getElementById('btnNuevoRol');
    if (btnNuevoRol) {
        btnNuevoRol.addEventListener('click', () => {
            mostrarModalNuevoRol();
        });
    }
    
    // Botones de editar rol
    document.querySelectorAll('.btn-editar-rol').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const rolId = e.currentTarget.getAttribute('data-rol-id');
            editarRol(parseInt(rolId));
        });
    });
    
    // Botones de eliminar rol
    document.querySelectorAll('.btn-eliminar-rol').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const rolId = e.currentTarget.getAttribute('data-rol-id');
            eliminarRol(parseInt(rolId));
        });
    });
}

function renderizarPermisos() {
    const contentPermisos = document.getElementById('content-permisos');
    if (!contentPermisos) return;
    
    contentPermisos.innerHTML = `
        <div class="bg-white rounded-lg shadow-md p-6">
            <div class="flex justify-between items-center mb-6">
                <h3 class="text-lg font-semibold text-gray-800">
                    <i class="fas fa-shield-alt mr-2"></i>
                    Gestión de Permisos
                </h3>
                <button id="btnNuevoPermiso" class="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg text-sm transition-colors duration-200">
                    <i class="fas fa-plus mr-2"></i>
                    Nuevo Permiso
                </button>
            </div>
            
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div class="space-y-4">
                    <h4 class="text-md font-medium text-gray-800">Permisos por Módulo</h4>
                    
                    <div class="border border-gray-200 rounded-lg">
                        <div class="bg-gray-50 px-4 py-3 border-b border-gray-200">
                            <h5 class="font-medium text-gray-800">👥 Gestión de Usuarios</h5>
                        </div>
                        <div class="p-4 space-y-2">
                            <div class="flex justify-between items-center">
                                <span class="text-sm text-gray-700">Ver usuarios</span>
                                <span class="text-xs bg-green-100 text-green-800 px-2 py-1 rounded">Activo</span>
                            </div>
                            <div class="flex justify-between items-center">
                                <span class="text-sm text-gray-700">Crear usuarios</span>
                                <span class="text-xs bg-green-100 text-green-800 px-2 py-1 rounded">Activo</span>
                            </div>
                            <div class="flex justify-between items-center">
                                <span class="text-sm text-gray-700">Editar usuarios</span>
                                <span class="text-xs bg-green-100 text-green-800 px-2 py-1 rounded">Activo</span>
                            </div>
                            <div class="flex justify-between items-center">
                                <span class="text-sm text-gray-700">Eliminar usuarios</span>
                                <span class="text-xs bg-red-100 text-red-800 px-2 py-1 rounded">Restringido</span>
                            </div>
                        </div>
                    </div>
                    
                    <div class="border border-gray-200 rounded-lg">
                        <div class="bg-gray-50 px-4 py-3 border-b border-gray-200">
                            <h5 class="font-medium text-gray-800">🎫 Gestión de Tickets</h5>
                        </div>
                        <div class="p-4 space-y-2">
                            <div class="flex justify-between items-center">
                                <span class="text-sm text-gray-700">Ver tickets</span>
                                <span class="text-xs bg-green-100 text-green-800 px-2 py-1 rounded">Activo</span>
                            </div>
                            <div class="flex justify-between items-center">
                                <span class="text-sm text-gray-700">Crear tickets</span>
                                <span class="text-xs bg-green-100 text-green-800 px-2 py-1 rounded">Activo</span>
                            </div>
                            <div class="flex justify-between items-center">
                                <span class="text-sm text-gray-700">Asignar tickets</span>
                                <span class="text-xs bg-yellow-100 text-yellow-800 px-2 py-1 rounded">Solo Admin</span>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="space-y-4">
                    <h4 class="text-md font-medium text-gray-800">Matriz de Permisos por Rol</h4>
                    
                    <div class="overflow-x-auto">
                        <table class="min-w-full border border-gray-200 rounded-lg">
                            <thead class="bg-gray-50">
                                <tr>
                                    <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Acción</th>
                                    <th class="px-4 py-2 text-center text-xs font-medium text-gray-500 uppercase">Admin</th>
                                    <th class="px-4 py-2 text-center text-xs font-medium text-gray-500 uppercase">Manager</th>
                                    <th class="px-4 py-2 text-center text-xs font-medium text-gray-500 uppercase">Usuario</th>
                                </tr>
                            </thead>
                            <tbody class="divide-y divide-gray-200">
                                <tr>
                                    <td class="px-4 py-2 text-sm text-gray-700">Gestionar usuarios</td>
                                    <td class="px-4 py-2 text-center"><i class="fas fa-check text-green-600"></i></td>
                                    <td class="px-4 py-2 text-center"><i class="fas fa-times text-red-600"></i></td>
                                    <td class="px-4 py-2 text-center"><i class="fas fa-times text-red-600"></i></td>
                                </tr>
                                <tr class="bg-gray-50">
                                    <td class="px-4 py-2 text-sm text-gray-700">Ver reportes</td>
                                    <td class="px-4 py-2 text-center"><i class="fas fa-check text-green-600"></i></td>
                                    <td class="px-4 py-2 text-center"><i class="fas fa-check text-green-600"></i></td>
                                    <td class="px-4 py-2 text-center"><i class="fas fa-times text-red-600"></i></td>
                                </tr>
                                <tr>
                                    <td class="px-4 py-2 text-sm text-gray-700">Crear tickets</td>
                                    <td class="px-4 py-2 text-center"><i class="fas fa-check text-green-600"></i></td>
                                    <td class="px-4 py-2 text-center"><i class="fas fa-check text-green-600"></i></td>
                                    <td class="px-4 py-2 text-center"><i class="fas fa-check text-green-600"></i></td>
                                </tr>
                                <tr class="bg-gray-50">
                                    <td class="px-4 py-2 text-sm text-gray-700">Configurar sistema</td>
                                    <td class="px-4 py-2 text-center"><i class="fas fa-check text-green-600"></i></td>
                                    <td class="px-4 py-2 text-center"><i class="fas fa-times text-red-600"></i></td>
                                    <td class="px-4 py-2 text-center"><i class="fas fa-times text-red-600"></i></td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    `;
}

function renderizarAuditoria(auditoria) {
    const contentAuditoria = document.getElementById('content-auditoria');
    if (!contentAuditoria) return;
    
    if (!auditoria || !auditoria.logs || auditoria.logs.length === 0) {
        contentAuditoria.innerHTML = `
            <div class="text-center py-8">
                <i class="fas fa-clipboard-list text-4xl text-gray-300 mb-4"></i>
                <p class="text-gray-500 text-lg">No hay logs de auditoría disponibles</p>
                <p class="text-gray-400 text-sm">Los logs aparecerán aquí cuando se realicen acciones en el sistema</p>
            </div>
        `;
        return;
    }
    
    // Calcular estadísticas
    const exitos = auditoria.logs.filter(log => log.resultado === 'ÉXITO').length;
    const fallos = auditoria.logs.filter(log => log.resultado === 'FALLO').length;
    const usuariosUnicos = new Set(auditoria.logs.map(log => log.usuario)).size;
    
    let html = `
        <!-- Estadísticas de auditoría -->
        <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
            <div class="bg-blue-50 p-4 rounded-lg">
                <div class="flex items-center">
                    <i class="fas fa-list-alt text-blue-600 text-2xl mr-3"></i>
                    <div>
                        <p class="text-sm text-blue-600">Total Eventos</p>
                        <p class="text-2xl font-bold text-blue-800">${auditoria.total || auditoria.logs.length}</p>
                    </div>
                </div>
            </div>
            <div class="bg-green-50 p-4 rounded-lg">
                <div class="flex items-center">
                    <i class="fas fa-check-circle text-green-600 text-2xl mr-3"></i>
                    <div>
                        <p class="text-sm text-green-600">Éxitos</p>
                        <p class="text-2xl font-bold text-green-800">${exitos}</p>
                    </div>
                </div>
            </div>
            <div class="bg-red-50 p-4 rounded-lg">
                <div class="flex items-center">
                    <i class="fas fa-exclamation-circle text-red-600 text-2xl mr-3"></i>
                    <div>
                        <p class="text-sm text-red-600">Fallos</p>
                        <p class="text-2xl font-bold text-red-800">${fallos}</p>
                    </div>
                </div>
            </div>
            <div class="bg-purple-50 p-4 rounded-lg">
                <div class="flex items-center">
                    <i class="fas fa-users text-purple-600 text-2xl mr-3"></i>
                    <div>
                        <p class="text-sm text-purple-600">Usuarios Únicos</p>
                        <p class="text-2xl font-bold text-purple-800">${usuariosUnicos}</p>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Tabla de logs -->
        <div class="bg-white rounded-lg shadow-md">
            <div class="px-6 py-4 border-b border-gray-200">
                <h3 class="text-lg font-semibold text-gray-800">Registro de Actividad</h3>
            </div>
            <div class="overflow-x-auto">
                <table class="min-w-full divide-y divide-gray-200">
                    <thead class="bg-gray-50">
                        <tr>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Fecha</th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Usuario</th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Acción</th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Módulo</th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Resultado</th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">IP</th>
                        </tr>
                    </thead>
                    <tbody class="bg-white divide-y divide-gray-200">
    `;
    
    auditoria.logs.forEach(log => {
        const fecha = new Date(log.fecha).toLocaleString('es-ES');
        const resultadoClass = log.resultado === 'ÉXITO' ? 'text-green-800 bg-green-100' : 'text-red-800 bg-red-100';
        
        // Iconos por tipo de acción
        const iconos = {
            'LOGIN_SUCCESS': 'fas fa-sign-in-alt',
            'LOGIN_FAILED': 'fas fa-sign-in-alt',
            'USER_CREATED': 'fas fa-user-plus',
            'USER_UPDATED': 'fas fa-user-edit',
            'USER_DELETED': 'fas fa-user-minus',
            'PASSWORD_CHANGED': 'fas fa-key',
            'ROLE_ASSIGNED': 'fas fa-user-tag',
            'LOGOUT': 'fas fa-sign-out-alt',
            'DATA_MIGRATION': 'fas fa-database',
            'REPORT_GENERATED': 'fas fa-chart-bar',
            'SYSTEM_CONFIG_CHANGED': 'fas fa-cogs'
        };
        const iconoAccion = iconos[log.accion] || 'fas fa-info-circle';
        
        html += `
            <tr class="hover:bg-gray-50">
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${fecha}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">${log.usuario}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    <div class="flex items-center">
                        <i class="${iconoAccion} text-gray-400 mr-2"></i>
                        <div>
                            <div class="font-medium">${log.accion.replace(/_/g, ' ')}</div>
                            <div class="text-xs text-gray-500">${log.descripcion}</div>
                        </div>
                    </div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    <span class="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-gray-100 text-gray-800">
                        ${log.modulo}
                    </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm">
                    <span class="inline-flex px-2 py-1 text-xs font-semibold rounded-full ${resultadoClass}">
                        ${log.resultado}
                    </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${log.ip}</td>
            </tr>
        `;
    });
    
    html += `
                    </tbody>
                </table>
            </div>
        </div>
    `;
    
    contentAuditoria.innerHTML = html;
}

// ==================== GESTIÓN DE PESTAÑAS ====================

function cambiarTab(tabName) {
    // Remover clase active de todas las pestañas
    document.querySelectorAll('.tab-button').forEach(tab => {
        tab.classList.remove('active', 'border-blue-500', 'text-blue-600');
        tab.classList.add('border-transparent', 'text-gray-500');
    });
    
    // Ocultar todo el contenido
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.add('hidden');
    });
    
    // Activar la pestaña seleccionada
    const selectedTab = document.getElementById(`tab-${tabName}`);
    if (selectedTab) {
        selectedTab.classList.add('active', 'border-blue-500', 'text-blue-600');
        selectedTab.classList.remove('border-transparent', 'text-gray-500');
    }
    
    // Mostrar el contenido correspondiente
    const selectedContent = document.getElementById(`content-${tabName}`);
    if (selectedContent) {
        selectedContent.classList.remove('hidden');
    }
    
    // Cargar datos específicos según la pestaña
    switch(tabName) {
        case 'usuarios':
            cargarUsuarios();
            break;
        case 'roles':
            cargarRoles();
            break;
        case 'permisos':
            cargarPermisos();
            break;        case 'auditoria':
            cargarAuditoria();
            break;
    }
    
    tabActual = tabName;
}

// ==================== INICIALIZACIÓN ====================
document.addEventListener('DOMContentLoaded', function() {
    // Inicializar (limpiar URL si tiene token)
    initializeToken();

    console.log('🚀 Iniciando aplicación de gestión de usuarios...');
    
    // Configurar event listeners
    setupEventListeners();
    
    // Cargar datos iniciales
    cargarUsuarios();
    cargarEstadisticas();
    
    console.log('✅ Aplicación de gestión de usuarios iniciada correctamente');
});
